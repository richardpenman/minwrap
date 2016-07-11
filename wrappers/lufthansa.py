# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
            ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
            ('bri', ['Brindisi', 'Brisbane', 'bds', 'bne', 'Brisbane area airports', 'Gold Coast, Queensland', 'Bristol', 'brs', 'Bristol - Tennessee', 'tri', 'Britton', 'Britton area airports']),
            ('new', ['New Bern','ewn','New Orleans','msy','New York, all airports',"nyc","New York area airports","New York - JFK International, NY","jfk","New York - La Guardia","lga","New York - Newark International, NJ","ewr","Allentown/Bethl","abe"]),
        ]
        self.website = 'http://www.lufthansa.com/uk/en/Homepage'
        self.category = 'flight'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'AJAX callback triggered on KeyUp event'

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
        browser.wait_load('div.rw-popup')
