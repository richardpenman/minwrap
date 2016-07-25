# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class Wrapper:
    def __init__(self):
        self.data = [
            ('Paris', None),
            ('New York', None),
            ('Berlin', None),
            ('Rome', None),
        ]
        self.website = 'https://www.expedia.co.uk/Flights'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output. Discovers the correct URLs but unable to abstract IDs (1f91f5fd-e9c1-4d43-9418-d23cd9843fce)'
        self.enabled = False

    def run(self, browser, input_value):
        # XXX executes but model fails because uses session ID
        browser.get(self.website)
        browser.keys('input#flight-origin', 'London')
        browser.keys('input#flight-destination', input_value)
        now = datetime.now()
        browser.keys('input#flight-departing', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        browser.keys('input#flight-returning', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        browser.click('#search-button')
        browser.wait_steady(120)
        return [e.toPlainText().strip() for e in browser.find('div.offer-price > span.visuallyhidden')]
