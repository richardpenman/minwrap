# -*- coding: utf-8 -*-

import os, sys, csv, re, json, urlparse, urllib, collections, difflib, pprint, numbers
import deepdiff
import common, parser, webkit
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
        self.replies = []

    def finished(self, reply):
        super(AjaxBrowser, self).finished(reply)
        if not hasattr(reply, 'data'):
            return

        if reply.data is not None:
            print
            print 'Request', reply.url().toString(), reply.data
            for header in reply.orig_request.rawHeaderList():
                print header, ':', reply.orig_request.rawHeader(header)
            print 'Reply'
            for header in reply.rawHeaderList():
                print header, ':', reply.rawHeader(header)
            open('test.html', 'w').write(reply.response)
        return
        if not reply.response:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        # main page has loaded
        #response = common.to_unicode(
        response = common.to_unicode(str(reply.response))#.lower()

        if reply.url() == self.view.url():
            # wait for AJAX events to load
            self.orig_html = response
            self.replies = []
            #self.wait_quiet()
            #self.inputs = self.parse_form()
        elif 'application/x-www-form-urlencoded' in content_type or 'application/xml' in content_type or 'application/javascript' in content_type or 'application/json' in content_type:
            # XXX check if updates interface?
            #self.matches_input(reply)
            if self.orig_html:
                js = parser.parse(response)
                if js is not None:
                    # XXX need to parse in callback after rendered
                    values = [common.to_unicode(value) for value in js_values(js) if value]#.lower()
                    print 'able to parse:', reply.url().toString(), reply.data, values
                    self.replies.append((reply, values))

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
                        print url, key, ':', value, len(reply.response), len(reply.data or '')
                        matches.append((GET, key, text_parser, input_value))
                        break
        # XXX need to also check POST data
        #if reply.data:
        #    print 'data:', reply.data

        if matches:
            reply.parsed_response = parser.parse(str(reply.response))
            if reply.parsed_response:
                self.transitions.append((reply, matches))
            else:
                print 'unable to parse response:', url
            return True
        return False


class AjaxAbstraction:
    def __init__(self):
        self.transitions = []

    def update(self, transitions):
        if transitions:
            print 'setting:', transitions
            self.transitions = transitions

    def run(self, current_input):
        status = False
        for reply, matches in self.transitions:
            # update query string
            params = collections.OrderedDict(reply.url().queryItems())
            for method, key, text_parser, original_input in matches:
                if method == GET:
                    params[key] = params[key].replace(text_parser(original_input), text_parser(current_input))
                elif method == POST:
                    pass # XXX
                else:
                    raise AjaxError('Unrecognized method: {}'.format(method))

            url = reply.url().toString().split('?')[0] + '?' + urllib.urlencode(params)
            #'&'.join('{}={}'.format(key, value) for key, value in params.items())
            print reply.url().toString(), '->', url
            from webscraping import download
            #print 'init ratio:', difflib.SequenceMatcher(a=download.Download().get(reply.url().toString()), b=reply.response).ratio()

            html = download.Download().get(url)
            parsed_response = parser.parse(html)
            if parsed_response is not None:
                diff = deepdiff.DeepDiff(reply.parsed_response, parsed_response)
                pprint.pprint(diff)
                #DiffWriter('rows.csv').parse(diff)
            else:
                print 'failed to parse:', url
            #s = difflib.SequenceMatcher(a=reply.response, b=html)
            #print 'ratio:', s.ratio()
            #for operation, i1, i2, j1, j2 in s.get_opcodes():
            #    if operation == 'replace':
            #        print reply.response[i1:i2], '->', html[j1:j2]
            status = True
        return status



class DiffWriter:
    def __init__(self, filename):
        self.writer = csv.writer(open(filename, 'w'))
        self.seen = {}
        self.header = []

    def __del__(self):
        pass # XXX write header
        self.writer.writerow(self.header)

    def parse(self, diff):
        old_record, new_record = {}, {}
        last_key = None
        for key, result in diff['values_changed'].items():
            match = re.search("'([^\]]*?)'\]$", key)
            if match:
                key = match.groups()[0]
                if key in old_record and last_key != key:
                    print 'new row:', key
                    # time to write values
                    self.write(old_record)
                    self.write(new_record)
                    old_record, new_record = {}, {}
                # add values to records
                if key not in self.header:
                    self.header.append(key)

                for record, value in (old_record, result['oldvalue']), (new_record, result['newvalue']):
                    value = common.unescape(unicode(value))
                    record[key] = record[key] + '|' + value if key in record else value
                last_key = key
            else:
                print 'no match:', key
        # write current versions 
        self.write(old_record)
        self.write(new_record)

    def write(self, record):
        """Write row to CSV if not seen before
        """
        if record:
            row = [record.get(field) for field in self.header]
            h = hash(tuple(row))
            if h not in self.seen:
                self.seen[h] = True
                #print row
                self.writer.writerow(row)


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
    model = []

    while browser.running:
        #browser.wait()
        browser.wait_quiet()
        if browser.replies:
            replies, browser.replies = browser.replies, []
            orig_html = browser.orig_html
            cur_html = common.to_unicode(browser.current_html())#.lower()
            for reply, values in replies:
                total_changed = num_changed = 0
                for value in values:
                    total_changed += 1
                    if value in cur_html and value not in orig_html:
                        #print 'changed:', value
                        num_changed += 1
                if num_changed > 0:
                    print '{} / {}'.format(num_changed, total_changed)
                    #399 / 2712
                    if num_changed / float(total_changed) > 0.2 and num_changed > 50:
                        model.append(reply)
                        #print values
                        #open('test_cur.html', 'w').write(common.to_ascii(cur_html))
                        #open('test_orig.html', 'w').write(common.to_ascii(orig_html))

    #print reply.rawHeader()
    #browser.run()
    return
    abstraction = AjaxAbstraction()

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
