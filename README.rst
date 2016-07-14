Dependencies
============

Install modules for parsing JSON and HTML:

.. sourcecode:: bash

    pip install demjson templater xmltodict


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
                (input value1, [expected output values1]),
                (input value2, [expected output values2]),
                (input value3, [expected output values3]),
                (input value4, [expected output values4]),
            ]
            self.website = 'http://...'
            self.category = 'autocomplete/car dealer/etc'
            self.http_method = GET/POST'
            self.response_format = 'XML/JSON/JSONP/HTML/JavaScript/etc'
            self.notes = '...'

        def run(self, browser, input_value):
            browser.load(self.website)
            # interact with browser to perform execution for this input value


A wrapper defines a class called Wrapper with several required attributes:

- data: a list of tuples defining the input and expected output strings ('London': ['...', '...']). A minimum of 2 cases are needed, though the more the better.
- run(): this method performs the browser execution for the given input value. It can optionally return the expected output values if this is not known until run time.
- website: the website this wrapper is for

There are also several optional attributes that are used for displaying a summary in the start window:

- category: the category of website (autocomplete, car dealers, etc)
- http_method: the HTTP method used for downloading the key data (GET/POST)
- response_format: the content type of the key data (JSON/JSONP/XML/HTML/etc)
- notes: any further notes about this website
- enabled: True/False flag for whether this wrapper is visible 


Here is an implementation for Lufthunsa from *wrappers/lufthunsa.py*:

.. sourcecode:: python

    class Wrapper:
        def __init__(self):
            self.data = [
                ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
                ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
                ('bri', ['Brindisi', 'Brisbane', 'bds', 'bne', 'Brisbane area airports', 'Gold Coast, Queensland', 'Bristol', 'brs', 'Bristol - Tennessee', 'tri', 'Britton', 'Britton area airports']),
                ('new', ['New Bern','ewn','New Orleans','msy','New York, all airports',"nyc","New York area airports","New York - JFK International, NY","jfk","New York - La Guardia","lga","New York - Newark International, NJ","ewr","Allentown/Bethl","abe"]),
            ]
            self.website = 'http://www.lufthansa.com/uk/en/Homepage'
            self.category = 'autocomplete'
            self.http_method = 'POST'
            self.response_format = 'JSON'
            self.notes = 'AJAX callback triggered on KeyUp event'

        def run(self, browser, input_value):
            browser.load(self.website)
            browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
            browser.wait_load('div.rw-popup')


And here is an implementation for Lexus from *wrappers/lexus.py*:

.. sourcecode:: python

    class Wrapper:
        def __init__(self):
            self.data = [
                ('paris', ['58, Boulevard Saint Marcel', '75005', '01 55 43 55 00', '3, rue des Ardennes', '75019', '01 40 03 16 00', '4, avenue de la Grande Armée', '75017', '01 40 55 40 00']),
                ('toulouse', ['123, Rue Nicolas', 'Vauquelin', '31100', '05 61 61 84 29', '4 rue Pierre-Gilles de Gennes', '64140', '05 59 72 29 00']),
                ('marseille', ['36 Boulevard Jean Moulin', '13005', '04 91 229 229', 'ZAC Aix La Pioline', 'Les Milles', '13290', '04 42 95 28 78', 'Rue Charles Valente', 'ZAC de la Castelette', 'Montfavet', '84143', '04 90 87 47 00']),
                ('nice', ['1 AVENUE EUGÈNE DONADEÏ', 'SAINT LAURENT DU VAR', '04 83 32 22 11', '(RÉPARATEUR AGRÉÉ LEXUS) Lexus Monaco', '31-39 avenue Hector Otto', 'Monaco', '98000', '00 377 93 30 10 05']),
            ]
            self.website = 'http://www.lexus.fr/forms/find-a-retailer'
            self.category = 'car dealer'
            self.http_method = 'GET'
            self.response_format = 'JSON'
            self.notes = 'Uses variables in the URL path and requires a geocoding intermediary step'

        def run(self, browser, input_value):
            browser.load(self.website)
            browser.click('span[class="icon icon--base icon-close"]') # accept cookies
            browser.wait_load('div.form-control__item__postcode')
            browser.fill('div.form-control__item__postcode input', input_value)
            browser.click('div.form-control__item__postcode button')


WebKit
======

The Browser class is a wrapper around WebKit's *QWebView* class for rendering web pages, which is documented at http://doc.qt.io/qt-4.8/qwebview.html. Some shortcut methods have been defined in webkit.Browser:

- **get(url)**: Load the given URL and waits until loadFinished event called, then returns the loaded content.
- **js(script)**: Execute this JavaScript script on the currently loaded webpage.
- **click(pattern)**: Click all elements that match the CSS pattern. Returns number of elements clicked.
- **keys(pattern, text)**: Simulate typing by focusing on elements that match the CSS pattern and triggering key events. Returns number of elements set.
- **attr(pattern, name, value)**: Set attribute of matching CSS pattern to value. Returns number of elements set.
- **fill(pattern, value)**: Set text of the form elements that match this CSS pattern to value. Returns number of elements set.
- **find(pattern)**: Returns the elements matching this CSS pattern.
- **wait_load(pattern, timeout=60)**: Wait for this content to be loaded up to maximum timeout, by default 60 seconds. Returns True if pattern was loaded before the timeout.
- **wait_quiet(timeout=20)**: Wait for all outstanding requests to complete up to the given timeout, by default 20 seconds. Returns whether outstanding requests completed in this time.
- **wait_steady(timeout=60)**: Wait for the DOM to be steady, defined as no changes over a 1 second period. Returns True if DOM is steady before the given timeout.
- **wait(delay)**: Wait for the specified delay (in seconds).


Algorithm
=========

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
   c0-param0=string:washington
   c0-param0=string:london
   c0-param0=string:paris
#. If these checks still fail then we do not understand how a parameter is formed in this model and so need to try the next group of transitions. This commonly happens when a parameter is constructed dynamically with JavaScript and so is not found in any response content.

#. If a model is successfully built then it is executed over the input values from the wrapper.

    * Here is the representation of the model for Dacia that has some POST keys that can be ignored and a location key for the input parameter:

    .. sourcecode::

        {
            "data": [
                [ "search", "" ],
                ...
                [ "location", "{}" ],
                [ "search", "" ]
            ],
            "ignored": [
                [ "POST", "_sourcePage" ],
                [ "POST", "__fp" ]
            ],
            "override": [
                [ "POST", "location", "{}", null ]
            ],
            "url": "http://dacia.at/dealerlocator/search.action"
        }

    * And this model for the local country website is an example with multiple steps:

    .. sourcecode::

        {
            "override": [
                [ "PATH", 5, "{}.json", 
                    {
                        "override": [
                            [ "PATH", 5, "{}.json", null ]
                        ],
                        "selector": "(u'id',)",
                        "url": "http://localhost:8000/examples/country/api/countries/{}"
                    }
                ]
            ],
            "url": "http://localhost:8000/examples/country/api/cities/{}"
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
