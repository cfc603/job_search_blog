import csv
import json
import random

from urllib.parse import urlencode

from selenium import webdriver
from unipath import Path

from settings import DATA_DIR


class Business:

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

    @property
    def city(self):
        return self.data_dict["City"]

    @property
    def name(self):
        return self.data_dict["Company Name"]

    @property
    def web_address(self):
        return self.data_dict["Website"]

    def google_search_url(self):
        # use urlencode to properly format the query
        # https://docs.python.org/3.3/library/urllib.parse.html#urllib.parse.urlencode
        query = urlencode({"q": f"{self.name.lower()} {self.city.lower()}"})
        return f"https://www.google.com/search?{query}"

    def has_web_address(self):
        if self.web_address:
            return True
        return False


def main(driver):
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

    # get past businesses
    all_past = []
    past_file = Path(DATA_DIR, "past_businesses.json")
    if past_file.exists():
        with open(past_file) as open_file:
            for b_data in json.load(open_file):
                all_past.append(Business(b_data))

    # loop over each business
    another_business = True # need a way to stop the loop
    while another_business:
        business = _all.pop(random.randint(0, len(_all)))
        if not business in all_past:
            driver.get(business.google_search_url())
            all_past.append(business)

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


if __name__ == "__main__":
    # open chrome
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        main(driver)
    except:
        driver.close()
        raise
