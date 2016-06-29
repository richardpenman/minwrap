# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Lisboa', ['Avenida Marechal Gomes Costa, 33, Lisboa, 1800-255', 'Carclasse', '211 901 000', '211 901 099', 'miguel.igrejas@carclasse.pt', 'http://carclasse.landrover.pt/']),
            ('Alcafaz', ['M. Coutinho Porto', 'Av. Dr. Francisco Sá Carneiro, Apartado 149, Paredes, Porto, 4580-104', '255 780 100', '255 780 111', 'mcoutinhoporto@mcoutinho.pt', 'http://mcoutinho.landrover.pt/']),
        ]
        self.website = 'http://www.landrover.pt/national-dealer-locator.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Final response is HTML and scraping this is not yet supported'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('input[name=placeName]', input_value)
            browser.click('input[type=submit]')
            yield output_values
