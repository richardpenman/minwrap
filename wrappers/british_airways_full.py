# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        # The expected result data will be filled in by run()
        self.data = [
            {'country': "GB", 'airport': "LHR", 'prefix': "new"}, 
            {'country': "GB", 'airport':"LGW", 'prefix': "edin"},
            {'country': "US", 'airport': "JFK", 'prefix': "lond"},
            {'country': "US", 'airport': "SFO", 'prefix': "new"},
        ]
        self.website = 'http://www.britishairways.com/travel/home/public/en_gb'
        self.category = 'flight'
        self.http_method = ''
        self.response_format = ''
        self.notes = ''

    def run(self, browser, inputs):
        
        from_country, from_airport, to_string = inputs['country'], inputs['airport'], inputs['prefix']
        
        browser.get(self.website)
        browser.wait_quiet()
        browser.wait(5)
        
        # Dismiss the cookies policy
        # TODO: This does not show properly (although the click does work)
        browser.click("div#accept_ba_cookies a")
        browser.wait(1)
        
        # Fill the origin
        browser.fill("select#depCountry", from_country)
        browser.wait(1)
        browser.fill("select#from", from_airport)
        browser.wait(1)
        
        # Fill the destination (using the autocomplete)
        browser.keys("input#planTripFlightDestination", to_string)
        browser.wait(1)
        browser.click('input#planTripFlightDestination') # TODO: This is required to show the autocomlete.
        browser.wait(1)
        browser.click("ul#destChoices > li:first-child")
        browser.wait(1)
        
        # Date pickers
        browser.click("input#depDate", True)
        browser.wait(1)
        # Select second week of next month so the selector will always match.
        browser.click("div.ui-datepicker-group-last table.ui-datepicker-calendar tr:nth-of-type(2) td:nth-of-type(1)")
        browser.wait(1)
        # Select the return date one week later, which is now shown on the left.
        browser.click("input#retDate", True)
        browser.wait(1)
        # TODO: The second date picker is not showing properly (although it doesn't matter the date we pick, so we can still progress)
        #browser.click("div.ui-datepicker-group-first table.ui-datepicker-calendar tr:nth-of-type(3) td:nth-of-type(1)")
        browser.click("div.ui-datepicker-group-last table.ui-datepicker-calendar tr:nth-of-type(3) td:nth-of-type(1)")
        browser.wait(1)
        
        # Submit
        browser.click("input#flightSearchButton", True)
        
        # Wait for the results page.
        browser.wait_load("div#OutboundFlightHeadingSection")
        browser.wait(1)
        
        # Extract the target data.
        extractions = [x.toInnerXml() for x in browser.find("table.flightList td:not(.hidden) span.time, table.flightList td:not(.hidden) span.date, table.flightList td:not(.hidden) span.priceSelection label:nth-of-type(2)")]
        #print extractions
        
        return {'prices': extractions}
        
