# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Rome'}, ['MOTOR EUROPE SRL', 'Via Gregorio VII', '00165', 'ROMA', '0640045100', 's.bernabei@motorcityonline.it', 'FASTWAGEN S.R.L. (3.25 km)', 'Via di Portinaccio, 21 F/G', '00159', 'ROMA', '06-43565032', 'info@fastwagen.it']),
            ({'city': 'Milan'}, ['LOMBARDA MOTORI S.P.A.', 'Via Luigi Rizzo, 8', '20151', 'Milano', '0269969311', 'mauro.dellatorre@lombardamotori.it', 'LOMBARDA MOTORI S.p.a.', 'Via Buonarroti, 128', '20052', 'MONZA (MI)', '039-284501', 'maurizio.folliero@lombardamotori.it']),
        ]
        self.website = 'http://www.seat-italia.it/concessionari.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'Interface does not load properly'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.click('a.accept-cookie')
        browser.keys('input.dealerLocation', inputs['city'])
        browser.click('input[type="submit"]')
