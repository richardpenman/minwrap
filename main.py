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
        self.view.page().mainFrame().loadStarted.connect(self._load_start)
        self._load_start()
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
        # keep track of the potentially useful transitions
        self.wrapper = None
        # store transitions with the same path and similar querystring / POST at the same key
        self.models = {}


    def _load_start(self):
        """Start loading new page so clear the state
        """
        self.orig_html = self.orig_txt = ''
        self.transitions = []

    def _load_finish(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok and not self.current_url().startswith('file'):
            common.logger.info('loaded: {} {}'.format(ok, self.current_url()))
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
                    new_transition = transition.Transition(reply, js)
                    self.transitions.append(new_transition)
                    key = hash(new_transition)
                    try:
                        this_model = self.models[key]
                    except KeyError:
                        # start a new model for this key
                        self.models[key] = this_model = model.Model()
                    this_model.add(new_transition)


"""
when multiple then abstract
if appears in DOM then is assumed to be final node 
else may be intermediate stage
    load leaf nodes into table
"""

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
    browser = AjaxBrowser(gui=True, use_cache=True, load_images=False)
    set_start_state(browser)

    while browser.running:
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
            for prev_transition in browser.transitions:
                total_changed = num_changed = 0
                for value in prev_transition.values:
                    total_changed += 1
                    # XXX should instead isolate new part of DOM and compare against that
                    if (value in cur_html and value not in browser.orig_html) or (value in cur_text and value not in browser.orig_txt):
                        # found a change in this AJAX request that is not in the original DOM
                        num_changed += 1
       
                # XXX adjust this threshold for each website? STD around mean?
                if num_changed > 1:
                    parsed_transitions.append(prev_transition)
                    common.logger.info('Transition updates DOM: {} {} {} / {}'.format(prev_transition.url.toString(), prev_transition.data, num_changed, total_changed))
                    key = hash(prev_transition)
                    this_model = browser.models[key]
                    for event_i, (url, headers, data) in enumerate(this_model.run()):
                        # model has generated an AJAX request
                        if browser.running:
                            if event_i == 0:
                                # initialize the result table with the already known transitions
                                for result_transition in this_model.transitions:
                                    browser.table.add_rows(*parser.json_to_rows(result_transition.js))
                                    
                            common.logger.debug('Calling abstraction: {} {}'.format(url.toString(), data))
                            browser.load(url=url, headers=headers, data=data)
                            js = parser.parse(browser.current_text())
                            if js:
                                browser.table.add_rows(*parser.json_to_rows(js))
                        else:
                            break
                else:
                    common.logger.debug('Transition updates DOM: {} {} {} / {}'.format(prev_transition.url.toString(), prev_transition.data, num_changed, total_changed))
            for t in parsed_transitions:
                try:
                    browser.transitions.remove(t)
                except ValueError:
                    pass


if __name__ == '__main__':
    main()
