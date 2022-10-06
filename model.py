import logging
import pickle
import traceback
from pathlib import Path

import typing
from pydantic import BaseModel, Field, validator
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
    """ Extension of the output file, stands for ookamitai! """

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
    pre_utterance: int = Field(0, alias="PreUtterance", ge=0)
    velocity: int = Field(100, alias="Velocity", ge=0)
    intensity: int = Field(0, alias="Intensity", ge=0)
    modulation: int = Field(0, alias="Modulation", ge=0)
    start_point: int = Field(0, alias="StartPoint", ge=0)

    @validator(
        "pre_utterance", "velocity", "intensity", "modulation", "start_point", pre=True
    )
    def validate(cls, v):
        return v or 0


class Project(BaseModel):
    version: str = "OKMT 0.0.0"
    tempo: float = Field(120.00, alias="Tempo")
    tracks: int = Field(1, alias="Tracks")
    name: str = Field("Untitled", alias="ProjectName")
    voice_dir: Path = Field(Path(), alias="VoiceDir")
    out_file: Path = Field(Path(), alias="OutFile")
    cache_dir: Path = Field(Path(), alias="CacheDir")
    tools: typing.List[str] = []
    modes: typing.List[str] = []
    flags: typing.List[str] = []
    notes: typing.List[Note] = []

    def __int__(
        self,
        *notes: Note,
        data: dict = None,
        flags: typing.List[str] = None,
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
    def get_note(self, index: int) -> typing.Optional[Note]:
        """
        Get a note from the project

        :param index: Index of the note
        :return: Note, or None if the index is out of range
        """

        try:
            return self.notes[index]
        except IndexError:
            return None

    # Why sorting the notes?
    # This still doesn't make any sense to me since nearly all the start_points of the notes are zero,
    # or it's some obscure technique I didn't know
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
        name: str = (name or self.name) + Setting().extension
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


class OTOEntry(BaseModel):
    file: str = Field("", alias="FileName")
    alias: str = Field("", alias="Alias")
    offset: float = Field(0.0, alias="Offset", ge=0)
    fixed: float = Field(0.0, alias="Fixed", ge=0)
    blank: float = Field(0.0, alias="Blank", ge=0)
    preutter: float = Field(0.0, alias="PreUtter", ge=0)
    overlap: float = Field(0.0, alias="Overlap", ge=0)

    @catch_exception
    def __init__(self):
        super().__init__()

    @catch_exception
    def from_string(self, line) -> Self:

        line = line.replace("\n", "", 1)
        self.file = line.split("=", maxsplit=1)[0]
        _alias = line.split("=", maxsplit=1)[1].split(",", maxsplit=5)[0]
        self.alias = _alias if _alias != "" else self.file.split(".", maxsplit=1)[0]

        try:
            self.offset, self.fixed, self.blank, self.preutter, self.overlap = [
                float(d) for d in line.split("=", maxsplit=1)[1].split(",", maxsplit=5)[1:]
                if d.replace('-', '', 1).replace(".", "", 1).isdigit()
            ]
        except ValueError:
            self.offset, self.fixed, self.blank, self.preutter, self.overlap = (0, 0, 0, 0, 0)
            print(f"Error processing {line}, this line has been set to default values:\n"
                  f"{self.file}={self.alias},{self.offset},{self.fixed},{self.blank},{self.preutter},{self.overlap}")

        return self

    @catch_exception
    def to_string(self) -> str:
        return (
            f"{self.file}={self.alias},{self.offset},{self.fixed},{self.blank},{self.preutter},{self.overlap}"
        )


class OTOSetting(BaseModel):
    size: int = Field(0, alias="Size", ge=0)
    path: Path = None
    settings: typing.List[OTOEntry] = []

    @catch_exception
    def __init__(self):
        super().__init__()

    @catch_exception
    def from_file(self, path: Path) -> Self:
        assert isinstance(path, Path), "path must be a Path object"
        self.path = path
        count = 0
        with open(path, "r", encoding="shift-jis") as oto:
            for line in oto:
                self.settings.append(OTOEntry().from_string(line))
                count += 1
        self.size = count
        print(
            f"Loaded {count} entry from {path}" if count == 1 else f"Loaded {count} entries from {path}"
        )
        return self

    @catch_exception
    def get_entry(self, index: int) -> OTOEntry:
        return self.settings[index]

    @catch_exception
    def remove_entry(self, index: int) -> Self:
        self.settings.pop(index)
        return self

    @catch_exception
    def append_entry(self, index: int, data: OTOEntry) -> Self:
        self.settings.insert(index, data)
        return self

    @catch_exception
    def find_entry(self, target: str, data: (str, int)) -> typing.Tuple[OTOEntry]:
        ret = ()
        for entry in self.settings:
            if entry.__getattribute__(target) == data:
                ret += (entry,)

        return ret if len(ret) != 0 else (OTOEntry(),)

    @catch_exception
    def to_file(self, path: Path) -> None:
        oto = open(path, "w", encoding="shift-jis")
        count = 0
        for entry in range(len(self.settings)):
            oto.write(
                f"{self.settings[entry].to_string()}\n"
            )
            count += 1
        print(
            f"{count} entry written to {path}." if count == 1 else f"{count} entries written to {path}."
        )
        oto.close()


class VoiceBank(BaseModel):
    name: str = Field("None", alias="VoiceBank Name")
    author: str = Field("None", alias="VoiceBank Author")
    image: str = Field("None", alias="VoiceBank Icon")
    sample: str = Field("Random", alias="Sample")
    web: str = Field("None", alias="Website")
    readme: str = Field("None", alias="Readme")
    settings: typing.Dict[str, OTOSetting] = Field({}, alias="OTO Configuration")
    prefix_map: typing.Dict[str, str] = Field({}, alias="OTO Configuration")
    # ^ This has yet to be implemented

    oto_count: int = Field(0, alias="OTO Count", ge=0)
    file_count: int = Field(0, alias="File Count", ge=0)

    @catch_exception
    def __init__(self, path: Path):
        super().__init__()
        target = ["name", "author", "image", "sample", "web"]
        assert isinstance(path, Path), "path is not a Path object"
        with open(Path(path) / "character.txt", "r", encoding="shift-jis") as char:
            i = 0
            for lines in char:
                if lines.lower().startswith(f"{target[i]}="):
                    self.__setattr__(target[i], lines.split("=", 1)[1].replace("\n", "", 1))
                i += 1 if i < len(target) - 1 else 0

        with open(Path(path) / "readme.txt", "r", encoding="shift-jis") as read:
            self.readme = read.read()

        self.sample = "Random" if self.sample == "" else self.sample

        for config in Path(path).rglob('oto.ini'):
            print(f"Configuration found at {config.parent.absolute().name}/{config.name}")
            self.settings[config.parent.absolute().name] = OTOSetting().from_file(config)

        for i in range(len(self.settings)):
            self.oto_count += list(self.settings.values())[i].size

        for d in Path(path).rglob('*.wav'):
            self.file_count += 1

        print(f"Loaded VoiceBank {self.name}.")

    @catch_exception
    def find_entry(self, target: str, data: (str, int)) -> typing.Tuple[OTOEntry]:
        ret = ()
        for parent, oto in self.settings.items():
            for entry in oto.settings:
                if entry.__getattribute__(target) == data:
                    ret += (entry,)

        return ret if len(ret) != 0 else (OTOEntry(),)
