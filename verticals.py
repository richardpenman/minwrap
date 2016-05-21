# -*- coding: utf-8 -*-

__doc__ = 'Allow classifying inputs and extending them to all cases in the same domain'

import collections, csv, glob
import common


def hash_key(value):
    """Define a hash for this value that ignores case
    """
    return hash(value.lower())


def load_data():
    """Load sample vertical data into a dictionary with a key for each column
    """
    data = collections.defaultdict(dict)
    for filename in glob.glob('verticals/*.csv'):
        for row in csv.reader(open(filename)):
            for i, v in enumerate(row):
                if v:
                    data['{}-field{}'.format(filename, i)][hash_key(v)] = v
    return data
data = load_data()


def extend(examples):
    """Attempt abstacting these examples
    If successful return a list of similar entities else None"""
    scores = collections.defaultdict(int)
    for example in examples:
        for label, hash_dict in type_data.items():
            # use overlap instead of exact match? XXX
            if hash_key(example) in hash_dict:
                scores[label] += 1

    if scores:
        # a perfect score will match all labels
        num_perfect_labels = scores.values().count(len(examples))
        if num_perfect_labels == 1:
            label = [key for key in scores if scores[key] == len(examples)][0]
            common.logger.info('Using vertical: {}'.format(label))
            return type_data[label].values()
        elif num_perfect_labels == 0:
            common.logger.debug('Partially matched: {}'.format(label))
        else:
            common.logger.info('Multiple keys match all examples: {}'.format([key for key in scores if scores[key] == count]))

    else:
        common.logger.info('Insufficient data to abstract: {}'.format(examples))
