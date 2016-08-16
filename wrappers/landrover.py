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
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.fill('input[name=placeName]', inputs['city'])
        browser.click('input[type=submit]')
        browser.wait_load('span.dealerNameText')
        return {
            'name': browser.text('span.dealerNameText'),
            'address': browser.text('div.address'),
            'phone': browser.text('tr.tel > td > a'),
            #'email': browser.attr('tr.email > td > a', 'href'),
            #'website': browser.attr('a.website', 'href'),
        }
