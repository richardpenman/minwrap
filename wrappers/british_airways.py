# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('lon', ['London, London (All Airports) (LON), United Kingdom', 'London, City Airport (LCY), United Kingdom', 'London, Gatwick (LGW), United Kingdom', 'London, Heathrow (LHR), United Kingdom', 'London, Luton (LTN), United Kingdom', 'London, Stansted (STN), United Kingdom', 'Londonderry, Londonderry (LDY), United Kingdom', 'Long Beach (CA), Long Beach (CA) (LGB), USA', 'Longview, East Texas Regional (TX) (GGG), USA', 'Longyearbyen, Svalbard (LYR), Norway', 'Changchun, Longjia Intl (CGQ), China', 'East London, East London (ELS), South Africa']),
            ('par', ['Paris, Paris (All) (PAR), France', 'Paris, Charles de Gaulle (CDG), France', 'Paris, Orly (ORY), France', 'Paramaribo, Paramaribo (PBM), Suriname', 'State College, University Park (PA) (SCE), USA']),
        ]
        self.website = 'http://www.britishairways.com/travel/home/public/en_gb'
        self.category = 'autocomplete'
        self.http_method = 'GET'
        self.response_format = 'JavaScript'
        self.notes = 'JavaScript results use content-type text/plain and then modified before being inserted into document'

    def run(self, browser):
        # XXX why does not autofill properly when reload homepage for each input?
        browser.load(self.website)
        for i, (input_value, output_values) in enumerate(self.data):
            if i == 0:
                browser.click('div#accept_ba_cookies a')
            browser.fill('input#planTripFlightDestination', input_value)
            browser.click('input#planTripFlightDestination')
            yield output_values
