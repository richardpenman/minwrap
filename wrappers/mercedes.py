# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('New Delhi', ['F-85, Okhla Industrial Area, Phase -I', '110020', 'New Delhi', '+91 11 47133700', '+91 11 47133725', 'C7-C8, Okhla Industrial Estate, Phase I', '110020', '+91 11 41017610', '+91 11 41017617']),
            ('Mumbai', ['C/o Bombay Cycle & Motor Agency Ltd., Oriental Bldg., 7, Jamshedji Tata Road, Next to RITZ Hotel', '400020', '+91 22 66263022', '+91 22 66263012', 'Metro Motors Auto Hangar Division', 'Metro Motors Auto Hangar', 'Motor House, Ground Floor, 66 Sitaram Patkar Marg, Charni Road', '400007', 'Mumbai', '+91 22 6612 3500', '+91 22 6612 3535']),
        ]
        self.website = 'http://dealersearch.mercedes-benz.com/mercedes-benz-in/sl/shoplocator/ANX-DLp'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'All data is available on initial page'

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.keys('input#mbDLCity', input_value)
        browser.click('div.mbDLsearchformSubmit a.mbDLbuttonRightGrey')
