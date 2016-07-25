# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Zurich', ['Garage Wiedikon - Bruno Cajacob AG', 'Grubenstrasse 32', '044 463 22 33', 'http://garage.toyota.ch/de/zuerich-garage-wiedikon-bruno-cajacob-ag/', 'Grubenstrasse 32', 'Garage Wiedikon - Bruno Cajacob AG']),
            ('Geneva', ['Emil Frey SA - Centre Automobile aux Vernets', 'Rue François-Dussaud 13', 'geneve@emilfrey.ch', 'http://garage.toyota.ch/fr/geneve-26-emil-frey-sa-centre-automobile-aux-vernets/', 'Rue François-Dussaud 13', 'geneve@emilfrey.ch']),
        ]
        self.website = 'https://fr.toyota.ch/#/ajax/%2Fforms%2Fforms.json%3Ftab%3Dpane-dealer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'Geocodes the location but then rounds the latitude/longitude before querying API'
        #self.enabled = False

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input.suggest-places', input_value)
        browser.click('a.btn-search-dealers', True)
