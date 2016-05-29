# -*- coding: utf-8 -*-

__doc__ = 'Wrappers to interact with websites and trigger AJAX events'


class britishairways:
    def __init__(self):
        self.inputs = 'lon', 'new', 'par'

    def run(self, browser):
        browser.load('http://www.britishairways.com/travel/home/public/en_gb')
        browser.wait_quiet()
        browser.click('div#accept_ba_cookies a')
        for value in self.inputs:
            browser.fill('input#planTripFlightDestination', value)
            browser.click('input#planTripFlightDestination')
            browser.wait_quiet()
            yield


class delta:
    def __init__(self):
        self.inputs = 'lon', 'new', 'par'

    def run(self, browser):
        browser.load('http://www.delta.com/')
        for value in self.inputs:
            browser.fill('input#originCity', value)
            browser.click('input#originCity')
            browser.wait_quiet()
            yield


class lufthansa:
    def __init__(self):
        self.inputs = 'vie', 'aus'

    def run(self, browser):
        # XXX need to simulate keyup event to get working
        for value in self.inputs:
            browser.load('http://www.lufthansa.com/uk/en/Homepage')
            #browser.click('input#flightmanagerFlightsFormOrigin')
            browser.fill('input#flightmanagerFlightsFormOrigin', value)
            browser.click('input#flightmanagerFlightsFormOrigin')
            browser.wait_load('div.rw-popup')
            yield

class fiat:
    def __init__(self):
        # the inputs 
        self.inputs = 'OX1', 'CB2'

    def run(self, browser):
        browser.load('http://www.fiat.co.uk/find-dealer')
        for value in self.inputs:
            browser.fill('div.input_text input', value)
            browser.click('div.input_text button.search')
            browser.wait_quiet()
            yield


class peugeot:
    def __init__(self):
        self.inputs = 'amsterdam', 'leiden'

    def run(self, browser):
        browser.load('http://www.peugeot.nl/zoek-een-dealer/')
        for value in self.inputs:
            browser.wait_load('div.main_search')
            browser.fill('div.main_search input#dl_main_search', value)
            browser.click('div.main_search input[type=submit]')
            browser.wait_quiet()
            yield
