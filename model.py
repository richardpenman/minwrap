# -*- coding: utf-8 -*-

import csv, operator, collections, urllib, itertools
import common, verticals
# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl
from templater import Templater
import parser

# constants to indicate GET and POST requests
GET, POST = 0, 1



class Model:
    """Build a model for these transitions and extend to all known cases 
    """
    def __init__(self, key):
        # the hash of transitions that will fit this model
        self.key = key
        # the example transitions that follow this template
        self.transitions = [] 
        # the data extracted from these transitions
        self.records = []
        # the field names for the extracted data
        self.fields = []
        # the generated model GET/POST parameters
        self.model = None
        # whether model has already been executed
        self.used = False 
        # which parameters can be ignored
        self.ignored = []


    def add(self, transition):
        """Add this transition to the model
        """
        if not self.used:
            self.transitions.append(transition)
            self.build()
            if transition.js:
                for record in parser.json_to_records(transition.js):
                    self.records.append(record)
                    for field in record:
                        if field not in self.fields:
                            self.fields.append(field)


    def run(self, browser):
        """Run the model if has successfully been built
        """
        if self.used:
            return
        if self.ready():
            # remove redundant parameters that do not change the result, such as counters
            for transition in self.transitions:
                if transition.output:
                    # found a transition that matches a known output
                    # check which parameters can be removed while still producing the same result
                    common.logger.info('Check whether any parameters in the model are redundant')
                    for (key, _), method in self.model:
                        ignore = key, method
                        if ignore not in self.ignored:
                            test_html = browser.load(**self.gen_request(ignored=[ignore], transition=transition))
                            if transition.matches(transition.output, test_html):
                                self.ignored.append(ignore)
                                print 'can ignore key:', ignore
                    break # just need to test a single transition

            # abstract the example cases
            remove_empty = lambda es: [e for e in es if e]
            abstraction = remove_empty([[((key, case), method) for case in self.abstract(examples)] for ((key, examples), method) in self.model if (key, method) not in self.ignored])
            
            for override_params in zip(*abstraction):
                # found an abstraction
                common.logger.debug('key: {}'.format(override_params))
                self.used = True
                download_params = self.gen_request(override_params)
                common.logger.debug('Calling abstraction: {url} {data}'.format(**download_params))
                yield browser.load(**download_params)

        else:
            # check whether multiple identical requests returned the same data
            unique_outputs = set([id(t.output) for t in self.transitions if t.output])
            if len(unique_outputs) > 1:
                common.logger.debug('Single request matches multiple outputs: {}'.format(str(self.transitions[-1])))
                self.used = True
                yield browser.load(**self.gen_request())


    def gen_request(self, override_params=None, ignored=None, transition=None):
        """Generate a request modifying the transitions for this model with the provided parameters

        override_params: a list of ((key, value), method) pairs to override the parameters for this transition
        ignored: a list of (key, method) pairs of parameters that can be left out
        transition: a specific transition to use rather than the first one for this model
        """
        get_dict = dict([param for (param, method) in (override_params or []) if method == GET])
        post_dict = dict([param for (param, method) in (override_params or []) if method == POST])
        ignored = ignored or []
        transition = transition or self.transitions[0]
        url = QUrl(transition.url)
        qs_items = transition.qs
        data_items = transition.data

        qs_items = [(key, urllib.quote_plus(get_dict[key].encode('utf-8')) if key in get_dict else value) for (key, value) in qs_items if (key, GET) not in ignored]
        url.setEncodedQueryItems(qs_items)
        data_items = [(key, post_dict[key] if key in post_dict else value) for (key, value) in data_items if (key, POST) not in ignored]
        return dict(url=url, headers=transition.headers, data=self.encode_data(data_items))


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
            get_diffs = self.find_diffs([t.qs for t in self.transitions])
            post_diffs = self.find_diffs([t.data for t in self.transitions])
            if get_diffs or post_diffs:
                self.model = [(diff, GET) for diff in get_diffs] + [(diff, POST) for diff in post_diffs]
            else:
                # found a duplicate transition
                common.logger.debug('Duplicate requests: {}'.format(self.transitions[-1]))


    def find_diffs(self, kvs):
        """Find keys with different values
        """
        model = []
        kvdicts = [dict(kv) for kv in kvs]
        for key, _ in kvs[0]:
            #if key.startswith('_'): continue # XXX
            values = [kvdict[key] for kvdict in kvdicts if kvdict[key]]
            if not all(value == values[0] for value in values):
                # found a key with differing values
                model.append((key, values))
        return model


    def abstract(self, examples):
        """Attempt abstacting these examples and if successful return a list of similar entities else None
        """
        if examples is not None:
            similar_cases = verticals.extend(examples)
            if similar_cases is not None:
                common.logger.info('Abstracted {}'.format(examples))
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
                            common.logger.info('Abstracted {}'.format(examples))
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
        return self.model is not None
