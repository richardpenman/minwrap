# -*- coding: utf-8 -*-


class Wrapper:
    """Dummy wrapper that does nothing and then can interact with browser
    """
    def __init__(self):
        self.data = [
            (None, None),
            (None, None),
        ]
        self.website = ''
        self.enabled = False

    def run(self, browser, input_value):
        pass
