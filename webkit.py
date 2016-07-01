# -*- coding: utf-8 -*-

__doc__ = 'Interface to qt webkit for loading and interacting with JavaScript dependent webpages'

import sys, os, re, urllib2, random, itertools
reload(sys)
sys.setdefaultencoding('utf-8')
from time import time, sleep
from datetime import datetime

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtGui import QApplication, QDesktopServices, QImage, QPainter
from PyQt4.QtCore import QByteArray, QUrl, QTimer, QEventLoop, QIODevice, QObject
from PyQt4.QtWebKit import QWebFrame, QWebView, QWebElement, QWebPage, QWebSettings, QWebInspector
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkRequest, QNetworkReply, QNetworkDiskCache

# maximum number of bytes to read from a POST request
MAX_POST_SIZE = 2 ** 25
# output directory where to save generated files
OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

import common, db


class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, proxy, use_cache):
        """Subclass QNetworkAccessManager for finer control network operations

        proxy: the string of a proxy to download through
        use_cache: whether to cache replies so that can load faster with the same content subsequent times
        """
        super(NetworkAccessManager, self).__init__()
        self.setProxy(proxy)
        self.sslErrors.connect(self.sslErrorHandler)
        # the requests that are still active
        self.active_requests = [] 
        self.cache = db.DbmDict(os.path.join(OUTPUT_DIR, 'cache.db')) if use_cache else None


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
            if fragments['host']:
                QNetworkAccessManager.setProxy(self,
                    QNetworkProxy(QNetworkProxy.HttpProxy,
                      fragments['host'], int(fragments['port']),
                      fragments['username'], fragments['password']
                    )
                )
            else:
                common.logger.info('Invalid proxy: ' + str(proxy))


    def createRequest(self, operation, request, post):
        """Override creating a network request
        """
        url = request.url().toString()
        if str(request.url().path()).endswith('.ttf'):
            # block fonts, which can cause webkit to crash
            common.logger.debug('Blocking: {}'.format(url))
            request.setUrl(QUrl())

        data = self.parse_data(post)
        key = '{} {}'.format(url, data)
        use_cache = not url.startswith('file')
        if self.cache is not None and use_cache and key in self.cache:
            common.logger.debug('Load from cache: ' + key)
            content, headers, attributes = self.cache[key]
            reply = CachedNetworkReply(self, request.url(), content, headers, attributes)
        else:
            common.logger.debug('Request: {} {}'.format(url, post or ''))
            reply = QNetworkAccessManager.createRequest(self, operation, request, post)
            reply.error.connect(self.catch_error)
            self.active_requests.append(reply)
            reply.destroyed.connect(self.active_requests.remove)
            # save reference to original request
            reply.content = QByteArray()
            reply.readyRead.connect(self._save_content(reply))
            if self.cache is not None and use_cache:
                reply.finished.connect(self._cache_content(reply, key))
        reply.orig_request = request
        reply.data = data
        return reply
    
    
    def _save_content(self, r):
        """Save copy of reply content before is lost
        """
        def save_content():
            r.content.append(r.peek(r.size()))
        return save_content
   
    def _cache_content(self, r, key):
        """Cache downloaded content
        """
        def cache_content():
            headers = [(header, r.rawHeader(header)) for header in r.rawHeaderList()]
            attributes = []
            attributes.append((QNetworkRequest.HttpStatusCodeAttribute, r.attribute(QNetworkRequest.HttpStatusCodeAttribute).toInt()))
            attributes.append((QNetworkRequest.HttpReasonPhraseAttribute, r.attribute(QNetworkRequest.HttpReasonPhraseAttribute).toByteArray()))
            #attributes.append((QNetworkRequest.RedirectionTargetAttribute, r.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()))
            attributes.append((QNetworkRequest.ConnectionEncryptedAttribute, r.attribute(QNetworkRequest.ConnectionEncryptedAttribute).toBool()))
            #attributes.append((QNetworkRequest.CacheLoadControlAttribute, r.attribute(QNetworkRequest.CacheLoadControlAttribute).toInt()))
            #attributes.append((QNetworkRequest.CacheSaveControlAttribute, r.attribute(QNetworkRequest.CacheSaveControlAttribute).toBool()))
            #attributes.append((QNetworkRequest.SourceIsFromCacheAttribute, r.attribute(QNetworkRequest.SourceIsFromCacheAttribute).toBool()))
            #print 'save cache:', key, len(r.content), len(headers), attributes
            self.cache[key] = r.content, headers, attributes
        return cache_content


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



