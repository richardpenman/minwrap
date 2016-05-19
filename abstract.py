# -*- coding: utf-8 -*-

import csv, glob, operator, collections, urllib
import common
# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl



class TransitionModel:
    """Generate a model for these transitions
    """
    def __init__(self):
        self.transitions = []
        self.model = None
        self._used = False
        self.abstraction = AbstractCases()

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
            qs_abstraction = [(key, self.abstraction(examples)) for (key, examples) in qs_diffs]
            post_abstraction = [(key, self.abstraction(examples)) for (key, examples) in post_diffs]
            
            for qs_key, qs_cases in qs_abstraction or default:
                for qs_case in qs_cases or default_cases:
                    for post_key, post_cases in post_abstraction or default:
                        for post_case in post_cases or default_cases:
                            if qs_case is not None or post_case is not None:
                                # found an abstraction
                                self._used = True
                                yield self.gen_request(qs_key, qs_case, post_key, post_case)

    def gen_request(self, qs_key, qs_value, post_key, post_value):
        """Generate a request modifying the transitions for this model with the provided parameters
        """
        transition = self.transitions[0]
        url = QUrl(transition.url)
        qs_items = transition.qs
        data_items = transition.data

        if qs_value is not None:
            qs_items = [(key, urllib.quote_plus(qs_value) if key == qs_key else value) for (key, value) in qs_items]
            url.setEncodedQueryItems(qs_items)
        if post_value is not None:
            # need to properly encode POST? XXX
            data_items = [(key, post_value if key == post_key else value) for (key, value) in data_items]
        return url, transition.headers, common.list_to_qs(data_items)


    def build(self):
        """Build model of these transitions
        """
        if len(self.transitions) > 1:
            qs_diffs = self.compare([t.qs for t in self.transitions])
            post_diffs = self.compare([t.data for t in self.transitions])
            if qs_diffs or post_diffs:
                self.model = qs_diffs, post_diffs
            else:
                # remove the duplicate transition
                common.logger.debug('Duplicate requests')
                self.transitions = self.transitions[:1]


    def compare(self, kvs):
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


    def ready(self):
        """Whether this model is ready to be used
        """
        return self.model is not None and not self._used



class AbstractCases:
    # dictionary of sample data
    # uses a class variable so is only loaded once over all instances
    type_data = None
    
    def __init__(self):
        if AbstractCases.type_data is None:
            self.load_types()


    def load_types(self):
        AbstractCases.type_data = collections.defaultdict(dict)
        # load training data
        for filename in glob.glob('types/*.csv'):
            for row in csv.reader(open(filename)):
                for i, v in enumerate(row):
                    if v:
                        AbstractCases.type_data['{}-field{}'.format(filename, i)][self.hash_key(v)] = v


    def __call__(self, examples):
        """Attempt abstacting these examples
        If successful return a list of similar entities else None"""
        if examples is not None:
            scores = collections.defaultdict(int)
            template, examples = self.strip_surroundings(examples)
            common.logger.info('Abstraction template: {} {}'.format(template, examples))
            for example in examples:
                for label, hash_dict in AbstractCases.type_data.items():
                    # use overlap? XXX
                    if self.hash_key(example) in hash_dict:
                        scores[label] += 1
            
            if scores:
                label = self.get_max_key(scores)
                if label is not None:
                    if scores[label] == len(examples):
                        common.logger.info('Using types: {}'.format(label))
                        values = AbstractCases.type_data[label].values()
                        for value in values:
                            yield template.format(value)
                    else:
                        common.logger.debug('Partially matched: {}'.format(label))
            else:
                # XXX return None ?
                common.logger.info('Insufficient data to abstract: {}'.format(examples))


    def strip_surroundings(self, examples):
        """Build a template that removes the common prefix and suffix

        >>> AbstractCases.type_data = {}
        >>> ac = AbstractCases()
        >>> ac.get_surroundings(['<div>hello</div>', '<div>world</div>'])
        ('<div>{}</div>', ['hello', 'world'])
        >>> ac.get_surroundings(['aba', 'aca'])
        ('a{}a', ['b', 'c'])
        >>> ac.get_surroundings(['hello', 'world'])
        ('{}', ['hello', 'world'])
        """
        prefix = ''
        suffix = ''
        for i, letters in enumerate(zip(*examples)):
            if len(set(letters)) == 1:
                prefix += letters[0]
            else:
                for letters in reversed(list(zip(*examples))[i:]): 
                    if len(set(letters)) == 1:
                        suffix = letters[0] + suffix
                    else:
                        break
                break
        escape_brackets = lambda v: v.replace('{', '{{').replace('}', '}}')
        return escape_brackets(prefix) + '{}' + escape_brackets(suffix), [example[len(prefix) : len(example) - len(suffix)] for example in examples]

    def hash_key(self, value):
        """Define a hash for this value that ignores case
        """
        return hash(value.lower())


    def get_max_key(self, scores):
        """Returns the the key with the maximum value from a dict
        If multiple keys have this value then return None - need more cases"""
        label, count = max(scores.iteritems(), key=operator.itemgetter(1))
        if scores.values().count(count) == 1:
            return label
        else:
            common.logger.info('Multiple keys with same count "{}": {}'.format(count, [key for key in scores if scores[key] == count]))


#class AbstractionError(Exception):
#    pass
