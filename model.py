# -*- coding: utf-8 -*-

import csv, operator, collections, urllib, itertools, os, json
import common, verticals
# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl
import parser, scrape, selector, transition

# constants for type of parameter
PATH, GET, POST, COOKIE = 0, 1, 2, 3



def build(browser, transitions, input_values, prev_transitions=None):
    """Build a model of these transitions. 
        A recursion via abstract(browser, input_values, examples).
    
    Parameters
    ----------
    browser: AjaxBrowser
    transitions: group of transaction of the same kind (same step in interactive wrapper) to be analyzed
    input_values: dictionary
            input keys and values of the interactive wrapper
        
    Returns the model or None if failed to abstract transitions.
    """
    diffs = find_differences(transitions) # differing parameters can potentially be relevant parameters dependent on the input into the original wrapper.
    if diffs:
        ignored = filter_redundant_params(browser, transitions, diffs) # list of parameters which do not change the result, i.e. final page
        override = []
        for param_type, param_key, examples in diffs:
            if any(isinstance(e, dict) for e in examples):
                common.logger.debug('No support for difference between dicts: {}'.format(examples))
                return
            elif (param_type, param_key) not in ignored:
                common.logger.info('Attempting abstraction of: {}'.format(examples))
                model = abstract(browser, input_values, examples, prev_transitions or [])
                if model is None:
                    # try partial matches
                    template, partial_examples = find_overlap(examples)
                    if partial_examples != examples and all(partial_examples):
                        common.logger.info('Attemping abstraction of partial matches: {}'.format(partial_examples))
                        model = abstract(browser, input_values, partial_examples, prev_transitions or [])
                    if model is None:
                        common.logger.info('Failed to abstract: {}'.format(examples))
                        return # abstraction failed
                else:
                    template = '{}'
                override.append((param_type, param_key, template, model))
        return Model(transitions[0], override=override, ignored=ignored)

    else:
        # check whether this request satisfied multiple expected data
        if any(transitions[0].output != t.output for t in transitions[1:]):
            common.logger.info('Single request matches multiple outputs: {}'.format(str(transitions[0])))
            return Model(transitions[0])
        else:
            common.logger.debug('Single request does not match all cases: {}'.format(str(transitions[0])))



def filter_redundant_params(browser, transitions, diffs):
    """remove redundant parameters (GET, POST) that do not change the result, such as counters.
        Assumption: "redundant" parameters are independent and can be removed in any order.
        
    Parameters
    ----------
    browser: AjaxBrowser
    transitions: list of items of the type Transition
    diffs: list of tuples (ParameterType, key, values)
    
    Returns
    -------
    ignored: list of (param_type, key)
            Parameters which can be ignored. Key is the name of the parameter.
            param_type, e.g. GET=1 or POST=2.
    
    """
    ignored = []
    for transition in transitions:
        if transition.columns and (transition.qs or transition.data):
            # found a transition that matches a known output and uses querystring or data
            # check which variable parameters can be removed while still producing the same result
            common.logger.info('Check whether any parameters in the model are redundant')
            for param_type, key, _ in diffs:
                ignore = param_type, key
                if param_type in (GET, POST) and ignore not in ignored:
                    content = browser.get(**gen_request(transition, ignored=ignored + [ignore]))
                    document = parser.parse(content, transition.content_type)
                    if document is not None:
                        try:
                            if scrape.extract_columns(document, transition.columns):
                                common.logger.info('Can ignore key: {}'.format(ignore))
                                ignored.append(ignore)
                        except selector.NotFoundError:
                            pass
            break # just need to test redundant parameters on a single transition
    return ignored



def find_differences(transitions):
    """
    For the list of transactions (HTTP requests-responses),
    in different places of the HTTP request! (e.g. URL Query string, URL Path, POST's body),
    it identifies changes in values for specific keys.
    
    Returns
    -------
    diffs: list of tuples (Location/ParameterType, key, values),
            in which 'Location' is code for PATH=0/GET=1/POST=2,
            key is the name of the parameter/key,
            values is a list of values with at least 2 differing items.
    """
    if len(transitions) > 1:
        path_diffs = find_diffs([path_to_dict(t.path).items() for t in transitions])
        get_diffs = find_diffs([t.qs for t in transitions])
        post_diffs = find_diffs([t.data for t in transitions])
        if get_diffs or post_diffs or path_diffs:
            diffs = [(PATH,) + diff for diff in path_diffs] + [(GET,) + diff for diff in get_diffs] + [(POST,) + diff for diff in post_diffs] 
            common.logger.info('Difference found: {}'.format(diffs))
            return diffs
        else:
            # found a duplicate transition
            common.logger.debug('Duplicate requests: {}'.format(transitions[-1]))
    return []



