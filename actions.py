import json
import requests
import time

from pyperclip import copy
from unipath import Path

from elements import Page
from settings import BASE_URL, DATA_DIR, API_KEY


class Action:

    _continue = True

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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


class CopyCustomMessage(Action):

    desc = "Copy custom message."

    def run(self):
        headers = {"Authorization": f"token {API_KEY}"}
        response = requests.get(BASE_URL + "/campaigns/", headers=headers)
        campaigns = response.json()

        # show campaign options
        complete = False
        while not complete:
            print("\nChoose from the following campaigns:\n")
            for i, campaign in enumerate(campaigns):
                print(f"{i} {campaign['name']}")
            print("")

            # get campaign selection
            try:
                choosen = input("Enter selection: ")
                choosen = campaigns[int(choosen)]
                complete = True
            except ValueError:
                print("\nNot a vaild selection. Try again.")

        # get campaign template
        response = requests.post(
            BASE_URL + "/businesses/create/",
            headers=headers,
            data={"name": self.business.name, "campaign": choosen["pk"]}
        )
        copy(response.json()["template"])
        return super().run()


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


class FindForm(Action):

    desc = "Find Form"

    def run(self):
        page = Page(self.driver)
        if page.has_form():
            print("\nSelect one of the following forms:")

            count = 1
            selected = False
            while not selected:
                forms = page.get_forms()
                for i, form in enumerate(forms):
                    if form.has_input():
                        print(f"{i} Form ID {form.id}")
                        for _input in form.get_visible_inputs():
                            print("")
                            print(f"  Name: {_input.name}")
                            print(f"  Title: {_input.title}")
                            print(f"  ID: {_input.id}")
                        print("")
                        count += 1
                    else:
                        forms.pop(i)
                print(f"{count + 1} No Form")
                print(f"{count + 2} Debug")
                print("")

                try:
                    selection = int(input("Enter selection: "))
                    form = forms[selection]
                    form.display()
                    selected = True
                except (ValueError, IndexError):
                    if selection == count + 1:
                        selected = True
                    elif selection == count + 2:
                        import IPython; IPython.embed()
                    else:
                        print("\nNot a valid option, try again.\n")
        else:
            print("\nNo form on page\n")

        return super().run()


class MoreInfo(Action):

    desc = "Display business info."

    def run(self):
        print("\n" + self.business.name)
        print(self.business.address + "\n")
        return super().run()


class Search(Action):

    desc = "Search for business"

    def run(self):
        search_options = [
            ["DuckDuckGo", "https://duckduckgo.com/?"],
            ["Google", "https://www.google.com/search?"]
        ]

        another = True
        while another:
            print("Choose from the following search options:\n")
            for i, option in enumerate(search_options):
                print(f"{i} {option[0]}")
            print("")

            try:
                choosen = int(input("Enter selection: "))
                url = search_options[choosen][1]
                url += self.business.search_params()
                self.driver.get(url)
                another = False
            except (ValueError, IndexError):
                print("\nNot a valid search option, try again.\n")
        return super().run()


class WebAddress(Action):

    desc = "Add current web address to business."

    def run(self):
        self.business.set_web_address(self.driver.current_url)

        cache_file = Path(DATA_DIR, "web_addresses.json")
        with open(cache_file) as open_file:
            web_addresses = json.load(open_file)

        if self.business.web_address in web_addresses:
            # need a prominent message to ensure not
            # contacted again
            for i in range(10):
                print()
            print("\nPreviously visited web_address!\n")
            for i in range(10):
                print()
            time.sleep(1)
        else:
            web_addresses.append(self.business.web_address)
            with open(cache_file, "w") as open_file:
                json.dump(web_addresses, open_file, indent=4)

        return super().run()
