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

    file_name = ""

    @property
    def name(self):
        return f"{self.__class__.__name__}: {self.file_name}"

    def display(self):
        return f"Copy template to clipboard."

    def run(self):
        print("\nChoose from the following templates")

        selected = False
        templates = Path(DATA_DIR, "templates").listdir()
        while not selected:
            for i, template in enumerate(templates):
                print(f"{i} {template.name}")
            print("")

            try:
                template = templates[int(input("Enter selection: "))]
                with open(template) as open_file:
                    copy(open_file.read())
                selected = True
                self.file_name = template.name
            except (ValueError, IndexError):
                print("\nNot a valid option, try again.\n")

        return super().run()
