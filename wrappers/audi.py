# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('Antwerpen', ['Auto Natie', 'info@autonatie.audi.be', '+32 3 231 59 30', 'Groenendaallaan, 397 ANTWERPEN 3', 'Garage Thuy n.v.', 'Lakborslei, 81 DEURNE (ANTWERPEN)', '+32 3 326 11 22', 'info@thuy.audi.be']),
            ('Bruxelles', ['D\'Ieteren Mail', 'Rue Du Mail, 50 IXELLES', '+32 2 536 55 11', 'info@dmail.audi.be', 'Audi Center Brussels', 'Bemptstraat, 38 DROGENBOS', '+32 2 371 27 11', 'info@ddrogenbos.audi.be']),
            ('Brugge', ['Garage Raes Brugge nv', 'Oostendse Steenweg, 115 BRUGGE', '+32 50 45 80 20', 'info@raesbrugge.audi.be']),
            ('Ostend', ['Phlips Oostende(d.Fre-Kar bvba', 'Brugsesteenweg, 53 BREDENE', '+32 59 55 20 10', 'info@phlipso.audi.be']),
        ]
        self.website = 'http://www.dealerlocator.audi.be/default.aspx'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'All data pre-loaded in single AJAX request'

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input#addressinput', input_value)
        browser.click('span#lnk_search')
        browser.wait(1)
