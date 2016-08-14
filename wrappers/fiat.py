# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'postcode': 'OX1'},
            {'postcode': 'CB2'},
            {'postcode': 'E1'}, 
            {'postcode': 'BA1'},
        ]
        self.website = 'http://www.fiat.co.uk/find-dealer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSONP'
        self.notes = 'Two potential AJAX requests by postcode and sales type'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.fill('div.input_text input', inputs['postcode'])
        browser.click('div.tab_dealer div.input_text button.search')
        browser.wait_load('div.result')
        return dict(
            names = browser.text('div.result div.fn.org'),
            addresses = browser.text('div.result span.street-address'),
            cities = browser.text('div.result span.locality'),
            postcodes = browser.text('div.result span.postal-code'),
        )
