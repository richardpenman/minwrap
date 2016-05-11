# -*- coding: utf-8 -*-

import re, json
import xml.etree.ElementTree as ET
import demjson


def parse_json(s):
    """Parse this string into a dict if json else return None

    >>> parse_json('')
    None
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


def parse(t):
    """Try all parsers on this input
    """
    for fn in parse_json, parse_jsonp, parse_xml:
        result = fn(t)
        if result is not None:
            return result



def main():
    D = download.Download(proxy_file='proxies.txt', num_retries=1, delay=0)
    #writer = common.UnicodeWriter('.csv')
    #writer.writerow(HEADER)


if __name__ == '__main__':
    main()

