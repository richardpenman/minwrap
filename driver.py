# -*- coding: utf-8 -*-

# for using native Python strings
import sip
sip.setapi('QString', 2)

import os, collections, pprint
import abstract, common, parser, webkit
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl

"""
use intermediary HAR format?
    https://github.com/scrapinghub/splash/blob/master/splash/har/
how to check chain of requests?
check for cookies?

"""


class AjaxBrowser(webkit.Browser):
    def __init__(self, **argv):
        super(AjaxBrowser, self).__init__(**argv)
        self.transitions = []
        #self.inputs = {}
        self.orig_html = ''
        # keep track of the potentially useful transitions
        self.transitions = []

    def finished(self, reply):
        super(AjaxBrowser, self).finished(reply)
        if not reply.content:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        #print 'Request', reply.url().toString(), reply.data, content_type
        # main page has loaded
        content = common.to_unicode(str(reply.content))
        # XXX how to properly determine when main page is being loaded
        if reply.url() == self.view.url() and not reply.data:
            # wait for AJAX events to load
            self.orig_html = content
            self.transitions = []
        elif 'application/x-www-form-urlencoded' in content_type or 'application/xml' in content_type or 'application/javascript' in content_type or 'application/json' in content_type:# or 'text/javascript' in content_type:# or 'text/plain' in content_type:
            # have found a response that can potentially be parsed
            if self.orig_html:
                js = parser.parse(content, content_type)
                if js is None:
                    common.debug('failed to parse: {} {}'.format(reply.url().toString(), reply.data))
                else:
                    # were able to parse response
                    # save for checking later once interface has been updated
                    values = [common.to_unicode(value) for value in parser.json_values(js) if value]
                    common.logger.info('able to parse: {} {} {}'.format(reply.url().toString(), reply.data, len(values)))
                    self.transitions.append((Transition(reply, js), values))



class Transition:
    """Wrapper around a single transition using the QNetworkReply,
    which will be deleted by Qt so a local copy of details is necessary
    """
    def __init__(self, reply, js):
        self.url = reply.url()
        self.host = self.url.host()
        self.path = self.url.path()
        self.qs = self.url.queryItems()
        self.data = reply.data
        self.js = js
        request = reply.orig_request
        self.headers = [(header, request.rawHeader(header)) for header in request.rawHeaderList()]

    def key(self):
        """A unique key to represent this transition
        """
        get_keys = lambda es: tuple(k for (k,v) in es)
        return self.host, self.path, get_keys(self.qs), get_keys(self.data)

    def __str__(self):
        return '{} {}'.format(self.url.toString(), self.data)


def run(inputs, callback):
    """
    callback takes an AjaxBrowser instance and input parameter and executes the workflow for that input
    """
    browser = AjaxBrowser(gui=True)
    browser.view.setUrl(QUrl.fromLocalFile(os.path.abspath('start.html')))

    models = {}
    while browser.running:
        browser.wait_quiet()
        if browser.transitions:
            transitions, browser.transitions = browser.transitions, []
            orig_html = browser.orig_html
            cur_html = browser.current_html()
            for transition, values in transitions:
                total_changed = num_changed = 0
                for value in values:
                    total_changed += 1
                    if value in cur_html and value not in orig_html:
                        num_changed += 1

                common.logger.info('transition updates: {} {} / {}'.format(transition.url.toString(), num_changed, prop_changed))
                if num_changed > 0:
                    #399 / 2712
                    # XXX specific to each website - use std outside the mean?
                    if num_changed > 1:
                        key = transition.key()
                        if key in models:
                            model = models[key]
                        else:
                            models[key] = model = abstract.TransitionModel()
                        model.add(transition)
                        # XXX start new thread window
                        for url, headers, data in model.run():
                            if browser.running:
                                print 'Run:', url, data
                                browser.load(url=url, headers=headers, data=data)
                                js = parser.parse(browser.current_text())
                                if js:
                                    header, entries = json_to_list(js)
                                    print header
                                    #print entries
                                    browser.set_table(header, entries)
                            else:
                                break
                        #print values
                        #open('test_cur.html', 'w').write(common.to_ascii(cur_html))
                        #open('test_orig.html', 'w').write(common.to_ascii(orig_html))
    #browser.run()
    return

    for input_parameter in inputs:
        if abstraction.run(input_parameter):
            pass
            # XXX set browser interface to show download
        else:
            # XXX do this implicitly from form values?
            browser.input_parameter = input_parameter
            callback(browser, input_parameter)
            browser.wait_quiet()
            abstraction.update(browser.transitions)


# XXX move to specialist browser
def json_to_list(js):
    counter = parser.json_counter(js)
    num_entries = common.most_common([len(values) for values in counter.values()])
    # get the fields with the correct number of entries
    fields = sorted(key for key in counter.keys() if len(counter[key]) == num_entries)
    print 'num:', num_entries
    results = zip(*[counter[field] for field in fields])
    return fields, results
    
    


def main():
    postcodes = 'OX1', 'CB1'
    run(postcodes, fiat)
    #run(peugeot)
    searches = 'vie', 'aus'
    #run(searches, lufthunsa)

def fiat(browser, input_parameter):
    browser.load('http://www.fiat.co.uk/find-dealer')
    browser.fill('div.input_text input', input_parameter)
    browser.click('div.input_text button')

def peugeot(browser, input_parameter):
    browser.load('http://www.peugeot.nl/zoek-een-dealer/')
    print browser.wait_load('div.main_search')
    print browser.fill('div.main_search input#dl_main_search', input_parameter)
    print browser.click('div.main_search input[type=submit]')

def lufthunsa(browser, input_parameter):
    browser.load('http://www.lufthansa.com/uk/en/Homepage')
    print browser.fill('input#flightmanagerFlightsFormOrigin', input_parameter)

#delta


if __name__ == '__main__':
    main()
