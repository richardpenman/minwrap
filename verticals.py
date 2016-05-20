# -*- coding: utf-8 -*-

import collections, csv, glob
import common


class Verticals:
    """Wrapper around the vertical data
    """
    # dictionary of sample data
    # uses a class variable so is only loaded once over all instances
    type_data = None

    def __init__(self):
        if Verticals.type_data is None:
            self.load()


    def load(self):
        """Load the available vertical data
        """
        Verticals.type_data = collections.defaultdict(dict)
        # load training data
        for filename in glob.glob('verticals/*.csv'):
            for row in csv.reader(open(filename)):
                for i, v in enumerate(row):
                    if v:
                        Verticals.type_data['{}-field{}'.format(filename, i)][self.hash_key(v)] = v


    def extend(self, examples):
        """Attempt abstacting these examples
        If successful return a list of similar entities else None"""
        scores = collections.defaultdict(int)
        for example in examples:
            for label, hash_dict in Verticals.type_data.items():
                # use overlap instead of exact match? XXX
                if self.hash_key(example) in hash_dict:
                    scores[label] += 1

        if scores:
            # a perfect score will match all labels
            num_perfect_labels = scores.values().count(len(examples))
            if num_perfect_labels == 1:
                label = [key for key in scores if scores[key] == len(examples)][0]
                common.logger.info('Using vertical: {}'.format(label))
                return Verticals.type_data[label].values()
            elif num_perfect_labels == 0:
                common.logger.debug('Partially matched: {}'.format(label))
            else:
                common.logger.info('Multiple keys match all examples: {}'.format([key for key in scores if scores[key] == count]))

        else:
            common.logger.info('Insufficient data to abstract: {}'.format(examples))


    def hash_key(self, value):
        """Define a hash for this value that ignores case
        """
        return hash(value.lower())
