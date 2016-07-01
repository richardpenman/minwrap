# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtGui import QWidget, QVBoxLayout, QLineEdit, QShortcut, QKeySequence, QTableWidget, QTableWidgetItem
from PyQt4.QtCore import Qt

import csv, os, re, collections
import webkit, common, model, parser, transition



class AjaxBrowser(QWidget):
    """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
    """
    def __init__(self, gui=True, **argv):
        """
        gui: whether to show webkit window or run headless
        """
        super(AjaxBrowser, self).__init__()
        self.view = webkit.Browser(**argv)
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
        self.view.page().networkAccessManager().finished.connect(self.finished)

        # use grid layout to hold widgets
        self.grid = QVBoxLayout()
        self.url_input = UrlInput(self.view)
        self.grid.addWidget(self.url_input)
        self.grid.addWidget(self.view)
        self.table = ResultsTable()
        self.grid.addWidget(self.table)
        self.setLayout(self.grid)
        self.add_shortcuts()
        if gui:
            self.show()
            self.raise_() # give focus to this browser window
        # transitions found so far
        self.transitions = []
        self.running = True


    def __del__(self):
        # not sure why, but to avoid seg fault need to release the QWebPage instance manually
        self.view.setPage(None)


    def __getattr__(self, name):
        """Pass unknown methods through to the view
        """
        def method(*args):
            #print 'child method', name, args
            return getattr(self.view, name)(*args)
        return method


    def find(self, pattern):
        return self.view.find(pattern)


    def _load_finish(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok:
            # a webpage has loaded successfully
            common.logger.info('loaded: {} {}'.format(ok, self.current_url()))
            self.update_address(self.current_url())


    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        if not reply.content:
            return # no response so reply is not of interest

        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        # main page has loaded
        if re.match('(image|audio|video|model|message)/', content_type) or content_type == 'text/css':
            pass # ignore these irrelevant content types
        else:
            common.logger.debug('Response: {} {}'.format(reply.url().toString(), reply.data))
            # have found a response that can potentially be parsed for useful content
            content = common.to_unicode(str(reply.content))
            if re.match('(application|text)/', content_type):
                js = parser.parse(content, content_type)
            else:
                js = None
            # save for checking later once interface has been updated
            self.transitions.append(transition.Transition(reply, js))


    def add_shortcuts(self):
        """Define shortcuts for convenient interaction
        """
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence.Back, self, self.view.back)
        QShortcut(QKeySequence.Forward, self, self.view.forward)
        QShortcut(QKeySequence.Save, self, self.view.save)
        QShortcut(QKeySequence.New, self, self.view.home)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.fullscreen)


    def fullscreen(self):
        """Alternate fullscreen mode
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def update_address(self, url):
        """Set address of the URL text field
        """
        self.url_input.setText(url)


    def closeEvent(self, event):
        """Catch the close window event and stop the script
        """
        self.app.quit()
        self.running = False
        self.page().networkAccessManager().shutdown()



class UrlInput(QLineEdit):
    """Address URL input widget
    """
    def __init__(self, view):
        super(UrlInput, self).__init__()
        self.view = view
        # add event listener on "enter" pressed
        self.returnPressed.connect(self._return_pressed)


    def _return_pressed(self):
        url = QUrl(self.text())
        # load url into browser frame
        self.view.get(url)



class ResultsTable(QTableWidget):
    def __init__(self):
        """A table to display results from the scraping
        """
        super(ResultsTable, self).__init__()
        # also save data to a CSV file
        self.hide()
        self.clear()

    def clear(self):
        # avoid displaying duplicate rows
        self.row_hashes = set()
        self.fields = None
        self.writer = csv.writer(open(os.path.join(webkit.OUTPUT_DIR, 'data.csv'), 'w'))
        super(ResultsTable, self).clear()

    def add_records(self, records):
        """Add these rows to the table and initialize fields if not already
        """
        for record in records:
            if self.fields is None:
                self.fields = sorted(record.keys())
                self.setColumnCount(len(self.fields))
                header = [field.title() for field in self.fields]
                self.setHorizontalHeaderLabels(header)
                self.writer.writerow(header)
                self.show()
            # filter to fields in the header
            filtered_row = [record.get(field) for field in self.fields]
            if any(filtered_row):
                self.add_row(filtered_row)

    def add_row(self, cols):
        """Add this row to the table if is not duplicate
        """
        key = hash(tuple(cols))
        if key not in self.row_hashes:
            self.row_hashes.add(key)
            num_rows = self.rowCount()
            self.insertRow(num_rows)
            for i, col in enumerate(cols):
                self.setItem(num_rows, i, QTableWidgetItem(col))
            self.writer.writerow(cols)

