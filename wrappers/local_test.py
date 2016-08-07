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
        browser.wait(1)
        
        
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
        browser.wait(5)
        
