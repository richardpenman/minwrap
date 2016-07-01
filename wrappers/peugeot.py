# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Rotterdam', ['Blauwendaal Rotterdam', 'Koningslaan 90-92', '3067', 'TG ROTTERDAM', '(010) 850 4370', 'Eigenraam Schiedam B.V.', '3125', 'BE SCHIEDAM', '(010) 462 20 22', '(010) 415 66 30']),
            ('The Hague', ['DAVO Den Haag', 'Kerketuinenweg 18', '2544 CW DEN HAAG', '(070) 850 25 00', '(070) 346 51 24', 'http://dealer.peugeot.nl/davo-denhaag', 'Autobedrijf Duindam B.V.', 'Heulweg 54 B', '2295 KH KWINTSHEUL', '(0174) 29 36 61', '(0174) 29 67 90']),
            ('Amsterdam', ['Van Mossel Amsterdam Noord', 'Joh. van Hasseltweg 65', '1021 KN AMSTERDAM', '(088) 0014 200', '(088) 001 42 09', 'Van Mossel Amsterdam Zuidoost', 'Klokkenbergweg 29', '1101 AK AMSTERDAM', '(088) 0014 500', '(088) 001 45 09']),
            ('Leiden', ['Van Mossel Leiderdorp', 'Van der Valk Boumanweg 2', '2352 JC LEIDERDORP', '(088) 0014 700', '(088) 0014 709', 'DAVO Leidschendam', 'Veurse Achterweg 22', '2264 SG LEIDSCHENDAM', '(070) 850 2400']),
        ]
        self.website = 'http://www.peugeot.nl/zoek-een-dealer/'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'Output is JSON but then bulk of this is a HTML block, so parsing is less useful'

    def run(self, browser, input_value):
        browser.get(self.website)
        #browser.wait_load('div.main_search')
        browser.fill('div.main_search input#dl_main_search', input_value)
        browser.click('div.main_search input[type=submit]')
