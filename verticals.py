# -*- coding: utf-8 -*-

__doc__ = 'Allow classifying inputs and extending them to all cases in the same domain'

import collections, csv, glob, threading
import common


def hash_key(value):
    """Define a hash for this value that ignores case
    """
    return hash(value.lower())


vertical_data = collections.defaultdict(dict)
def load_data():
    """Load sample vertical data into a dictionary with a key for each column
    """
    common.logger.debug('Start loading verticals data')
    global vertical_data
    for filename in glob.glob('verticals/*.csv'):
        for row in csv.reader(open(filename)):
            for i, v in enumerate(row):
                if v:
                    vertical_data['{}-field{}'.format(filename, i)][hash_key(v)] = v
    common.logger.debug('Completed loading verticals data')
# load vertical data in background thread
threading.Thread(target=load_data, args=()).start()


def extend(examples):
    """Attempt abstacting these examples
    If successful return a list of similar entities else None"""
    scores = collections.defaultdict(int)
    for example in examples:
        for label, hash_dict in vertical_data.items():
            # use overlap instead of exact match? XXX
            if hash_key(example) in hash_dict:
                scores[label] += 1

    if scores:
        # a perfect score will match all examples
        num_perfect_labels = scores.values().count(len(examples))
        if num_perfect_labels == 1:
            # found that a unique category matched these examples
            label = [key for key in scores if scores[key] == len(examples)][0]
            common.logger.info('Using vertical: {}'.format(label))
            return vertical_data[label].values()
        elif num_perfect_labels == 0:
            # found no category perfectly matched
            common.logger.debug('Partially matched: {}'.format(label))
        else:
            # found multiple categories perfectly matched, so need more examples
            common.logger.info('Multiple keys match all examples: {}'.format([key for key in scores if scores[key] == count]))

    else:
        # no matches to examples
        common.logger.info('Examples do not match available vertical data: {}'.format(examples))
