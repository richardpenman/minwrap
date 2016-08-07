# -*- coding: utf-8 -*-

from browser_wrapper import BrowserWrapper

# s7
# Make a flight search for a single trip with locations and the departure date specified 

class Wrapper():
    def __init__(self):
        self.data = [
            ({'from': 'Vienna', 'to': 'Moscow'}, None),
            ({'from': 'Vienna', 'to': 'London'}, None),
            ({'from': 'London', 'to': 'Vienna'}, None)
        ]
        self.website = 'http://www.s7.ru/'
        self.category = 'flight search (s7)'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser, inputs):
        origin_airport, destination_airport = inputs['from'], inputs['to']
        
        bw = BrowserWrapper(browser)
        bw.get(self.website)
        
        # Change language from Russian to English
        bw.userClick("a.lang-item.en")

#         # Select Locations
        bw.userKeys('form#aviaBot input#flights_origin', origin_airport)
        bw.userClick('form#aviaBot div#smart_search_ac_flights_origin li.item:nth-of-type(1)')

        bw.userKeys('form#aviaBot input#flights_destination', destination_airport)
        bw.userClick('form#aviaBot div#smart_search_ac_flights_destination li.item:nth-of-type(1)')

        # Single trip
#         browser.click('form#aviaBot div.select-wrapper.date.form-control:nth-of-type(1)', False)
        bw.userClick('form#aviaBot label[for="flights_one_way_bot"]')
        
        # Select date
        # Select dates (Always the first day in the second week of the next month)
        bw.userClick('form#aviaBot .ui-datepicker-next.ui-corner-all')
        bw.userClick('form#aviaBot #datepicker>div>table>tbody>tr:nth-of-type(2)>td:nth-of-type(1)>a')
#         browser.wait(10)
        
        # Search!
        bw.userClick('button#search-btn-expand-bot')
        #browser.wait(11)
        browser.wait_load("div.select-flights div.mobile-select-item-full span[data-qa='amount']")
        
#         def myreplace(x):
#             return x.replace(u'(&nbsp;|\xa0|\\s)+','')
        
        # get prices
        outputs = bw.getOutput([
                   ("div.select-flights div.mobile-select-item-full span[data-qa='amount']",
                        None,
                        None
                    )
                   ],
                    None)
        outputs = [output.replace(u'\xa0', '&nbsp;') for output in outputs]
        print 'outputs:', outputs
        return outputs
