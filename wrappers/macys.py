# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'search': 'shirts'}, ["GUESS Shirts","Men's Shirts","Men's Dress Shirts","Kids' Shirts","Michael Kors Dress Shirts","Men's Polo Shirts","Shiseido Men's","Women's Shirts"]),
            ({'search': 'pants'}, ["GUESS Pants","Pans","Corduroy Pants","Fleece Pants","Kids' Pants","Pants - Maternity","Pants - Plus Size","Women's Pants","Michael Kors Pants"]),
            ({'search': 'hats'}, ["Michael Kors Hats","Charter Club Hats","Fleece Hats","Men's Hats","Women's Hats","Kids' Hats","August Hats Women's","Woolrich Hats","The North Face Hats"]),
            ({'search': 'watches'}, ["GUESS Watches","Women's Watches","Men's Watches","Diesel Watches","Tommy Hilfiger Watches","G-Shock Watches","Vince Camuto Watches"]),
        ]
        self.website = 'http://macys.com'
        self.category = 'fashion'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = ''

    def run(self, browser, inputs):
        browser.get(self.website)
        print browser.click('a#closeButton')
        print browser.keys('input#globalSearchInputField', inputs['search'])
