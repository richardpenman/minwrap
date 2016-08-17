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
import socket, threading, SimpleHTTPServer, SocketServer
import ajaxbrowser, common, model, parser, wrappertable, visualisation, scrape



def main():
    """Process command line arguments to select the wrapper
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--all-wrappers', action='store_true', help='execute all wrappers sequentially')
    ap.add_argument('-p', '--port', type=int, help='the port to run local HTTP server at', default=8000)
    ap.add_argument('-s', '--show-wrappers', action='store_true', help='display a list of available wrappers')
    ap.add_argument('-w', '--wrapper', action='append', help='the wrapper to execute')
    ap.add_argument('-c', '--cache', help='enable caching of downloads', action='store_true')
    args = ap.parse_args()
    wrapper_names = wrappertable.get_wrappers()
    start_local_server(args.port)
    if args.show_wrappers:
        print 'Available wrappers:', wrapper_names
    else:
        app = QApplication(sys.argv)
        if args.all_wrappers:
            # select all wrappers
            selected_wrapper_names = wrapper_names
        elif not args.wrapper:
            # let user choose wrapper to execute 
            wt = wrappertable.WrapperTable()
            app.exec_()
            if not wt.wrapper_name:
                return
            selected_wrapper_names = [wt.wrapper_name]
        else:
            # use selected wrappers
            for wrapper_name in args.wrapper:
                if wrapper_name not in wrapper_names:
                    ap.error('This wrapper "{}" does not exist. Available wrappers are: {}'.format(wrapper_name, wrapper_names))
                    return
            selected_wrapper_names = args.wrapper

        # execute selected wrappers
        load_media = True
        browser = ajaxbrowser.AjaxBrowser(app=app, gui=True, use_cache=args.cache, load_images=load_media, load_java=load_media, load_plugins=load_media, delay=0)
        for wrapper_name in selected_wrapper_names:
            wrapper = wrappertable.load_wrapper(wrapper_name)
            if wrapper is None: continue
            try:
                if args.all_wrappers and not wrapper.enabled:
                    continue
            except AttributeError:
                pass
            test_cases, final_transitions = run_wrapper(browser, wrapper)
            # completed running the wrapper for training, so now try to build a model of the generated transitions
            input_values = [v for v, _ in test_cases]
            models = build_models(browser, wrapper, input_values, final_transitions)
            if models:
                browser.stats.save_models(wrapper, models)
                for model in models:
                    # display results of optimized execution
                    # XXX commented out until types fixed for Audi
                    #visualisation.ModelLog.log_model("Final Model", model)
                    num_passed = evaluate_model(browser, wrapper, model, test_cases)
                    browser.add_status('Evaluation: {}% accuracy (from {} test cases)'.format(100 * num_passed / len(test_cases), len(test_cases)))
            else:
                browser.add_status('Failed to train model') 
        common.logger.info('Done')
        visualisation.WrapperLog.save()
        if browser.running:
            app.exec_() # wait until window closed
    


def start_local_server(port):
    """start local HTTP server on this port to serve local example web applications
    """
    class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass # prevent error messages
    server = SocketServer.TCPServer(('', port), Handler, bind_and_activate=False)
    # allow reusing port, otherwise will get address in use error if running multiple instances simultaneously
    server.allow_reuse_address = True 
    try:
        server.server_bind()
    except socket.error:
        pass # server already running
    else:
        server.server_activate()
        thread = threading.Thread(target=server.serve_forever, args=())
        thread.daemon = True # daemonize thread so responds to ctrl-c
        thread.start()



def run_wrapper(browser, wrapper):
    """
    Execute the selected wrapper.
    
    Parameters
    ----------
    browser: AjaxBrowser
    wrapper: Wrapper
    
    Returns
    -------
    test_cases: List.
            List of test cases with (input_value, expected_output) items.
    final_transitions: List.
            List of transitions of type Transition with the expected output in its content.
    """
    # create a browser instance
    QApplication.setOverrideCursor(Qt.WaitCursor)
    browser.new_wrapper()
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
        browser.new_execution()
        browser.stats.start(wrapper, 'Training')
        input_value = training_cases.pop(0)
        if isinstance(input_value, tuple):
            input_value, expected_output = input_value
        scraped_data = wrapper.run(browser, input_value)
        browser.wait_quiet()
        browser.stats.stop()
        if scraped_data is not None:
            # set dynamic expected output
            expected_output = {k:[e for e in vs if e] for (k,vs) in scraped_data.items()}
            common.logger.info('Scraped: {}'.format(common.pretty_dict(expected_output)))
        # save the expected output for checking test cases later
        test_cases.append((input_value, expected_output))
        visualisation.TransitionLog.finished_training_case(input_value, expected_output, browser.transitions[transition_offset:]) # These are only the transitions from the most recent wrapper execution.

        while transition_offset < len(browser.transitions):
            # have more transitions to check from the execution path
            # check whether the transitions that were discovered contain the expected output
            for t in browser.transitions[transition_offset:]:
                transition_offset += 1
                if t.parsed_content is not None:
                    columns = scrape.find_columns(t.url.toString(), t.parsed_content, expected_output)
                    if columns:
                        t.columns = columns
                        t.output = expected_output
                        # found a transition that matches the expected output so add it to model
                        final_transitions.append(t)
                        browser.add_status('Found matching reply for training data: {}'.format(common.pretty_dict(expected_output)))
            browser.wait_quiet()

    QApplication.restoreOverrideCursor()
    return test_cases, final_transitions



def build_models(browser, wrapper, input_values, final_transitions):
    """Build a list of possible models from these transitions that satisfy the expected output data.
        Sort models by the number of requests required in ascending order.
        
        Returns
        -------
        results: List.
            Returns a list of models, sorted by the number of requests (transactions) in ascending order.
    """
    models = []
    # first try matching transitions on full paths, then allow abstracting paths
    for abstract_path in (False, True):
        # XXX redundancy here of checking non-path models twice
        for transition_group in group_transitions(final_transitions, abstract_path):
            common.logger.debug('Building model for: {}'.format('|'.join(str(t) for t in transition_group)))
            wrapper_model = model.build(browser, transition_group, input_values)
            if wrapper_model is None:
                common.logger.debug('Failed to build model for transition group')
            else:
                common.logger.info('Built model of requests:\n{}'.format(str(wrapper_model)))
                # initialize the result table with the already known transition records (extracted variables)
                for t in transition_group:
                    if t.columns:
                        browser.add_records(scrape.extract_columns(t.parsed_content, t.columns))
                models.append(wrapper_model)
        if models:
            break # already have models without abstracting path, so exit now
    return sorted(models, key=lambda m: len(m))



def group_transitions(transitions, abstract_path):
    """Organize these transitions into groups with the similar properties.
        The similarity is defined by the equality of sets of the names of parameters and the path of the URL.
    
    Parameters
    ----------
    transitions: List.
            List of transition to be grouped.
    abstract_path: boolean.
            True, if only number of the URL's components (together with other parameters of transitions) should be considered for grouping.
    
    Returns
    -------
        results: List.
            Returns a list of transition groups, sorted by the number of unique URLs in each group.
    """
    groups = collections.defaultdict(list)
    for t in transitions:
        key = t.key(abstract_path)
        groups[key].append(t)
    for key, group in groups.items():
        common.logger.info('Transition group {}: {}'.format(key, [t.url.toString() for t in group]))
    return sorted(groups.values(), key=lambda ts: len(set([t.url.toString() for t in ts])))



def evaluate_model(browser, wrapper, wrapper_model, test_cases):
    """Run the model and check how many of test cases were successfully parsed
    """
    browser.new_wrapper()
    num_passed = 0
    transition_offset = 0 # how many transitions have processed
    for input_value, expected_output in test_cases:
        if not browser.running:
            break
        browser.new_execution()
        #browser.page().networkAccessManager().render = False
        browser.stats.start(wrapper, 'Testing')
        parsed_content = wrapper_model.execute(browser, input_value)
        browser.wait_quiet()
        browser.stats.stop()

        records = scrape.extract_columns(parsed_content, wrapper_model.columns)
        if records:
            #print 'found:', browser.current_url(), t.url.toString(), wrapper_model.transition.url.toString()
            found_columns = True
            browser.add_status('Found test data: {}'.format(common.pretty_dict(records)))
            num_passed += 1
            browser.add_records(records)
        else:
            print 'no records', records
    return num_passed



if __name__ == '__main__':
    main()
