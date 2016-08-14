# -*- coding: utf-8 -*-

import re, json, numbers, collections
from difflib import SequenceMatcher
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
import lxml.html, lxml.etree
#import xmltodict
import demjson
import common, selector



class Document:
    pass


class JsonTree(Document):
    """
    >>> tree = JsonTree([{'person': 'richard', 'location': 'oxford'}, {'person': 'tim', 'location': 'oxford'}])
    >>> [str(path) for _, path in tree.find(['richard'])]
    ["[0]['person']"]
    >>> [str(path) for _, path in tree.find(['oxford'])]
    ["[0]['location']", "[1]['location']"]
    >>> [str(path) for _, path in tree.find(['cambridge'])]
    []
    """
    def __init__(self, js):
        self.js = js

    def get(self):
        return self.js

    def find(self, goals, data=None, parents=None):
        """Find all selectors to strings in the goals list
        """
        data = self.js if data is None else data
        parents = [] if parents is None else parents
        if isinstance(data, dict):
            for key, record in data.items():
                for result in self.find(goals, record, parents[:] + [key]):
                    yield result
        elif isinstance(data, (tuple, list)):
            for index, record in enumerate(data):
                for result in self.find(goals, record, parents[:] + [index]):
                    yield result
        else:
            for goal in goals:
                if similar(goal, data):
                    yield goal, selector.JsonPathSelector(parents)
                    break


class XPathTree(Document):
    """
    >>> tree = parse_html('''
    ... <html>
    ...     <body>
    ...         <div id="results">
    ...             <span class="result">
    ...                 <span>Oxford</span>
    ...                 <span>UK</span>
    ...             </span>
    ...             <span class="result">
    ...                 <span>Harvard</span>
    ...                 <span>USA</span>
    ...             </span>
    ...             <span class="result">
    ...                 <span>Sorbonne</span>
    ...                 <span>France</span>
    ...             </span>
    ...         </div>
    ...     </body>
    ... </html>''')
    >>> [str(path) for _, path in tree.find(['Oxford'])]
    ['/html/body/div/span[1]/span[1]']
    >>> [str(path) for _, path in tree.find(['USA', 'France'])]
    ['/html/body/div/span[2]/span[2]', '/html/body/div/span[3]/span[2]']
    """
    def __init__(self, tree):
        self.tree = tree
        #raise Exception(str(dir(tree)))
        self.root = tree.getroottree()

    def get(self):
        return self.tree

    def find(self, goals):
        for element in self.root.iter():
            if isinstance(element.tag, basestring): 
                # ignore comments and meta data
                if element.text:
                    path = None
                    for goal in goals:
                        if similar(goal, element.text):
                            # XXX need a better XPath generation, builtin just uses indices
                            path = path or self.root.getpath(element)
                            yield goal, selector.XPathSelector(path)
                            break




def similar(goal, data):
    """Define 2 inputs as similar if they are equal 
    or have 95% string similarity after ignoring case and surrounding whitespace
    """
    if goal == data:
        return True
    elif isinstance(goal, basestring) and isinstance(data, basestring):
        #goal = common.to_unicode(goal).strip().lower()
        #data = common.to_unicode(data).strip().lower()
        goal = goal.strip().lower()
        data = data.strip().lower()
        if goal in data:
            return True
        v = SequenceMatcher(None, goal, data).ratio()
        #if v > 0.80:
        #    print 'sm:', v, repr(goal), repr(data)
        return SequenceMatcher(None, goal, data).ratio() > 0.95
    return False



def parse(html, content_type, text=None):
    """Parse inputs based on content type
    """
    if 'html' in content_type:
        # parse HTML DOM tree
        return parse_html(html)
    elif 'xml' in content_type:
        return parse_xml(html)
    elif re.match('(application|text)/', content_type):
        # interpret json format if possible
        return parse_json(text or html)



def parse_json(s):
    """Parse this string into a dict if json or jsonp else return None

    >>> parse_json('')
    >>> parse_json('{"a":3}').get()
    {u'a': 3}
    >>> parse_json('{a:3}').get()
    {u'a': 3}
    >>> parse_json('callback({"a":3}) ').get()
    {u'a': 3}
    """
    if isinstance(s, dict):
        return s
    match = re.compile('\s*\w*\(({.*?})\)\s*$', flags=re.DOTALL).match(s)
    if match:
        # try parsing the internal json
        s = match.groups()[0]
    try:
        js = json.loads(s)
    except ValueError:
        # try a more relaxed parser for JavaScript
        try:
            js = demjson.decode(s)
        except demjson.JSONDecodeError:
            return
    return JsonTree(js)


def parse_html(s):
    try:
        tree = lxml.html.fromstring(s)
    except lxml.etree.LxmlError:
        pass
    else:
        return XPathTree(tree)



def parse_xml(s):
    """Parse this XML into a dict
    """
    try:
        tree = lxml.etree.fromstring(s)
    except lxml.etree.LxmlError:
        pass
    else:
        return XPathTree(tree)


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
