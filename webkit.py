__doc__ = 'Interface to qt webkit for parsing JavaScript dependent webpages'

import sys, os, re, urllib2, random, itertools
reload(sys)
sys.setdefaultencoding('utf-8')
from time import time, sleep
from datetime import datetime

# for using native Python strings
import sip
sip.setapi('QString', 2)
from PyQt4.QtGui import QApplication, QDesktopServices, QImage, QPainter, QGridLayout, QLineEdit, QWidget, QWidget, QShortcut, QKeySequence
from PyQt4.QtCore import QByteArray, QUrl, QTimer, QEventLoop, QIODevice, QObject, Qt
from PyQt4.QtWebKit import QWebFrame, QWebView, QWebElement, QWebPage, QWebSettings, QWebInspector
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkProxy, QNetworkRequest, QNetworkReply, QNetworkDiskCache

import agent
import common

"""
TODO
textbox for jquery input
    http://www.rkblog.rk.edu.pl/w/p/webkit-pyqt-rendering-web-pages/
"""


class NetworkAccessManager(QNetworkAccessManager):
    """Subclass QNetworkAccessManager for finer control network operations
    """

    def __init__(self, proxy, forbidden_extensions, allowed_regex, cache_size=100, cache_dir='.webkit_cache'):
        """
        See Browser for details of arguments
    
        cache_size:
            the maximum size of the webkit cache (MB)
        """
        super(NetworkAccessManager, self).__init__()
        # initialize the manager cache
        QDesktopServices.storageLocation(QDesktopServices.CacheLocation)
        cache = QNetworkDiskCache()
        cache.setCacheDirectory(cache_dir)
        cache.setMaximumCacheSize(cache_size * 1024 * 1024) # need to convert cache value to bytes
        self.setCache(cache)
        # and proxy
        self.setProxy(proxy)
        self.allowed_regex = allowed_regex
        self.forbidden_extensions = forbidden_extensions
        #self.sslErrors.connect(sslErrorHandler)
        self.active_requests = [] # XXX needs to be thread safe?

    def shutdown(self):
        self.setNetworkAccessible(QNetworkAccessManager.NotAccessible)
        for request in self.active_requests:
            request.abort()
            request.deleteLater()

    def setProxy(self, proxy):
        """Allow setting string as proxy
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
                proxy = None


    def createRequest(self, operation, request, data):
        if operation == self.GetOperation:
            if self.is_forbidden(request):
                # deny GET request for banned media type by setting dummy URL
                # XXX abort properly
                request.setUrl(QUrl('forbidden://localhost/'))
            else:
                common.logger.debug(common.to_unicode(request.url().toString()).encode('utf-8'))
        
        #print request.url().toString(), operation
        #XXX request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
        reply = QNetworkAccessManager.createRequest(self, operation, request, data)
        reply.error.connect(self.catch_error)
        self.active_requests.append(reply)
        reply.destroyed.connect(self.active_requests.remove)
        return reply
        
        # add Base-Url header, then we can get it from QWebView
        """if isinstance(request.originatingObject(), QWebFrame):
            try:
                reply.setRawHeader(QByteArray('Base-Url'), QByteArray('').append(request.originatingObject().page().mainFrame().baseUrl().toString()))
            except Exception, e:
                common.logger.debug(e)
        """
        custom_reply = NetworkReply(self, reply, data)
        custom_reply.orig_request = request
        if data:
            import pdb
            #pdb.set_trace()
        return custom_reply

    def is_forbidden(self, request):
        """Returns whether this request is permitted by checking URL extension and regex
        XXX head request for mime?
        """
        forbidden = False
        url = common.to_unicode(request.url().toString()).encode('utf-8')
        if self.forbidden_extensions and common.get_extension(url) in self.forbidden_extensions:
            forbidden = True
        elif re.match(self.allowed_regex, url) is None:
            forbidden = True
        return forbidden

    def catch_error(self, eid):
        """Interpret the HTTP error ID received
        """
        #self.active_requests -= 1
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


def sslErrorHandler(reply, errors): 
    print errors
    reply.ignoreSslErrors() 


class NetworkReply(QNetworkReply):
    """Override QNetworkReply so can save the original data
    """
    def __init__(self, parent, reply, data):
        super(NetworkReply, self).__init__(parent)
        self.reply = reply # reply to proxy
        if data is not None:
            self.data = data.peek(2*20)#data.readAll()
        else:
            self.data = None
        self.response = '' # contains downloaded data
        self.offset = 0 # 
        self.setOpenMode(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)
        #print dir(reply)
        
        # connect signal from proxy reply
        reply.metaDataChanged.connect(self.applyMetaData)
        reply.readyRead.connect(self.readInternal)
        reply.finished.connect(self.finished)
        reply.uploadProgress.connect(self.uploadProgress)
        reply.downloadProgress.connect(self.downloadProgress)
        reply.aboutToClose.connect(self.aboutToClose)
        reply.bytesWritten.connect(self.bytesWritten)
        reply.readChannelFinished.connect(self.readChannelFinished)
        reply.destroyed.connect(self.destroyed)
        reply.sslErrors.connect(self.sslErrors)
        reply.error.connect(self.error)
        #reply.ignoreSslErrors()

    
    def __getattribute__(self, attr):
        """Send undefined methods straight through to proxied reply
        """
        # send these attributes through to proxy reply 
        if attr in ('operation', 'request', 'url', 'abort', 'close'):#, 'isSequential'):
            value = self.reply.__getattribute__(attr)
        else:
            value = QNetworkReply.__getattribute__(self, attr)
        return value
    
    def abort(self):
        pass # qt requires that this be defined
    
    def isSequential(self):
        return True

    def applyMetaData(self):
        for header in self.reply.rawHeaderList():
            self.setRawHeader(header, self.reply.rawHeader(header))

        self.setHeader(QNetworkRequest.ContentTypeHeader, self.reply.header(QNetworkRequest.ContentTypeHeader))
        self.setHeader(QNetworkRequest.ContentLengthHeader, self.reply.header(QNetworkRequest.ContentLengthHeader))
        self.setHeader(QNetworkRequest.LocationHeader, self.reply.header(QNetworkRequest.LocationHeader))
        self.setHeader(QNetworkRequest.LastModifiedHeader, self.reply.header(QNetworkRequest.LastModifiedHeader))
        self.setHeader(QNetworkRequest.SetCookieHeader, self.reply.header(QNetworkRequest.SetCookieHeader))

        self.setAttribute(QNetworkRequest.HttpStatusCodeAttribute, self.reply.attribute(QNetworkRequest.HttpStatusCodeAttribute))
        self.setAttribute(QNetworkRequest.HttpReasonPhraseAttribute, self.reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute))
        self.setAttribute(QNetworkRequest.RedirectionTargetAttribute, self.reply.attribute(QNetworkRequest.RedirectionTargetAttribute))
        self.setAttribute(QNetworkRequest.ConnectionEncryptedAttribute, self.reply.attribute(QNetworkRequest.ConnectionEncryptedAttribute))
        self.setAttribute(QNetworkRequest.CacheLoadControlAttribute, self.reply.attribute(QNetworkRequest.CacheLoadControlAttribute))
        self.setAttribute(QNetworkRequest.CacheSaveControlAttribute, self.reply.attribute(QNetworkRequest.CacheSaveControlAttribute))
        self.setAttribute(QNetworkRequest.SourceIsFromCacheAttribute, self.reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute))
        # attribute is undefined
        #self.setAttribute(QNetworkRequest.DoNotBufferUploadDataAttribute, self.reply.attribute(QNetworkRequest.DoNotBufferUploadDataAttribute))
        self.metaDataChanged.emit()

    def bytesAvailable(self):
        """How many bytes in the buffer are available to be read
        """
        return len(self.response) - self.offset + QNetworkReply.bytesAvailable(self)

    def readInternal(self):
        """New data available to read
        """
        s = self.reply.readAll()
        self.response += s
        self.readyRead.emit()

    def readData(self, size):
        """Return up to size bytes from buffer
        """
        end = min(self.offset + size, len(self.response))
        content = self.response[self.offset:end]
        self.offset = end
        return (str(content))


class WebPage(QWebPage):
    """Override QWebPage to set User-Agent and JavaScript messages

    user_agent: 
        the User Agent to submit
    confirm:
        default response to confirm dialog boxes
    """

    def __init__(self, user_agent, confirm=True):
        super(WebPage, self).__init__()
        self.user_agent = user_agent
        self.confirm = confirm
        self.setForwardUnsupportedContent(True)
        self.unsupportedContent.connect(self.test)

    def test(self, reply):
        print 'unsupported:', reply.url().toString()

    def userAgentForUrl(self, url):
        return self.user_agent

    def javaScriptAlert(self, frame, message):
        """Override default JavaScript alert popup and print results
        """
        common.logger.debug('Alert:' + message)

    def javaScriptConfirm(self, frame, message):
        """Override default JavaScript confirm popup and print results
        """
        common.logger.debug('Confirm:' + message)
        return self.confirm

    def javaScriptPrompt(self, frame, message, default):
        """Override default JavaScript prompt popup and print results
        """
        common.logger.debug('Prompt:%s%s' % (message, default))

    def javaScriptConsoleMessage(self, message, line_number, source_id):
        """Print JavaScript console messages
        """
        common.logger.debug('Console:%s%s%s' % (message, line_number, source_id))

    def shouldInterruptJavaScript(self):
        """Disable javascript interruption dialog box
        """
        return True


class WebView(QWebView):
    def __init__(self, page, enable_plugins, load_images):
        super(WebView, self).__init__()
        self.setPage(page)
        # enable flash plugin etc.
        self.settings().setAttribute(QWebSettings.PluginsEnabled, enable_plugins)
        self.settings().setAttribute(QWebSettings.JavaEnabled, enable_plugins)
        self.settings().setAttribute(QWebSettings.AutoLoadImages, load_images)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        #self.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        #self.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)



class UrlInput(QLineEdit):
    def __init__(self, view):
        super(UrlInput, self).__init__()
        self.view = view
        # add event listener on "enter" pressed
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QUrl(self.text())
        # load url into browser frame
        self.view.load(url)


class Browser(QWidget):
    """Render webpages using webkit

    gui:
        whether to show webkit window or run headless
    user_agent:
        the user-agent when downloading content
    proxy:
        a QNetworkProxy to download through
    load_images:
        whether to download images
    forbidden_extensions
        a list of extensions to prevent downloading
    allowed_regex:
        a regular expressions of URLs to allow
    timeout:
        the maximum amount of seconds to wait for a request
    delay:
        the minimum amount of seconds to wait between requests
    """

    def __init__(self, gui=False, user_agent='Webkit', proxy=None, load_images=True, forbidden_extensions=None, allowed_regex='.*?', timeout=20, delay=5, enable_plugins=True):
        self.running = True
        self.app = QApplication(sys.argv) # must instantiate first
        super(Browser, self).__init__()
        manager = NetworkAccessManager(proxy, forbidden_extensions, allowed_regex)
        manager.finished.connect(self.finished)
        page = WebPage(user_agent or agent.rand_agent())
        page.setNetworkAccessManager(manager)
        self.view = WebView(page, enable_plugins, load_images)
        """self.inspector = QWebInspector()
        self.inspector.setPage(page)
        self.inspector.setVisible(True)"""
        self.timeout = timeout
        self.delay = delay

        grid = QGridLayout()
        self.url_input = UrlInput(self.view)
        # url_input at row 1 column 0 of our grid
        grid.addWidget(self.url_input, 1, 0)
        # browser frame at row 2 column 0 of our grid
        grid.addWidget(self.view, 2, 0)
        self.setLayout(grid)
        # add shortcuts
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence.Back, self, self.view.back)
        QShortcut(QKeySequence.Forward, self, self.view.forward)
        QShortcut(QKeySequence.Save, self, self.save)
        if gui: 
            #self.showMaximized() 
            self.show()
            self.raise_() # raise this window


    def save(self):
        html = self.current_html()
        for i in itertools.count(1):
            filename = 'data/test{}.html'.format(i)
            if not os.path.exists(filename):
                open(filename, 'w').write(common.to_unicode(html))
                print 'save', filename
                break

    def __del__(self):
        # not sure why, but to avoid seg fault need to release the QWebPage manually
        self.view.setPage(None)

    def set_proxy(self, proxy):
        self.view.page().networkAccessManager().setProxy(proxy)

    def current_url(self):
        """Return current URL
        """
        return str(self.view.url().toString())

    def current_html(self):
        """Return current rendered HTML
        """
        return unicode(self.view.page().mainFrame().toHtml())


    def get(self, url=None, html=None, num_retries=1):
        """Load given url in webkit and return html when loaded

        url:
            the URL to load
        html: 
            optional HTML to set instead of downloading
        num_retries:
            how many times to try downloading this URL
        """
        t1 = time()
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        self.view.loadFinished.connect(loop.quit)
        if url:
            if html:
                self.view.setHtml(html, QUrl(url))
            else: 
                self.view.load(QUrl(url))
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
                common.logger.debug('Timeout - retrying')
                parsed_html = self.get(url, num_retries=num_retries-1)
            else:
                common.logger.debug('Timed out')
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

        Uses standard CSS pattern matching: http://www.w3.org/TR/CSS2/selector.html
        Returns the number of elements clicked
        """
        es = self.find(pattern)
        for e in es:
            e.evaluateJavaScript("var evObj = document.createEvent('MouseEvents'); evObj.initEvent('click', true, true); this.dispatchEvent(evObj);")
        return len(es)

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
        # format xpath to webkit style
        #pattern = re.sub('["\']\]', ']', re.sub('=["\']', '=', pattern.replace('[@', '[')))
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
        #self.view.page().networkAccessManager().active_requests -= 1
        if reply.url() == self.view.url():
            self.url_input.setText(reply.url().toString())
        

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
    w.get('http://duckduckgo.com')
    # fill search textbox 
    #w.fill('input[id=search_form_input_homepage]', 'web scraping')
    # take screenshot of webpage
    #w.screenshot('duckduckgo.jpg')
    # click search button 
    #w.click('input[id=search_button_homepage]')
    w.run()
    # show webpage for 10 seconds
    #w.wait(10)
