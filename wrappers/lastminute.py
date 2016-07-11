# -*- coding: utf-8 -*-


class Wrapper:
    def __init__(self):
        self.data = [
            ('Paris', None),
            ('New York', None),
            ('Berlin', None),
            ('Rome', None),
        ]
        self.website = 'http://www.lastminute.com/flights/'
        self.category = 'flight'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.enabled = False

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.wait_steady()
        browser.keys('input#flights-search-from', 'London')
        # XXX set input but still invisible
        print browser.attr('input#flights-search-from', 'value')
        browser.keys('input#flights-search-to', input_value)
        #browser.js('document.getElementById("flights-search-from").value = "{}";'.format(input_value))
        browser.click('form[name="flights_search"] button[type="submit"]')
        browser.wait_steady(120)
        return [e.toPlainText().strip() for e in browser.find('div.offer-price > span.visuallyhidden')]
