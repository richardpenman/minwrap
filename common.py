# -*- coding: utf-8 -*-
__doc__ = 'Common web scraping related functions'

import sys, os, re, urllib, string, htmlentitydefs, urlparse
import logging, logging.handlers
try:
    import json
except ImportError:
    import simplejson as json
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl

class WebScrapingError(Exception):
    pass


# known media file extensions
MEDIA_EXTENSIONS = ['ai', 'aif', 'aifc', 'aiff', 'asc', 'avi', 'bcpio', 'bin', 'c', 'cc', 'ccad', 'cdf', 'class', 'cpio', 'cpt', 'csh', 'css', 'csv', 'dcr', 'dir', 'dms', 'doc', 'drw', 'dvi', 'dwg', 'dxf', 'dxr', 'eps', 'etx', 'exe', 'ez', 'f', 'f90', 'fli', 'flv', 'gif', 'gtar', 'gz', 'h', 'hdf', 'hh', 'hqx', 'ice', 'ico', 'ief', 'iges', 'igs', 'imq', 'ips', 'ipx', 'jpe', 'jpeg', 'jpg', 'js', 'kar', 'latex', 'lha', 'lsp', 'lzh', 'm', 'man', 'me', 'mesh', 'mid', 'midi', 'mif', 'mime', 'mov', 'movie', 'mp2', 'mp3', 'mpe', 'mpeg', 'mpg', 'mpga', 'ms', 'msh', 'nc', 'oda', 'pbm', 'pdb', 'pdf', 'pgm', 'pgn', 'png', 'pnm', 'pot', 'ppm', 'pps', 'ppt', 'ppz', 'pre', 'prt', 'ps', 'qt', 'ra', 'ram', 'ras', 'raw', 'rgb', 'rm', 'roff', 'rpm', 'rtf', 'rtx', 'scm', 'set', 'sgm', 'sgml', 'sh', 'shar', 'silo', 'sit', 'skd', 'skm', 'skp', 'skt', 'smi', 'smil', 'snd', 'sol', 'spl', 'src', 'step', 'stl', 'stp', 'sv4cpio', 'sv4crc', 'swf', 't', 'tar', 'tcl', 'tex', 'texi', 'tif', 'tiff', 'tr', 'tsi', 'tsp', 'tsv', 'unv', 'ustar', 'vcd', 'vda', 'viv', 'vivo', 'vrml', 'w2p', 'wav', 'wmv', 'wrl', 'xbm', 'xlc', 'xll', 'xlm', 'xls', 'xlw', 'xml', 'xpm', 'xsl', 'xwd', 'xyz', 'zip']


def to_ascii(html):
    """Return ascii part of html
    """
    return ''.join(c for c in (html or '') if ord(c) < 128)

def to_int(s, default=0):
    """Return integer from this string

    >>> to_int('90')
    90
    >>> to_int('-90.2432')
    -90
    >>> to_int('a90a')
    90
    >>> to_int('a')
    0
    >>> to_int('a', 90)
    90
    """
    return int(to_float(s, default))

def to_float(s, default=0.0):
    """Return float from this string

    >>> to_float('90.45')
    90.45
    >>> to_float('')
    0.0
    >>> to_float('90')
    90.0
    >>> to_float('..9')
    0.0
    >>> to_float('.9')
    0.9
    >>> to_float(None)
    0.0
    >>> to_float(1)
    1.0
    """
    result = default
    if s:
        valid = string.digits + '.-'
        try:
            result = float(''.join(c for c in str(s) if c in valid))
        except ValueError:
            pass # input does not contain a number
    return result


def most_common(l):
    """Returns the most common element in this list

    >>> most_common([1,2,3,4,5,3,2,2,4,5,4,2,2,1,1,1,1,1,1])
    1
    """
    return max(set(l), key=l.count)

    
