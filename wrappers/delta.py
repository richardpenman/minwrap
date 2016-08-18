# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'text': 'lon'}, 
            {'text': 'par'},
            {'text': 'new'},
            #('bri', 
            #('per', 
            #('bei', 
        ]
        self.website = 'http://www.delta.com/'
        self.category = 'flight'
        self.http_method = 'POST'
        self.response_format = 'JavaScript'
        self.notes = 'Request has 2 parameters - the prefix and a query counter. Each time loaded generates a different session ID which is in JSESSIONID cookie.'

    def run(self, browser, inputs):
        browser.get(self.website) # XXX each time loaded generates different session ID
        browser.wait_quiet()
        browser.keys('input#originCity', inputs['text'])
        browser.wait_load('ul.ui-autocomplete li a')
        return {
            'name': browser.text('ul.ui-autocomplete li a'),
        }
