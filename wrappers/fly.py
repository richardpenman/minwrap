# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Paris'}, None),
            ({'city': 'New York'}, None),
            ({'city': 'Berlin'}, None),
            ({'city': 'Rome'}, None),
        ]
        self.website = 'http://www.fly.com/uk/'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_quiet()
        browser.keys('input#from-field', 'London')
        browser.keys('input#from-field', '\n', True)
        browser.wait(1)
        browser.keys('input#to-field', inputs['city'])
        browser.keys('input#to-field', '\n', True)
        browser.wait(1)
        now = datetime.now()
        browser.keys('input#date-depart', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        browser.keys('input#date-return', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        browser.click('#search-btn')
        browser.wait_load('div.priceContainer')
        return [e.toPlainText().strip().replace(u'\xa3', '') for e in browser.find('div.priceContainer')]
