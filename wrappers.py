# -*- coding: utf-8 -*-

__doc__ = 'Wrappers to interact with websites and trigger AJAX events'


def fiat(browser):
    postcodes = 'OX1', 'CB2'
    browser.load('http://www.fiat.co.uk/find-dealer')
    for postcode in postcodes:
        browser.fill('div.input_text input', postcode)
        browser.click('div.input_text button')
        browser.wait_quiet()

def lufthansa(browser):
    # XXX need to simulate keyup event to get working
    searches = 'vie', 'aus'
    browser.load('http://www.lufthansa.com/uk/en/Homepage')
    for search in searches:
        browser.click('input#flightmanagerFlightsFormOrigin')
        for letter in search:
            browser.keydown(letter)
        #browser.fill('input#flightmanagerFlightsFormOrigin', search)
        browser.wait(3)
        browser.wait_load('div.rw-popup')

def peugeot(browser):
    locations = 'amsterdam', 'leiden'
    browser.load('http://www.peugeot.nl/zoek-een-dealer/')
    browser.wait_load('div.main_search')
    for location in locations:
        browser.fill('div.main_search input#dl_main_search', location)
        browser.click('div.main_search input[type=submit]')
        browser.wait_quiet()
