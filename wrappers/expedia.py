# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Paris'},
            {'city': 'New York'}, 
            {'city': 'Berlin'}, 
            {'city': 'Rome'}, 
        ]
        self.website = 'https://www.expedia.co.uk/Flights'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output. Discovers the correct URLs but unable to abstract IDs, which do not appear exactly in cookies'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#flight-origin', 'London')
        browser.keys('input#flight-destination', inputs['city'])
        now = datetime.now()
        browser.keys('input#flight-departing', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        browser.keys('input#flight-returning', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        browser.click('#search-button')
        browser.wait_steady(120)
        return {'prices': [e.replace(u'\\xa', '') for e in browser.text('div.offer-price > span.visuallyhidden')]}
