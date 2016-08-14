# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            {'search': 'supermarket near Oxford'}, 
            {'search': 'libraries near Oxford'}, 
            {'search': 'parks near Oxford'}, 
            {'search': 'colleges near Oxford'}, 
        ]
        self.website = 'http://maps.google.com'
        self.category = 'maps'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses dynamic results for expected output. '
        self.enabled = False

    def run(self, browser, inputs):
        browser.get(self.website)
        # XXX input not visible
        input_value = inputs['search']
        print browser.keys('input#ml-searchboxinput', input_value, True)
        print browser.keys('div#gs_lc50', input_value, True)
        print browser.attr('input#ml-searchboxinput', 'value')
        #print browser.click('div.ml-searchbox-directions-button-filler', True)
        print browser.click('button.searchbox-searchbutton', True)
        browser.wait_load('h3.widget-pane-section-result-title span')
        vs = browser.text('h3.widget-pane-section-result-title span')
        return {'names': vs}
