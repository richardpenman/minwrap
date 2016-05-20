# -*- coding: utf-8 -*-

# for using native Python strings
import sip
sip.setapi('QString', 2)

import os, collections, pprint
import common, model, parser, transition, webkit, wrappers
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl



class AjaxBrowser(webkit.Browser):
    def __init__(self, **argv):
        """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
        """
        super(AjaxBrowser, self).__init__(**argv)
        self.orig_html = ''
        # keep track of the potentially useful transitions
        self.transitions = []


    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        super(AjaxBrowser, self).finished(reply)
        if not reply.content:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        # main page has loaded
        content = common.to_unicode(str(reply.content))
        # XXX how to properly determine when main page is being loaded?
        if reply.url() == self.view.url() and not reply.data:
            # wait for AJAX events to load
            self.orig_html = content
            self.transitions = []
        elif 'application/x-www-form-urlencoded' in content_type or 'application/xml' in content_type or 'application/javascript' in content_type or 'application/json' in content_type:# or 'text/javascript' in content_type or 'text/plain' in content_type:
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
                    self.transitions.append((transition.Transition(reply, js), values))



def set_start_state(browser):
    """Temporary hack to load a start page for choosing which wrapper to load
    """
    browser.view.setUrl(QUrl.fromLocalFile(os.path.abspath('start.html')))
    browser.view.page().setLinkDelegationPolicy(2)
    def link_clicked(url):
        link = url.toString()
        if link.endswith('/runfiat'):
            wrappers.fiat(browser)
        elif link.endswith('/runlufthansa'):
            wrappers.lufthansa(browser)
        elif link.endswith('/runpeugeot'):
            wrappers.peugeot(browser)
        else:
            # load the link
            browser.view.load(url)
    browser.view.linkClicked.connect(link_clicked)



def main():
    browser = AjaxBrowser(gui=True)
    set_start_state(browser)

    models = {}
    while browser.running:
        browser.wait_quiet()
        if browser.transitions:
            # check the transitions that were discovered
            transitions, browser.transitions = browser.transitions, []
            orig_html = browser.orig_html
            cur_html = browser.current_html()
            for transition, values in transitions:
                total_changed = num_changed = 0
                for value in values:
                    total_changed += 1
                    if value in cur_html and value not in orig_html:
                        # found a change in this AJAX request that is not in the original DOM
                        num_changed += 1

                common.logger.info('Transition updates DOM: {} {} {} / {}'.format(transition.url.toString(), transition.data, num_changed, total_changed))
                # XXX adjust this threshold for each website? STD around mean?
                if num_changed > 1:
                    key = transition.key()
                    if key in models:
                        this_model = models[key]
                    else:
                        # start a new model for this key
                        models[key] = this_model = model.Model()
                    this_model.add(transition)
                    for event_i, (url, headers, data) in enumerate(this_model.run()):
                        # model has generated an AJAX request
                        if browser.running:
                            if event_i == 0:
                                # initialize the result table with the already known transitions
                                for transition in this_model.transitions:
                                    browser.table.add_rows(*parser.json_to_rows(transition.js))
                                    
                            common.logger.debug('Calling abstraction: {} {}'.format(url.toString(), data))
                            browser.load(url=url, headers=headers, data=data)
                            js = parser.parse(browser.current_text())
                            if js:
                                browser.table.add_rows(*parser.json_to_rows(js))
                        else:
                            break



if __name__ == '__main__':
    main()
