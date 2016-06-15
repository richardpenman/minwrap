# -*- coding: utf-8 -*-

import re, json, numbers, collections
import xml.etree.ElementTree as ET
import xmltodict
import demjson
import common


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
    return xmltodict.parse(t)


def parse_js(t):
    """Parse the key/value pairs from this JavaScript

    >>> text = r'var s0=[];var s1={};var s4=[];var s2={};var s5=[];var s3={};var s6=[];s0[0]=s1;s0[1]=s2;s0[2]=s3; s1.airportCode="MEL";s1.airportFullName="Melbourne, Australia (MEL)";s1.airportName="Tullamarine";s1.aliases=s4;s1.cityCode="MEL";s1.cityName="Melbourne";s1.countryCode="AU";s1.region="Australia"; s4[0]="Melbourne, Australia (MEL)";s4[1]="Tullamarine";s4[2]="Australia"; s2.airportCode="MLB";s2.airportFullName="Melbourne, FL (MLB)";s2.airportName="Melbourne Intl";s2.aliases=s5;s2.cityCode="MLB";s2.cityName="Melbourne";s2.countryCode="US";s2.region="FL"; s5[0]="Melbourne, FL (MLB)";s5[1]="Melbourne Intl";s5[2]="Florida"; s3.airportCode="DOM";s3.airportFullName="Marigot, Dominica (DOM)";s3.airportName="Melville Hall Arpt";s3.aliases=s6;s3.cityCode="DOM";s3.cityName="Marigot";s3.countryCode="DM";s3.region="Dominica"; s6[0]="Marigot, Dominica (DOM)";s6[1]="Melville Hall Arpt";s6[2]="Dominica"; dwr.engine._remoteHandleCallback("3","0",{citiesDWR:s0,code:"mel"});'
    >>> parse_js(text)
    [{'airportCode': 'MEL'}, {'airportFullName': 'Melbourne, Australia (MEL)'}, {'airportName': 'Tullamarine'}, {'cityCode': 'MEL'}, {'cityName': 'Melbourne'}, {'countryCode': 'AU'}, {'region': 'Australia'}, {'airportCode': 'MLB'}, {'airportFullName': 'Melbourne, FL (MLB)'}, {'airportName': 'Melbourne Intl'}, {'cityCode': 'MLB'}, {'cityName': 'Melbourne'}, {'countryCode': 'US'}, {'region': 'FL'}, {'airportCode': 'DOM'}, {'airportFullName': 'Marigot, Dominica (DOM)'}, {'airportName': 'Melville Hall Arpt'}, {'cityCode': 'DOM'}, {'cityName': 'Marigot'}, {'countryCode': 'DM'}, {'region': 'Dominica'}]
    >>> text = r'var s0={};var s1="Melbourne, Melbourne (MEL), Australia";s0["MEL"]=s1;var s2="Melilla, Melilla (MLN), Spain";s0["MLN"]=s2; DWREngine._handleResponse("null", s0);'
    >>> parse_js(text)
    [{'s1': 'Melbourne, Melbourne (MEL), Australia'}, {'s2': 'Melilla, Melilla (MLN), Spain'}]
    """
    matches = re.findall('\W(\w+)\s*=\s*"([^<>\[\]{}=|@#^\*]*?)"', t) + re.findall("\W(\w+)\s*=\s*'(.*?)'", t)
    js = [{key : value.strip()} for (key, value) in matches if value.strip()]
    return js or None


def parse(text, content_type=''):
    """Try all parsers on this input
    """
    if content_type == 'text/xml':
        return parse_xml(text)
    for fn in parse_json, parse_jsonp:
        result = fn(text)
        if result is not None:
            return result
    if 'html' not in content_type:
        return parse_js(text)


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


def json_to_records(js):
    """Extract records from this json object by finding the leaf nodes and taking the nodes with most common counts as the columns
    """
    records = []
    counter = json_counter(js)
    if counter:
        num_entries = common.most_common([len(values) for values in counter.values()])
        # get the fields with the correct number of entries
        fields = [key for key in counter.keys() if len(counter[key]) == num_entries]
        for i in range(num_entries):
            result = dict([(field, counter[field][i]) for field in fields])
            records.append(result)
    return records
