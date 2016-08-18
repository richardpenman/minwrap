# -*- coding: utf-8 -*-


import re, numbers
import common, parser
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkCookie


class Transition:
    """Wrapper around a single transition using the QNetworkReply,
    which will be deleted by Qt so a local copy of details is necessary
    
    Fields (subset)
    ----------
    url: URL used in the HTTP request (string)
    host: host of the URL (string)
    path: Path of the URL (string)
    qs: parameters of the URL (dictionary)
    data: parameters of the POST request (dictionary)
    content: the content of the HTTP response (string)
    js: parsed content of the HTTP response (dictionary)
    values: list of values from js (values of the dictionary)
    cookies: Cookies from the HTTP-response
    content_type: content type of the HTTP response
    headers: headers of the HTTP request ( list of pairs (key, value) )
    verb: Type of the HTTP-response (HEAD, GET, PUT, POST, DELETE, or CUSTOM)
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
        except ValueError as e:
            print 'Error parsing URL with lxml: {}'.format(self.url.toString())
            self.parsed_content = None
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
        self.request_headers = [(header, request.rawHeader(header)) for header in request.rawHeaderList()]
        self.response_headers = [(header, request.rawHeader(header)) for header in reply.rawHeaderList()]
        #for key, value in self.response_headers:
        #    if key == 'activity-id':
        #        print key, value, str(self.url.toString())


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
        # find the keys used in this list of key,value pairs
        # recursively calls itself in the case of dictionaries
        get_keys = lambda es: tuple((k, get_keys(sorted(v.items())) if isinstance(v, dict) else None) for (k,v) in es)
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
