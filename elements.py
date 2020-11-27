from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException
)


class Element:

    def __init__(self, web_element):
        self.we = web_element

    @property
    def id(self):
        return self.we.get_attribute("id")

    def is_displayed(self):
        return self.we.is_displayed()


class Form(Element):

    def display(self):
        self.get_visible_inputs()[0].click()

    def get_inputs(self):
        if not hasattr(self, "_inputs"):
            self._inputs = []
            for _input in self.we.find_elements_by_xpath(".//input"):
                self._inputs.append(Input(_input))

            for textarea in self.we.find_elements_by_xpath(".//textarea"):
                self._inputs.append(Input(textarea))
        return self._inputs

    def get_visible_inputs(self):
        if not hasattr(self, "_visible_inputs"):
            self._visible_inputs = []
            for i in self.get_inputs():
                if i.is_displayed():
                    self._visible_inputs.append(i)
        return self._visible_inputs

    def has_input(self):
        if self.get_visible_inputs():
            return True
        return False


class Input(Element):

    @property
    def name(self):
        return self.we.get_attribute("name")

    @property
    def title(self):
        return self.we.get_attribute("title")

    def click(self):
        self.we.click()


class Link(Element):

    def __init__(self, page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page

    def __eq__(self, other):
        return self.url.geturl() == other.url.geturl()

    @property
    def name(self):
        return self.we.text

    @property
    def url(self):
        if not hasattr(self, "_url"):
            self._url = urlparse(self.we.get_attribute("href"))
        return self._url

    def follow(self):
        try:
            self.we.click()
        except ElementClickInterceptedException:
            print("\nUnable to follow.\n")
        except:
            import IPython; IPython.embed()
            raise

    def is_internal(self):
        return self.page.current_url.netloc == self.url.netloc


class Page:

    def __init__(self, driver):
        self.d = driver

    @property
    def current_url(self):
        if not hasattr(self, "_current_url"):
            self._current_url = urlparse(self.d.current_url)
        return self._current_url

    def get_forms(self):
        if not hasattr(self, "_forms"):
            self._forms = []
            for form in self.d.find_elements_by_xpath("//form"):
                self._forms.append(Form(form))
        return self._forms

    def get_links(self):
        if not hasattr(self, "_links"):
            self._links = []
            for a in self.d.find_elements_by_xpath("//a"):
                link = Link(self, a)
                if link not in self._links:
                    self._links.append(link)
        return self._links

    def get_internal_links(self):
        if not hasattr(self, "_internal_links"):
            self._internal_links = []
            for link in self.get_links():
                if link.is_internal():
                    self._internal_links.append(link)
        return self._internal_links

    def has_captcha(self):
        try:
            self.d.find_element_by_xpath(
                "//script[contains(@src, 'google.com/recaptcha')]"
            )
            return True
        except NoSuchElementException:
            return False

    def has_form(self):
        if self.get_forms():
            return True
        return False

    def has_link(self):
        if self.get_internal_links():
            return True
        return False
