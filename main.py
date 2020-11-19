import base64
import csv
import hashlib
import json
import random

from datetime import datetime
from urllib.parse import urlencode

from selenium import webdriver
from unipath import Path

from actions import Continue, CopyTemplateAction
from settings import DATA_DIR


class Business:

    path = Path(DATA_DIR, "business_files/past")

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

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
        return self.data_dict["Website"]

    def exists(self):
        return Path(self.path, self.file_name).exists()

    def google_search_url(self):
        # use urlencode to properly format the query
        # https://docs.python.org/3.3/library/urllib.parse.html#urllib.parse.urlencode
        query = urlencode({"q": f"{self.name.lower()} {self.city.lower()}"})
        return f"https://www.google.com/search?{query}"

    def has_web_address(self):
        if self.web_address:
            return True
        return False

    def save(self):
        with open(Path(self.path, self.file_name), "w") as open_file:
            json.dump(self.data_dict, open_file, indent=4)


def store_session(session):
    session_cache = Path(DATA_DIR, "session_cache.json")

    # log stop session
    session["stop"] = str(datetime.now())

    # get existing sessions
    if session_cache.exists():
        with open(session_cache) as open_file:
            sessions = json.load(open_file)
    else:
        sessions = []

    # add new session
    sessions.append(session)

    # store all sessions
    with open(session_cache, "w") as open_file:
        json.dump(sessions, open_file, indent=4)


def main(driver, session):
    web_address_count = 0
    _all = []
    # iterate over each file download in project/data/business_files
    for _file in Path(DATA_DIR, "business_files").listdir("*.csv"):
        with open(_file) as open_file:
            # use DictReader to parse each row into a dict
            # https://docs.python.org/3/library/csv.html#csv.DictReader
            reader = csv.DictReader(open_file)
            for row in reader:
                _all.append(Business(row))

    # loop over each business
    another_business = True # need a way to stop the loop
    while another_business:
        business = _all.pop(random.randint(0, len(_all)))
        if not business.exists():
            session["total"] += 1
            driver.get(business.google_search_url())

            # display actions
            actions = [
                Continue(session),
                CopyTemplateAction(session),
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

            business.save()

            if "n" == input("Next business (y/n)? ").lower():
                driver.close()
                another_business = False

    # convert Business instances back to dicts
    b_dicts = []
    for business in all_past:
        b_dicts.append(business.data_dict)

    # store them all
    with open(past_file, "w") as open_file:
        json.dump(b_dicts, open_file, indent=2)

    return session


if __name__ == "__main__":
    # open chrome
    driver = webdriver.Chrome()
    driver.maximize_window()

    # create a new session
    session = {
        "start": str(datetime.now()),
        "total": 0,
        "actions": {},
    }

    try:
        session = main(driver, session)
        store_session(session )
    except:
        driver.close()
        raise
