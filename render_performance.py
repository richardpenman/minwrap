# -*- coding: utf-8 -*-

import sys, csv, re, json, urlparse, os, urllib2, socket
socket.setdefaulttimeout(10)
from zipfile import ZipFile
from StringIO import StringIO
from time import time, sleep
#import lxml.html

import webkit
import common
from PyQt4.QtGui import QApplication
app = QApplication(sys.argv)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'


def download(url):
    status = html = None
    try:
        headers = {'User-Agent' : USER_AGENT}
        request = urllib2.Request(url, None, headers)
        response = request.urlopen(url)
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
  


b = RenderBrowser(app=app, gui=False, user_agent=USER_AGENT, delay=0, timeout=10, load_plugins=False, load_java=False)

def test_performance(website):
    bag = {}
    bag['website'] = website

    t0 = time()
    html, bag['status'] = download(website)
    bag['static_ms'] = time() - t0

    if html:
        bag['static_nodes'] = num_nodes(html)
        bag['static_requests'] = 1
        bag['static_size'] = len(html)

        for images in (False, True):
            for js in (False, True):
                key = '{}js_{}images_render'.format('' if images else 'no_', '' if js else 'no_')
                print key

                b.view.settings().setAttribute(QWebSettings.AutoLoadImages, images)
                b.view.settings().setAttribute(QWebSettings.JavascriptEnabled, js)
                b.reset()
                t0 = time()
                #b.get(website)
                b.load(url=website, num_retries=0)
                if b.wait_quiet():
                    bag[key + '_ms'] = time() - t0
                    rendered_html = b.current_html()
                    if rendered_html:
                        bag[key + '_nodes'] = num_nodes(rendered_html)
                        if bag.get(key + '_nodes') == 0:
                            return
                        bag[key + '_requests'] = b.num_requests
                        if b.reply_size == 0:
                            return
                        else:
                            bag[key + '_size'] = b.reply_size
                        print b.reply_size
                        print 'completed'
                    else:
                        print 'no html'
                        return
                else:
                    print 'no wait'
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
    for render in ('static', 'no_js_no_images_render', 'no_js_images_render', 'js_no_images_render', 'js_images_render'):
        for suffix in ('ms', 'nodes', 'requests', 'size'):
            fields.append(render + '_' + suffix)
    fp = open('RenderStats.csv', 'w')
    writer = csv.writer(fp)
    writer.writerow([field.replace('_', ' ') for field in fields])

    written = {}
    repeats = 10
    progress = True
    while progress:
        progress = False    
        for i, website in enumerate(alexa()):
            try:
                results = cache[website]
                if not results:
                    print 'skipping:', website
                    continue
            except KeyError:
                cache[website] = results = []
            if not written.get(website):
                # write previously scraped records to CSV
                written[website] = True
                for bag in results:
                    row = [bag.get(field) for field in fields]
                    writer.writerow(row)
                    fp.flush()
                    
            if len(results) < repeats:
                print website
                bag = test_performance(website)
                if bag:
                    results.append(bag)
                    cache[website] = results
                    progress = True

                    row = [bag.get(field) for field in fields]
                    writer.writerow(row)
                    fp.flush()
            if i >= 100:
                break
        

if __name__ == '__main__':
    main()
