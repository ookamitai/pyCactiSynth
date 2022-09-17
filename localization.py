from pydantic import BaseModel

from model import Setting


class ExceptionLocalization(BaseModel):
    """ Exception localization model """

    GENERAL: str = "Exception occurred: {}"
    UNKNOWN: str = "An unknown error occurred. {}"
    OUTPUT_PATH_NOT_A_DIRECTORY: str = "Output path ({}) is not a directory"
    PROJECT_FILE_NOT_VALID: str = "{} is not a valid project file"
    PROJECT_FILE_NOT_EXIST: str = "{} is not a file, or does not exist"
    DATA_TYPE_NOT_VALID: str = "{} is not a valid data type"


class NoteLocalization(BaseModel):
    """ Note localization model """


class Language(BaseModel):
    """ Defines a language and its properties """

    name: str
    exception: ExceptionLocalization
    note: NoteLocalization


class Localization:
    """ A singleton class for storing localization """

    __instance: "Localization" = None

    languages: dict[str, Language] = {}
    """ List of languages """

    def __init__(self, *_, **__):
        print("Init")

    def __new__(cls, language: str = Setting().language):
        # This magic method is called when a new instance is created,
        # and is the only place where we can return an existing instance
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        assert language in cls.__instance.languages, f"Language {language} is not supported"
        return cls.__instance.languages[language]

    def __call__(self, language: str) -> Language:
        assert language in self.languages, f"Language {language} is not supported"
        return self.languages[language]

    def register_language(self, language: Language):
        """ Register a language """

        self.languages[language.name] = language

    def unregister_language(self, language: str):
        """ Unregister a language """

        assert language in self.languages, f"Language {language} is not supported"
        del self.languages[language]
