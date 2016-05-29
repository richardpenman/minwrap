# -*- coding: utf-8 -*-

__doc__ = 'Interface to qt webkit for loading and interacting with JavaScript dependent webpages'

import sys, os, re, urllib2, random, itertools, csv
reload(sys)
sys.setdefaultencoding('utf-8')
from time import time, sleep
from datetime import datetime

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtGui import QApplication, QDesktopServices, QImage, QPainter, QVBoxLayout, QLineEdit, QWidget, QWidget, QShortcut, QKeySequence, QTableWidget, QTableWidgetItem
from PyQt4.QtCore import QByteArray, QUrl, QTimer, QEventLoop, QIODevice, QObject, Qt
from PyQt4.QtWebKit import QWebFrame, QWebView, QWebElement, QWebPage, QWebSettings, QWebInspector
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkRequest, QNetworkReply, QNetworkDiskCache

import common

# maximum number of bytes to read from a POST request
MAX_POST_SIZE = 2 ** 25



class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, proxy):
        """Subclass QNetworkAccessManager for finer control network operations

        proxy: the string of a proxy to download through
        cache_size: the maximum size of the webkit cache (MB)
        cache_dir: where to place the cache
        """
        super(NetworkAccessManager, self).__init__()
        # and proxy
        self.setProxy(proxy)
        self.sslErrors.connect(self.sslErrorHandler)
        # the requests that are still active
        self.active_requests = [] 


    def shutdown(self):
        """Network is shutting down event
        """
        # prevent new requests
        self.setNetworkAccessible(QNetworkAccessManager.NotAccessible)
        # abort existing requests
        for request in self.active_requests:
            request.abort()
            request.deleteLater()


    def setProxy(self, proxy):
        """Parse proxy components from proxy
        """
        if proxy:
            fragments = common.parse_proxy(proxy)
            if fragments.host:
                QNetworkAccessManager.setProxy(self, 
                    QNetworkProxy(QNetworkProxy.HttpProxy, 
                      fragments.host, int(fragments.port), 
                      fragments.username, fragments.password
                    )
                )
            else:
                common.logger.info('Invalid proxy: ' + str(proxy))


    def createRequest(self, operation, request, post):
        """Override creating a network request
        """
        if str(request.url().path()).endswith('.ttf'):
            # block fonts, which can cause webkit to crash
            common.logger.debug('Blocking: {}'.format(request.url().toString()))
            request.setUrl(QUrl())
        else:
            common.logger.debug('Request: {} {}'.format(request.url().toString(), post or ''))
        reply = QNetworkAccessManager.createRequest(self, operation, request, post)
        reply.error.connect(self.catch_error)
        self.active_requests.append(reply)
        reply.destroyed.connect(self.active_requests.remove)
        # save reference to original request
        reply.orig_request = request
        reply.data = self.parse_data(post)
        reply.content = ''
        def save_content(r):
            # save copy of reply content before is lost
            def _save_content():
                r.content += r.peek(r.size())
            return _save_content
        reply.readyRead.connect(save_content(reply))
        return reply
       

    def parse_data(self, data):
        """Parse this posted data into a list of key/value pairs
        """
        if data is not None:
            url = QUrl('')
            url.setEncodedQuery(data.peek(MAX_POST_SIZE))
            return url.queryItems()
        return []


    def catch_error(self, eid):
        """Interpret the HTTP error ID received
        """
        if eid not in (5, 301):
            errors = {
                0 : 'no error condition. Note: When the HTTP protocol returns a redirect no error will be reported. You can check if there is a redirect with the QNetworkRequest::RedirectionTargetAttribute attribute.',
                1 : 'the remote server refused the connection (the server is not accepting requests)',
                2 : 'the remote server closed the connection prematurely, before the entire reply was received and processed',
                3 : 'the remote host name was not found (invalid hostname)',
                4 : 'the connection to the remote server timed out',
                5 : 'the operation was canceled via calls to abort() or close() before it was finished.',
                6 : 'the SSL/TLS handshake failed and the encrypted channel could not be established. The sslErrors() signal should have been emitted.',
                7 : 'the connection was broken due to disconnection from the network, however the system has initiated roaming to another access point. The request should be resubmitted and will be processed as soon as the connection is re-established.',
                101 : 'the connection to the proxy server was refused (the proxy server is not accepting requests)',
                102 : 'the proxy server closed the connection prematurely, before the entire reply was received and processed',
                103 : 'the proxy host name was not found (invalid proxy hostname)',
                104 : 'the connection to the proxy timed out or the proxy did not reply in time to the request sent',
                105 : 'the proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)',
                201 : 'the access to the remote content was denied (similar to HTTP error 401)',
                202 : 'the operation requested on the remote content is not permitted',
                203 : 'the remote content was not found at the server (similar to HTTP error 404)',
                204 : 'the remote server requires authentication to serve the content but the credentials provided were not accepted (if any)',
                205 : 'the request needed to be sent again, but this failed for example because the upload data could not be read a second time.',
                301 : 'the Network Access API cannot honor the request because the protocol is not known',
                302 : 'the requested operation is invalid for this protocol',
                99 : 'an unknown network-related error was detected',
                199 : 'an unknown proxy-related error was detected',
                299 : 'an unknown error related to the remote content was detected',
                399 : 'a breakdown in protocol was detected (parsing error, invalid or unexpected responses, etc.)',
            }
            common.logger.debug('Error %d: %s (%s)' % (eid, errors.get(eid, 'unknown error'), self.sender().url().toString()))


    def sslErrorHandler(self, reply, errors): 
        common.logger.info('SSL errors: {}'.format(errors))
        reply.ignoreSslErrors() 



