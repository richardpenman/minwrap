# -*- coding: utf-8 -*-

import os, sys, csv, re, json, urlparse, urllib, collections, difflib, pprint, numbers
import abstract, common, parser, webkit
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl

"""
use intermediary HAR format?
    https://github.com/scrapinghub/splash/blob/master/splash/har/
how to check chain of requests?
check for cookies?

"""

GET, POST = 'GET', 'POST'


# text parsers to test
text_parsers = [
    lambda s: s, # original string
    lambda s: s.replace(' ', '+'), # plus encoding
    lambda s: s.replace(' ', '%20'), # space encoding
    lambda s: urllib.quote(s), # percent encoding
]


def js_values(es):
    """
    >>> list(js_values({'name': 'bob', 'children': ['alice', 'sarah']}))
    ['bob', 'alice', 'sarah']
    """
    if isinstance(es, dict):
        for e in es.values():
            for result in js_values(e):
                yield result
    elif isinstance(es, list):
        for e in es:
            for result in js_values(e):
                yield result
    elif isinstance(es, basestring):
        yield es
    elif isinstance(es, numbers.Number):
        yield str(es)
    elif es is None:
        pass
    else:
        print 'unknown type:', type(es)


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

        """
            for header in reply.orig_request.rawHeaderList():
                print header, ':', reply.orig_request.rawHeader(header)
            print 'Reply'
            for header in reply.rawHeaderList():
                print header, ':', reply.rawHeader(header)
            print reply.content
            open('test.html', 'w').write(reply.content)
        """

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        #print 'Request', reply.url().toString(), reply.data, content_type
        # main page has loaded
        content = common.to_unicode(str(reply.content))
        # XXX how to properly determine when main page is being loaded
        if reply.url() == self.view.url() and not reply.data:
            # wait for AJAX events to load
            self.orig_html = content
            self.transitions = []
        elif 'application/x-www-form-urlencoded' in content_type or 'application/xml' in content_type or 'application/javascript' in content_type or 'application/json' in content_type:
            # have found a response that can potentially be parsed
            if self.orig_html:
                js = parser.parse(content)
                if js is None:
                    print 'failed to parse:', reply.url().toString(), reply.data
                else:
                    # were able to parse response
                    # save for checking later once interface has been updated
                    values = [common.to_unicode(value) for value in js_values(js) if value]
                    print 'able to parse:', reply.url().toString(), reply.data, len(values)
                    self.transitions.append((Transition(reply, js), values))

        #print reply.rawHeaderList()
        #print reply.rawHeaderPairs()
        #print dir(reply)

    def parse_form(self):
        inputs = {}
        for e in self.find('input'):
            inputs[e] = e.attribute('value')
        return inputs

    def changed_form(self):
        changed = []
        return changed
        for e in self.find('div.input_text input'):
            print 'input:', e.attribute('value')
            for s in e.attributeNames():
                print s
        for e, v in self.parse_form().items():
            print e
            old_v = self.inputs.get(e)
            if v and v != old_v:
                changed.append(v)
        if changed:
            print 'changed:', changed
        return changed


    def matches_input(self, reply):
        """Returns whether the input was found in these parameter values
        """
        return False
        matches = []
        url = reply.url().toString()
        for input_value in self.changed_form():
            for key, value in reply.url().queryItems():
                for text_parser in text_parsers:
                    if text_parser(input_value) == value:
                        print url, key, ':', value, len(reply.content), len(reply.data or '')
                        matches.append((GET, key, text_parser, input_value))
                        break

        if matches:
            reply.parsed_response = parser.parse(str(reply.response))
            if reply.parsed_response:
                self.transitions.append((reply, matches))
            else:
                print 'unable to parse response:', url
            return True
        return False



