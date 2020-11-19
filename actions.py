import json

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


class AddOutcome(Action):

    _continue = False
    desc = "Set outcome."
    outcomes_cache = Path(DATA_DIR, "outcomes_cache.json")

    def __init__(self, business, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business

    def get_outcomes(self):
        with open(self.outcomes_cache) as open_file:
            return json.load(open_file)

    def set_outcomes(self, outcomes):
        with open(self.outcomes_cache, "w") as open_file:
            json.dump(outcomes, open_file, indent=4)

    def set_session(self):
        super().set_session()
        if self.outcome not in self.session["outcomes"]:
            self.session["outcomes"][self.outcome] = 0
        self.session["outcomes"][self.outcome] += 1

    def run(self):
        outcomes = self.get_outcomes()

        selected = False
        while not selected:
            print("\nChoose from the following outcomes")
            print("or enter your own outcome.\n")
            for i, outcome in enumerate(outcomes):
                print(f"{i} {outcome}")
            print("")

            try:
                choosen = input("Enter selection: ")
                choosen = outcomes[int(choosen)]
                selected = True
            except ValueError:
                print(f"\nYou entered {choosen}")
                if "y" == input("Would you like to save this outcome (y/n)? "):
                    self.set_outcomes(outcomes + [choosen])
                    selected = True

            self.outcome = choosen
            self.business.set_outcome(choosen)

        return super().run()


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
