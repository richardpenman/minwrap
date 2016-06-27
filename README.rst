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

Wrappers are classes defined in *wrappers.py* and are structured like this:

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

Here is an implementation for Lufthunsa:

.. sourcecode:: python

    class lufthansa:
        def __init__(self):
            self.data = [
                ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
                ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
            ]
            self.website = 'http://www.lufthansa.com/uk/en/Homepage'
            self.category = 'autocomplete'
            self.http_method = 'POST'
            self.response_format = 'JSON'
            self.notes = 'AJAX callback triggered on KeyUp event'

        def run(self, browser):
            for input_value, output_values in self.data:
                browser.load(self.website)
                browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
                browser.wait_load('div.rw-popup')
                yield output_values


And here is an implementation for Lexus:

.. sourcecode:: python

    class lexus:
        def __init__(self):
            self.data = [
                ('paris', ['58, Boulevard Saint Marcel', '75005', '01 55 43 55 00', '3, rue des Ardennes', '75019', '01 40 03 16 00', '4, avenue de la Grande Armée', '75017', '01 40 55 40 00']),
                ('toulouse', ['123, Rue Nicolas', 'Vauquelin', '31100', '05 61 61 84 29', '4 rue Pierre-Gilles de Gennes', '64140', '05 59 72 29 00']),
                ('marseille', ['36 Boulevard Jean Moulin', '13005', '04 91 229 229', 'ZAC Aix La Pioline', 'Les Milles', '13290', '04 42 95 28 78', 'Rue Charles Valente', 'ZAC de la Castelette', 'Montfavet', '84143', '04 90 87 47 00']),
            ]
            self.website = 'http://www.lexus.fr/forms/find-a-retailer'
            self.category = 'car dealer'
            self.http_method = 'GET'
            self.response_format = 'JSON'
            self.notes = 'Uses variables in the URL path and requires a geocoding intermediary step'

        def run(self, browser):
            for input_value, output_values in self.data:
                browser.load(self.website)
                browser.click('span[class="icon icon--base icon-close"]') # accept cookies
                browser.wait_load('div.form-control__item__postcode')
                browser.fill('div.form-control__item__postcode input', input_value)
                browser.click('div.form-control__item__postcode button')
                yield output_values


Further examples are available in *wrappers.py*.


Files
=====

\*.py - modules documented at http://ajaxbrowser.readthedocs.io/en/latest/

output/browser.log - a log generated when running the wrappers

output/cache.db - a cache of network traffic

verticals/ - training data to abstract inputs, which currently only cover locations
