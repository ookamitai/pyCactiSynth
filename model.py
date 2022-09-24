from __future__ import annotations

import logging
import pickle
import traceback
from pathlib import Path

from pydantic import BaseModel, Field
from typing_extensions import Self

from decorator import catch_exception


class Setting:
    """A singleton class for storing settings"""

    __instance: "Setting" = None

    language: str = "en"

    program_path: Path = Path(__file__).parent
    """ Program path """

    output_path: Path = program_path / "output"
    """ Output path """

    extension: str = ".okmt"
    """ Extension of the output file, stands for Ookamitai! """

    def __init__(self, output_path: Path = None):
        if output_path is not None:
            self.output_path = output_path

    def __new__(cls, *args, **kwargs):
        # This magic method is called when a new instance is created,
        # and is the only place where we can return an existing instance
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def set_output_path(self, output_path: Path, mkdir: bool = True):
        """Set output path"""

        assert not output_path.is_file(), "Output path cannot be a file"
        self.output_path = output_path
        if mkdir:
            self.output_path.mkdir(parents=True, exist_ok=True)


class Note(BaseModel):
    length: int = Field(alias="Length", ge=0)
    lyric: str = Field(alias="Lyric")
    note_num: int = Field(alias="NoteNum", ge=0)
    pre_utterance: int = Field(alias="PreUtterance", ge=0)
    velocity: int = Field(alias="Velocity", ge=0)
    intensity: int = Field(alias="Intensity", ge=0)
    modulation: int = Field(alias="Modulation", ge=0)
    start_point: int = Field(alias="StartPoint", ge=0)


class Project(BaseModel):
    version: str = ""
    tempo: float = Field(alias="Tempo")
    tracks: int = Field(alias="Tracks")
    name: str = Field(alias="ProjectName")
    voice_dir: Path = Field(alias="VoiceDir")
    out_file: Path = Field(alias="OutFile")
    cache_dir: Path = Field(alias="CacheDir")
    notes: list[Note] = []

    def __int__(
        self,
        *notes: Note,
        data: dict = None,
        flags: list[str] = None,
        tools: list = None,
        modes: list = None,
    ):
        assert isinstance(data, dict), "data must be a dict"
        super().__init__(**data)
        self.notes = []
        self.add_note(*notes)
        self.tools = tools or []
        self.modes = modes or []
        self.flags = flags or []

    @property
    def is_empty(self) -> bool:
        """Check if the project is empty"""

        return len(self.notes) == 0

    @catch_exception
    def add_note(self, *notes: Note) -> Self:
        """
        Add notes to the project

        :param notes: Notes to add
        :return: self
        """

        self.sort_notes()

        for note in notes:
            self.notes.insert(self.find_note_index(note), note)

        return self

    @catch_exception
    def remove_note_by_index(self, index: int) -> Self:
        """
        Remove a note by index

        :param index: Index of the note to remove
        :return: self
        """

        self.notes.pop(index)
        return self

    @catch_exception
    def get_note(self, index: int) -> Note | None:
        """
        Get a note from the project

        :param index: Index of the note
        :return: Note, or None if the index is out of range
        """

        try:
            return self.notes[index]
        except IndexError:
            return None

    @catch_exception
    def sort_notes(self, reverse: bool = False) -> Self:
        """
        Sort notes by start_point, ascending by default

        :param reverse: Reverse the sort order
        :return: self
        """

        self.notes.sort(key=lambda note: note.start_point, reverse=reverse)
        return self

    @catch_exception
    def find_note_index(self, note: Note) -> int:
        """
        Find the index of a note in the project

        :param note: Note to find
        :return: Index of the note
        """

        start_points = list(
            map(
                lambda n: n.start_point,
                sorted(self.notes, key=lambda _: _.start_point),
            )
        )

        if note.start_point <= start_points[0]:
            return 0
        if note.start_point >= start_points[-1]:
            return len(self.notes) - 1
        return [
            start_points.index(start_point)
            for start_point in start_points
            if start_point > note.start_point
        ][0]

    @catch_exception
    def to_file(self, path: Path = Setting().output_path, name: str = None) -> None:
        """
        Save the project to a file

        :param path: Path to save the file, default to output_path
        :param name: Name of the file, default to the project name
        :return: None
        """

        assert isinstance(path, Path), "path must be a Path object"
        assert isinstance(name, str) or name is None, "name must be a string"
        name: str = name or self.name + Setting().extension
        path: Path = path / name
        with path.open("wb") as file:
            pickle.dump(self, file)
            logging.info(f"Saved project to {path}")

    @staticmethod
    def from_file(path: Path) -> Self:
        try:
            assert path.is_file(), f"{path} is not a file, or does not exist"
            with path.open("rb") as file:
                assert isinstance(
                    data := file.read(), bytes
                ), f"{path} is not a valid project file"
                loaded = pickle.loads(data)
                assert isinstance(
                    loaded, Project
                ), f"{path} is not a valid project file"
                return loaded
        except AssertionError as e:
            logging.error(e.args[0])
        except (EOFError, TypeError, pickle.UnpicklingError) as e:
            logging.error(f"{path} is not a valid project file")
            logging.error(e)
        except Exception as e:
            logging.error(
                f"An unknown error occurred while loading {path}\n"
                f"{''.join(traceback.format_tb(e.__traceback__))}"
            )