class CachedNetworkReply(QNetworkReply):
    def __init__(self, parent, url, content, headers, attributes):
        super(CachedNetworkReply, self).__init__(parent)
        self.setUrl(url)
        self.content = content
        self.offset = 0
        for header, value in headers:
            self.setRawHeader(header, value)
        #self.setHeader(QNetworkRequest.ContentLengthHeader, len(content))
        for attribute, value in attributes:
            self.setAttribute(attribute, value)
        self.setOpenMode(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)
        # trigger signals that content is ready
        QTimer.singleShot(0, self.readyRead)
        QTimer.singleShot(0, self.finished)

    def bytesAvailable(self):
        return len(self.content) - self.offset

    def isSequential(self):
        return True

    def abort(self):
        pass # qt requires that this be defined

    def readData(self, size):
        """Return up to size bytes from buffer
        """
        if self.offset >= len(self.content):
            return ''
        number = min(size, len(self.content) - self.offset)
        data = self.content[self.offset : self.offset + number]
        self.offset += number
        return str(data)



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



class Browser(QWebView):
    def __init__(self, user_agent='WebKit', proxy=None, load_images=True, load_javascript=True, load_java=True, load_plugins=True, timeout=20, delay=5, app=None, use_cache=False):
        """Widget class that contains the address bar, webview for rendering webpages, and a table for displaying results

        user_agent: the user-agent when downloading content
        proxy: a QNetworkProxy to download through
        load_images: whether to download images
        load_javascript: whether to enable javascript
        load_java: whether to enable java
        load_plugins: whether to enable browser plugins
        timeout: the maximum amount of seconds to wait for a request
        delay: the minimum amount of seconds to wait between requests
        app: QApplication object so that can instantiate multiple browser objects
        use_cache: whether to cache all replies
        """
        # must instantiate the QApplication object before any other Qt objects
        self.app = app or QApplication(sys.argv)
        super(Browser, self).__init__()

        page = WebPage(user_agent)
        manager = NetworkAccessManager(proxy, use_cache)
        page.setNetworkAccessManager(manager)
        self.setPage(page)
        # set whether to enable plugins, images, and java
        self.settings().setAttribute(QWebSettings.AutoLoadImages, load_images)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, load_javascript)
        self.settings().setAttribute(QWebSettings.JavaEnabled, load_java)
        self.settings().setAttribute(QWebSettings.PluginsEnabled, load_plugins)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.timeout = timeout
        self.delay = delay


    def home(self):
        """Go back to initial page in history
        """
        history = self.history()
        history.goToItem(history.itemAt(0))


    def save(self):
        """Save the current HTML state to disk
        """
        for i in itertools.count(1):
            filename = os.path.join(OUTPUT_DIR, 'state{}.html'.format(i))
            if not os.path.exists(filename):
                html = self.current_html()
                open(filename, 'w').write(common.to_unicode(html))
                print 'save', filename
                break


    def set_proxy(self, proxy):
        """Shortcut to set the proxy
        """
        self.page().networkAccessManager().setProxy(proxy)


    def current_url(self):
        """Return current URL
        """
        return str(self.url().toString())


    def current_html(self):
        """Return current rendered HTML
        """
        return common.to_unicode(str(self.page().mainFrame().toHtml()))


    def current_text(self):
        """Return text from the current rendered HTML
        """
        return common.to_unicode(str(self.page().mainFrame().toPlainText()))


    def get(self, url, html=None, headers=None, data=None):
        """Load given url in webkit and return html when loaded

        url: the URL to load
        html: optional HTML to set instead of downloading
        headers: the headers to attach to the request
        data: the data to POST
        """
        if isinstance(url, basestring):
            # convert string to Qt's URL object
            url = QUrl(url)
        if html:
            # load pre downloaded HTML
            self.setContent(html, baseUrl=url)
            return html

        t1 = time()
        loop = QEventLoop()
        self.loadFinished.connect(loop.quit)
        # need to make network request
        request = QNetworkRequest(url)
        if headers:
            # add headers to request when defined
            for header, value in headers:
                request.setRawHeader(header, value)
        fn = super(Browser, self)
        if data:
            # POST request
            fn.load(request, QNetworkAccessManager.PostOperation, data)
        else:
            # GET request
            fn.load(request)

        # set a timeout on the download loop
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(self.timeout * 1000)
        loop.exec_() # delay here until download finished or timeout
    
        if timer.isActive():
            # downloaded successfully
            timer.stop()
            parsed_html = self.current_html()
            self.wait(self.delay - (time() - t1))
        else:
            # did not download in time
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
        """Wait until all requests have completed up to a maximum timeout.
        Returns True if all requests complete before the timeout.
        """
        self.app.processEvents()
        deadline = time() + timeout
        manager = self.page().networkAccessManager()
        while time() < deadline and manager.active_requests:
            sleep(0)
            self.app.processEvents()
        self.app.processEvents()
        return manager.active_requests == []


    def wait_load(self, pattern, timeout=60):
        """Wait for this content to be loaded up to maximum timeout.
        Returns True if pattern was loaded before the timeout.
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
        return self.page().mainFrame().evaluateJavaScript(script).toString()


    def click(self, pattern='input'):
        """Click all elements that match the pattern.

        Uses standard CSS pattern matching: http://www.w3.org/TR/CSS2/selector.html
        Returns the number of elements clicked
        """
        es = self.find(pattern)
        for e in es:
            e.evaluateJavaScript("var evObj = document.createEvent('MouseEvents'); evObj.initEvent('click', true, true); this.dispatchEvent(evObj);")
        return len(es)


    def keys(self, pattern, text):
        """Simulate typing by focusing on elements that match the pattern and triggering key events.
        Returns the number of elements matched.
        """
        es = self.find(pattern)
        for e in es:
            e.evaluateJavaScript("this.focus()")
        self.fill(pattern, text)
        for e in es:
            for event_type in ('keydown', 'keyup', 'keypress'):
                e.evaluateJavaScript("var evObj = document.createEvent('Event'); evObj.initEvent('{}', true, true); this.dispatchEvent(evObj);".format(event_type))
        return len(es)


    def attr(self, pattern, name, value=None):
        """For the elements that match this pattern, set attribute if value is defined, else return the value.
        """
        if value is None:
            # want to get attribute
            return str(self.page().mainFrame().findFirstElement(pattern).attribute(name))
        else:
            es = self.find(pattern)
            for e in es:
                e.setAttribute(name, value)
            return len(es)


    def fill(self, pattern, value):
        """Set text of the matching form elements to value, and return the number of elements matched.
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
        """Returns the elements matching this CSS pattern.
        """
        if isinstance(pattern, basestring):
            matches = self.page().mainFrame().findAllElements(pattern).toList()
        elif isinstance(pattern, list):
            matches = pattern
        elif isinstance(pattern, QWebElement):
            matches = [pattern]
        else:
            common.logger.warning('Unknown pattern: ' + str(pattern))
            matches = []
        return matches


    def screenshot(self, output_file):
        """Take screenshot of current webpage and save results
        """
        frame = self.page().mainFrame()
        self.page().setViewportSize(frame.contentsSize())
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        common.logger.debug('saving: ' + output_file)
        image.save(output_file)




if __name__ == '__main__':
    # initiate webkit and show gui
    # once script is working you can disable the gui
    w = Browser(gui=True) 
    # load webpage
    w.get('http://duckduckgo.com')
    # fill search textbox 
    w.fill('input[id=search_form_input_homepage]', 'web scraping')
    # take screenshot of webpage
    w.screenshot('duckduckgo.jpg')
    # click search button 
    w.click('input[id=search_button_homepage]')
    # show webpage for 10 seconds
    w.wait(10)
