from pyperclip import copy
from unipath import Path

from settings import DATA_DIR


class Action:

    _continue = True

    @classmethod
    def display(cls):
        if not hasattr(cls, "desc"):
            raise NotImplementedError("Must have desc attribute.")
        return cls.desc

    def run(self):
        return self._continue


class Continue(Action):

    _continue = False
    desc = "Next?"


class CopyTemplateAction(Action):

    def __init__(self, file_name):
        self.file_name = file_name

    def display(self):
        return f"Copy {self.file_name} template to clipboard."

    def run(self):
        with open(Path(DATA_DIR, "templates"), self.file_name) as open_file:
            copy(open_file.read())
        return super().run()
