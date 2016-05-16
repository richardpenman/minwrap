# -*- coding: utf-8 -*-

import csv, glob, operator, collections


class Abstraction:
    def __init__(self):
        self.type_data = collections.defaultdict(list)
        # load training data
        for filename in glob.glob('types/*.csv'):
            for row in csv.reader(open(filename)):
                for i, v in enumerate(row):
                    self.type_data['{}_{}'.format(filename, i)].append(v.lower())
            # XXX index each row; bag of words?
 
    def __call__(self, examples):
        if examples is None:
            return [None]
        else:
            scores = collections.defaultdict(int)
            for example in examples:
                example = example.lower()
                for label, values in self.type_data.items():
                    for value in values:
                        # use overlap? ignore case XXX
                        if example == value:
                            scores[label] += 1
                            break
            #print 'scores:', scores
            if scores:
                best_type = get_max_key(scores)
                return self.type_data[best_type]
            else:
                raise AbstractionError('Unable to abstract: {}'.format(examples))


def get_max_key(stats):
    """Returns the key with the maximum value from a dict
    """
    return max(stats.iteritems(), key=operator.itemgetter(1))[0]


class AbstractionError(Exception):
    pass
