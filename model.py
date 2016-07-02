# -*- coding: utf-8 -*-

import csv, operator, collections, urllib, itertools
import common, verticals
# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl
from templater import Templater
import parser, transition

# constants to indicate GET and POST requests
PATH, GET, POST = 0, 1, 2



class Model:
    """Build a model for these transitions and extend to all known cases 
    """
    def __init__(self, input_values, transitions=None):
        # the input values used to generate this model
        self.input_values = input_values
        # the data extracted from these transitions
        self.records = []
        # the field names for the extracted data
        self.fields = []
        # the generated model PATH/GET/POST parameters
        self.params = None
        # whether model has already been executed
        self.used = False 
        # which parameters can be ignored
        self.ignored = []
        # the input values that triggered the transitions of this model
        self.data = []
        # the example transitions that follow this template
        self.transitions = []
        for transition in transitions or []:
            self.add(transition)


    def __len__(self):
        """Return the number of unique URL's in this model
        """
        return len(set([t.url.toString() for t in self.transitions]))


    def add(self, transition):
        """Add transition to model
        """
        self.transitions.append(transition)
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
        if self.build():
            # remove redundant parameters that do not change the result, such as counters
            for transition in self.transitions:
                if transition.output and (transition.qs or transition.data):
                    # found a transition that matches a known output
                    # check which parameters can be removed while still producing the same result
                    common.logger.info('Check whether any parameters in the model are redundant')
                    for (key, _), method in self.params:
                        ignore = key, method
                        if method in (GET, POST) and ignore not in self.ignored:
                            test_html = browser.view.get(**self.gen_request(ignored=self.ignored + [ignore], transition=transition))
                            if transition.matches(transition.output, test_html):
                                common.logger.info('Can ignore key: {}'.format(ignore))
                                self.ignored.append(ignore)
                    break # just need to test a single transition

            # abstract the example cases
            abstraction = []
            def gen_params(key, method, case_iter):
                for case in case_iter:
                    yield (key, case), method
            for ((key, examples), method) in self.params: 
                if (key, method) not in self.ignored:
                    abstraction.append(gen_params(key, method, self.abstract(browser, examples)))
            #remove_empty = lambda es: [e for e in es if e]
            
            for override_params in itertools.izip(*abstraction):
                # found an abstraction
                self.used = True
                download_params = self.gen_request(override_params)
                common.logger.debug('Calling abstraction: {url} {data}'.format(**download_params))
                yield browser.view.get(**download_params)

        else:
            # check whether multiple identical requests returned the same data
            unique_outputs = set([id(t.output) for t in self.transitions if t.output])
            if len(unique_outputs) > 1:
                common.logger.debug('Single request matches multiple outputs: {}'.format(str(self.transitions[-1])))
                self.used = True
                html = None#self.transitions[0].content
                yield browser.view.get(html=html, **self.gen_request())


    def gen_request(self, override_params=None, ignored=None, transition=None):
        """Generate a request modifying the transitions for this model with the provided parameters

        override_params: a list of ((key, value), method) pairs to override the parameters for this transition
        ignored: a list of (key, method) pairs of parameters that can be left out
        transition: a specific transition to use rather than the first one for this model
        """
        override_params = override_params or []
        ignored = ignored or []
        transition = transition or self.transitions[0]
        url = QUrl(transition.url)
        get_dict = dict([param for (param, method) in override_params if method == GET])
        post_dict = dict([param for (param, method) in override_params if method == POST])
        path_dict = self.path_to_dict(transition.path)
        for (key, case), method in override_params:
            if method == PATH:
                path_dict[key] = case
        url.setPath(self.dict_to_path(path_dict))
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
            path_diffs = self.find_diffs([self.path_to_dict(t.path).items() for t in self.transitions])
            get_diffs = self.find_diffs([t.qs for t in self.transitions])
            post_diffs = self.find_diffs([t.data for t in self.transitions])
            if get_diffs or post_diffs or path_diffs:
                self.params = [(diff, PATH) for diff in path_diffs] + [(diff, GET) for diff in get_diffs] + [(diff, POST) for diff in post_diffs] 
                common.logger.info('Model built: {}'.format(self.params))
                return True
            else:
                # found a duplicate transition
                common.logger.debug('Duplicate requests: {}'.format(self.transitions[-1]))
        return False


    def path_to_dict(self, path):
        return dict(enumerate(path.split('/')))

    def dict_to_path(self, d):
        return '/'.join(unicode(value) for _, value in sorted(d.items()))


    def find_diffs(self, kvs):
        """Find keys with different values
        kvs: list of (key, value) pairs
        """
        model = []
        kvdicts = [dict(kv) for kv in kvs]
        for key, _ in kvs[0]:
            values = [kvdict[key] for kvdict in kvdicts if kvdict[key]]
            if not all(value == values[0] for value in values):
                # found a key with differing values
                model.append((key, values))
        return model


    def extend_inputs(self, examples):
        for example in examples:
            if example not in self.input_values:
                return []
        # matches all examples
        print 'extended inputs:', examples, self.input_values
        return [value for value in self.input_values if value not in examples]


    def abstract(self, browser, examples):
        """Attempt abstacting these examples and if successful return a list of similar entities else None
        """
        if examples is not None:
            # check if examples are in the input values
            matches = self.extend_inputs(examples)
            if matches:
                browser.add_status('Abstraction uses input values: {}'.format(matches))
                for input_value in matches:
                    yield input_value

            else:
                # try extending from known vertical data
                similar_cases = verticals.extend(examples)
                if similar_cases is not None:
                    browser.add_status('Abstraction uses known vertical data: {}'.format(examples))
                    for case in similar_cases:
                        if case not in examples:
                            yield case
                else:
                    success = False
                    # check if examples are located at common location in a transition
                    for case in self.find_transitions(browser, examples):
                        if not success:
                            success = True
                            browser.add_status('Abstraction uses previous transition: {}'.format(examples))
                        if case not in examples:
                            yield case

                    if not success:
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
                                similar_cases.append(self.extend_inputs(examples) or verticals.extend(examples) or [])
                                if similar_cases[-1]:
                                    browser.add_status('Abstraction uses partial match: {}'.format(examples))
                                else:
                                    common.logger.info('Failed to abstract: {}'.format(examples))
                            else:
                                # create iterator of empty strings
                                similar_cases.append('' for _ in itertools.count())

                        if similar_cases:
                            for vector in zip(*similar_cases):
                                yield template.join(vector)
                        # XXX add support for partial matches over dependencies - need to find example
                        #else:
                        #    for result in self.navigate_dependencies(browser, examples):
                        #        yield template.join(result)


    def find_transitions(self, browser, examples):
        """Find transitions that have the example data we are after at the same JSON path
        """
        path_transitions = collections.defaultdict(list)
        for example in examples:
            for t in browser.transitions:
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
                for _ in model.Model(self.data, ts).run(browser):
                    js = parser.parse(self.current_text())
                    if js:
                        success = True
                        yield path(js)
                if success:
                    break # this model was successful so can exit
