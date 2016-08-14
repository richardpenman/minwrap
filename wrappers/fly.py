# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Paris'}, 
            {'city': 'New York'},
            #{'city': 'Berlin'},
            #{'city': 'Rome'}, 
        ]
        self.website = 'http://www.fly.com/uk/'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_quiet()
        browser.keys('input#from-field', 'London\n', True)
        browser.keys('input#to-field', inputs['city'] + '\n', True)
        now = datetime.now()
        browser.keys('input#date-depart', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        browser.keys('input#date-return', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        browser.click('#search-btn')
        browser.wait_load('div.priceContainer')
        return {'prices': [e.replace(u'\xa3', '') for e in browser.text('div.priceContainer')]}
