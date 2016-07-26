# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'zip': '33520'}, ['ADRESSE DU CENTRE', '469, Route du Médoc', 'Bruges', '33520', 'INFINITI BORDEAUX', 'INFINITI SERVICE PARTNER BAYONNE', '22, bis, rue Ernest Lannebère', 'Anglet', '64600']),
            ({'zip': '06110'}, ['INFINITI CANNES', '50 Avenue du Campon', 'Le Cannet', '06110', 'INFINITI SERVICE PARTNER NICE- OUVERTURE PROCHAINE', '79, Boulevard Gambetta - Palais de Porta', 'Nice', '06000']),
            ({'zip': '63000'}, ['INFINITI CLERMONT-FERRAND', '8, Rue Louis Blériot', 'Clermont-Ferrand', '63000', 'INFINITI LYON', '45 Avenue Foch', 'Lyon', '69006']),
        ]
        self.website = 'https://www.infiniti.fr/centre-locator.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.keys('input.location-input', inputs['zip'])
        #browser.click('button.btn-search', True)
        # XXX button did not work so needed to submit form
        for form in browser.find('form'):
            form.evaluateJavaScript('this.submit();')
