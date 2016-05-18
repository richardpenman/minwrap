# -*- coding: utf-8 -*-

import re, json, numbers, collections
import xml.etree.ElementTree as ET
import demjson


def parse_json(s):
    """Parse this string into a dict if json else return None

    >>> parse_json('')
    >>> parse_json('{"a":3}')
    {u'a': 3}
    >>> parse_json('{a:3}')
    {u'a': 3}
    """
    try:
        return json.loads(s)
    except ValueError:
        # try a more relaxed parser for JavaScript
        try:
            return demjson.decode(s)
        except demjson.JSONDecodeError:
            pass
       

def parse_jsonp(t):
    """Parse this string into a dict if jsonp else return None
    
    >>> parse_jsonp('callback({"a":3}) ')
    {u'a': 3}
    """
    match = re.compile('\s*\w*\(({.*?})\)\s*$', flags=re.DOTALL).match(t)
    if match:
        # try parsing the internal json
        return parse_json(match.groups()[0])


def parse_xml(t):
    """Parse this XML into a dict
    """
    pass
    """try:
        # check if is XML
        reply.parsed_response = ET.fromstring(response)
    except ET.ParseError:
        # XXX add support for JavaScript
        return
    """


def parse_js(t):
    words = [word.strip() for word in re.findall('[=:]\s*"([^<>\[\]{}=|@#^\*]*?)"', t) if word.strip()]
    print 'JS:', words
    return words or None


def parse(text, content_type=''):
    """Try all parsers on this input
    """
    for fn in parse_json, parse_jsonp, parse_xml:
        result = fn(text)
        if result is not None:
            return result
    # still have not parsed
    #if 'javascript' in content_type or 'plain' in content_type:
        # try extract strings
    #    return parse_js(text)


# text parsers to test
text_parsers = [
    lambda s: s, # original string
    lambda s: s.replace(' ', '+'), # plus encoding
    lambda s: s.replace(' ', '%20'), # space encoding
    lambda s: urllib.quote(s), # percent encoding
]


def json_values(es):
    """Parse values from this json dict

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


def json_counter(es, result=None):
    """Parse number of times each key-value pair occurs in json

    >>> result = json_counter([{'name': 'bob', 'age': 29}, {'name': 'sara', 'age': 17}, 'hello', 6])
    >>> print sorted(result.items())
    [('age', [29, 17]), ('name', ['bob', 'sara'])]
    """
    if result is None:
        result = collections.defaultdict(list)
    if isinstance(es, dict):
        for k, v in es.items():
            if v is None or isinstance(v, (numbers.Number, basestring)):
                result[k].append(v)
            else:
                json_counter(v, result)
    elif isinstance(es, list):
        for e in es:
            json_counter(e, result)
    elif es is None or isinstance(es, (numbers.Number, basestring)):
        pass # no data about parent
    return result


def main():
    D = download.Download(proxy_file='proxies.txt', num_retries=1, delay=0)
    #writer = common.UnicodeWriter('.csv')
    #writer.writerow(HEADER)


if __name__ == '__main__':
    main()

