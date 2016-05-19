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
        self.view.page().setLinkDelegationPolicy(2)
        self.view.linkClicked.connect(self.link_clicked)

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
                    common.logger.debug('failed to parse: {} {}'.format(reply.url().toString(), reply.data))
                else:
                    # were able to parse response
                    # save for checking later once interface has been updated
                    values = [common.to_unicode(value) for value in parser.json_values(js) if value]
                    common.logger.debug('Successfully parsed response: {} {} {}'.format(reply.url().toString(), reply.data, values))
                    self.transitions.append((Transition(reply, js), values))

    def link_clicked(self, url):
        link = url.toString()
        if link.endswith('/runfiat'):
            fiat(self)
        elif link.endswith('/runlufthansa'):
            lufthansa(self)
        elif link.endswith('/runpeugeot'):
            peugeot(self)
        else:
            # load the link
            self.view.load(url)


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


def main():
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

                common.logger.info('Transition updates DOM: {} {} {} / {}'.format(transition.url.toString(), common.list_to_qs(transition.data), num_changed, total_changed))
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
                                common.logger.debug('Calling abstraction: {} {}'.format(url.toString(), data))
                                browser.load(url=url, headers=headers, data=data)
                                js = parser.parse(browser.current_text())
                                if js:
                                    header, entries = json_to_list(js)
                                    browser.update_table(header, entries)
                            else:
                                break


# XXX move to specialist browser
def json_to_list(js):
    counter = parser.json_counter(js)
    num_entries = common.most_common([len(values) for values in counter.values()])
    # get the fields with the correct number of entries
    fields = sorted(key for key in counter.keys() if len(counter[key]) == num_entries)
    results = zip(*[counter[field] for field in fields])
    return [field.title() for field in fields], results
    
    


def fiat(browser):
    postcodes = 'OX1', 'CB2'
    browser.load('http://www.fiat.co.uk/find-dealer')
    for postcode in postcodes:
        browser.fill('div.input_text input', postcode)
        browser.click('div.input_text button')
        browser.wait_quiet()

def lufthansa(browser):
    searches = 'vie', 'aus'
    browser.load('http://www.lufthansa.com/uk/en/Homepage')
    for search in searches:
        browser.click('input#flightmanagerFlightsFormOrigin')
        for letter in search:
            browser.keydown(letter)
        #browser.fill('input#flightmanagerFlightsFormOrigin', search)
        browser.wait(3)
        browser.wait_load('div.rw-popup')

def peugeot(browser):
    locations = 'amsterdam', 'leiden'
    browser.load('http://www.peugeot.nl/zoek-een-dealer/')
    print browser.wait_load('div.main_search')
    for location in locations:
        print browser.fill('div.main_search input#dl_main_search', location)
        print browser.click('div.main_search input[type=submit]')
        browser.wait_quiet()


if __name__ == '__main__':
    main()
