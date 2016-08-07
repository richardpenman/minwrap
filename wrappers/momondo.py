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
        self.website = 'https://www.momondo.co.uk'
        self.category = 'flight'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        print browser.keys('input#Content_ctl04_SearchFormv8_SearchFormFlight_InputOrigin', 'London', True)
        print browser.keys('input#Content_ctl04_SearchFormv8_SearchFormFlight_InputDestination', inputs['city'], True)
        now = datetime.now()
        browser.keys('input[name="ctl00$Content$ctl04$SearchFormv8$SearchFormFlight$InputDepart"]', (now + timedelta(days=1)).strftime('%d/%m/%Y'), True)
        browser.keys('input#Content_ctl04_SearchFormv8_SearchFormFlight_InputReturn', (now + timedelta(days=5)).strftime('%d/%m/%Y'), True)
        browser.wait_quiet()
        # XXX unable to click, even manually
        print browser.click('div.submit-container a:first-child span span', True)
        browser.wait_steady(120)
        while True:
            print [e.toPlainText().strip() for e in browser.find('span.price > span.value')]
            if browser.wait_steady(2):
                break
            
        return [e.toPlainText().strip() for e in browser.find('span.price > span.value')]
