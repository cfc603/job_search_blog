import base64
import csv
import hashlib
import json
import random

from urllib.parse import urlencode, urlparse

from selenium import webdriver
from unipath import Path

from actions import (
    AddOutcome, Continue, CopyCustomMessage,
    CopyTemplateAction, FindForm, MoreInfo,
    Search, WebAddress
)
from games import ContactFormGame
from sessions import get_new_session, store_session
from settings import DATA_DIR
from utils import get_now_str


class Business:

    path = Path(DATA_DIR, "business_files/past")

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

    @property
    def address(self):
        _d = self.data_dict
        return f"{_d['Address']}, {_d['City']}, {_d['ZIP Code']}"

    @property
    def city(self):
        return self.data_dict["City"]

    @property
    def file_name(self):
        # borrowed from
        # https://github.com/pypa/pipenv/blob/master/pipenv/project.py#L409
        _hash = hashlib.sha256(self.name.encode()).digest()[:6]
        return base64.urlsafe_b64encode(_hash).decode()

    @property
    def name(self):
        return self.data_dict["Company Name"]

    @property
    def web_address(self):
        try:
            return self.data_dict["web_address"]
        except KeyError:
            web_address = self.data_dict.get("Website")
            if web_address:
                parsed = urlparse(web_address)
                web_address = parsed.geturl()
                if not parsed.scheme:
                    web_address = "http://" + web_address
                return web_address
        return None

    def exists(self):
        return Path(self.path, self.file_name).exists()

    def search_params(self):
        return urlencode({"q": f"{self.name.lower()} {self.city.lower()}"})

    def search_url(self):
        return f"https://duckduckgo.com/?{self.search_params()}"

    def has_outcome(self):
        return "outcome" in self.data_dict

    def has_web_address(self):
        if self.web_address:
            return True
        return False

    def save(self):
        with open(Path(self.path, self.file_name), "w") as open_file:
            json.dump(self.data_dict, open_file, indent=4)

    def set_outcome(self, outcome):
        self.data_dict["outcome"] = {
            "desc": outcome,
            "time": get_now_str(),
        }

    def set_web_address(self, web_address):
        self.data_dict["web_address"] = urlparse(web_address).netloc


def main(driver, session):
    _all = []
    # iterate over each file download in project/data/business_files
    for _file in Path(DATA_DIR, "business_files").listdir("*.csv"):
        with open(_file) as open_file:
            # use DictReader to parse each row into a dict
            # https://docs.python.org/3/library/csv.html#csv.DictReader
            reader = csv.DictReader(open_file)
            for row in reader:
                _all.append(Business(row))

    # start game
    game = ContactFormGame()

    # loop over each business
    another_business = True # need a way to stop the loop
    while another_business:
        business = _all.pop(random.randint(0, len(_all)))
        if not business.exists():
            session["total"] += 1

            # try data provided web site first, if exists
            if business.has_web_address():
                try:
                    driver.get(business.web_address)
                except:
                    pass
            else:
                driver.get(business.search_url())

            # display actions
            kwargs = {
                "session": session, "business": business, "driver": driver
            }
            actions = [
                Continue(**kwargs),
                MoreInfo(**kwargs),
                WebAddress(**kwargs),
                AddOutcome(**kwargs),
                CopyTemplateAction(**kwargs),
                CopyCustomMessage(**kwargs),
                Search(**kwargs),
                FindForm(**kwargs),
            ]

            another_action = True
            while another_action:
                print("Choose from the following actions:\n")
                for i, action in enumerate(actions):
                    print(f"{i} {action.display()}")
                print("")

                try:
                    chosen_action = int(input("Enter selection: "))
                    session, another_action = actions[chosen_action].run()
                except (ValueError, IndexError):
                    print("\nNot a valid option, try again.\n")

            if business.has_outcome():
                business.save()
                game.update(session)

            if "n" == input("Next business (y/n)? ").lower():
                driver.close()
                game.display_exit()
                another_business = False

    return session


if __name__ == "__main__":
    # open chrome
    driver = webdriver.Chrome()
    driver.maximize_window()

    # create a new session
    session = get_new_session()

    try:
        session = main(driver, session)
        store_session(session )
    except:
        driver.close()
        raise
