# -*- coding: utf-8 -*-


class Wrapper:
    def __init__(self):
        self.data = [
            ({'city': 'Paris'}, None),
            ({'city': 'New York'}, None),
            ({'city': 'Berlin'}, None),
            ({'city': 'Rome'}, None),
        ]
        self.website = 'http://www.lastminute.com/flights/'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_steady()
        print browser.keys('input#flights-search-from', 'London')#, True, True)
        # XXX set input but still invisible
        #print browser.attr('input#flights-search-from', 'value')
        print browser.keys('input#flights-search-to', inputs['city'])#, True, True)
        #for e in browser.find('input#flights-search-to'):
        #    e.evaluateJavaScript('this.blur();')
        #browser.js('document.getElementById("flights-search-from").value = "{}";'.format(input_value))
        print browser.click('form[name="flights_search"] div.col-xs-6 button.btn.btn-primary.lmn-icon.lmn-icon-angle-right.submit-cannonball')
        browser.wait_steady(120)
        return [e.toPlainText().strip() for e in browser.find('div.offer-price > span.visuallyhidden')]
