# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import argparse, sys, re, os, collections, pprint
import webkit, common, model, parser, transition, verticals, wrappertable



class AjaxBrowser(webkit.Browser):
    def __init__(self, **argv):
        """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
        """
        super(AjaxBrowser, self).__init__(**argv)
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
        # keep track of the potentially useful transitions
        self.wrapper = None
        # transitions found so far
        self.transitions = []


    def _load_finish(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok:
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
            # have found a response that can potentially be parsed for useful content
            content = common.to_unicode(str(reply.content))
            if re.match('(application|text)/', content_type):
                js = parser.parse(content, content_type)
            else:
                js = None
            # save for checking later once interface has been updated
            self.transitions.append(transition.Transition(reply, js))


    def run_models(self, models):
        """Try running models first that potentially use less steps, given by the length of the model
        """
        for final_model in sorted(models.values(), key=lambda m: len(m), reverse=True): # XXX reverse sort to test geocode
            event_i = None
            for event_i, _ in enumerate(final_model.run(self)):
                if event_i == 0:
                    # initialize the result table with the already known transition records
                    self.table.clear()
                    self.table.add_records(final_model.records)
                # model has generated an AJAX request
                if self.running:
                    js = parser.parse(self.current_text())
                    if js:
                        self.table.add_records(parser.json_to_records(js))
                else:
                    break
            if event_i is not None:
                break # sucessfully executed a model so can exit


    def find_transitions(self, examples):
        """Find transitions that have the example data we are after at the same path
        """
        path_transitions = collections.defaultdict(list)
        for example in examples:
            for t in self.transitions:
                if example in t.values:
                    # data exists in this transition
                    for path in transition.generate_path(t.js, example):
                        path_transitions[path].append(t)

        # check if any of these matches can be modelled
        for path, ts in path_transitions.items():
            if len(ts) == len(examples):
                # found a path that satisfies all conditions
                common.logger.info('Found a path: {}'.format(path))
                success = False
                for _ in model.Model(ts).run(self):
                    js = parser.parse(self.current_text())
                    if js:
                        success = True
                        yield path(js)
                if success:
                    break # this model was successful so can exit



def main(wrapper_name):
    app = QApplication(sys.argv)
    if wrapper_name is None:
        wt = wrappertable.WrapperTable()
        app.exec_()
        if wt.wrapper is None:
            return
        wrapper_name = wt.wrapper_name

    # execute the selected wrapper 
    browser = AjaxBrowser(app=app, gui=True, use_cache=False, load_images=False, load_java=False, load_plugins=False)
    browser.wrapper = wrappertable.load_wrapper(wrapper_name).run(browser)
    QApplication.setOverrideCursor(Qt.WaitCursor)

    models = {} 
    expected_output = None
    while browser.running:
        if browser.wrapper is not None:
            try:
                expected_output = browser.wrapper.next()
                browser.wait_quiet()
            except StopIteration:
                # completed running the wrapper
                expected_output = browser.wrapper = None
                QApplication.restoreOverrideCursor()
                browser.run_models(models)
        browser.app.processEvents() 

        if browser.transitions and expected_output:
            # check whether the transitions that were discovered contain the expected output
            for t in reversed(browser.transitions):
                if t.matches(expected_output):
                    # found a transition that matches the expected output so add it to model
                    try:
                        m = models[hash(t)]
                    except KeyError:
                        m = models[hash(t)] = model.Model()
                    m.add(t)
                    browser.transitions.remove(t)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--show-wrappers', action='store_true', help='display a list of available wrappers')
    ap.add_argument('-w', '--wrapper', help='the wrapper to execute')
    args = ap.parse_args()
    wrapper_names = wrappertable.get_wrappers()
    if args.show_wrappers:
        print 'Available wrappers:', wrapper_names
    else:
        if args.wrapper is None or args.wrapper in wrapper_names:
            main(args.wrapper)
        else:
            ap.error('This wrapper does not exist. Available wrappers are: {}'.format(wrapper_names))
