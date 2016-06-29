# -*- coding: utf-8 -*-

__doc__ = """Wrappers to interact with websites and trigger AJAX events

A wrapper defines a class called Wrapper with several required attributes:
- data: a list of tuples defining the input and expected output strings ('London': ['...', '...'])
- run(): this method takes an AjaxBrowser instance and performs each execution on the browser, calling yield after each iteration to relinquish control to the parent thread so that network traffic from the execution path can be analysed.

There are also several optional attributes that are used for displaying a summary in the start window:
- website: the website this wrapper is for
- category: the category of website (autocomplete, car dealers, etc)
- http_method: the HTTP method used for downloading the key data (GET/POST)
- response_format: the content type of the key data (JSON/JSONP/XML/HTML/etc)
- notes: any further notes about this website
"""

import os, glob
# dynamically load all the modules
modules = glob.glob(os.path.dirname(__file__) + '/*.py')
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not os.path.basename(f).startswith('_')]
