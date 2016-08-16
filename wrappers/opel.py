# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Rome'}, 
            {'city': 'Venice'}, 
        ]
        self.website = 'https://www.opel.it/tools/opel-locate-dealer.html'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_quiet()
        browser.keys('input#field_city', inputs['city'])
        browser.click('div.modDl_search_1 button[type="submit"]')
        browser.wait_load('dd.dealer-contact')
        return {
            'name': browser.text('dd.dealer-contact > h3 > a'),
            'address': browser.text('dd.dealer-contact div.dealer-address p:nth-child(1)'),
            'postcode': browser.text('dd.dealer-contact div.dealer-address p:nth-child(2) span:nth-child(1)'),
            'city': browser.text('dd.dealer-contact div.dealer-address p:nth-child(2) span:nth-child(2)'),
        }
