# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Rome', ['Via Veturia 39/49/51/53/55', '00181', 'Roma (RM)', '06/784601', 'Via Oderisi da Gubbio 207/209/211/233', '00146', 'Roma (RM)', '06/5566044', 'AUTOIMPORT']),
            ('Venice', ['Via Giustizia 25/27', '30171', 'Mestre (VE)', '041/926722', 'V. Roma, 163/A', '30030', 'Salzano (VE)', '041/437833', 'AUTOSANLORENZO srl', 'AUTOSANLORENZO SRL']),
            ('Rome', ['Via Veturia 39/49/51/53/55', '00181', 'Roma (RM)', '06/784601', 'Via Oderisi da Gubbio 207/209/211/233', '00146', 'Roma (RM)', '06/5566044', 'AUTOIMPORT']),
            ('Venice', ['Via Giustizia 25/27', '30171', 'Mestre (VE)', '041/926722', 'V. Roma, 163/A', '30030', 'Salzano (VE)', '041/437833', 'AUTOSANLORENZO srl', 'AUTOSANLORENZO SRL']),
        ]
        self.website = 'https://www.opel.it/tools/opel-locate-dealer.html'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input#field_city', input_value)
        browser.click('button[type="submit"]')
