# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import re, os, collections, pprint
import webkit, common, model, parser, transition, verticals, wrappers



class AjaxBrowser(webkit.Browser):
    def __init__(self, **argv):
        """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
        """
        super(AjaxBrowser, self).__init__(**argv)
        #self.view.page().mainFrame().loadStarted.connect(self._load_start)
        #self._load_start()
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
        # keep track of the potentially useful transitions
        self.wrapper = None
        # store transitions with the same path and similar querystring / POST at the same key
        self.models = {}
        # transitions found so far
        self.transitions = []


    #def _load_start(self):
    #    """Start loading new page so clear the state
    #    """

    def _load_finish(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok and not self.current_url().startswith('file'):
            # a webpage has loaded successfully
            common.logger.info('loaded: {} {}'.format(ok, self.current_url()))
 

    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        super(AjaxBrowser, self).finished(reply)
        if not reply.content:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        # main page has loaded
        if re.match('(image|audio|video|model|message)/', content_type) or content_type == 'text/css':
            pass # ignore these irrelevant content types
        else:
            common.logger.debug('Response: {} {}'.format(reply.url().toString(), reply.data))
            # have found a response that can potentially be parsed
            content = common.to_unicode(str(reply.content))
            if re.match('(application|text)/', content_type):
                js = parser.parse(content, content_type)
            else:
                js = None
            # save for checking later once interface has been updated
            new_transition = transition.Transition(reply, js)
            self.transitions.append(new_transition)
            key = hash(new_transition)
            try:
                this_model = self.models[key]
            except KeyError:
                # start a new model for this key
                self.models[key] = this_model = model.Model(key)
            this_model.add(new_transition)
            if False and this_model.ready():
                # add data to verticals for supporting multiple step abstractions
                verticals.add_model(this_model, self)



def set_start_state(browser):
    """Temporary hack to load a start page for choosing which wrapper to load
    """
    browser.view.setUrl(QUrl.fromLocalFile(os.path.abspath('start.html')))
    browser.view.page().setLinkDelegationPolicy(2)
    def link_clicked(url):
        link = url.toString()
        match = re.search('file.*/run(\w+)$', link)
        if match:
            try:
                wrapper = getattr(wrappers, match.groups()[0])()
            except AttributeError:
                pass
            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                browser.wrapper = wrapper.run(browser)
        else:
            # load the link
            browser.view.load(url)
    browser.view.linkClicked.connect(link_clicked)



def main():
    browser = AjaxBrowser(gui=True, use_cache=False, load_images=False, load_java=False, load_plugins=False)
    set_start_state(browser)

    expected_output = None
    while browser.running:
        if browser.wrapper is not None:
            try:
                expected_output = browser.wrapper.next()
                browser.wait_quiet()
            except StopIteration:
                QApplication.restoreOverrideCursor()
                browser.wrapper = None
        browser.app.processEvents() 

        if browser.transitions and expected_output:
            used_transitions = []
            # check whether the transitions that were discovered contain the expected output
            for prev_transition in browser.transitions:
                if prev_transition.matches(expected_output):
                    used_transitions.append(prev_transition)
                    key = hash(prev_transition)
                    this_model = browser.models[key]

                    for event_i, _ in enumerate(this_model.run(browser)):
                        if event_i == 0:
                            # initialize the result table with the already known transition records
                            browser.table.clear()
                            browser.table.add_records(this_model.records)
                        # model has generated an AJAX request
                        if browser.running:
                            js = parser.parse(browser.current_text())
                            if js:
                                browser.table.add_records(parser.json_to_records(js))
                        else:
                            break
            for t in used_transitions:
                try:
                    browser.transitions.remove(t)
                except ValueError:
                    pass


if __name__ == '__main__':
    main()
