# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Amsterdam'}, ['Van Mossel Amsterdam Noord', 'Johan van Hasseltweg 65', 'amsterdam-noord@vanmossel.peugeot.nl', '(088) 0014 200', 'http://dealer.peugeot.nl/vanmossel-amsterdam-noord', 'http://www.peugeot.nl/api/vcf/pf11/nl/23/0000046587']),
            ({'city': 'The Hague'}, ['DAVO Den Haag', 'Kerketuinenweg 18', 'info@peugeotdavo.nl', '(070) 850 25 00', '(070) 346 51 24', 'http://dealer.peugeot.nl/davo-denhaag', 'Autobedrijf Duindam', 'Heulweg 54 B', '2295 KH KWINTSHEUL', '(0174) 29 36 61', '(0174) 29 67 90']),
            ({'city': 'Leiden'}, ['Van Mossel Leiderdorp', 'Van der Valk Boumanweg 2', '2352 JC LEIDERDORP', '(088) 0014 700', '(088) 0014 709', 'DAVO Leidschendam', 'Veurse Achterweg 22', '2264 SG LEIDSCHENDAM', '(070) 850 2400']),
        ]
        self.website = 'http://www.peugeot.nl/zoek-een-dealer/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Website uses shortened latitude/longitude as key, so fails to abstract'
        #self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        print browser.keys('input#search-loc-input', inputs['city'])
        print browser.click('form#form_search_dealer input[type="submit"]')
