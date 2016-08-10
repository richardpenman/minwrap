# -*- coding: utf-8 -*-

__doc__ = 'Common helper functions'

import sys, os, re, urllib, string, htmlentitydefs, urlparse
import logging, logging.handlers
try:
    import json
except ImportError:
    import simplejson as json
import sip
sip.setapi('QString', 2)
from PyQt4.QtCore import QUrl



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


def to_ascii(html):
    """Return ascii part of html
    """
    return ''.join(c for c in (html or '') if ord(c) < 128)


def to_unicode(obj, encoding='utf-8'):
    """Convert obj to unicode
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = obj.decode(encoding, 'ignore')
    return obj


def average(l):
    """Returns average of a list, or None if empty

    >>> average([])
    >>> average([1, 2, 3, 4])
    2.5
    """
    if l:
        return sum(l) / float(len(l))


def most_common(l):
    """Returns the most common element in this list

    >>> most_common([1,2,3,4,5,3,2,2,4,5,4,2,2,1,1,1,1,1,1])
    1
    """
    return max(set(l), key=l.count)


def parse_proxy(proxy):
    """Parse a proxy into its fragments
    Returns a dict with username, password, host, and port

    >>> f = parse_proxy('login:pw@66.197.208.200:8080')
    >>> f['username']
    'login'
    >>> f['password']
    'pw'
    >>> f['host']
    '66.197.208.200'
    >>> f['port']
    '8080'
    >>> f = parse_proxy('66.197.208.200')
    >>> f['username'] == f['password'] == f['port'] == ''
    True
    >>> f['host']
    '66.197.208.200'
    """
    fragments = {}
    if isinstance(proxy, basestring):
        match = re.match('((?P<username>\w+):(?P<password>\w+)@)?(?P<host>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})(:(?P<port>\d+))?', proxy)
        if match:
            groups = match.groupdict()
            fragments['username'] = groups.get('username') or ''
            fragments['password'] = groups.get('password') or ''
            fragments['host'] = groups.get('host')
            fragments['port'] = groups.get('port') or ''
    return fragments

    
def remove_tags(html):
    """Remove tags from this html string
    """
    return re.compile('<[^<]*?>').sub('', html)


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


def get_logger(output_file, level=logging.INFO, maxbytes=0, truncate=False, console_logging=True):
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
        file_mode = 'w' if truncate else 'a'
        try:
            if not maxbytes:
                file_handler = logging.FileHandler(output_file, mode=file_mode)
            else:
                file_handler = logging.handlers.RotatingFileHandler(output_file, maxBytes=maxbytes, mode=file_mode)
        except IOError:
            pass # can not write file
        else:
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(file_handler)

        if console_logging:
            console_handler = ConsoleHandler()
            console_handler.setLevel(level)
            logger.addHandler(console_handler)

    return logger

logger = get_logger('output/browser.log', maxbytes=2*1024*1024*1024)

def write_to_file(filename, content):
    """Writes a string into a file, overwriting the existing contents if any."""
    with open(filename, "w") as f:
        f.write(content)

