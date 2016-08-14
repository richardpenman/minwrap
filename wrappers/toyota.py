# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Zurich'}, 
            {'city': 'Geneva'},
        ]
        self.website = 'https://fr.toyota.ch/#/ajax/%2Fforms%2Fforms.json%3Ftab%3Dpane-dealer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'Geocodes the location but then rounds the latitude/longitude before querying API'
        self.enabled = False

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input.suggest-places', input_value)
        browser.click('a.btn-search-dealers', True)
        browser.wait_load()
        return {
            'name': browser.text('div.search-results ul li span.name'),
        }
