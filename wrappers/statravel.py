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
        self.website = 'http://www.statravel.co.uk/cheap-flights.htm'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        #self.notes = 'Uses dynamic results for expected output. Discovers the correct URLs but unable to abstract IDs (1f91f5fd-e9c1-4d43-9418-d23cd9843fce)'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        # XXX unable to set value
        browser.wait_steady()
        print browser.keys('input[class="flight_depart_location ui-autocomplete-input"]', 'London', True)
        print browser.keys('input[class="flight_arrive_location ui-autocomplete-input"]', inputs['city'], True)
        now = datetime.now()
        print browser.keys('input[class="date_pick flight_depart_date hasDatepicker"]', (now + timedelta(days=1)).strftime('%d/%m/%Y'))
        print browser.keys('input[class="date_pick flight_return_date hasDatepicker"]', (now + timedelta(days=5)).strftime('%d/%m/%Y'))
        #print browser.click('div.js_enabled fieldset[class="submit contain"] p.contain button[type=submit]')
        browser.wait_steady(120)
        return [e.toPlainText().strip() for e in browser.find('div.offer-price > span.visuallyhidden')]
