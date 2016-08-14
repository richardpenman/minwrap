# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'search': 'shirts'}, 
            {'search': 'pants'}, 
            {'search': 'hats'}, 
            {'search': 'watches'},
        ]
        self.website = 'http://macys.com'
        self.category = 'fashion'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.click('a#closeButton')
        browser.keys('input#globalSearchInputField', inputs['search'])
        browser.wait_load('ul.ui-autocomplete div.suggestion')
        return {
            'name': browser.text('ul.ui-autocomplete div.suggestion'),
        }
