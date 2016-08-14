Dependencies
============

Install modules for parsing JSON and HTML:

.. sourcecode:: bash

    pip install demjson templater xmltodict lxml


Install Qt and Python bindings for Webkit

Linux:

.. sourcecode:: bash

    apt-get install python-qt4

OSX:

.. sourcecode:: bash

    brew install qt pyqt sip



Module documentation
====================

The module documentation relies on Sphinx:

.. sourcecode:: bash

    pip install Sphinx

It can be generated locally by running this command:

.. sourcecode:: bash

    cd docs && make html


Wrappers
========

Wrappers are classes defined in the *wrappers* directory and are structured like this:

.. sourcecode:: python

    class Wrapper:
        def __init__(self):
            self.data = [
                ({param1: input1, param2: input2, ...}, {field1: values, field2: values}),
                ({'city': 'London', 'date': '1/1/2016'}, {'price': [100, 101, 150, 94], 'locations': ['Paris', 'Berlin', 'Moscrow']},
                ...
            ]
            self.website = 'http://...'
            self.category = 'autocomplete/car dealer/etc'
            self.http_method = GET/POST'
            self.response_format = 'XML/JSON/JSONP/HTML/JavaScript/etc'
            self.notes = '...'

        def run(self, browser, inputs):
            browser.load(self.website)
            # interact with browser to perform execution for this input value


A wrapper defines a class called Wrapper with several required attributes:

- data: a list of tuples defining the input parameters and expected output strings. A minimum of 2 cases are needed, though the more the better.
- run(): this method performs the browser execution for the given input value. It can optionally return the expected output values if this is not known until run time.
- website: the website this wrapper is for

There are also several optional attributes that are used for displaying a summary in the start window:

- category: the category of website (autocomplete, car dealers, etc)
- http_method: the HTTP method used for downloading the key data (GET/POST)
- response_format: the content type of the key data (JSON/JSONP/XML/HTML/etc)
- notes: any further notes about this website
- enabled: True/False flag for whether this wrapper is visible 


Here is an implementation for Fiat from *wrappers/fiat.py*:

.. sourcecode:: python

    class Wrapper:
        def __init__(self):
            self.data = [
                ({'postcode': 'OX1'}, None),
                ({'postcode': 'CB2'}, None),
                ({'postcode': 'E1'}, None),
                ({'postcode': 'BA1'}, None),
            ]
            self.website = 'http://www.fiat.co.uk/find-dealer'
            self.category = 'car dealer'
            self.http_method = 'GET'
            self.response_format = 'JSONP'
            self.notes = 'Two potential AJAX requests by postcode and sales type'

        def run(self, browser, inputs):
            browser.get(self.website)
            browser.fill('div.input_text input', inputs['postcode'])
            browser.click('div.tab_dealer div.input_text button.search')
            browser.wait_load('div.result')
            return dict(
                names = browser.text('div.result div.fn.org'),
                addresses = browser.text('div.result span.street-address'),
                cities = browser.text('div.result span.locality'),
                postcodes = browser.text('div.result span.postal-code'),
            )

Further examples can be found in the wrappers directory.


WebKit
======

The Browser class is a wrapper around WebKit's *QWebView* class for rendering web pages, which is documented at http://doc.qt.io/qt-4.8/qwebview.html. Some shortcut methods have been defined in webkit.Browser:

- **attr(pattern, name)**: Gets the given attribute for the matching elements.
- **attr(pattern, name, value)**: Set attribute of matching CSS pattern to value. Returns number of elements set.
- **click(pattern, native=False)**: Click all elements that match the CSS pattern. If native then will try GUI level click. Returns number of elements clicked.
- **fill(pattern, value)**: Set text of the form elements that match this CSS pattern to value. Returns number of elements set.
- **find(pattern)**: Returns the elements matching this CSS pattern.
- **get(url)**: Load the given URL and waits until loadFinished event called, then returns the loaded content.
- **js(script)**: Execute this JavaScript script on the currently loaded webpage.
- **keys(pattern, text, native=False)**: Simulate typing by focusing on elements that match the CSS pattern and triggering key events. If native then will try GUI level typing. Returns number of elements set.
- **text(pattern)**: Returns the text of the elements matching this CSS pattern.
- **wait(delay)**: Wait for the specified delay (in seconds).
- **wait_load(pattern, timeout=60)**: Wait for this content to be loaded up to maximum timeout, by default 60 seconds. Returns True if pattern was loaded before the timeout.
- **wait_quiet(timeout=20)**: Wait for all outstanding requests to complete up to the given timeout, by default 20 seconds. Returns whether outstanding requests completed in this time.
- **wait_steady(timeout=60)**: Wait for the DOM to be steady, defined as no changes over a 1 second period. Returns True if DOM is steady before the given timeout.


Implementation details
======================

#. The training cases for a wrapper are executed.
#. Network traffic is monitored and the required features (URL, content, headers, etc) from each generated request/response are stored in a Transition object.
#. The transitions are found that contain the expected output from each execution path.
#. These transitions are divided into groups with the same domain, path, querystring keys, and POST keys. 

   * If the subsequent steps fail to build a model then the path criteria is changed to just needing the same number of segments (parts of path separated by /). This is necessary when the input data is contained within the path like this:
   
      http://www.lexus.fr/api/dealer/nearest/2.3522219/48.856614/10/
      http://www.lexus.fr/api/dealer/nearest/4.835659/45.764043/10/

#. These transition groups are iterated until a model is successfully built.

   * Groups with a smaller number of unique URL's are checked first in case there is a single URL that contains all expected data, such as this one:
   
      http://www.lexus.fr/api/dealers/all

#. To build a model the transitions are compared for differences in path segments, querystring values, and POST values. For example given these two URL's:

    http://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&serv=sales&mkt=3112&brand=00&func=finddealerxml&address=OX1&rad=100
    http://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&serv=sales&mkt=3112&brand=00&func=finddealerxml&address=CB2&rad=100
   The only difference is with the values for *address*. 
#. A list of these differences is formed using this format:
   [(POST|GET|PATH, key|index, [example1, example2, ...]), ...]

   * For the above examples this would be: [(GET, 'address', ['OX1', 'CB2'])]
   * If the difference is a path segment then a 1-based index of the segment is used.

#. For each of the GET/POST keys in this list a modified request is made without this key. If the response still contains the expected data then this key is removed from the model.

   * This is particularly relevant for session ID's, such as this for Dacia: __fp=GUFQeOFjGNBhWWMMKKgneiF9p-reJ13npCfnQQDvQmE%3D

#. If the list of differences is empty then there is nothing to abstract. 

   * In this case the content of a transition is checked to see whether it contains all of the expected data. If so then a convenient API has been discovered that covers all cases, such as the Lexus example above. Otherwise the model generation fails for this group of transitions.

#. If there are differences then it needs to be determined where they came from. For each difference the following are checked:

   #. Whether the examples correspond to input values defined in the wrapper. In this case the model is complete and we know how to get from the input values to the expected data.
   #. Whether the examples are found in previous transitions. 
    
      * This is achieved by checking each *structured* transition (JSON/JSONP/XML) and building a path to the data of interest.
        
        * The path is a list of indices and keys to follow from the root.
        * HTML could be supported using XPath but I have not found such an example yet - typically this dynamic intermediary data would be structured.

      * If the same path can be used in different transitions to reach all the examples then we recursively build a model of these parent transitions, and continue until have reached the initial input values.

#. If these checks fail then any common prefix and suffix is removed from the examples and the above criteria are checked again. For example with Delta the parameters include a prefix:

   * c0-param0=string:washington
   * c0-param0=string:london
   * c0-param0=string:paris
   
#. If these checks still fail then we do not understand how a parameter is formed in this model and so need to try the next group of transitions. This commonly happens when a parameter is constructed dynamically with JavaScript and so is not found in any response content.

#. If a model is successfully built then it is executed over the input values from the wrapper.

   * Here is the model for Fiat that has a GET key from the address parameter and scrapes 4 columns:

   .. sourcecode::

        {
            "columns": {
                "addresses": "[u'results'][*][u'ADDRESS']",
                "cities": "[u'results'][*][u'TOWN']",
                "names": "[u'results'][*][u'COMPANYNAM']",
                "postcodes": "[u'results'][*][u'ZIPCODE']"
            },
            "headers": [
                [
                    "User-Agent",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                ],
                [
                    "Accept",
                    "*/*"
                ],
                [
                    "Referer",
                    "http://www.fiat.co.uk/find-dealer"
                ]
            ],
            "url": "http://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&serv=sales&mkt=3112&brand=00&func=finddealerxml&address={}&rad=100",
            "variables": [
                {
                    "key": "address",
                    "origin": "GET",
                    "source": "postcode",
                    "template": "{}"
                }
            ],
            "verb": "GET"
        }


   * And this model for the local country website is an example with multiple steps, where the second step uses the country input in the path:

   .. sourcecode::

        {
            "columns": {
                "countries": "[u'cities'][*]"
            },
            "headers": [
                [
                    "X-Requested-With",
                    "XMLHttpRequest"
                ],
                [
                    "User-Agent",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                ],
                [
                    "Accept",
                    "application/json, text/javascript, */*; q=0.01"
                ],
                [
                    "Referer",
                    "http://localhost:8000/examples/country/"
                ]
            ],
            "url": "http://localhost:8000/examples/country/api/cities/{}",
            "variables": [
                {
                    "key": 5,
                    "origin": "Path",
                    "source": {
                        "headers": [
                            [
                                "X-Requested-With",
                                "XMLHttpRequest"
                            ],
                            [
                                "User-Agent",
                                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                            ],
                            [
                                "Accept",
                                "application/json, text/javascript, */*; q=0.01"
                            ],
                            [
                                "Referer",
                                "http://localhost:8000/examples/country/"
                            ]
                        ],
                        "selector": "[u'id']",
                        "url": "http://localhost:8000/examples/country/api/countries/{}",
                        "variables": [
                            {
                                "key": 5,
                                "origin": "Path",
                                "source": "country",
                                "template": "{}.json"
                            }
                        ],
                        "verb": "GET"
                    },
                    "template": "{}.json"
                }
            ],
            "verb": "GET"
        }
        

#. To evaluate correctness the model is executed over the test data and checked how many execution paths contain the same expected output as defined in the wrapper.
#. Measurements of performance (time, bandwidth) of the initial wrapper and the optimized wrapper are saved in output/stats.csv.


Command line interface
======================

.. sourcecode:: bash
    
    $ python main.py -h
    usage: main.py [-h] [-a] [-p PORT] [-s] [-w WRAPPER]

    optional arguments:
      -h, --help            show this help message and exit
      -a, --all-wrappers    execute all wrappers sequentially
      -p PORT, --port PORT  the port to run local HTTP server at
      -s, --show-wrappers   display a list of available wrappers
      -w WRAPPER, --wrapper WRAPPER
                            the wrapper to execute

A wrapper to execute can be passed from the command line. If no wrapper is passed then a window with details of each defined wrapper will be displayed and the *Go* button can be clicked to execute one of them.



Directories
===========

output/ - files generated during operation such as the log and cache

examples/ - static websites that wrappers can execute reliably locally

verticals/ - training data to abstract inputs, which currently only cover locations

wrappers/ - definitions of how to interact with each website are defined here


Model Visualisation
===================

``output/model.gv`` contains a GraphViz graph showing how the resuired transitions and parameters in the final optimised model.

It can be viewed interactively with ``xdot output/model.gv`` or as an image with ``dot -Tpng -O output/model.gv``.