def find_overlap(examples):
    """Find the common prefix and suffix of this list of strings 
    Returns a string template with this overlap and a list of the dynamic part of these example strings

    >>> find_overlap(['hello world! END', 'hello! END', 'hello my friend! END'])
    ('hello{}! END', [' world', '', ' my friend'])
    >>> find_overlap(['string:lon', 'string:par', 'string:bri', 'string:new'])
    ('string:{}', ['lon', 'par', 'bri', 'new'])
    """
    suffix = os.path.commonprefix(examples)
    prefix = os.path.commonprefix([e[::-1] for e in examples])[::-1]
    template = suffix + '{}' + prefix
    return template, [e[len(suffix):len(e)-len(prefix)] for e in examples]
   


def path_to_dict(path):
    """
    Convert the URL path into the dictionary with the key as index (starting from 1)
    and the value as the component of the path, split by '/'
    """
    return dict(enumerate(path.split('/')))

def dict_to_path(d):
    return '/'.join(unicode(value) for _, value in sorted(d.items()))



def find_diffs(kvs):
    """Find keys with different values.
    
    Parameters
    ----------
    kvs: List of lists of (key, value) pairs.
    
    Returns
    -------
    diffs: List of (key, values) pairs, in which there for each key are at least 2 different values. 
    """
    diffs = []
    kvdicts = [dict(kv) for kv in kvs]
    for key, _ in kvs[0]:
        values = [kvdict[key] for kvdict in kvdicts if kvdict.get(key)] # XXX why was key missing for fiat?
        if not all(value == values[0] for value in values):
            # found a key with differing values
            diffs.append((key, values))
    return diffs



def gen_request(transition, override_params=None, ignored=None):
    """Generate a request modifying the transitions for this model with the provided parameters
    
    Parameters
    ----------
    transition: Transition.
            A specific transition to use rather than the first one for this model
    override_params: a list of (param_type, key, value) pairs to override the parameters for this transition
    ignored: list of (param_type, key)
        a list of (param_type, key) pairs of parameters that can be left out
    
    Returns
    -------
        dictionary with data sufficient for sending a query in the web browser
    
    """
    override_params = override_params or []
    ignored = ignored or []
    url = QUrl(transition.url)
    get_dict = dict([(key, value) for (param_type, key, value) in override_params if param_type == GET])
    post_dict = dict([(key, value) for (param_type, key, value) in override_params if param_type == POST])
    path_dict = path_to_dict(transition.path)
    for param_type, key, value in override_params:
        if param_type == PATH:
            path_dict[key] = value
    url.setPath(dict_to_path(path_dict))
    qs_items = transition.qs
    data_items = transition.data

    qs_items = [(key, urllib.quote_plus(get_dict[key].encode('utf-8')) if key in get_dict else value)
                for (key, value) in qs_items if (GET, key) not in ignored]
    url.setEncodedQueryItems(qs_items)
    data_items = [(key, post_dict[key] if key in post_dict else value)
                for (key, value) in data_items if (POST, key) not in ignored]
    return dict(url=url, headers=transition.headers, data=encode_data(data_items, transition.content_type))



def encode_data(items, content_type):
    """Convert these querystring items into a string of data
    """
    if items:
        if 'json' in content_type:
            result = json.dumps(dict(items))
        else:
            url = QUrl('')
            url.setEncodedQueryItems(items)
            result = str(url.toString())[1:]
    else:
        result = ''
    return result



def all_in(l1, l2):
    """Returns True if all values in l1 are found in l2
    """
    l2 = [v.lower() for v in l2]
    for v in l1:
        if v.lower() not in l2:
            return False
    return True



def abstract(browser, input_values, examples, prev_transitions):
    """Attempt abstacting these examples

    prev_transitions are transitions that are used earlier in this model
        External recursion with build(browser, transitions, input_values).
    
    Parameters
    ----------
    browser: AjaxBrowser
    input_values: dictionary of input parameters from the interactive wrapper
    examples: list of values of differing a parameter, which can be sensitive to the input
    
    Returns
    -------
    input_key: String
            the parameter from the input, all values of which are in the examples
            (corresponding to the specific transaction, i.e. HTTP request),
                i.e. this transaction can be the first transaction for this input_key.
    OR
    model: Model
    """
    # Find a parameter in the input which is a subset of the values in the example parameter (which is a list of values)
    print 'inputs:', input_values
    for input_key in input_values[0].keys():
        print 'input key:', input_key
        # get all values from input_values for a specific key (input_key) from the input:
        key_values = [input_value[input_key] for input_value in input_values if input_key in input_value]
        print 'key values:', key_values
        print 'examples:', examples
        # check if examples are in the input values
        if all_in(examples, key_values):
            browser.add_status('Abstraction uses input values: {}'.format(key_values))
            return input_key

        # check if examples are located at common location in a transition
        for parent_transitions, path in find_matching_transitions(browser.transitions, examples):
            if any(t in parent_transitions for t in prev_transitions):
                pass # avoid creating a loop in transitions
            else:
                model = build(browser, parent_transitions, input_values, prev_transitions + parent_transitions)
                if model is not None:
                    model.selector = path
                    return model



