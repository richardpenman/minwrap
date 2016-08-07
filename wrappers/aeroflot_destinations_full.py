# -*- coding: utf-8 -*-

from browser_wrapper import BrowserWrapper

# Aeroflot
# Make a flight search for a single trip with locations and the departure date specified

class Wrapper():
    def __init__(self):
        self.data = [
            ({'from': 'Vienna', 'to': 'Moscow', 'date': '30.10.2016'}, None),
            ({'from': 'Vienna', 'to': 'London', 'date': '30.10.2016'}, None),
            ({'from': 'London', 'to': 'Vienna', 'date': '30.10.2016'}, None)
        ]
        self.website = 'http://www.aeroflot.ru/ru-en'
        self.category = 'flight search (aeroflot)'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser, inputs):
        origin_airport, destination_airport, departure_date = inputs['from'], inputs['to'], inputs['date']
        
        bw = BrowserWrapper(browser)
        bw.get(self.website)
        
        # Single trip
        bw.userClick('#ttOW')
        
        # Select Locations
        bw.userKeys('#ttOri0', origin_airport)
        bw.userClick('#ui-id-1')

        bw.userKeys('#ttDest0', destination_airport)
        bw.userClick('#ui-id-2')

        # Select date
        bw.userKeys('#ttLeaveDate0', departure_date)
        
        #Confirm
        bw.userClick('#ttConfirm')
        
        # Search!
        bw.userClick('#ttSubmitBtn')
        #browser.wait(11)
        browser.wait_load(".prices-alternative")
        
#         def myreplace(x):
#             return x.replace(u'(&nbsp;|\xa0|\\s)+','')
        
        outputs = bw.getOutput([
                   (".prices-alternative",
                        None,
                        None
                    )
                   ],
                    None)
        print 'outputs:', outputs
        return outputs
