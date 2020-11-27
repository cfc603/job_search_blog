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


class Page:

    def __init__(self, driver):
        self.d = driver

    def get_forms(self):
        if not hasattr(self, "_forms"):
            self._forms = []
            for form in self.d.find_elements_by_xpath("//form"):
                self._forms.append(Form(form))
        return self._forms

    def has_form(self):
        if self.get_forms():
            return True
        return False
