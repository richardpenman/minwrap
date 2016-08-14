# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'city': 'linz'}, 
            {'city': 'salzburg'}, 
            {'city': 'graz'}, 
            {'city': 'Klagenfurt'}, 
        ]
        self.website = 'http://dacia.at/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Includes redundant parameters _sourcePage and __fp. Final response is HTML and scraping this is not yet supported.'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.fill('input#quicksearch-overnav', inputs['city'])
        browser.click('button')
        browser.wait_load('div.item')
        return {
            'name': browser.text('div.item h3.title1_b'),
            'address': browser.text('div.item p:nth-child(2)'),
        }