class TransitionModel:
    """Generate a model for these transitions
    """
    def __init__(self):
        self.transitions = []
        self.model = None
        self._used = False
        self.abstraction = abstract.Abstraction()

    def add(self, transition):
        """Add this transition to the model
        """
        if not self._used:
            print 'add reply', transition
            self.transitions.append(transition)
            self.build()
       
    def run(self):
        """Run the model if has successfully been built
        """
        if self.ready():
            default = [(None, [None])]
            qs_diffs, post_diffs = self.model
            # abstract the example cases
            qs_diffs = [(key, self.abstraction(examples)) for (key, examples) in qs_diffs]
            post_diffs = [(key, self.abstraction(examples)) for (key, examples) in post_diffs]
            print qs_diffs
            print post_diffs

            for qs_key, qs_cases in qs_diffs or default:
                for qs_case in qs_cases:
                    for post_key, post_cases in post_diffs or default:
                        for post_case in post_cases:
                            yield self.gen_request(qs_key, qs_case, post_key, post_case)                            

    def gen_request(self, qs_key, qs_value, post_key, post_value):
        """Generate a request modifying the transitions for this model with the provided parameters
        """
        transition = self.transitions[0]
        url = QUrl(transition.url)
        qs_items = transition.qs
        data_items = transition.data

        if qs_value is not None:
            # need to properly encode XXX
            qs_items = [(key, qs_value if key == qs_key else value) for (key, value) in qs_items]
            url.setEncodedQueryItems(qs_items)
        if post_value is not None:
            data_items = [(key, post_value if key == post_key else value) for (key, value) in data_items]
        return url, self.to_data(data_items)


    def to_data(self, items):
        """Convert these items into a string of data
        """
        url = QUrl('')
        url.setEncodedQueryItems(items)
        return str(url.toString())[1:]

    def build(self):
        """Build model of these transitions
        """
        if len(self.transitions) > 1:
            qs_diffs = self.compare([t.qs for t in self.transitions])
            post_diffs = self.compare([t.data for t in self.transitions])
            if qs_diffs or post_diffs:
                self.model = qs_diffs, post_diffs
            else:
                # remove the duplicate transition
                print 'duplicate requests'
                self.transitions = self.transitions[:1]

    def compare(self, kvs):
        """Find keys with different values
        """
        model = []
        kvdicts = [dict(kv) for kv in kvs]
        for key, _ in kvs[0]:
            values = [kvdict[key] for kvdict in kvdicts]
            if not all(value == values[0] for value in values):
                # found a key with differing values
                model.append((key, values))
        return model

    def ready(self):
        """Whether this model is ready to be used
        """
        return self.model is not None and not self._used



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

    def key(self):
        """A unique key to represent this transition
        """
        get_keys = lambda es: tuple(k for (k,v) in es)
        return self.host, self.path, get_keys(self.qs), get_keys(self.data)

    def __str__(self):
        return '{} {}'.format(self.url.toString(), self.data)


class AjaxEror(Exception):
    pass



def run(inputs, callback):
    """
    callback takes an AjaxBrowser instance and input parameter and executes the workflow for that input
    """
    browser = AjaxBrowser(gui=True)
    browser.view.setHtml(open('start.html').read())
    #browser.view.setUrl(QUrl.fromLocalFile(os.path.abspath('start.html')))

    #browser.get('http://www.lufthansa.com/uk/en/Homepage')
    #browser.get('http://www.fiat.co.uk/find-dealer')
    #browser.fill('div.input_text input', 'OX1')
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
                        #print 'changed:', value
                        num_changed += 1
                if num_changed > 0:
                    prop_changed = num_changed / float(total_changed)
                    print '{} / {} ({})'.format(num_changed, total_changed, prop_changed)
                    #399 / 2712
                    # XXX specific to each website - use std outside the mean?
                    if num_changed > 1:
                        key = transition.key()
                        if key in models:
                            model = models[key]
                        else:
                            models[key] = model = TransitionModel()
                        model.add(transition)
                        # XXX start new thread window
                        for url, data in model.run():
                            print url, data
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


def main():
    postcodes = 'OX1', 'CB1'
    run(postcodes, fiat)
    #run(peugeot)
    searches = 'vie', 'aus'
    #run(searches, lufthunsa)

def fiat(browser, input_parameter):
    browser.get('http://www.fiat.co.uk/find-dealer')
    browser.fill('div.input_text input', input_parameter)
    browser.click('div.input_text button')

def peugeot(browser, input_parameter):
    browser.get('http://www.peugeot.nl/zoek-een-dealer/')
    print browser.wait_load('div.main_search')
    print browser.fill('div.main_search input#dl_main_search', input_parameter)
    print browser.click('div.main_search input[type=submit]')

def lufthunsa(browser, input_parameter):
    browser.get('http://www.lufthansa.com/uk/en/Homepage')
    print browser.fill('input#flightmanagerFlightsFormOrigin', input_parameter)

#delta


if __name__ == '__main__':
    main()
