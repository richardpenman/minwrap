# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'prefix': 'lon'}, ['London, London (All Airports) (LON), United Kingdom', 'London, City Airport (LCY), United Kingdom', 'London, Gatwick (LGW), United Kingdom', 'London, Heathrow (LHR), United Kingdom', 'London, Luton (LTN), United Kingdom', 'London, Stansted (STN), United Kingdom', 'Londonderry, Londonderry (LDY), United Kingdom', 'Long Beach (CA), Long Beach (CA) (LGB), USA', 'Longview, East Texas Regional (TX) (GGG), USA', 'Longyearbyen, Svalbard (LYR), Norway', 'Changchun, Longjia Intl (CGQ), China', 'East London, East London (ELS), South Africa']),
            ({'prefix': 'par'}, ['Paris, Paris (All) (PAR), France', 'Paris, Charles de Gaulle (CDG), France', 'Paris, Orly (ORY), France', 'Paramaribo, Paramaribo (PBM), Suriname', 'State College, University Park (PA) (SCE), USA']),
            ({'prefix': 'bri'}, ['Bari, Bari (BRI), Italy', 'Bridgetown, Bridgetown (BGI), Barbados', 'Brindisi, Brindisi (BDS), Italy', 'Brisbane, Brisbane (BNE), Australia', 'Bristol, Bristol (BRS), United Kingdom', 'Beef Island, Beef Island (EIS), British Virgin Islands']),
            ({'prefix': 'new'}, ['New York, New York (All Airports) (NYC), USA', 'New York, John F Kennedy (NY) (JFK), USA', 'New York, La Guardia (NY) (LGA), USA', 'New York, Newark Liberty International (NJ) (EWR), USA', 'New Delhi, Indira Gandhi Intl (DEL), India', 'New Orleans, Louis Armstrong International (LA) (MSY), USA', 'Newcastle, Newcastle International (NCL), United Kingdom', 'Newquay, Newquay Cornwall Airport (NQY), United Kingdom']),
        ]
        self.website = 'http://www.britishairways.com/travel/home/public/en_gb'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JavaScript'
        self.notes = 'JavaScript results use content-type text/plain and then modified before being inserted into document. Need to clear cookies for input box to work on subsequent page loads.'

    def run(self, browser, inputs):
        # need to clear cookies 
        browser.get(self.website)
        browser.click('div#accept_ba_cookies a', True)
        browser.keys('input#planTripFlightDestination', inputs['prefix'])
        browser.click('input#planTripFlightDestination', False)
