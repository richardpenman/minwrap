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
        #self.values = [value for value in json_values(js) or [] if value] # XXX need to convert unicode?
        request = reply.orig_request
        self.headers = [(header, request.rawHeader(header)) for header in request.rawHeaderList()]


    def __str__(self):
        return '{} {}'.format(self.url.toString(), self.data)


    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


    def __hash__(self):
        """A unique key to represent this transition
        """
        get_keys = lambda es: tuple(k for (k,v) in es)
        return hash((self.host, self.path, get_keys(self.qs), get_keys(self.data)))


    def matches(self, expected_output, content=None):
        """Return whether the expected output is found in this transition
        """
        num_found = 0
        for e in expected_output:
            if e in (content or self.content):
                # found a value we are after in this response
                num_found += 1
        # XXX adjust this threshold for each website?
        if num_found > len(expected_output) / 4:
            common.logger.info('Transition matches expected output: {} {} {} / {}'.format(self.url.toString(), self.data, num_found, len(expected_output)))
            self.output = expected_output
            return True
        else:
            common.logger.debug('Transition does not match expected output: {} {} {} / {}'.format(self.url.toString(), self.data, num_found, len(expected_output)))
            return False


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
