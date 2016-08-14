# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'zaragoza'},
            #{'city': 'andorra'},
            {'city': 'madrid'}, 
            {'city': 'granada'},
        ]
        self.website = 'http://www.kia.com/es/dealerfinder2011/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'All dealers are fetched in a single XML AJAX call'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#ds-searchinput', inputs['city'], False)
        browser.click('a#ds-submit-search', True)
        browser.wait_quiet()
        #browser.wait_load('span.ds-resultslist-item-xml-n')
        return {
            #'name': browser.text('span.ds-resultslist-item-xml-n'),
            'address': browser.text('span.ds-resultslist-item-xml-s'),
            'postcode': browser.text('span.ds-resultslist-item-xml-z'),
            'city': browser.text('span.ds-resultslist-item-xml-c'),
        }
