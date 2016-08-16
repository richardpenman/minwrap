# -*- coding: utf-8 -*-

"""
A small synthetic test page which can be used for testing interactions with the page.
"""

import os


class Wrapper:
    def __init__(self):
        self.data = [(None, None), (None, None), (None, None)]
        self.website = "file://" + os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "examples", "local_test", "index.html"))
        self.category = ''
        self.http_method = ''
        self.response_format = ''
        self.notes = ''
        
        self.enabled = False

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.wait_quiet()
        browser.wait(1)
        
        self.test_xpath_lookups(browser)
        browser.wait(1)
        
        self.test_select_box_filling(browser)
        browser.wait(1)
        
        self.test_click_simulation(browser)
        browser.wait(5)
    
    def test_xpath_lookups(self, browser):
        browser.add_status("Getting elements by XPath")
        
        singleXPath = "//h1"
        singleElt = browser.findSingleElementByXPath(singleXPath)
        browser.add_status("    Single element: {}\n        {}".format(singleXPath, singleElt.toOuterXml()))
        
        multiXPath = "//h2"
        multiElt = browser.findByXPath(multiXPath)
        browser.add_status("    Multiple elements: {}\n        {}".format(multiXPath, "\n        ".join([x.toOuterXml() for x in multiElt])))
        
        emptyXPath = "//h3"
        emptyElt = browser.findByXPath(emptyXPath)
        browser.add_status("    No elements: {}\n        {} found".format(emptyXPath, emptyElt.count()))
    
    def test_select_box_filling(self, browser):
        browser.add_status("Filling select box")
        
        mySelect = browser.find("select#mySelect")[0]
        
        browser.add_status("    1: Via 'attr'")
        # N.B. Checking browser.attr("select#mySelect", "value") is no use, as this is the static attribute, not the changing DOM property.
        orig_value = mySelect.evaluateJavaScript("this.value").toString()
        browser.attr("select#mySelect", "value", "b")
        # For the same reason, this is not expected to work.
        new_value = mySelect.evaluateJavaScript("this.value").toString()
        browser.add_status("        {} ({} -> {})".format("OK" if new_value == "b" else "FAILED", orig_value, new_value))
        browser.wait(1)
        
        browser.add_status("    2. Via 'fill'")
        orig_value = mySelect.evaluateJavaScript("this.value").toString()
        # This is expected to work, after special handling for <select> was added to Browser.fill().
        browser.fill("select#mySelect", "c")
        new_value = mySelect.evaluateJavaScript("this.value").toString()
        browser.add_status("        {} ({} -> {})".format("OK" if new_value == "c" else "FAILED", orig_value, new_value))
        
    
    def test_click_simulation(self, browser):
        browser.add_status("Clicking button")
        
        browser.add_status("    1. Simple click")
        browser.click("button#myButton", False)
        browser.wait(1)
        
        browser.add_status("    2. JS-level simulated click")
        browser.click("button#myButton", True)
        browser.wait(1)
        
        browser.add_status("    3. GUI-level simulated click")
        browser.click_by_gui_simulation_via_selector("button#myButton")
        browser.wait(1)
        
        browser.add_status("    4. GUI-level simulated click, with scrolling")
        browser.click_by_gui_simulation_via_selector("button#myButton2")
        browser.wait(1)
        
        browser.add_status(browser.find("p#click-result")[0].evaluateJavaScript("this.textContent").toString())
        
