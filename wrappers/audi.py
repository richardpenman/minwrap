# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Antwerpen'},
            {'city': 'Bruxelles'},
            {'city': 'Brugge'}, 
            {'city': 'Ostend'},
        ]
        self.website = 'http://www.dealerlocator.audi.be/default.aspx'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'All data pre-loaded in single AJAX request'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#addressinput', inputs['city'])
        browser.click('span#lnk_search')
        browser.wait_quiet()
        return {
            'name': browser.text('h2.ddealername'),
            #'latitude': browser.attr('ul#accordion li', 'gpslat'), # period changed to comma
            #'longitude': browser.attr('ul#accordion li', 'gpslong'),
            #'address': browser.text('ul#accordion li a p'), # sub text
        }
