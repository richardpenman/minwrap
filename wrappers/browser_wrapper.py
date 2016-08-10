# -*- coding: utf-8 -*-

import re

class BrowserWrapper:
    def __init__(self, browser):
        self.browser = browser

    def get(self, url):
        self.browser.get(url)
        self.wait_steady_go()
    
    def wait_steady_go(self, timeout=2, tries=5):
        for i in range(0, tries):
            if self.browser.wait_steady(timeout):
                return True
        raise ValueError('Cannot get DOM steady')

    def userClick(self, pattern='input'):
        result = self.browser.click(pattern, False)#True)
        self.wait_steady_go()
        return result
        
    def userKeys(self, pattern, text):
        """Simulate typing by clicking and focusing on elements that match the pattern and triggering key events.
        Returns the number of elements matched.
        It is implemented similar to click_by_user_event_simulation.
        """
        self.userClick(pattern)
        len_es = self.browser.keys(pattern, text) # TODO check if the function is correct
        self.wait_steady_go()
        return len_es
    
    def getOutput(self, extractors, transform): #selectors, regexps, groups
        rez = []
        for selector, regexp, groupNum in extractors:
            vals = [x.toPlainText() for x in self.browser.find(selector)]
            for val in vals:
                rezItem = None
                if regexp is not None:
                    r = re.compile(regexp)
                    m = r.match(val)
                    if m:
                        if groupNum and m.group(groupNum) is not None:
                            rezItem = m.group(groupNum)
                        else:
                            rezItem = m.group()
                else:
                    rezItem = val
                if transform is not None and rezItem is not None:
                    rezItem = transform(rezItem)
                if rezItem is not None:
                    rez.append(rezItem)
        return rez
    
    
