# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'zip': '33520'}, 
            {'zip': '06110'}, 
            {'zip': '63000'}, 
        ]
        self.website = 'https://www.infiniti.fr/centre-locator.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_quiet()
        browser.click('div#psyma_close_link')
        browser.keys('input.location-input', inputs['zip'] + '\n', True)
        #browser.wait_load('span.autocomplete-suggestions button')
        #print browser.click('span.autocomplete-suggestions button:nth-child(1)')
        #browser.click('button.btn-search', True)
        browser.wait_load('div.dealer-address')
        return {
            'name': browser.text('h2 span'),
            'address': browser.text('div.dealer-address p:nth-child(2)'),
            'city': browser.text('div.dealer-address p:nth-child(3)'),
            'postcode': browser.text('div.dealer-address p:nth-child(4)'),
        }
