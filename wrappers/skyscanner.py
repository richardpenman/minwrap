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
        self.website = 'https://www.skyscanner.net/'
        self.category = 'flight'
        self.http_method = ''
        self.response_format = ''
        self.notes = 'Requires user-agent to avoid being detected as a bot'
        self.enabled = False
        self.counter = 0

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_steady()
        # XXX fail to set inputs
        print browser.keys('input#js-origin-input', 'London', True)
        print browser.keys('input#js-destination-input', inputs['city'], True)
        now = datetime.now()
        print browser.keys('input#js-depart-input', (now + timedelta(days=1)).strftime('%d/%m/%Y'), True)
        #print browser.keys('input#flight-returning', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        print browser.click('section.traditional-search button.js-search-button.wc-button-large.wc-button-spinner', True)
        browser.wait_quiet()
        print browser.wait_load('div.browse-data-route')
        es = browser.find('div.browse-data-route')
        print len(es)
        browser.click_by_gui_simulation(es[self.counter])
        self.counter += 1
        browser.wait_quiet()
        while True:
            prices = [e.toPlainText().strip() for e in browser.find('a.mainquote-price.expand-cba.select-action span')]
            print prices 
            if browser.wait_steady(2):
                break

        prices = [e.toPlainText().strip() for e in browser.find('div.cba-price > div > a')]
        return {'prices': prices}
