# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('supermarket near Oxford', None),
            ('libraries near Oxford', None),
            ('parks near Oxford', None),
            ('colleges near Oxford', None),
        ]
        self.website = 'http://maps.google.com'
        self.category = 'maps'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output. '
        self.enabled = False

    def run(self, browser, input_value):
        browser.get(self.website)
        # XXX input not visible
        print browser.keys('input#ml-searchboxinput', input_value, True)
        print browser.keys('div#gs_lc50', input_value, True)
        print browser.attr('input#ml-searchboxinput', 'value')
        #print browser.click('div.ml-searchbox-directions-button-filler', True)
        print browser.click('button.searchbox-searchbutton', True)
        browser.wait_load('h3.widget-pane-section-result-title span')
        es = browser.find('h3.widget-pane-section-result-title span')
        vs = [e.toPlainText() for e in es]
        return vs
