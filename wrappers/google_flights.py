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
        self.website = 'https://www.google.co.uk/flights/'
        self.category = 'flight'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        # XXX value not set - div creates input dynamically
        browser.wait_steady()
        print 'click:', browser.click('div.FCS5SWB-sb-a', native=True)
        print 'keys:', browser.keys('input.FCS5SWB-Db-g', 'London', native=True)
        print 'click2:', browser.click('div.FCS5SWB-sb-e', native=True)
        print 'keys2:', browser.keys('input#FCS5SWB-Db-g', inputs['city'], native=True)
        print 'click3', browser.click('#search-button', native=True)
        browser.wait_steady(120)
        return {'prices': browser.text('div.offer-price > span.visuallyhidden')}
