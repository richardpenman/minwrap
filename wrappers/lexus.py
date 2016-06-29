# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('paris', ['58, Boulevard Saint Marcel', '75005', '01 55 43 55 00', '3, rue des Ardennes', '75019', '01 40 03 16 00', '4, avenue de la Grande Armée', '75017', '01 40 55 40 00']),
            ('toulouse', ['123, Rue Nicolas', 'Vauquelin', '31100', '05 61 61 84 29', '4 rue Pierre-Gilles de Gennes', '64140', '05 59 72 29 00']),
            ('marseille', ['36 Boulevard Jean Moulin', '13005', '04 91 229 229', 'ZAC Aix La Pioline', 'Les Milles', '13290', '04 42 95 28 78', 'Rue Charles Valente', 'ZAC de la Castelette', 'Montfavet', '84143', '04 90 87 47 00']),
        ]
        self.website = 'http://www.lexus.fr/forms/find-a-retailer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses variables in the URL path and requires a geocoding intermediary step'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.click('span[class="icon icon--base icon-close"]') # accept cookies
            browser.wait_load('div.form-control__item__postcode')
            browser.fill('div.form-control__item__postcode input', input_value)
            browser.click('div.form-control__item__postcode button')
            yield output_values
