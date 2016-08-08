# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QShortcut, QKeySequence, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QFont
from PyQt4.QtCore import Qt, QUrl

import csv, os, re, collections
import webkit, common, model, parser, transition, stats



class AjaxBrowser(QWidget):
    """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
    """
    def __init__(self, gui=True, **argv):
        """
        gui: whether to show webkit window or run headless
        """
        super(AjaxBrowser, self).__init__()
        self.argv = argv
        self.stats = stats.RenderStats()
        # use grid layout to hold widgets
        self.grid = QVBoxLayout()
        self.url_input = UrlInput(self.load_url)
        self.grid.addWidget(self.url_input)
        self._view = None
        # create status box
        self.status_table = StatusTable()
        self.grid.addWidget(self.status_table)
        # create results table
        self.records_table = ResultsTable()
        self.grid.addWidget(self.records_table)
        self.setLayout(self.grid)
        # log all responses
        response_filename = os.path.join(webkit.OUTPUT_DIR, 'responses.csv')
        self.response_writer = csv.writer(open(response_filename, 'w'))
        self.response_writer.writerow(['URL', 'Content-Type', 'Referer', 'Size'])

        # Define keyboard shortcuts for convenient interaction
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.fullscreen)

        if gui:
            self.showMaximized()
            self.raise_() # give focus to this browser window


    def __del__(self):
        # not sure why, but to avoid segmentation fault need to release the QWebPage instance manually
        self._view.setPage(None)


    def __getattr__(self, name):
        """Pass unknown methods through to the view
        """
        def method(*args, **kwargs):
            return getattr(self._view, name)(*args, **kwargs)
        return method


    def new_wrapper(self):
        # transitions found so far
        self.transitions = []
        # models of each step
        self.models = []
        self.running = True
        self.response_writer.writerow(['New wrapper'])

    
    def new_execution(self):
        #self.url_input.clear()
        self.records_table.clear()
        if self._view is not None:
            self.grid.removeWidget(self._view)
            self._view.hide()
            self._view.page().networkAccessManager().shutdown()
            del self._view
        self._view = webkit.Browser(**self.argv)
        self._view.page().mainFrame().loadStarted.connect(self._load_started)
        self._view.page().mainFrame().loadFinished.connect(self._load_finished)
        self._view.page().networkAccessManager().finished.connect(self.finished)
        self.grid.insertWidget(1, self._view)
        QShortcut(QKeySequence.Back, self, self._view.back)
        QShortcut(QKeySequence.Forward, self, self._view.forward)
        QShortcut(QKeySequence.Save, self, self._view.save)
        QShortcut(QKeySequence.New, self, self._view.home)
        self.response_writer.writerow(['New execution'])


    def find(self, pattern):
        # need to override builtin QWebkit function
        return self._view.find(pattern)


    def _load_started(self):
        # XXX how to get URL when start load?
        pass #self.update_address(self.current_url())
    
    
    def _load_finished(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok:
            # a webpage has loaded successfully
            common.logger.info('loaded: {} {}'.format(ok, self.current_url()))
            self.update_address(self.current_url())
            #print 'Bytes:', self.current_url(), self._view.page().totalBytes(), self._view.page().bytesReceived()
            self.stats.rendered()


    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        common.logger.debug('Response: {} {}'.format(reply.url().toString(), reply.data))
        if not reply.content:
            return # no response so reply is not of interest
        self.stats.add_response(reply.content)

        reply.content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        referrer = reply.orig_request.rawHeader("Referer")
        self.response_writer.writerow([reply.url().toString(), reply.content_type, referrer, len(reply.content)])
        if re.match('(image|audio|video|model|message)/', reply.content_type) or reply.content_type == 'text/css':
            pass # ignore irrelevant content types such as media and CSS
        else:
            # have found a response that can potentially be parsed for useful content
            content = common.to_unicode(str(reply.content))
            if re.match('(application|text)/', reply.content_type):
                js = parser.parse(content, reply.content_type)
            else:
                js = None
            # save for checking later once interface has been updated
            self.transitions.append(transition.Transition(reply, js))



    def fullscreen(self):
        """Toggle fullscreen mode
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def add_status(self, text):
        """Add status message to text box
        """
        common.logger.info(text)
        self.status_table.add(text)

    
    def add_records(self, records): 
        """Add these records to the results table
        """
        self.records_table.add_records(records)


    def update_address(self, url):
        """Set address of the URL text field
        """
        self.url_input.setText(url)


    def load_url(self, url):
        """Load view with given URL
        """
        self._view.get(url)


    def closeEvent(self, event):
        """Catch the close window event and stop the script
        """
        self._view.app.quit()
        self.running = False
        self.page().networkAccessManager().shutdown()
    

class UrlInput(QLineEdit):
    """Address URL input widget
    Callback takes a QUrl of the url to load
    """
    def __init__(self, callback):
        super(UrlInput, self).__init__()
        self.cb = callback
        # add event listener on "enter" pressed
        self.returnPressed.connect(self._return_pressed)


    def _return_pressed(self):
        url = QUrl(self.text())
        # load url into browser frame
        self.cb(url)



class StatusTable(QListWidget):
    def __init__(self):
        super(StatusTable, self).__init__()
        font = QFont('Times New Roman', 16)
        font.setBold(True)
        header = QListWidgetItem('Status')
        header.setFont(font)
        self.addItem(header)
        self.hide()

    def add(self, message):
        self.show()
        self.addItem(message)


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
        self.setRowCount(0)
        self.setColumnCount(0)
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

