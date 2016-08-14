# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Marseilles'},
            {'city': 'Paris'}, 
            {'city': 'Lyon'}, 
        ]
        self.website = 'https://www.mazda.fr/forms-v2/dealer-locatorfrance/'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'Uses JSON for payload'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_load('input[name="bylocation"]')#div.main-search')
        browser.keys('input[name="bylocation"]', inputs['city'] + '', False)#True)
        browser.click('div.main-search > button', True)
        browser.wait_load('div.dealer-name a')
        return {
            'name': [e.partition('. ')[-1] for e in browser.text('div.dealer-name a')],
            'address': browser.text('li[ng-if="address.FirstLine"]'),
            'city': browser.text('li[ng-if="address.TownCity"]'),
            'postcode': browser.text('li[ng-if="address.PostCode"]'),
        }
