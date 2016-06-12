# -*- coding: utf-8 -*-

import csv, operator, collections, urllib, itertools
import common, verticals
# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl
from templater import Templater



class Model:
    """Build a model for these transitions and extend to all known cases 
    """
    def __init__(self):
        # the transitions that follow this template
        self.transitions = [] 
        self.model = None
        self._used = False # whether model has already been executed


    def add(self, transition):
        """Add this transition to the model
        """
        if not self._used:
            self.transitions.append(transition)
            self.build()


    def run(self):
        """Run the model if has successfully been built
        """
        if self.ready():
            default_cases = [None]
            default = [(None, default_cases)]
            qs_diffs, post_diffs = self.model
            # abstract the example cases
            remove_empty = lambda es: [e for e in es if e]
            qs_abstraction = remove_empty([[(key, case) for case in self.abstract(examples)] for (key, examples) in qs_diffs])
            post_abstraction = remove_empty([[(key, case) for case in self.abstract(examples)] for (key, examples) in post_diffs])
            #print 'abstractions:', qs_abstraction, post_abstraction
            
            for qs_key_cases in zip(*(qs_abstraction)) or [()]:
                common.logger.debug('qs key: {}'.format(qs_key_cases))
                for post_key_cases in zip(*(post_abstraction)) or [()]:
                    common.logger.debug('post key: {}'.format(post_key_cases))
                    if qs_key_cases or post_key_cases:
                        # found an abstraction
                        self._used = True
                        yield self.gen_request(dict(qs_key_cases), dict(post_key_cases))


    def gen_request(self, qs_dict, post_dict):
        """Generate a request modifying the transitions for this model with the provided parameters
        """
        transition = self.transitions[0]
        url = QUrl(transition.url)
        qs_items = transition.qs
        data_items = transition.data

        qs_items = [(key, urllib.quote_plus(qs_dict[key].encode('utf-8')) if key in qs_dict else value) for (key, value) in qs_items]
        url.setEncodedQueryItems(qs_items)
        # need to properly encode POST? XXX
        data_items = [(key, post_dict[key] if key in post_dict else value) for (key, value) in data_items]
        return url, transition.headers, self.encode_data(data_items)


    def encode_data(self, items):
        """Convert these querystring items into a string of data
        """
        if items:
            url = QUrl('')
            url.setEncodedQueryItems(items)
            return str(url.toString())[1:]
        else:
            return ''
 

    def build(self):
        """Build model of these transitions
        """
        if len(self.transitions) > 1:
            qs_diffs = self.find_diffs([t.qs for t in self.transitions])
            post_diffs = self.find_diffs([t.data for t in self.transitions])
            if qs_diffs or post_diffs:
                self.model = qs_diffs, post_diffs
            else:
                # remove the duplicate transition
                common.logger.debug('Duplicate requests')
                self.transitions = self.transitions[:1]


    def find_diffs(self, kvs):
        """Find keys with different values
        """
        model = []
        kvdicts = [dict(kv) for kv in kvs]
        for key, _ in kvs[0]:
            values = [kvdict[key] for kvdict in kvdicts if kvdict[key]]
            if not all(value == values[0] for value in values):
                # found a key with differing values
                model.append((key, values))
        return model


    def abstract(self, examples):
        """Attempt abstacting these examples
        If successful return a list of similar entities else None"""
        if examples is not None:
            similar_cases = verticals.extend(examples)
            if similar_cases:
                common.logger.info('Abstracted {} to {} similar examples'.format(examples, len(similar_cases)))
                for case in similar_cases:
                    yield case
            else:
                # no known data for these exact examples
                # interesting data may just be a subset so generate a template of static components
                template = Templater()
                for text in examples:
                    template.learn(text)
                common.logger.info('Trained template: {}'.format(template._template))

                # and now check whether dynamic components can be abstracted
                parsed_examples = [template.parse(text) for text in examples]
                similar_cases = []
                for examples in zip(*parsed_examples):
                    if any(examples):
                        similar_cases.append(verticals.extend(examples) or [])
                        if similar_cases[-1]:
                            common.logger.info('Abstracted {} to {} similar examples'.format(examples, len(similar_cases[-1])))
                        else:
                            common.logger.info('Failed to abstract: {}'.format(examples))
                    else:
                        # create iterator of empty strings
                        similar_cases.append('' for _ in itertools.count())
                for vector in zip(*similar_cases):
                    yield template.join(vector)


    def ready(self):
        """Whether this model is ready to be used
        """
        return self.model is not None and not self._used
