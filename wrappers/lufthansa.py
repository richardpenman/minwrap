# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
            ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
        ]
        self.website = 'http://www.lufthansa.com/uk/en/Homepage'
        self.category = 'autocomplete'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'AJAX callback triggered on KeyUp event'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
            browser.wait_load('div.rw-popup')
            yield output_values