def to_unicode(obj, encoding='utf-8'):
    """Convert obj to unicode
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = obj.decode(encoding, 'ignore')
    return obj


def unescape(text, encoding='utf-8'):
    """Interpret escape characters

    >>> unescape('&lt;hello&nbsp;&amp;%20world&gt;')
    '<hello & world>'
    """
    if not text:
        return ''
    try:
        text = to_unicode(text, encoding)
    except UnicodeError:
        pass

    def fixup(m):
        text = m.group(0)
        if text[:2] == '&#':
            # character reference
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1].lower()])
            except KeyError:
                pass
        return text # leave as is
    text = re.sub('&#?\w+;', fixup, text)
    text = urllib.unquote(text)
    try:
        text = text.encode(encoding, 'ignore')
    except UnicodeError:
        pass
    
    if encoding != 'utf-8':
        return text

    # remove annoying characters
    chars = {
        '\xc2\x82' : ',',        # High code comma
        '\xc2\x84' : ',,',       # High code double comma
        '\xc2\x85' : '...',      # Tripple dot
        '\xc2\x88' : '^',        # High carat
        '\xc2\x91' : '\x27',     # Forward single quote
        '\xc2\x92' : '\x27',     # Reverse single quote
        '\xc2\x93' : '\x22',     # Forward double quote
        '\xc2\x94' : '\x22',     # Reverse double quote
        '\xc2\x95' : ' ',  
        '\xc2\x96' : '-',        # High hyphen
        '\xc2\x97' : '--',       # Double hyphen
        '\xc2\x99' : ' ',
        '\xc2\xa0' : ' ',
        '\xc2\xa6' : '|',        # Split vertical bar
        '\xc2\xab' : '<<',       # Double less than
        '\xc2\xae' : '®',
        '\xc2\xbb' : '>>',       # Double greater than
        '\xc2\xbc' : '1/4',      # one quarter
        '\xc2\xbd' : '1/2',      # one half
        '\xc2\xbe' : '3/4',      # three quarters
        '\xca\xbf' : '\x27',     # c-single quote
        '\xcc\xa8' : '',         # modifier - under curve
        '\xcc\xb1' : ''          # modifier - under line
    }
    def replace_chars(match):
        char = match.group(0)
        return chars[char]

    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)

   
def get_extension(url):
    """Return extension from given URL

    >>> get_extension('hello_world.JPG')
    'jpg'
    >>> get_extension('http://www.google-analytics.com/__utm.gif?utmwv=1.3&utmn=420639071')
    'gif'
    """
    return os.path.splitext(urlparse.urlsplit(url).path)[-1].lower().replace('.', '')


def get_domain(url):
    """Extract the domain from the given URL

    >>> get_domain('http://www.google.com.au/tos.html')
    'google.com.au'
    >>> get_domain('www.google.com')
    'google.com'
    """
    m = re.compile(r"^.*://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})").search(url)
    if m:
        # an IP address
        return m.groups()[0]
    
    suffixes = 'ac', 'ad', 'ae', 'aero', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'arpa', 'as', 'asia', 'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'biz', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cat', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'com', 'coop', 'cr', 'cu', 'cv', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'edu', 'ee', 'eg', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gov', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'info', 'int', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jobs', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mg', 'mh', 'mil', 'mk', 'ml', 'mm', 'mn', 'mo', 'mobi', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'name', 'nc', 'ne', 'net', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'org', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'pro', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'st', 'su', 'sv', 'sy', 'sz', 'tc', 'td', 'tel', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'xn', 'ye', 'yt', 'za', 'zm', 'zw'
    url = re.sub('^.*://', '', url).partition('/')[0].lower()
    domain = []
    for section in url.split('.'):
        if section in suffixes:
            domain.append(section)
        else:
            domain = [section]
    return '.'.join(domain)


def same_domain(url1, url2):
    """Return whether URLs belong to same domain
    
    >>> same_domain('http://www.google.com.au', 'code.google.com')
    True
    >>> same_domain('http://www.facebook.com', 'http://www.myspace.com')
    False
    """
    server1 = get_domain(url1)
    server2 = get_domain(url2)
    return server1 and server2 and (server1 in server2 or server2 in server1)


def read_list(file):
    """Return file as list if exists
    """
    l = []
    if os.path.exists(file):
        l.extend(open(file).read().splitlines())
    else:
        logger.debug('%s not found' % file)
    return l


def build_opener(cj=None):
    if cj is None:
        cj = cookielib.CookieJar()
    return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


class ConsoleHandler(logging.StreamHandler):
    """Log to stderr for errors else stdout
    """
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = None

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.stream = sys.stderr
        else:
            self.stream = sys.stdout
        logging.StreamHandler.emit(self, record)


def list_to_qs(items):
    """Convert these items into a string of data
    """
    if items:
        url = QUrl('')
        url.setEncodedQueryItems(items)
        return str(url.toString())[1:]
    else:
        return ''


def get_logger(output_file, level=logging.INFO, maxbytes=0):
    """Create a logger instance

    output_file:
        file where to save the log
    level:
        the minimum logging level to save
    maxbytes:
        the maxbytes allowed for the log file size. 0 means no limit.
    """
    logger = logging.getLogger(output_file)
    # avoid duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        try:
            if not maxbytes:
                file_handler = logging.FileHandler(output_file)
            else:
                file_handler = logging.handlers.RotatingFileHandler(output_file, maxBytes=maxbytes)
        except IOError:
            pass # can not write file
        else:
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(file_handler)

        console_handler = ConsoleHandler()
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    return logger
logger = get_logger('.ajax.log', maxbytes=2*1024*1024*1024)
