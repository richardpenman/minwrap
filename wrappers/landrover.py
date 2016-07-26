# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Lisboa'}, ['Avenida Marechal Gomes Costa, 33, Lisboa, 1800-255', 'Carclasse', '211 901 000', '211 901 099', 'miguel.igrejas@carclasse.pt', 'http://carclasse.landrover.pt/']),
            ({'city': 'Alcafaz'}, ['M. Coutinho Porto', 'Av. Dr. Francisco Sá Carneiro, Apartado 149, Paredes, Porto, 4580-104', '255 780 100', '255 780 111', 'mcoutinhoporto@mcoutinho.pt', 'http://mcoutinho.landrover.pt/']),
            ({'city': 'Coimbra'}, ['Jap', 'Rua Manuel Pinto de Azevedo 604', 'jop@jop.pt', '226 194 500', '226 194 599', 'M. Coutinho Porto', '4580-104', '255 780 100', '255 780 111', 'mcoutinhoporto@mcoutinho.pt']),
            ({'city': 'Almada'}, ['Av. Luis Bivar, 38B', '213 192 380', 'joaoesteves@seculo21.pt', 'Av. 25 Abril, nº 1011-C', '214 823 312', 'joaoesteves@seculo21.pt']),
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
