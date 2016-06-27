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


Run
===

.. sourcecode:: bash

    python main.py


Wrappers
========

Wrappers are classes defined in *wrappers.py* and look like this:

.. sourcecode:: python

    class wrapper_name:
        def __init__(self):
            self.data = [
                (input value1, [expected output values1]),
                (input value2, [expected output values2]),
            ]
            self.website = 'http://...'
            self.category = 'autocomplete/car dealer/etc'
            self.http_method = GET/POST'
            self.response_format = 'XML/JSON/JSONP/HTML/JavaScript/etc'
            self.notes = '...'

        def run(self, browser):
            for input_value, output_values in self.data:
                browser.load(self.website)
                # interact with browser - there are some shortcuts defined in webkit.py such as click() / fill() / wait_load() / etc
                ...
                # pass output values back to parent execution                
                yield output_values


The attributes *website*, *category*, *http_method*, *response_format*, and *notes* are optional - these are just displayed in the table on the initial loading page.
The necessary part is defined in *run()*, which takes an *AjaxBrowser* instance and defines the browser interaction. The *yield* command is use to relinquish control to the parent thread so that network traffic from the execution path can be analysed.


Files
=====

\*.py - modules documented at http://ajaxbrowser.readthedocs.io/en/latest/

output/browser.log - a log generated when running the wrappers

output/cache.db - a cache of network traffic

verticals/ - training data to abstract inputs, which currently only cover locations