def find_matching_transitions(transitions, examples):
    """Find transitions that have the list of example data we are after at the same JsonPath selector
        # Find the first transition (HTTP request-response) which contains all input? in its response.

    Parameters
    ----------
    transitions: list of items of the type Transition
    examples: list of values to be found in relevant transitions
    
    Returns
    -------
        generator, a list of (parent_transitions, selector)
            It is a list with transitions which contain all values (examples) and can be identified by the selector.
    """
    selector_transitions = collections.defaultdict(list)
    for t in transitions:
        # data exists in this transition
        if t.parsed_content:
            for _, path in t.parsed_content.find(examples):
                selector_transitions[path].append(t)
        for cookie in t.cookies:
            if cookie.value() in examples:
                print 'Found cookie example: {} {}'.format(cookie.name(), cookie.value())
                selector_transitions[transition.CookieName(cookie.name())].append(t)
            
    # check if any of these matches can be modelled
    for path, parent_transitions in selector_transitions.items():
        if len(parent_transitions) == len(examples):
            # found a selector that satisfies all conditions
            #common.logger.info('Found a selector to input parameter: {}'.format(selector))
            yield parent_transitions, path



class Model:
    """It models all for the current transition.
        Dependencies are represented as a dependency graph which models the parameter tracing.
    
    Fields (subset)
    ---------- 
    transition: Transition
        HTTP request-response representing the current transition
        override: List of (param_type, param_key, template, model).
            List of direct dependencies, which provide this transition with all relevant "local" inputs.
            param_type, e.g., GET=1, POST=2.
            param_key is the name of the input parameter of the current transaction.
            template: template, used to convert the incoming parameters (the original input from the interactive wrapper or another transaction) into the input of the current transaction.
            model: Model of the corresponding transaction necessary to execute the current one or the name of the input parameter of the interactive wrapper.
        ignored: List of (param_type, param_key)
                List of ignored keys which can be omitted from the query.
        selector: expression to extract data for the parent transaction.
    """
    def __init__(self, transition, override=None, ignored=None, selector=None):
        # the example transitions that follow this template
        self.transition = transition
        # which parameters need to be overriden
        self.override = override or []
        # which parameters can be ignored
        self.ignored = ignored or []
        # the selector of content that will be extracted
        self.selector = selector
        # the columns to select
        self.columns = transition.columns


    def __str__(self):
        """Create a string representation of this model that shows which parts differ
        """
        return json.dumps(self.data(), sort_keys=True, indent=4)

    
    def __len__(self):
        def size(d):
            """Recursively calculate the number of requests required in this model
            """
            count = 1
            for variable in d.get('variables', []):
                if isinstance(variable['source'], dict):
                    count += size(variable['source'])
            return count
        return size(self.data())

    
    def data(self):
        """Return all the data for this model (including dependencies) in a structured dict
        """
        empty_template = '{}'
        param_map = {PATH: 'Path', GET: 'GET', POST: 'POST', COOKIE: 'Cookie'}
        url = QUrl(self.transition.url)
        path_dict = path_to_dict(url.path())
        get_keys, post_keys = set(), set()
        output = {}
        if self.override:
            output['variables'] = []
            for param_type, key, template, parent_model in self.override:
                parent = parent_model if isinstance(parent_model, basestring) else parent_model.data()
                output['variables'].append({
                    'key': key, 
                    'origin': param_map[param_type], 
                    'source': parent,
                    'template': template, 
                })
                if param_type == PATH:
                    path_dict[key] = empty_template
                elif param_type == GET:
                    get_keys.add(key)
                elif param_type == POST:
                    post_keys.add(key)
        url.setPath(dict_to_path(path_dict))
        qs_items = [(key, empty_template if key in get_keys else value) for (key, value) in url.queryItems() if (GET, key) not in self.ignored]
        url.setEncodedQueryItems(qs_items)
        output['url'] = url.toString()
        data = dict([(key, empty_template if key in post_keys else value) for (key, value) in self.transition.data if (POST, key) not in self.ignored])
        if data:
            output['data'] = data
        #if self.ignored:
        #    output['ignored'] = [(param_map[param_type], value) for (param_type, value) in self.ignored]
        if self.selector is not None:
            output['columns'] = {'data': str(self.selector)}
        elif self.columns is not None:
            output['columns'] = {field:str(selector) for (field, selector) in self.columns.items()}
        output['headers'] = [(str(key), str(value)) for (key, value) in self.transition.headers if str(key).lower() not in ('content-length', )]
        output['verb'] = self.transition.verb
        return output


    def execute(self, browser, input_value):
        override_params = []
        for param_type, key, template, parent_model in self.override:
            if isinstance(parent_model, basestring):
                # have reached the base case and can use input value
                value = input_value[parent_model]
            else:
                # recursively execute this dependency model
                parsed_content = parent_model.execute(browser, input_value)
                try:
                    value = parent_model.selector(parsed_content.get())
                except selector.NotFoundError:
                    common.logger.info('Failed to extract content from dependency model: {}'.format(browser.current_url()))
                    continue
            override_params.append((param_type, key, template.format(value)))
        download_params = gen_request(self.transition, override_params=override_params, ignored=self.ignored)
        current_html = browser.get(**download_params)
        return parser.parse(current_html, browser.current_content_type())
