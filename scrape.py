# -*- coding: utf-8 -*-

import collections
import common, selector, transition



def find_columns(url, parsed_content, expected_output):
    """Receives the content of a web page and a dict of the expected output for each field.
    Returns a dict with a selector for each field if they can be found, else None.
    """
    if not expected_output:
        return
    columns = {}
    for field, values in expected_output.items():
        values = common.unique(values)
        paths = collections.defaultdict(list)
        for e, path in parsed_content.find(values):
            # found a selector value we are after in this response
            paths[e].append(path)

        if paths:
            common.logger.debug('AJAX results:')
            for e in paths:
                common.logger.debug('{} {}'.format(e, [str(path) for path in paths[e]]))
        # XXX adjust this threshold for each website?
        if paths and len(paths) > len(values) / 2:
            # found enough matches
            common.logger.info('Content matches expected output: {} {} ({} / {})'.format(url, field, len(paths), len(values)))
            column = common_selector(paths.values())
            if column:
                common.logger.info('Found match for column: {} {}'.format(field, column))
                columns[field] = column
            else:
                common.logger.debug('Failed to find match for column: {} {}'.format(field, len(paths)))
                return
        else:
            common.logger.debug('Content does not match expected output: {} {} ({} / {})'.format(url, field, len(paths), len(values)))
            return 
    return columns



def common_selector(selector_groups):
    """Takes a list of [selector] lists.
    Return an abstracted selector that can match the majority of them.

    >>> from transition import JsonPath as jp
    >>> # test changing index
    >>> print common_selector([[jp([0, 'name'])], [jp([1, 'name'])]])
    [*]['name']
    >>> # test no matches
    >>> common_selector([[jp([0, 'name'])], [jp([1, 'age'])]])
    >>> # test changing key
    >>> print common_selector([[jp([0, 'name'])], [jp([0, 'age'])]])
    [0][*]
    >>> # test multiple paths
    >>> print common_selector([[jp(['_']), jp([0, 'name'])], [jp([1, 'name']), jp([1, 'age'])]])
    [*]['name']
    >>> # test best possible path
    >>> print common_selector([[jp([0, 'name']), jp(['a'])], [jp(['b']), jp([1, 'name'])], [jp([2, 'name'])]])
    [*]['name']
    """
    abstracted_selectors = collections.defaultdict(int)
    for i, this_selectors in enumerate(selector_groups):
        for other_selectors in selector_groups[i+1:]:
            for this_selector in this_selectors:
                for other_selector in other_selectors:
                    abstract_selector = this_selector.abstract(other_selector)
                    if abstract_selector is not None:
                        abstracted_selectors[abstract_selector] += 1
                        if abstracted_selectors[abstract_selector] > len(selector_groups) / 2:
                            # found a selector that matches enough elements
                            return abstract_selector
    if abstracted_selectors:
        common.logger.info('Using best count available: {} / {}'.format(max(abstracted_selectors.values()), len(selector_groups)))
        return max(abstracted_selectors.iterkeys(), key=lambda key: abstracted_selectors[key])

        

def extract_columns(parsed_content, columns):
    """Extract columns from this content and return a list of rows
    """
    results = {}
    for field in columns.keys():
        #print 'extract', field, parsed_content
        column = columns[field](parsed_content.get())
        if column:
            results[field] = [e.strip() for e in column]
    return results

