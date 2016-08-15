# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'Lisboa'}, 
            {'city': 'Alcafaz'},
            {'city': 'Coimbra'},
            {'city': 'Almada'}, 
        ]
        self.website = 'http://www.landrover.pt/national-dealer-locator.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Final response is HTML and scraping this is not yet supported'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.fill('input[name=placeName]', inputs['city'])
        browser.click('input[type=submit]')

