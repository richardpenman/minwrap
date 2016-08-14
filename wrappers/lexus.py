# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'paris'},
            {'city': 'toulouse'}, 
            {'city': 'marseille'},
            {'city': 'nice'}, 
        ]
        self.website = 'http://www.lexus.fr/forms/find-a-retailer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses variables in the URL path and requires a geocoding intermediary step. Has multiple model solutions'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.click('span[class="icon icon--base icon-close"]') # accept cookies
        browser.wait_load('div.form-control__item__postcode')
        browser.fill('div.form-control__item__postcode input', inputs['city'])
        browser.click('div.form-control__item__postcode button')
        browser.wait_load('section.dealer-location-summary')
        return {
            'name': browser.text('h2.js-address-title'),
        }