class WebPage(QWebPage):
    def __init__(self, user_agent, confirm=True):
        """Override QWebPage to set User-Agent and JavaScript messages

        user_agent: the User Agent to submit
        confirm: default response to confirm dialog boxes
        """
        super(WebPage, self).__init__()
        self.user_agent = user_agent
        self.confirm = confirm
        self.setForwardUnsupportedContent(True)

    def userAgentForUrl(self, url):
        """Use same user agent for all URL's
        """
        return self.user_agent

    def javaScriptAlert(self, frame, message):
        """Override default JavaScript alert popup and send to log
        """
        common.logger.debug('Alert: ' + message)


    def javaScriptConfirm(self, frame, message):
        """Override default JavaScript confirm popup and send to log
        """
        common.logger.debug('Confirm: ' + message)
        return self.confirm


    def javaScriptPrompt(self, frame, message, default):
        """Override default JavaScript prompt popup and send to log
        """
        common.logger.debug('Prompt: {} {}'.format(message, default))


    def javaScriptConsoleMessage(self, message, line_number, source_id):
        """Override default JavaScript console and send to log
        """
        common.logger.debug('Console: {} {} {}'.format(message, line_number, source_id))


    def shouldInterruptJavaScript(self):
        """Disable javascript interruption dialog box
        """
        return True



class WebView(QWebView):
    def __init__(self, page, load_images, load_javascript, load_java, load_plugins):
        """Override QWebView to set which plugins to load
        """
        super(WebView, self).__init__()
        self.setPage(page)
        # set whether to enable plugins, images, and java
        self.settings().setAttribute(QWebSettings.AutoLoadImages, load_images)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, load_javascript)
        self.settings().setAttribute(QWebSettings.JavaEnabled, load_java)
        self.settings().setAttribute(QWebSettings.PluginsEnabled, load_plugins)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)



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
        self.view.load(url)



class ResultsTable(QTableWidget):
    def __init__(self):
        """A table to display results from the scraping
        """
        super(ResultsTable, self).__init__()
        # avoid displaying duplicate rows
        self.row_hashes = set()
        # also save data to a CSV file
        self.writer = csv.writer(open('data.csv', 'w'))
        self.fields = None
        self.hide()

    def add_rows(self, fields, rows=None):
        """Add these rows to the table and initialize fields if not already
        """
        if self.fields is None:
            self.show()
            self.fields = fields
            self.setColumnCount(len(fields))
            self.setHorizontalHeaderLabels(fields)
            self.writer.writerow(fields)
        for row in rows or []:
            self.add_row(row)

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



