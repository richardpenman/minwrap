# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Paris', ['Austerlitz Automobiles', '32 AVENUE DE LA REPUBLIQUE', 'Paris', '75011', 'mazda-paris@wanadoo.fr', '01 43 14 38 45', '147 Boulevard Murat', '75016', '01 53 84 20 30']),
            ('Lyon', ['Elite Motors', '96 rue Marietton', 'Lyon', '69009', '04 72 53 14 85', '51 RUE ROGER SALENGRO', 'VENISSIEUX', '69200', 'lyonsud.mazda.fr', 'agnes.bayle@elitemotors.fr', '04 37 25 05 00']),
        ]
        self.website = 'https://www.mazda.fr/rechercher-un-concessionnaire/#/search/location/'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'Uses JSON for payload'

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.wait_quiet()
        browser.keys('input[name="bylocation"]', input_value)
        browser.click('div.main-search > button', True)