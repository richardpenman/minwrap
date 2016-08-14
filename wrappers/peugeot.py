# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Amsterdam'}, 
            {'city': 'The Hague'}, 
            {'city': 'Leiden'}, 
        ]
        self.website = 'http://www.peugeot.nl/zoek-een-dealer/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Website uses shortened latitude/longitude as key, so fails to abstract'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#search-loc-input', inputs['city'])
        browser.click('form#form_search_dealer input[type="submit"]')
