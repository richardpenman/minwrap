# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'prefix': 'lon'}, ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
            ({'prefix': 'par'}, ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
            ({'prefix': 'bri'}, ['Brindisi', 'Brisbane', 'bds', 'bne', 'Brisbane area airports', 'Gold Coast, Queensland', 'Bristol', 'brs', 'Bristol - Tennessee', 'tri', 'Britton', 'Britton area airports']),
            ({'prefix': 'new'}, ['New Bern','ewn','New Orleans','msy','New York, all airports',"nyc","New York area airports","New York - JFK International, NY","jfk","New York - La Guardia","lga","New York - Newark International, NJ","ewr","Allentown/Bethl","abe"]),
        ]
        self.website = 'http://www.lufthansa.com/uk/en/Homepage'
        self.category = 'flight'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'AJAX callback triggered on KeyUp event. Currently error triggering autocomplete.'
        self.enabled = False

    def run(self, browser, inputs):
        # XXX currently unable to trigger autocomplete
        browser.get(self.website)
        browser.keys('input#flightmanagerFlightsFormOrigin', inputs['prefix'])
        #browser.keys('input#flightmanagerFlightsFormOrigin', ['DOWN'], True)
        browser.wait_load('div.rw-popup')
