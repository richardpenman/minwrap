# -*- coding: utf-8 -*-


import re, numbers
import common, parser
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkCookie


class Transition:
    """Wrapper around a single transition using the QNetworkReply,
    which will be deleted by Qt so a local copy of details is necessary
    """
    def __init__(self, reply):
        # save shortcuts to URL details
        self.url = reply.url()
        self.host = self.url.host()
        self.path = self.url.path()
        self.qs = self.url.queryItems()
        self.data = reply.data
        self.content_type = reply.content_type
        self.content = common.to_unicode(str(reply.content))
        try:
            self.parsed_content = parser.parse(self.content, self.content_type)
        except Exception as e:
            print 'Error parsing URL with lxml: {}'.format(self.url.toString())
            raise e
        self.columns = None
        self.cookies = QNetworkCookie.parseCookies(reply.rawHeader('Set-Cookie'))
        # map of Qt verbs
        verbs = {
            QNetworkAccessManager.HeadOperation: 'HEAD',
            QNetworkAccessManager.GetOperation: 'GET',
            QNetworkAccessManager.PutOperation: 'PUT',
            QNetworkAccessManager.PostOperation: 'POST',
            QNetworkAccessManager.DeleteOperation: 'DELETE',
            QNetworkAccessManager.CustomOperation: 'CUSTOM',
        }
        self.verb = verbs[reply.operation()]
        # save request details
        request = reply.orig_request
        self.headers = [(header, request.rawHeader(header)) for header in request.rawHeaderList()]


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
