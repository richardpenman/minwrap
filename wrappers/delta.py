# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('lon', ['London Area Airports, United Kingdom (LON)', 'London Metropolitan Area', 'London Area Airports', 'London-Heathrow, United Kingdom (LHR)', 'Heathrow Airport', 'London-Heathrow']),
            ('par', ['Paris Area Airports, France (PAR)', 'CDG/ORY', 'Paris Area Airports', 'CDG', 'Paris-De Gaulle, France (CDG)', 'Charles De Gaulle Intl Arpt', 'Paris-De Gaulle', 'Paraburdoo, Australia (PBO)', 'Paraburdoo,Orly Brazil (CKS)']),
            ('new', ['New York Area Airports, NY (NYC)', 'LGA/JFK/EWR/SWF', 'New York Area Airports', 'New York Area Airports, NY (NYC)', 'New York-Kennedy, NY (JFK)', 'John F Kennedy International']),
        ]
        self.website = 'http://www.delta.com/'
        self.category = 'autocomplete'
        self.http_method = 'POST'
        self.response_format = 'JavaScript'
        self.notes = 'Request has 2 parameters - the prefix and a query counter'

    def run(self, browser):
        browser.load(self.website) # XXX each time loaded generates different session ID
        for input_value, output_values in self.data:
            browser.keys('input#originCity', input_value)
            yield output_values
