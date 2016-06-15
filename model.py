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
        # XXX combine GET and POST into single list to reduce logic and match paper
        if self.used:
            return
        if self.ready():
            default_cases = [None]
            default = [(None, default_cases)]
            get_diffs, post_diffs = self.model
            # remove redundant parameters that do not change the result, such as counters
            for transition in self.transitions:
                if transition.output:
                    # found a transition that matches a known output
                    # check which parameters can be removed while still producing the same result
                    common.logger.info('Check whether any parameters in the model are redundant')
                    for key, _ in get_diffs:
                        ignore = key, GET
                        if ignore not in self.ignored:
                            test_html = browser.load(**self.gen_request(ignored=[(key, GET)], transition=transition))
                            if transition.matches(transition.output, test_html):
                                self.ignored.append(ignore)
                                print 'can ignore GET key:', key
                    for key, _ in post_diffs:
                        ignore = key, POST
                        if ignore not in self.ignored:
                            test_html = browser.load(**self.gen_request(ignored=[(key, POST)], transition=transition))
                            if transition.matches(transition.output, test_html):
                                ignored.append(ignore)
                                print 'can ignore POST key:', key
                    break

            # abstract the example cases
            remove_empty = lambda es: [e for e in es if e]
            get_abstraction = remove_empty([[(key, case) for case in self.abstract(examples)] for (key, examples) in get_diffs if (key, GET) not in self.ignored])
            post_abstraction = remove_empty([[(key, case) for case in self.abstract(examples)] for (key, examples) in post_diffs if (key, POST) not in self.ignored])
            
            for get_key_cases in zip(*(get_abstraction)) or [()]:
                common.logger.debug('qs key: {}'.format(get_key_cases))
                for post_key_cases in zip(*(post_abstraction)) or [()]:
                    common.logger.debug('post key: {}'.format(post_key_cases))
                    if get_key_cases or post_key_cases:
                        # found an abstraction
                        self.used = True
                        params = self.gen_request(dict(get_key_cases), dict(post_key_cases))
                        common.logger.debug('Calling abstraction: {url} {data}'.format(**params))
                        yield browser.load(**params)

        else:
            # check whether multiple identical requests returned the same data
            unique_outputs = set([id(t.output) for t in self.transitions if t.output])
            if len(unique_outputs) > 1:
                common.logger.debug('Single request matches multiple outputs: {}'.format(str(self.transitions[-1])))
                self.used = True
                yield browser.load(**self.gen_request())


    def gen_request(self, get_dict=None, post_dict=None, ignored=None, transition=None):
        """Generate a request modifying the transitions for this model with the provided parameters
        """
        get_dict = get_dict or {}
        post_dict = post_dict or {}
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
                self.model = get_diffs, post_diffs
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
