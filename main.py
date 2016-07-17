# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest, QNetworkCookieJar
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import argparse, sys, re, os, collections, pprint
from time import time
import threading, SimpleHTTPServer, SocketServer
import ajaxbrowser, common, model, parser, wrappertable



def main():
    """Process command line arguments to select the wrapper
    """
    app = QApplication(sys.argv)
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--all-wrappers', action='store_true', help='execute all wrappers sequentially')
    ap.add_argument('-p', '--port', type=int, help='the port to run local HTTP server at', default=8000)
    ap.add_argument('-s', '--show-wrappers', action='store_true', help='display a list of available wrappers')
    ap.add_argument('-w', '--wrapper', help='the wrapper to execute')
    args = ap.parse_args()
    wrapper_names = wrappertable.get_wrappers()
    if args.show_wrappers:
        print 'Available wrappers:', wrapper_names
    else:
        if args.all_wrappers:
            # select all wrappers
            selected_wrapper_names = wrapper_names
        elif args.wrapper is None:
            # let user choose wrapper to execute 
            wt = wrappertable.WrapperTable()
            app.exec_()
            if not wt.wrapper_name:
                return
            selected_wrapper_names = [wt.wrapper_name]
        elif args.wrapper in wrapper_names:
            # select just this wrapper
            selected_wrapper_names = [args.wrapper]
        else:
            ap.error('This wrapper does not exist. Available wrappers are: {}'.format(wrapper_names))
            return

        start_local_server(args.port)
        # execute selected wrappers
        load_media = True
        for wrapper_name in selected_wrapper_names:
            browser = ajaxbrowser.AjaxBrowser(app=app, gui=True, use_cache=False, load_images=load_media, load_java=load_media, load_plugins=load_media, delay=0)
            wrapper = wrappertable.load_wrapper(wrapper_name)
            try:
                if args.all_wrappers and not wrapper.enabled:
                    #browser.stats.writer.writerow(['Broken', wrapper.website])
                    continue
            except AttributeError:
                pass
            test_cases, final_transitions = run_wrapper(browser, wrapper)
            # completed running the wrapper for training
            model = examine_transitions(browser, wrapper, final_transitions)
            if model is not None:
                # display results of optimized execution
                num_passed = evaluate_model(browser, wrapper, model, test_cases)
                browser.add_status('Evaluation: {}% accuracy (from {} test cases)'.format(100 * num_passed / len(test_cases), len(test_cases)))
            else:
                browser.add_status('Failed to train model') 
        common.logger.info('Done')
        app.exec_() # wait until window closed
    


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



def run_wrapper(browser, wrapper):
    """execute the selected wrapper 
    """
    # create a browser instance
    QApplication.setOverrideCursor(Qt.WaitCursor)
    training_cases = wrapper.data[:]
    num_cases = len(training_cases)
    min_cases = 2
    if num_cases < min_cases:
        raise Exception('Wrapper needs at least {} cases to abstract'.format(min_cases))
    test_cases = []

    expected_output = None # the output that the current execution should produce
    final_transitions = [] # transitions that contain the expected output at the end of an execution
    transition_offset = 0 # how many transitions have processed
    while browser.running and training_cases:
        # clear browser cookies
        browser.view.page().networkAccessManager().setCookieJar(QNetworkCookieJar())
        browser.stats.start(wrapper.website, 'Training')
        input_value, expected_output = training_cases.pop(0)
        scraped_data = wrapper.run(browser, input_value)
        browser.wait_quiet()
        browser.stats.stop()
        if scraped_data is not None:
            # set dynamic expected output
            expected_output = scraped_data
        # save the expected output for checking test cases later
        test_cases.append((input_value, expected_output))

        while transition_offset < len(browser.transitions):
            # have more transitions to check
            # check whether the transitions that were discovered contain the expected output
            for t in browser.transitions[transition_offset:]:
                transition_offset += 1
                if model.content_matches(t.url.toString(), t.content, expected_output):
                    t.output = expected_output
                    # found a transition that matches the expected output so add it to model
                    final_transitions.append(t)
                    browser.add_status('Found matching reply for training data: {}'.format(summarize_list(expected_output)))
            browser.wait_quiet()
    QApplication.restoreOverrideCursor()
    return test_cases, final_transitions



def examine_transitions(browser, wrapper, final_transitions):
    """Recieves a list of transitions containing the expected output data.
    """
    input_values = [v for v, _ in wrapper.data]
    # first try matching transitions on full paths, then allow abstracting paths
    for abstract_path in (False, True):
        for transition_group in group_transitions(final_transitions, abstract_path):
            wrapper_model = model.build(browser, transition_group, input_values)
            if wrapper_model is not None:
                common.logger.info('Built model of requests:\n{}'.format(str(wrapper_model)))
                # initialize the result table with the already known transition records
                for t in transition_group:
                    if t.js:
                        browser.add_records(parser.json_to_records(t.js))
                return wrapper_model



def summarize_list(l, max_length=5):
    """If list is longer than max_length then just display the initial and final items
    """
    if len(l) > max_length:
        return '{}, ..., {}'.format(', '.join(l[:max_length/2]), ', '.join(l[-max_length/2:]))
    else:
        return ', '.join(l)



def group_transitions(transitions, abstract_path):
    """Organize these transitions into groups with the same properties
    Returns a list of these groups, sorted by the number of unique URLs in each group
    """
    groups = collections.defaultdict(list)
    for t in transitions:
        key = t.key(abstract_path)
        groups[key].append(t)
    return sorted(groups.values(), key=lambda ts: len(set([t.url.toString() for t in ts])))



def evaluate_model(browser, wrapper, wrapper_model, test_cases):
    """Run the model and check how many of test cases were successfully parsed
    """
    num_passed = 0
    for input_value, expected_output in test_cases:
        if not browser.running:
            break
        browser.stats.start(wrapper.website, 'Testing')
        wrapper_model.execute(browser, input_value)
        browser.stats.stop()
        content = browser.current_text()
        if model.content_matches(browser.current_url(), content, expected_output):
            browser.add_status('Found test data: {}'.format(summarize_list(expected_output)))
            num_passed += 1
        js = parser.parse(content)
        if js:
            browser.add_records(parser.json_to_records(js))
    return num_passed



if __name__ == '__main__':
    main()
