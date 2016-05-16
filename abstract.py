# -*- coding: utf-8 -*-

import csv, glob, operator, collections


class Abstraction:
    def __init__(self):
        self.type_data = {}
        # load training data
        for filename in glob.glob('types/*.csv'):
            self.type_data[filename] = [row for row in csv.reader(open(filename))]
            # XXX index each row; bag of words?
 
    def __call__(self, examples):
        if examples is None:
            return [None]
        else:
            scores = collections.defaultdict(int)
            for example in examples:
                for filename, rows in self.type_data.items():
                    for row in rows:
                        # use overlap? XXX
                        if example in row:
                            scores[filename] += 1
                            break
            print 'scores:', scores
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
