from pyperclip import copy
from unipath import Path

from settings import DATA_DIR


class Action:

    _continue = True

    def __init__(self, session):
        self.session = session

    @classmethod
    def display(cls):
        if not hasattr(cls, "desc"):
            raise NotImplementedError("Must have desc attribute.")
        return cls.desc

    @property
    def name(self):
        return self.__class__.__name__

    def set_session(self):
        if self.name not in self.session["actions"]:
            self.session["actions"][self.name] = 0
        self.session["actions"][self.name] += 1

    def run(self):
        self.set_session()
        return self.session, self._continue


class Continue(Action):

    _continue = False
    desc = "Next?"


class CopyTemplateAction(Action):

    def __init__(self, file_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_name = file_name

    @property
    def name(self):
        return f"{self.__class__.__name__}: {self.file_name}"

    def display(self):
        return f"Copy {self.file_name} template to clipboard."

    def run(self):
        with open(Path(DATA_DIR, "templates", self.file_name)) as open_file:
            copy(open_file.read())
        return super().run()
