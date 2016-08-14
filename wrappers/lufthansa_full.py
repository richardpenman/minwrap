# -*- coding: utf-8 -*-

import re

class Wrapper:
    def __init__(self):
        # The expected result data will be filled in by run().
        self.data = [
            {'from': 'LHR', 'to': 'VIE'}, 
            {'from': 'LHR', 'to': 'MUC'},
            {'from': 'LHR', 'to': 'BER'},
        ]
        self.website = 'http://www.lufthansa.com/uk/en/Homepage'
        self.category = ''
        self.http_method = ''
        self.response_format = ''
        self.notes = 'Takes ages in the testing loop because there are too many parameters to check.'

    def run(self, browser, inputs):
        origin_airport_search, destination_airport_search = inputs['from'], inputs['to']
        
        browser.get(self.website)
        
        browser.wait(0.5)
        
        browser.keys('input#flightmanagerFlightsFormOrigin', origin_airport_search)
        
        browser.wait_load('div.rw-popup')
        browser.wait_quiet()
        
        browser.wait(0.5)
        
        # Check that we found the autocomplete item
        #elem = browser.find('li.rw-list-option:first-of-type')[0]
        #print elem
        #print elem.toOuterXml()
        
        #browser.click('li.rw-list-option:first-of-type', mouseover=True)
        #elem.evaluateJavaScript("this.click()");
        #browser.click_by_user_event_simulation(elem);
        browser.click('li.rw-list-option:first-of-type', True)
        
        browser.wait(0.5)
        
        # Type the query
        browser.keys('input#flightmanagerFlightsFormDestination', destination_airport_search)
        # Wait for autocomplete popup
        browser.wait_load('div.rw-popup')
        browser.wait_quiet()
        # Click the first entry
        browser.click('li.rw-list-option:first-of-type', True)
        
        browser.wait(0.5)
        
        # Click the date picker
        browser.click('input#flightmanagerFlightsFormOutboundDateDisplay', True)
        browser.wait(0.5)
        
        # Select the dates - N.B. We select the first full week from next month so we know the dates will always be available!
        #print browser.find("div.months-wrapper div.month:nth-of-type(2) tr.days-row:nth-of-type(2) td.day-body:first-of-type button")[0].toInnerXml()
        #print browser.find("div.months-wrapper div.month:nth-of-type(2) tr.days-row:nth-of-type(3) td.day-body:first-of-type button")[0].toInnerXml()
        
        browser.click("div.months-wrapper div.month:nth-of-type(2) tr.days-row:nth-of-type(2) td.day-body:first-of-type button", True)
        browser.wait(0.5)
        browser.click("div.months-wrapper div.month:nth-of-type(2) tr.days-row:nth-of-type(3) td.day-body:first-of-type button", True)
        browser.wait(1)
        
        # Click submit
        #print browser.find("#flightmanagerFlightsForm button.btn-primary")
        browser.click("#flightmanagerFlightsForm button.btn-primary", True)
        
        # Page is loading...
        #print "Just clicked"
        browser.wait_load("section.wdk-result")
        browser.wait_quiet()
        #print "Result page loaded"
        
        # TODO: A better solution would be to connect to the loadFinished signal (with a timeout), as _load_finish does in AjaxBrowser in main.py.
        
        # Dynamically extract the "goal data".
        extractions = [x.toInnerXml() for x in browser.find("div.time span:nth-child(1), div.time span:nth-child(3), div.stops-and-duration span, td.fare-price label")]
        def filter_prices(x):
            r = re.compile("from ([0-9\.]+) GBP")
            m = r.match(x)
            if m:
                return m.group(1)
            else:
                return x
        extractions = map(filter_prices, extractions)
        #print extractions
        
        # Optinally return the scraped result data instead opf hard-coded result data set in __init__ above.
        return {'prices': extractions}

