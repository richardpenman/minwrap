# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'country': 'Australia'}, 
            {'country': 'Finland'}, 
            #{'country': 'Greece'},
        ]
        self.website = 'http://localhost:8000/examples/country/'
        self.category = ''
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses local custom website to demonstrate a multi-step wrapper'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_steady()
        browser.fill('input#country', inputs['country'])
        browser.click('button')
        browser.wait_quiet()
        return {'countries': browser.text('ul#results li')}
