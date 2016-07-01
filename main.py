# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import argparse, sys, re, os, collections, pprint
import ajaxbrowser, common, model, parser, wrappertable
app = QApplication(sys.argv)



def main():
    """Process command line arguments to select the wrapper
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--show-wrappers', action='store_true', help='display a list of available wrappers')
    ap.add_argument('-w', '--wrapper', help='the wrapper to execute')
    args = ap.parse_args()
    wrapper_names = wrappertable.get_wrappers()
    if args.show_wrappers:
        print 'Available wrappers:', wrapper_names
    else:
        if args.wrapper is None:
            # let user choose wrapper to execute 
            wt = wrappertable.WrapperTable()
            app.exec_()
            wrapper_name = wt.wrapper_name
        elif args.wrapper in wrapper_names:
            wrapper_name = args.wrapper
        else:
            ap.error('This wrapper does not exist. Available wrappers are: {}'.format(wrapper_names))
        if wrapper_name is not None:
            wrapper = wrappertable.load_wrapper(wrapper_name)
            run_wrapper(wrapper)


def run_wrapper(wrapper):
    """execute the selected wrapper 
    """
    browser = ajaxbrowser.AjaxBrowser(app=app, gui=True, use_cache=False, load_images=False, load_java=False, load_plugins=False)
    QApplication.setOverrideCursor(Qt.WaitCursor)
    num_cases = len(wrapper.data)
    min_cases = 3
    if num_cases <= min_cases:
        raise Exception('Wrapper needs atleast 3 cases to run'.format(min_cases))
    test_cases = wrapper.data[:num_cases / 2]
    training_cases = wrapper.data[num_cases / 2:]

    models = {} 
    expected_output = None
    while browser.running:
        if training_cases:
            input_value, expected_output = training_cases.pop(0)
            wrapper.run(browser, input_value)
            browser.wait_quiet()
        else:
            # completed running the wrapper
            expected_output = execution = None
            QApplication.restoreOverrideCursor()
            executed_model = run_models(browser, models)
            num_passed = evaluate_model(browser, test_cases)
            common.logger.info('Model success: {} / {}'.format(num_passed, len(test_cases)))
            app.exec_()
            break
        app.processEvents() 

        if browser.transitions and expected_output:
            # check whether the transitions that were discovered contain the expected output
            # (reverse order so that can remove from list without skipping items when iterating)
            for t in reversed(browser.transitions):
                if t.matches(expected_output):
                    # found a transition that matches the expected output so add it to model
                    try:
                        m = models[hash(t)]
                    except KeyError:
                        input_values = [v for v, _ in wrapper.data]
                        m = models[hash(t)] = model.Model(input_values)
                    m.add(t)
                    browser.transitions.remove(t)



def run_models(browser, models):
    """Recieves a list of potential models for the execution.
    Executes them in order, shortest first, until find one that successfully executes.
    Returns this successful model or None if does not succeed.
    """
    # XXX first don't abstract paths?
    for final_model in sorted(models.values(), key=lambda m: len(m)):#, reverse=True): # XXX reverse sort to test geocode
        event_i = None
        for event_i, _ in enumerate(final_model.run(browser)):
            if event_i == 0:
                # initialize the result table with the already known transition records
                browser.table.clear()
                browser.table.add_records(final_model.records)
            # model has generated an AJAX request
            if browser.running:
                js = parser.parse(browser.current_text())
                if js:
                    browser.table.add_records(parser.json_to_records(js))
            else:
                break
        if event_i is not None:
            # sucessfully executed a model so can ignore others
            return model


def evaluate_model(browser, test_cases):
    """Check how many of test cases were successfully parsed
    """
    num_passed = 0
    for _, expected_output in test_cases:
        for t in browser.transitions:
            if t.matches(expected_output):
                print 'found:', expected_output
                num_passed += 1
                break
    return num_passed


if __name__ == '__main__':
    main()