class Browser(QWidget):
    def __init__(self, gui=False, user_agent='WebKit', proxy=None, load_images=True, load_javascript=True, load_java=True, load_plugins=True, timeout=20, delay=5, app=None):
        """Widget class that contains the address bar, webview for rendering webpages, and a table for displaying results

        gui: whether to show webkit window or run headless
        user_agent: the user-agent when downloading content
        proxy: a QNetworkProxy to download through
        load_images: whether to download images
        load_javascript: whether to enable javascript
        load_java: whether to enable java
        load_plugins: whether to enable browser plugins
        timeout: the maximum amount of seconds to wait for a request
        delay: the minimum amount of seconds to wait between requests
        """
        # must instantiate the QApplication object before any other Qt objects
        self.app = app or QApplication(sys.argv)
        super(Browser, self).__init__()
        self.running = True
        manager = NetworkAccessManager(proxy)
        manager.finished.connect(self.finished)
        page = WebPage(user_agent)
        page.setNetworkAccessManager(manager)
        self.view = WebView(page, load_images, load_javascript, load_java, load_plugins)
        self.timeout = timeout
        self.delay = delay

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


    def __del__(self):
        # not sure why, but to avoid seg fault need to release the QWebPage manually
        self.view.setPage(None)


    def add_shortcuts(self):
        """Define shortcuts for convenient interaction
        """
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence.Back, self, self.view.back)
        QShortcut(QKeySequence.Forward, self, self.view.forward)
        QShortcut(QKeySequence.Save, self, self.save)
        QShortcut(QKeySequence.New, self, self.home)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.fullscreen)


    def save(self):
        """Save the current HTML to disk
        """
        html = self.current_html()
        for i in itertools.count(1):
            filename = 'data/test{}.html'.format(i)
            if not os.path.exists(filename):
                open(filename, 'w').write(common.to_unicode(html))
                print 'save', filename
                break


    def home(self):
        """Go back to initial page in history
        """
        history = self.view.history()
        history.goToItem(history.itemAt(0))


    def fullscreen(self):
        """Alternate fullscreen mode
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized() 


    def set_proxy(self, proxy):
        """Shortcut to set the proxy
        """
        self.view.page().networkAccessManager().setProxy(proxy)


    def current_url(self):
        """Return current URL
        """
        return str(self.view.url().toString())


    def current_html(self):
        """Return current rendered HTML
        """
        return common.to_unicode(str(self.view.page().mainFrame().toHtml()))


    def current_text(self):
        """Return text from the current rendered HTML
        """
        return common.to_unicode(str(self.view.page().mainFrame().toPlainText()))


    def load(self, url=None, html=None, headers=None, data=None, num_retries=1):
        """Load given url in webkit and return html when loaded

        url: the URL to load
        html: optional HTML to set instead of downloading
        headers: the headers to attach to the request
        data: the data to POST
        num_retries: how many times to try downloading this URL
        """
        if not self.running:
            return
        if isinstance(url, basestring):
            # convert string to Qt's URL object
            url = QUrl(url)
        t1 = time()
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        self.view.loadFinished.connect(loop.quit)
        if url:
            self.update_address(url)
            if html:
                # load pre downloaded HTML
                self.view.setContent(html, baseUrl=url)
            else:
                # need to make network request
                request = QNetworkRequest(url)
                if headers:
                    # add headers to request when defined
                    for header, value in headers:
                        request.setRawHeader(header, value)
                if data:
                    # POST request
                    self.view.load(request, QNetworkAccessManager.PostOperation, data)
                else:
                    # GET request
                    self.view.load(request)
        timer.start(self.timeout * 1000)
        loop.exec_() # delay here until download finished or timeout
    
        if timer.isActive():
            # downloaded successfully
            timer.stop()
            parsed_html = self.current_html()
            self.wait(self.delay - (time() - t1))
        else:
            # did not download in time
            if num_retries > 0:
                common.logger.debug('Timeout - retrying: {}'.format(url.toString()))
                parsed_html = self.load(url, num_retries=num_retries-1)
            else:
                common.logger.debug('Timed out: {}'.format(url.toString()))
                parsed_html = ''
        return parsed_html


    def wait(self, timeout=1):
        """Wait for delay time
        """
        deadline = time() + timeout
        while time() < deadline:
            sleep(0)
            self.app.processEvents()


    def wait_quiet(self, timeout=20):
        """Wait until all requests have completed
        `timeout' is the maximum amount of seconds to wait
        """
        self.app.processEvents()
        deadline = time() + timeout
        manager = self.view.page().networkAccessManager()
        while time() < deadline and manager.active_requests:
            sleep(0)
            self.app.processEvents()
        self.app.processEvents()
        return manager.active_requests == []


    def wait_load(self, pattern, timeout=60):
        """Wait for this content to be loaded up to maximum timeout
        Returns boolean of whether pattern was loaded in the time limit
        """
        deadline = time() + timeout
        while time() < deadline:
            sleep(0)
            self.app.processEvents()
            if self.find(pattern):
                return True
        return False


    def js(self, script):
        """Shortcut to execute javascript on current document and return result
        """
        self.app.processEvents()
        return self.view.page().mainFrame().evaluateJavaScript(script).toString()


    def click(self, pattern='input'):
        """Click all elements that match the pattern.
        XXX possible to do this with native API rather than JavaScript hack?

        Uses standard CSS pattern matching: http://www.w3.org/TR/CSS2/selector.html
        Returns the number of elements clicked
        """
        es = self.find(pattern)
        for e in es:
            e.evaluateJavaScript("var evObj = document.createEvent('MouseEvents'); evObj.initEvent('click', true, true); this.dispatchEvent(evObj);")
        return len(es)


    def keydown(self, key):
        """XXX Need to instantiate this and other native events
        """
        raise NotImplementedError('add support for native events')


    def attr(self, pattern, name, value=None):
        """Set attribute if value is defined, else get
        """
        if value is None:
            # want to get attribute
            return str(self.view.page().mainFrame().findFirstElement(pattern).attribute(name))
        else:
            es = self.find(pattern)
            for e in es:
                e.setAttribute(name, value)
            return len(es)


    def fill(self, pattern, value):
        """Set text of these elements to value
        """
        es = self.find(pattern)
        for e in es:
            tag = str(e.tagName()).lower()
            if tag == 'input':
                e.setAttribute('value', value)
                #e.evaluateJavaScript('this.value = "%s"' % value)
            else:
                e.setPlainText(value)
        return len(es)

 
    def find(self, pattern):
        """Returns whether element matching css pattern exists
        Note this uses CSS syntax, not Xpath
        """
        if isinstance(pattern, basestring):
            matches = self.view.page().mainFrame().findAllElements(pattern).toList()
        elif isinstance(pattern, list):
            matches = pattern
        elif isinstance(pattern, QWebElement):
            matches = [pattern]
        else:
            common.logger.warning('Unknown pattern: ' + str(pattern))
            matches = []
        return matches


    def response(self, url):
        """Get data for this downloaded resource, if exists
        """
        record = self.view.page().networkAccessManager().cache().data(QUrl(url))
        if record:
            data = record.readAll()
            record.reset()
        else:
            data = None
        return data
    
    
    def run(self):
        """Run the Qt event loop so can interact with the browser
        """
        self.app.exec_() # start GUI thread


    def finished(self, reply):
        """Override this method in subclasses to process downloaded urls
        """
        if reply.url() == self.view.url():
            self.update_address(reply.url())


    def update_address(self, url):
        self.url_input.setText(url.toString())
        

    def screenshot(self, output_file):
        """Take screenshot of current webpage and save results
        """
        frame = self.view.page().mainFrame()
        self.view.page().setViewportSize(frame.contentsSize())
        image = QImage(self.view.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        common.logger.debug('saving: ' + output_file)
        image.save(output_file)


    def closeEvent(self, event):
        """Catch the close window event and stop the script
        """
        self.app.quit()
        self.running = False
        self.view.page().networkAccessManager().shutdown()



if __name__ == '__main__':
    # initiate webkit and show gui
    # once script is working you can disable the gui
    w = Browser(gui=True) 
    # load webpage
    w.load('http://duckduckgo.com')
    # fill search textbox 
    w.fill('input[id=search_form_input_homepage]', 'web scraping')
    # take screenshot of webpage
    w.screenshot('duckduckgo.jpg')
    # click search button 
    w.click('input[id=search_button_homepage]')
    w.run()
    # show webpage for 10 seconds
    w.wait(10)
