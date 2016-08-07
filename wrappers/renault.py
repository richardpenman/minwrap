# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Paris'}, ['RENAULT PARIS GRENELLE', '0029 QU DE GRENELLE', 'PARIS 15', '75015', 'RENAULT MONTROUGE', '0059 AV ARISTIDE BRIAND', 'MONTROUGE', '92120', '+33146128840', 'CARROSSERIE DU MOULIN', '0003 R PIERRE ET MARIE CURIE', 'IVRY SUR SEINE', '94200']),
            ({'city': 'Orleans'}, ['RENAULT ORLEANS - RRG', '0539 FG BP 9 BANNIER', 'FLEURY LES AUBRAIS', '45400', '02.38.79.30.30', 'AUTOMOBILES CIGOGNE ST MARCEAU', '0002 R CLAUDE LEWY', 'ORLEANS', '45100', '+33238668888']),
            ({'city': 'Nice'}, ['AUTOSERVICE GORBELLA', '0005 BD GORBELLA', '06100', '33493841233', 'GARAGE BERLIOZ', '0020 R BERLIOZ', '06000', '33493888383', 'GARAGE DES RESIDENCES PASSY', '0021 R FREDERIC PASSY', 'NICE', '06000', '33493967702']),
        ]
        self.website = 'https://www.renault.fr/trouver-un-concessionnaire.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Requires native ENTER to submit'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_load('input.location-input')
        browser.keys('input.location-input', inputs['city'] + '\n', True)
        browser.wait_quiet()
