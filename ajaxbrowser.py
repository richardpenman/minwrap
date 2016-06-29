# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest

import re, collections
import webkit, common, model, parser, transition



class AjaxBrowser(webkit.Browser):
    """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
    """
    def __init__(self, **argv):
        super(AjaxBrowser, self).__init__(**argv)
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
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
        """Recieves a list of potential models for the execution. 
        Executes them in order, shortest first, until find one that successfully executes.
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
        """Find transitions that have the example data we are after at the same JSON path
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
