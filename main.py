# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)

import os, collections, pprint
import common, model, parser, transition, webkit, wrappers
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication



class AjaxBrowser(webkit.Browser):
    def __init__(self, **argv):
        """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
        """
        super(AjaxBrowser, self).__init__(**argv)
        #self.view.loadFinished.connect(self.loaded)
        self.view.page().mainFrame().loadFinished.connect(self.loaded)
        # XXX loadStarted signal to clear?
        self.orig_html = self.orig_txt = ''
        # keep track of the potentially useful transitions
        self.transitions = []
        self.wrapper = None


    def loaded(self, ok):
        if ok and not self.current_url().startswith('file'):
            print 'loaded:', ok, self.current_url()
            # a webpage has loaded successfully
            # store original content so that can compare later changes
            self.orig_html = self.current_html()
            self.orig_txt = self.current_text()
 

    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        super(AjaxBrowser, self).finished(reply)
        if not reply.content:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        # main page has loaded
        if 'application/x-www-form-urlencoded' in content_type or 'application/xml' in content_type or 'application/javascript' in content_type or 'application/json' in content_type or 'text/javascript' in content_type or 'text/plain' in content_type:
            # have found a response that can potentially be parsed
            if self.orig_html:
                content = common.to_unicode(str(reply.content))
                js = parser.parse(content, content_type)
                if js is None:
                    common.logger.debug('failed to parse: {} {}'.format(reply.url().toString(), reply.data))
                else:
                    # were able to parse response
                    common.logger.debug('Successfully parsed response: {} {} {}'.format(reply.url().toString(), reply.data, js))
                    # save for checking later once interface has been updated
                    self.transitions.append(transition.Transition(reply, js))

        #elif reply.url().toString() == self.current_url():
            # XXX how to properly determine when page loaded? loadFinished signal unreliable - check DOM change?
        #    self.loaded(True)


def set_start_state(browser):
    """Temporary hack to load a start page for choosing which wrapper to load
    """
    browser.view.setUrl(QUrl.fromLocalFile(os.path.abspath('start.html')))
    browser.view.page().setLinkDelegationPolicy(2)
    def link_clicked(url):
        link = url.toString()
        if link.endswith('/runbritishairways'):
            browser.wrapper = wrappers.britishairways().run(browser)
        elif link.endswith('/rundelta'):
            browser.wrapper = wrappers.delta().run(browser)
        elif link.endswith('/runfiat'):
            browser.wrapper = wrappers.fiat().run(browser)
        elif link.endswith('/runlufthansa'):
            browser.wrapper = wrappers.lufthansa().run(browser)
        elif link.endswith('/runpeugeot'):
            browser.wrapper = wrappers.peugeot().run(browser)
        else:
            # load the link
            browser.view.load(url)
    browser.view.linkClicked.connect(link_clicked)



def main():
    browser = AjaxBrowser(gui=True)
    set_start_state(browser)

    models = {}
    while browser.running:
        #browser.app.processEvents() 
        if browser.wrapper is not None:
            try:
                QApplication.setOverrideCursor(Qt.BusyCursor)
                browser.wrapper.next()
            except StopIteration:
                QApplication.restoreOverrideCursor()
                browser.wrapper = None
        browser.app.processEvents() 
        #browser.wait_quiet()

        if browser.transitions:
            parsed_transitions = []
            # check the transitions that were discovered
            #transitions, browser.transitions = browser.transitions, []
            cur_html = browser.current_html()
            cur_text = browser.current_text()
            for transition in browser.transitions:
                total_changed = num_changed = 0
                for value in transition.values:
                    total_changed += 1
                    # XXX should instead isolate new part of DOM and compare against that
                    if (value in cur_html and value not in browser.orig_html) or (value in cur_text and value not in browser.orig_txt):
                        # found a change in this AJAX request that is not in the original DOM
                        num_changed += 1
       
                # XXX adjust this threshold for each website? STD around mean?
                if num_changed > 1:
                    parsed_transitions.append(transition)
                    common.logger.info('Transition updates DOM: {} {} {} / {}'.format(transition.url.toString(), transition.data, num_changed, total_changed))
                    key = hash(transition)
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
                else:
                    common.logger.debug('Transition updates DOM: {} {} {} / {}'.format(transition.url.toString(), transition.data, num_changed, total_changed))
            #browser.transitions = []
            for t in parsed_transitions:
                browser.transitions.remove(t)


if __name__ == '__main__':
    main()
