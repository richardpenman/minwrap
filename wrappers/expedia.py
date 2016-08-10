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
        self.website = 'https://www.expedia.co.uk/Flights'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output. Discovers the correct URLs but unable to abstract IDs, which do not appear exactly in cookies'

    def run(self, browser, inputs):
        # XXX executes but model fails because uses session ID
        browser.get(self.website)
        browser.keys('input#flight-origin', 'London')
        browser.keys('input#flight-destination', inputs['city'])
        now = datetime.now()
        browser.keys('input#flight-departing', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        browser.keys('input#flight-returning', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        browser.click('#search-button')
        browser.wait_steady(120)
        return [e.toPlainText().strip() for e in browser.find('div.offer-price > span.visuallyhidden')]
