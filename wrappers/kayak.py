# -*- coding: utf-8 -*-

import re


class Wrapper:
    def __init__(self):
        self.data = [
            #({'city': 'Oxford'}, None),
            #({'city': 'Cambridge'}, None),
            ({'city': 'London'}, None),
            #({'city': 'York'}, None),
        ]
        self.website = 'https://www.kayak.co.uk/'
        self.category = 'maps'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output.'
        self.enabled = False

    def run(self, browser, inputs):
        # XXX unable to click autocomplete result, even manually
        browser.get(self.website)
        key = re.search('div id="(\w*?)" class="Hotels-Search-HotelSearchForm "', browser.current_html()).groups()[0]
        print browser.keys('input#{}-location'.format(key), inputs['city'], True)
        #print browser.keys('input#{}-location'.format(key), inputs['city'], True)
        #print browser.attr('input#{}-location'.format(key), 'value')
        print browser.keys('span#{}-stayDates-start-display'.format(key), '09/08/2016')
        print browser.keys('span#{}-stayDates-end-display'.format(key), '10/08/2016')
        print browser.click('button#{}-submit'.format(key), True)
        browser.wait(4)
        print 'waited'
        browser.wait_steady()
        #browser.view.app.exec_()
        #es = browser.find('h3.widget-pane-section-result-title span')
        #vs = [e.toPlainText() for e in es]
        #return vs
