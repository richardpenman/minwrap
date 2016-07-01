# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('lon', ['London Area Airports, United Kingdom (LON)', 'London Metropolitan Area', 'London Area Airports', 'London-Heathrow, United Kingdom (LHR)', 'Heathrow Airport', 'London-Heathrow']),
            ('par', ['Paris Area Airports, France (PAR)', 'CDG/ORY', 'Paris Area Airports', 'CDG', 'Paris-De Gaulle, France (CDG)', 'Charles De Gaulle Intl Arpt', 'Paris-De Gaulle', 'Paraburdoo, Australia (PBO)', 'Paraburdoo,Orly Brazil (CKS)']),
            ('new', ['New York Area Airports, NY (NYC)', 'LGA/JFK/EWR/SWF', 'New York Area Airports', 'New York Area Airports, NY (NYC)', 'New York-Kennedy, NY (JFK)', 'John F Kennedy International']),
            ('bri', ['Bari, Italy (BRI)', 'Palese', 'Brindisi, Italy (BDS)', 'Papola Casale', 'Brisbane, Australia (BNE)', 'Bristol', 'Abbotsford, BC (YXX)', 'Comox Valley Arpt', 'North Peace Regional Arpt']),
            ('per', ['Perth, Australia (PER)', 'Perm, Russia (PEE)', 'Perpignan, France (PGF)', 'Lima, Peru (LIM)', 'Florence, Italy (FLR)', 'Llabanere Airport', 'Perth International']),
            ('bei', ['Beihai, China (BHY)', 'Beihai Arpt', 'Beijing/Peking, China (PEK)', 'Peking, China (PEK)', 'Beirut, Lebanon (BEY)', 'Beirut Rafic Hariri Airport', 'Beijing Capital Int.']),
        ]
        self.website = 'http://www.delta.com/'
        self.category = 'autocomplete'
        self.http_method = 'POST'
        self.response_format = 'JavaScript'
        self.notes = 'Request has 2 parameters - the prefix and a query counter. Each time loaded generates a different session ID.'
        self.counter = 0

    def run(self, browser, input_value):
        if self.counter == 0:
            browser.get(self.website) # XXX each time loaded generates different session ID
        self.counter += 1
        browser.keys('input#originCity', input_value)
