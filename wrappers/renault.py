# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Cherbourg'},
            {'city': 'Orleans'},
            {'city': 'Amiens'}, 
        ]
        self.website = 'https://www.renault.fr/trouver-un-concessionnaire.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Requires native ENTER to submit'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_load('input.location-input')
        browser.keys('input.location-input', inputs['city'] + '\n', True)
        #browser.click('button.btn-search', True)
        browser.wait_load('div.dealer-address')
        return {
            #'address': browser.text('div.dealer-address p:nth-child(2)'),
            'city': browser.text('div.dealer-address p:nth-child(3)'),
            'postcode': browser.text('div.dealer-address p:nth-child(4)'),
        }
