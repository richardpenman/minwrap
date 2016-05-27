# -*- coding: utf-8 -*-

__doc__ = 'Wrappers to interact with websites and trigger AJAX events'


class fiat:
    def __init__(self):
        # the inputs 
        self.inputs = 'OX1', 'CB2'

    def run(self, browser, value):
        for value in self.inputs:
            browser.load('http://www.fiat.co.uk/find-dealer')
            browser.fill('div.input_text input', value)
            browser.click('div.input_text button')
            browser.wait_quiet()


class lufthansa:
    def __init__(self):
        self.inputs = 'vie', 'aus'

    def run(self, browser):
        # XXX need to simulate keyup event to get working
        for value in self.inputs:
            browser.load('http://www.lufthansa.com/uk/en/Homepage')
            browser.click('input#flightmanagerFlightsFormOrigin')
            for letter in search:
                browser.keydown(letter)
            #browser.fill('input#flightmanagerFlightsFormOrigin', search)
            browser.wait_load('div.rw-popup')


class peugeot:
    def __init__(self):
        self.inputs = 'amsterdam', 'leiden'

    def run(self, browser):
        for value in self.inputs:
            browser.load('http://www.peugeot.nl/zoek-een-dealer/')
            browser.wait_load('div.main_search')
            browser.fill('div.main_search input#dl_main_search', value)
            browser.click('div.main_search input[type=submit]')
            browser.wait_quiet()
