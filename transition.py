# -*- coding: utf-8 -*-


import numbers
import common


class Transition:
    """Wrapper around a single transition using the QNetworkReply,
    which will be deleted by Qt so a local copy of details is necessary
    """
    def __init__(self, reply, js):
        self.url = reply.url()
        self.host = self.url.host()
        self.path = self.url.path()
        self.qs = self.url.queryItems()
        self.data = reply.data
        self.content = common.to_unicode(str(reply.content))
        self.output = None
        self.js = js
        self.values = [value for value in json_values(js) or [] if value] # XXX need to convert unicode?
        request = reply.orig_request
        self.headers = [(header, request.rawHeader(header)) for header in request.rawHeaderList()]
        self.content_type = reply.content_type


    def __str__(self):
        return '{} {}'.format(self.url.toString(), self.data or '')


    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


    def key(self, abstract_path):
        """A key to represent this type of transition, which will be identical to other transitions with the same properties.
        If abstract_path is False then transitions must have the same URL path to match, else just the same number of components.
        """
        get_keys = lambda es: tuple(k for (k,v) in es)
        path = self.path.count('/') if abstract_path else self.path
        return hash((self.host, path, get_keys(self.qs), get_keys(self.data)))




def generate_selector(data, goal, parents=None):
    """Find the selector to the goal in this data structure

    >>> js = [{'person': 'richard', 'location': 'oxford'}, {'person': 'tim', 'location': 'oxford'}]
    >>> [jp.steps for jp in generate_selector(js, 'richard')]
    [(0, 'person')]
    >>> [jp.steps for jp in generate_selector(js, 'oxford')]
    [(0, 'location'), (1, 'location')]
    >>> [jp.steps for jp in generate_selector(js, 'cambridge')]
    []

    """
    parents = [] if parents is None else parents 
    if isinstance(data, dict):
        for key, record in data.items():
            for result in generate_selector(record, goal, parents[:] + [key]):
                yield result
    elif isinstance(data, list):
        for index, record in enumerate(data):
            for result in generate_selector(record, goal, parents[:] + [index]):
                yield result
    elif data == goal or unicode(data) == goal:
        yield JsonSelector(parents)



class JsonSelector:
    """Wrapper to iterate through a dictionary given a list of indices / keys

    >>> jp = JsonSelector([0, 'person'])
    >>> jp([{'person': 'richard'}, {'person': 'tim'}])
    'richard'
    >>> jp([])
    """
    def __init__(self, steps):
        self.steps = tuple(steps)

    def __str__(self):
        return str(self.steps)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(str(self))

    def __call__(self, js, steps=None):
        steps = list(self.steps) if steps is None else steps
        if steps:
            step = steps.pop(0)
            try:
                js = js[step]
            except (KeyError, IndexError):
                return None
            else:
                return self(js, steps)
        else:
            return js

    

def json_values(es):
    """Recursively parse values from this json dict

    >>> list(json_values({'name': 'bob', 'children': ['alice', 'sarah']}))
    ['bob', 'alice', 'sarah']
    """
    if isinstance(es, dict):
        for e in es.values():
            for result in json_values(e):
                yield result
    elif isinstance(es, list):
        for e in es:
            for result in json_values(e):
                yield result
    elif isinstance(es, basestring):
        yield es
    elif isinstance(es, numbers.Number):
        yield str(es)
    elif es is None:
        pass
    else:
        print 'unknown type:', type(es)
