from pathlib import Path

import typing

from decorator import catch_exception
from model import Project, Note


class USTParser:
    @classmethod
    @catch_exception
    def parse(cls, ust_path: Path):
        """Parse a UST file and return a Project object"""
        with ust_path.open("r", encoding="shift-jis") as file:
            lines = file.readlines()
        chunks = cls.__parse_chunks(lines)
        version = ""
        setting = {}
        notes = []
        for name, content in chunks.items():
            if not name:
                return
            name = name[1:-1].lstrip("#").lower()
            if name == "version":
                version = cls.__parse_version(content)
            elif name == "setting":
                setting = cls.__parse_setting(content)
            elif name.isdigit():
                if note := cls.__parse_note(content):
                    notes.append(note)
        return Project(
            version=version,
            **setting,
            notes=notes,
        )

    @staticmethod
    def __parse_chunks(lines: typing.List[str]) -> typing.Dict[str, typing.List[str]]:
        """Get a chunk from a list of lines"""
        chunk = {}
        for line in lines:
            if line.startswith("["):
                chunk[line.strip()] = []
            else:
                chunk[list(chunk.keys())[-1]].append(line.strip())
        return chunk

    @staticmethod
    def __parse_version(lines: typing.List[str]) -> typing.Optional[str]:
        """Parse the version of the UST file"""
        return lines[0] if lines else ""

    @staticmethod
    def __parse_setting(lines: typing.List[str]) -> typing.Dict[str, str]:
        """Parse the setting of the UST file"""
        setting = {}
        for line in lines:
            key, value = line.split("=")
            if key.startswith("Tool"):
                setting["tools"] = setting.get("tools", []) + [value]
            elif key.startswith("Mode"):
                setting["modes"] = setting.get("modes", []) + [value]
            elif key.startswith("Flags"):
                setting["flags"] = setting.get("flags", []) + [value]
            setting[key] = value
        return setting

    @staticmethod
    def __parse_note(lines: typing.List[str]) -> typing.Optional[Note]:
        """Parse the notes of the UST file"""
        if lines:
            return Note(
                **{
                    split[0]: split[1]
                    for line in lines
                    if len(split := line.split("=", maxsplit=1)) == 2
                }
            )


if __name__ == "__main__":
    project: Project = USTParser.parse(Path() / "assets" / "USTs" / "BALSAM VCV.ust")
    print(project.json(indent=4, ensure_ascii=False))
    project.to_file(Path())
    print(Project.from_file(Path("新規プロジェクト.okmt")).name)
