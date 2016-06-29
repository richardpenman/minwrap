# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('madrid', ['Calle Sinesio Delgado 36', '28029', 'San Francisco de Sales 34', '28003', 'kiturmadrid@kia.es', 'http://www.kiturmadrid.com', '911108878', 'autosselikar@kia.es', '914811535']),
            ('granada', ['Polígono Industrial de Guadix, M2, P11', '18500', 'Guadix', 'C/ Comercio (P.Ind El Florío)', '18015', 'Granada', 'armmotor@kia.es', 'http://www.dealershipdomain.com', '958126211']),
        ]
        self.website = 'http://www.kia.com/es/dealerfinder2011/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'All dealers are fetched in a single XML AJAX call'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('input#ds-searchinput', input_value) # XXX why not inserted
            browser.keys('input#ds-searchinput', input_value) # XXX why not inserted
            browser.wait(5)
            yield output_values
