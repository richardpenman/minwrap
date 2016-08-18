# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'New Delhi'}, 
            {'city': 'Mumbai'},
            {'city': 'Bangalore'},
            {'city': 'Pune'},
        ]
        self.website = 'http://dealersearch.mercedes-benz.com/mercedes-benz-in/sl/shoplocator/ANX-DLp'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'All data is available on initial page'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#mbDLCity', inputs['city'])
        browser.click('div.mbDLsearchformSubmit a.mbDLbuttonRightGrey')
        browser.wait_load('ul#dealerLocatorListResult div.padaddreass')
        return {
            'address': browser.text('ul#dealerLocatorListResult div.padaddreass div:nth-child(1)'),
            'city': browser.text('ul#dealerLocatorListResult div.padaddreass div:nth-child(4)'),
        }
