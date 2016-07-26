# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'zaragoza'}, ['AUTOSALDUBA, S.A.', 'Avenida Cataluña, 105', 'autosalduba@kia.es', 'http://autosalduba.com', '976577644', '976465577', 'AUTOSALDUBA, S.A.', 'Avenida San José, 58', 'autosalduba@kia.es', 'http://autosalduba.com']),
            ({'city': 'andorra'}, ['BECIER VEHICLES, S.A.U', 'Avenida d\'Enclar, 142', 'AD500', 'becier-posventa@kia.es', 'http://www.dealershipdomain.com', '376871820', 'BECIER VEHICLES, S.A.U', 'Avenida d\'Enclar, 31', 'becier@kia.es', 'http://www.dealershipdomain.com']),
            ({'city': 'madrid'}, ['Calle Sinesio Delgado 36', '28029', 'San Francisco de Sales 34', '28003', 'kiturmadrid@kia.es', 'http://www.kiturmadrid.com', '911108878', 'autosselikar@kia.es', '914811535']),
            ({'city': 'granada'}, ['Polígono Industrial de Guadix, M2, P11', '18500', 'Guadix', 'C/ Comercio (P.Ind El Florío)', '18015', 'Granada', 'armmotor@kia.es', 'http://www.dealershipdomain.com', '958126211']),
            #('cordoba', ['TURISCOR AUTOMÓVILES, S.L.', 'Avenida de la Torrecilla 45', '14013', 'TURISCOR AUTOMÓVILES, S.L.', 'Calle Simón Carpintero, nave 97', '14014']),
            #('ronda', ['IBERICAR MÓVIL SUR, S.L.', 'Calle Genal, 23 Pol.Ind. El Fuerte', '29400', 'IBERICAR MOVIL SUR, s.l.', 'Av/ Andalucia nº 165', '29680']),
        ]
        self.website = 'http://www.kia.com/es/dealerfinder2011/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'All dealers are fetched in a single XML AJAX call'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input#ds-searchinput', inputs['city'], True) # XXX why not inserted
