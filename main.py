# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import argparse, sys, re, os, collections, pprint
from time import time
import threading, SimpleHTTPServer, SocketServer
import ajaxbrowser, common, model, parser, wrappertable
app = QApplication(sys.argv)



def main():
    """Process command line arguments to select the wrapper
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--port', type=int, help='the port to run local server at', default=8000)
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
            start_local_server(args.port)
            run_wrapper(wrapper)



def start_local_server(port):
    """start local HTTP server on this port to serve local example web applications
    """
    class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass # prevent error messages
    server = SocketServer.TCPServer(('', port), Handler, bind_and_activate=False)
    server.allow_reuse_address = True # allow reusing port, otherwise often get address in use error
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.serve_forever, args=())
    thread.daemon = True # daemonize thread so responds to ctrl-c
    thread.start()



def run_wrapper(wrapper):
    """execute the selected wrapper 
    """
    browser = ajaxbrowser.AjaxBrowser(app=app, gui=True, use_cache=False, load_images=False, load_java=False, load_plugins=False, delay=0)
    QApplication.setOverrideCursor(Qt.WaitCursor)
    # divide wrapper cases into training and testing
    num_cases = len(wrapper.data)
    min_cases = 2
    if num_cases < min_cases:
        raise Exception('Wrapper needs at least {} cases to abstract'.format(min_cases))
    training_cases = wrapper.data[:]
    test_cases = []

    full_execution_times = [] # time taken for each execution time when run the full wrapper during training
    expected_output = None # the output that the current execution should produce
    final_transitions = [] # transitions that contain the expected output at the end of an execution
    transition_offset = 0 # how many transitions have processed
    while browser.running:
        if training_cases:
            input_value, expected_output = training_cases.pop(0)
            start_ms = time()
            scraped_data = wrapper.run(browser, input_value)
            full_execution_times.append(time() - start_ms)
            if scraped_data is not None:
                # set dynamic expected output
                expected_output = scraped_data
            test_cases.append((input_value, expected_output))

            browser.wait_quiet()
            while transition_offset < len(browser.transitions):
                # have more transitions to check
                # check whether the transitions that were discovered contain the expected output
                for t in browser.transitions[transition_offset:]:
                    transition_offset += 1
                    if t.matches(expected_output):
                        # found a transition that matches the expected output so add it to model
                        final_transitions.append(t)
                        browser.add_status('Found matching reply for training data: {}'.format(summarize_list(expected_output)))
                browser.wait_quiet()
                
        else:
            # completed running the wrapper for training
            expected_output = execution = None
            QApplication.restoreOverrideCursor()
            input_values = [v for v, _ in wrapper.data]
            opt_execution_times = run_models(browser, final_transitions, input_values)
            if opt_execution_times:
                # display results of optimized execution
                num_passed = evaluate_model(browser, test_cases)
                browser.add_status('Evaluation: {}% accuracy (from {} test cases)'.format(100 * num_passed / len(test_cases), len(test_cases)))
                ave_opt = common.average(opt_execution_times)
                ave_full = common.average(full_execution_times)
                browser.add_status('Performance: {:.2f} times faster (ave {:.2f} vs {:.2f})'.format(ave_full / ave_opt, ave_opt, ave_full))
                app.exec_()
            else:
                browser.add_status('Failed to train model') 
            break
        app.processEvents() 



def summarize_list(l, max_length=5):
    """If list is longer than max_length then just display the initial and final items
    """
    if len(l) > max_length:
        return '{}, ..., {}'.format(', '.join(l[:max_length/2]), ', '.join(l[-max_length/2:]))
    else:
        return ', '.join(l)



def run_models(browser, final_transitions, input_values):
    """Recieves a list of potential models for the execution.
    Executes them in order, shortest first, until find one that successfully executes.
    Returns a list of execution times, or None if failed.
    """
    # first try matching transitions on full paths, then allow abstracting paths
    for abstract_path in (False, True):
        models = build_models(final_transitions, abstract_path, input_values)
        for final_model in sorted(models.values(), key=lambda m: len(m)):#, reverse=True): # XXX reverse sort to test geocode
            event_i = None
            execution_times = []
            start_ms = time()
            for event_i, _ in enumerate(final_model.run(browser)):
                execution_times.append(time() - start_ms)
                if event_i == 0:
                    # initialize the result table with the already known transition records
                    browser.add_records(final_model.records)
                    browser.add_status('Built model of requests:')
                    for m in browser.models:
                        browser.add_status(str(m))
                # model has generated an AJAX request
                if browser.running:
                    js = parser.parse(browser.current_text())
                    if js:
                        browser.add_records(parser.json_to_records(js))
                else:
                    break
                start_ms = time()
            if event_i is not None:
                # sucessfully executed a model so can ignore others
                return execution_times



def build_models(ts, abstract_path, input_values):
    """Organize these transitions into models with the same properties
    """
    models = {}
    for t in ts:
        key = t.key(abstract_path)
        try:
            m = models[key]
        except KeyError:
            m = models[key] = model.Model(input_values)
        m.add(t)
    return models



def evaluate_model(browser, test_cases):
    """Check how many of test cases were successfully parsed
    """
    num_passed = 0
    for _, expected_output in test_cases:
        for t in browser.transitions:
            if t.matches(expected_output):
                browser.add_status('Found test data: {}'.format(summarize_list(expected_output)))
                num_passed += 1
                break
    return num_passed


if __name__ == '__main__':
    main()
