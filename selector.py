# -*- coding: utf-8 -*-

import sys, itertools
import common
import lxml.html



class NotFoundError(Exception):
    pass



class HashBase:
    """Define a base class that supports hash comparisons
    """
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(str(self))



class CookieName(HashBase):
    """Wrapper around cookie key
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'cookie:{}'.format(self.name)

    def __call__(self, cookies):
        for cookie in cookies:
            if cookie.name() == self.name:
                return cookie.value()
        raise NotFoundError()

    def get(self, browser):
        cj = browser.page().networkAccessManager().cookieJar()
        cookies = cj.cookiesForUrl(browser.url())
        return self(cookies)



class Selector(HashBase):
    pass



class XPathSelector(Selector):
    """Wrapper around an XPath selector

    >>> p1 = XPathSelector('/html/body/div[@class="first"]/span[2]/span[2]')
    >>> p2 = XPathSelector('/html/body/div[@class="second"]/span[3]/span[2]')
    >>> len(p1)
    6
    >>> p1.distance(p1)
    0
    >>> p1.distance(p2) == p2.distance(p1) == 2
    True
    >>> print p1.abstract(p2, 2)
    /html/body/div/span/span[2]
    """
    def __init__(self, path):
        self.path = path

    def __call__(self, doc):
        """Apply XPath to this document and return list of matching strings
        """
        return [self.tostring(e) for e in doc.xpath(self.path)]

    def __str__(self):
        return self.path

    def __len__(self):
        """Define length of an XPath as the number of components
        """
        return len(list(self.__iter__()))

    def __iter__(self):
        return iter(self.path.split('/'))

    def tostring(self, node):
        """Return the string of this node
        """
        try:
            return ''.join(filter(None,
                [node.text] + [lxml.html.tostring(e) for e in node]
            ))
        except AttributeError:
            return node

    def distance(self, other):
        count = 0
        for e1, e2 in itertools.izip_longest(self, other):
            if e1 != e2:
                count += 1
        return count
           
    def abstract(self, other, max_distance=1):
        """Generate abstracted XPath that satisfies both XPaths
        """
        if len(self) == len(other) and self.distance(other) <= max_distance:
            components = []
            for e1, e2 in zip(self, other):
                if e1 == e2:
                    components.append(e1)
                else:
                    tag = lambda e: e.split('[')[0]
                    tag1, tag2 = tag(e1), tag(e2)
                    if tag1 == tag2:
                        components.append(tag1)
                    else:
                        components.append(self.WILDCARD)
            return XPathSelector('/'.join(components))



class JsonPathSelector(Selector):
    """Wrapper around a JsonPath selector.
    JsonPath iterates through a dictionary given a list of indices / keys.

    >>> jp = JsonPathSelector([0, 'person'])
    >>> str(jp)
    "[0]['person']"
    >>> jp([{'person': 'richard'}, {'person': 'tim'}])
    'richard'
    >>> jp([])
    Traceback (most recent call last):
     ...
    NotFoundError
    >>> jp = JsonPathSelector(['universities', 0, 'name'])
    >>> str(jp)
    "['universities'][0]['name']"
    >>> jp({'universities': [{'name': 'Oxford', 'year': 1096}, {'name': 'Cambridge', 'year': 1209}]})
    'Oxford'
    """
    WILDCARD = '*' # match all elements

    def __init__(self, steps):
        self.steps = tuple(steps)

    def __len__(self):
        return len(self.steps)

    def __str__(self):
        return ''.join('[{}]'.format(step if step == self.WILDCARD else repr(step)) for step in self.steps)


    def __call__(self, js, steps=None):
        """Return the content at this step
        """
        steps = list(self.steps) if steps is None else steps
        if steps:
            step, steps = steps[0], steps[1:]
            try:
                if step == self.WILDCARD:
                    if isinstance(js, dict):
                        return [self(e, steps) for e in js.values()]
                    elif isinstance(js, (tuple, list)):
                        return [self(e, steps) for e in js]
                    else:
                        raise Exception('Unexpected type for wildcard: {}'.format(type(js)))
                else:
                    js = js[step]
            except (KeyError, IndexError):
                raise NotFoundError()
            else:
                return self(js, steps)
        else:
            return js

  
    def distance(self, other):
        """Returns number of different components between these JsonPaths.

        >>> p1 = JsonPathSelector([0, 'a'])
        >>> p2 = JsonPathSelector([0, 'a', 'b'])
        >>> p3 = JsonPathSelector([0, 'b'])
        >>> p1.distance(p1)
        0
        >>> p1.distance(p2) == p2.distance(p1) == 1
        True
        >>> p1.distance(p3)
        1
        """
        count = 0
        for this_step, other_step in itertools.izip_longest(self.steps, other.steps):
            if this_step != other_step and self.WILDCARD not in (this_step, other_step):
                count += 1
        return count
    

    def abstract(self, other, max_difference=1):
        """Return JsonPath that matches this JsonPath and other
        
        >>> p1 = JsonPathSelector([0, 'a'])
        >>> p2 = JsonPathSelector([0, 'b'])
        >>> p3 = JsonPathSelector([1, 'a'])
        >>> print p1.abstract(p1)
        [0]['a']
        >>> print p1.abstract(p2)
        [0][*]
        >>> print p1.abstract(p3)
        [*]['a']
        """
        if len(self) == len(other) and self.distance(other) <= max_difference:
            steps = []
            for this_step, other_step in zip(self.steps, other.steps):
                if this_step == other_step:
                    steps.append(this_step)
                else:
                    steps.append(self.WILDCARD)
            return JsonPathSelector(steps)
