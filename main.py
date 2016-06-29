# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import QApplication

import argparse, sys, re, os, collections, pprint
import ajaxbrowser, common, model, wrappertable
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
    execution = wrapper.run(browser)

    models = {} 
    expected_output = None
    while browser.running:
        if execution is not None:
            try:
                expected_output = execution.next()
                browser.wait_quiet()
            except StopIteration:
                # completed running the wrapper
                expected_output = execution = None
                QApplication.restoreOverrideCursor()
                browser.run_models(models)
        browser.app.processEvents() 

        if browser.transitions and expected_output:
            # check whether the transitions that were discovered contain the expected output
            for t in reversed(browser.transitions):
                if t.matches(expected_output):
                    # found a transition that matches the expected output so add it to model
                    try:
                        m = models[hash(t)]
                    except KeyError:
                        m = models[hash(t)] = model.Model()
                    m.add(t)
                    browser.transitions.remove(t)


if __name__ == '__main__':
    main()
