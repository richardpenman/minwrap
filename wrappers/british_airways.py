# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'prefix': 'lon'}, 
            {'prefix': 'par'},
            {'prefix': 'bri'},
            {'prefix': 'new'},
        ]
        self.website = 'http://www.britishairways.com/travel/home/public/en_gb'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JavaScript'
        self.notes = 'JavaScript results use content-type text/plain and then modified before being inserted into document. Need to clear cookies for input box to work on subsequent page loads.'

    def run(self, browser, inputs):
        # need to clear cookies 
        browser.get(self.website)
        browser.click('div#accept_ba_cookies a', True)
        browser.keys('input#planTripFlightDestination', inputs['prefix'])
        browser.click('input#planTripFlightDestination', False)
        browser.wait_load('ul#destChoices li')
        cities = browser.attr('ul#destChoices li', 'id')
        return {
            'cities': cities
        }
