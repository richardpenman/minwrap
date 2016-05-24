# -*- coding: utf-8 -*-

import sys, csv, re, json, urlparse, os, urllib2, socket
socket.setdefaulttimeout(10)
from zipfile import ZipFile
from StringIO import StringIO
from time import time
import lxml.html

import webkit
import common
from PyQt4.QtGui import QApplication
app = QApplication(sys.argv)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'


def download(url):
    status = html = None
    try:
        response = urllib2.urlopen(url)
        status = response.code
        html = response.read()
    except Exception as e:
        print e
    return html, status


def alexa():
    """top 1 million URL's will be stored in this list
    """
    alexa_file = 'top-1m.csv.zip'
    if os.path.exists(alexa_file) and os.path.getsize(alexa_file) > 0:
        zipped_data = open(alexa_file, 'rb').read()
    else:
        print 'Downloading Alexa file'
        zipped_data, _ = download('http://s3.amazonaws.com/alexa-static/top-1m.csv.zip')
        open(alexa_file, 'wb').write(zipped_data)
    with ZipFile(StringIO(zipped_data)) as zf:
        csv_filename = zf.namelist()[0]
        for _, website in csv.reader(zf.open(csv_filename)):
            if website.endswith('.com'):
                yield 'http://' + website


from PyQt4.QtWebKit import QWebSettings
  

class RenderBrowser(webkit.Browser):
    def __init__(self, **argv):
        """Extend webkit.Browser to add some specific functionality for abstracting AJAX requests
        """
        super(RenderBrowser, self).__init__(**argv)
        self.reset()

    def reset(self):
        self.num_requests = 0
        self.reply_size = 0

    def finished(self, reply):
        self.num_requests += 1
        self.reply_size += len(reply.content)


from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from PyQt4.QtNetwork import *
  
class RenderBrowser2(QWebView):  
    def __init__(self, app):  
        QWebView.__init__(self)  
        self.manager = NetworkAccessManager()
        self.page().setNetworkAccessManager(self.manager)
        self.manager.finished.connect(self._replyFinished)
        self.app = app
 
    def get(self, url):
        self.num_requests = self.reply_size = 0
        self.loadFinished.connect(self._loadFinished)  
        self.load(QUrl(url))  
        self.app.exec_()  
  
    def _loadFinished(self, result):  
        self.app.quit()  

    def _replyFinished(self, reply):
        self.num_requests += 1
        #print 'raw:', reply.rawHeader('Content-Length') or 0
        self.reply_size += reply.content_size#int(reply.rawHeader('Content-Length') or 0)


class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self):
        super(NetworkAccessManager, self).__init__()

    def createRequest(self, operation, request, post):
        """Override creating a network request
        """
        reply = QNetworkAccessManager.createRequest(self, operation, request, post)
        #reply.error.connect(self.catch_error)
        #self.active_requests.append(reply)
        #reply.destroyed.connect(self.remove_inactive)
        # save reference to original request
        #reply.orig_request = request
        #reply.data = self.parse_data(post)
        reply.content_size = 0
        def save_content(r):
            # save copy of reply content before is lost
            def _save_content():
                r.content_size += len(r.peek(r.size()))
            return _save_content
        reply.readyRead.connect(save_content(reply))
        return reply



b = RenderBrowser(app=app, gui=False, user_agent=USER_AGENT, delay=0, timeout=10, load_plugins=False, load_java=False)
#b = RenderBrowser2(app)
def test_n_times(website, num_retries):
    download(website)
    for _ in range(num_retries):
        bag = test_performance(website)
        if bag:
            print bag
            yield bag


def test_performance(website):
    bag = {}
    bag['website'] = website

    t0 = time()
    html, bag['status'] = download(website)

    if html:
        tree = lxml.html.fromstring(html)
        bag['lxml_ms'] = time() - t0
        bag['lxml_nodes'] = num_nodes(html)
        bag['lxml_requests'] = 1
        bag['lxml_size'] = len(html)

        for images in (False, True):
            for js in (False, True):
                key = '{}js_{}images_render'.format('' if images else 'no_', '' if js else 'no_')
                print key

                b.view.settings().setAttribute(QWebSettings.AutoLoadImages, images)
                b.view.settings().setAttribute(QWebSettings.JavascriptEnabled, js)
                b.reset()
                t0 = time()
                #b.get(website)
                rendered_html = b.load(url=website, num_retries=0)
                bag[key + '_ms'] = time() - t0
                #rendered_html = common.to_unicode(b.page().mainFrame().toHtml())
                if rendered_html:
                    bag[key + '_nodes'] = num_nodes(rendered_html)
                    bag[key + '_requests'] = b.num_requests
                    bag[key + '_size'] = b.reply_size
                    print b.reply_size
                    print 'completed'
                b.wait_quiet()
                if not rendered_html:
                    return
        return bag
    else:
        print 'empty'


def num_nodes(html):
    return len(re.findall('<\w+', html))
    """try:
        tree = lxml.html.fromstring(html)
    except Exception as e:
        print e
        return len(re.findall('<\w+', html))
    else:
        print len(re.findall('<\w+', html)), tree.xpath('count(//*)')
        return tree.xpath('count(//*)')
    """
 
def main():
    from webscraping import pdict
    cache = pdict.PersistentDict('.render.db')

    fields = ['website', 'status']
    for render in ('lxml', 'no_js_no_images_render', 'no_js_images_render', 'js_no_images_render', 'js_images_render'):
        for suffix in ('ms', 'nodes', 'requests', 'size'):
            fields.append(render + '_' + suffix)
    fp = open('RenderStats.csv', 'w')
    writer = csv.writer(fp)
    writer.writerow([field.replace('_', ' ') for field in fields])

    for i, website in enumerate(alexa()):
        if website not in cache:# or not cache[website]:
            print website
            cache[website] = []
            bags = [bag for bag in test_n_times(website, 10)]
            cache[website] = bags
        else:
            bags = cache[website]
            #if not bag.get('no_js_images_render_size'):
            #    print 'deleting:', website
            #    del cache[website]

        for bag in bags:
            valid = True
            for render in ('lxml', 'no_js_no_images_render', 'no_js_images_render', 'js_no_images_render', 'js_images_render'):
                if not bag.get(render + '_nodes') or not bag.get(render + '_size'):
                    valid = False
                    #print 'deleting:', website
                    #del cache[website]
                    break
            if valid:
                row = [bag.get(field) for field in fields]
                writer.writerow(row)
            fp.flush()
        if i >= 3:
            break
    

if __name__ == '__main__':
    main()
