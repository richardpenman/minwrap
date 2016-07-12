# -*- coding: utf-8 -*-

__doc__ = 'Interface to run the ajax browser'

import sip
sip.setapi('QString', 2)
from PyQt4.QtNetwork import QNetworkRequest
from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QShortcut, QKeySequence, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QFont
from PyQt4.QtCore import Qt

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
        self.view = webkit.Browser(**argv)
        self.view.page().mainFrame().loadFinished.connect(self._load_finish)
        self.view.page().networkAccessManager().finished.connect(self.finished)

        # use grid layout to hold widgets
        self.grid = QVBoxLayout()
        self.url_input = UrlInput(self.view)
        self.grid.addWidget(self.url_input)
        self.grid.addWidget(self.view)
        # create status box
        self.status_table = StatusTable()
        self.grid.addWidget(self.status_table)
        # create results table
        self.records_table = ResultsTable()
        self.grid.addWidget(self.records_table)
        # set the grid
        self.setLayout(self.grid)
        self.add_shortcuts()
        if gui:
            self.show()
            self.raise_() # give focus to this browser window
        # transitions found so far
        self.transitions = []
        # models of each step
        self.models = []
        self.stats = stats.RenderStats()
        self.running = True


    def __del__(self):
        # not sure why, but to avoid segmentation fault need to release the QWebPage instance manually
        self.view.setPage(None)


    def __getattr__(self, name):
        """Pass unknown methods through to the view
        """
        def method(*args):
            return getattr(self.view, name)(*args)
        return method

    def find(self, pattern):
        # need to override builtin QWebkit function
        return self.view.find(pattern)


    def _load_finish(self, ok):
        """Finished loading a page so store the initial state
        """
        if ok:
            # a webpage has loaded successfully
            common.logger.info('loaded: {} {}'.format(ok, self.current_url()))
            self.update_address(self.current_url())
            #print 'Bytes:', self.current_url(), self.view.page().totalBytes(), self.view.page().bytesReceived()
            self.stats.rendered()


    def finished(self, reply):
        """Override the reply finished signal to check the result of each request
        """
        if not reply.content:
            return # no response so reply is not of interest

        self.stats.add_response(reply.content)
        content_type = reply.header(QNetworkRequest.ContentTypeHeader).toString().lower()
        if re.match('(image|audio|video|model|message)/', content_type) or content_type == 'text/css':
            pass # ignore irrelevant content types such as media and CSS
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
        """Define keyboard shortcuts for convenient interaction
        """
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence.Back, self, self.view.back)
        QShortcut(QKeySequence.Forward, self, self.view.forward)
        QShortcut(QKeySequence.Save, self, self.view.save)
        QShortcut(QKeySequence.New, self, self.view.home)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.fullscreen)


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


    def clear(self):
        """Clear the outputs
        """
        self.status_table.clear()
        self.records_table.clear()


    def closeEvent(self, event):
        """Catch the close window event and stop the script
        """
        self.view.app.quit()
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

