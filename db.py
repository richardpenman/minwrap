__doc__ = """
pdict has a dictionary like interface and a sqlite backend
It uses pickle to store Python objects and strings, which are then compressed
Multithreading is supported
"""

import os
import zlib
import threading
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    # gdbm produces best performance
    import gdbm as dbm
except ImportError:
    import anydbm as dbm



class DbmDict:
    """Key value database built on the the dbm module, 
    which allows lazy writes instead of a transaction for each write

    filename: where to store sqlite database. Uses in memory by default.
    compress_level: between 1-9 (in my test levels 1-3 produced a 1300kb file in ~7 seconds while 4-9 a 288kb file in ~9 seconds)

    >>> filename = 'dbm.db'
    >>> cache = DbmDict(filename)
    >>> url = 'http://google.com/abc'
    >>> html = '<html>abc</html>'
    >>>
    >>> url in cache
    False
    >>> cache[url] = html
    >>> url in cache
    True
    >>> cache[url] == html
    True
    >>> cache.meta(url)
    {}
    >>> cache.meta(url, 'meta')
    >>> cache.meta(url)
    'meta'
    >>> urls = list(cache)
    >>> del cache[url]
    >>> url in cache
    False
    >>> os.remove(filename)
    """
    def __init__(self, filename='.dbm.db', compress_level=6):
        """initialize a new PersistentDict with the specified database file.
        """
        self.filename, self.compress_level = filename, compress_level
        self.db = dbm.open(filename, 'c')
        self.lock = threading.Lock()


    def __copy__(self):
        """make a copy of current cache settings
        """
        return DbmDict(filename=self.filename, compress_level=self.compress_level)


    def __contains__(self, key):
        """check the database to see if a key exists
        """
        with self.lock:
            return self.db.has_key(key)
   

    def __iter__(self):
        """iterate each key in the database
        """
        with self.lock:
            key = self.db.firstkey()
        while key != None:
            yield key
            with self.lock:
                key = self.db.nextkey(key)
           

    def __getitem__(self, key):
        """return the value of the specified key or raise KeyError if not found
        """
        with self.lock:
            value = self.db[key]
        return self.deserialize(value)


    def __delitem__(self, key):
        """remove the specifed value from the database
        """
        with self.lock:
            del self.db[key]


    def __setitem__(self, key, value):
        """set the value of the specified key
        """
        value = self.serialize(value)
        with self.lock:
            self.db[key] = value


    def serialize(self, value):
        """convert object to a compressed pickled string to save in the db
        """
        return zlib.compress(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL), self.compress_level)
   

    def deserialize(self, value):
        """convert compressed pickled string from database back into an object
        """
        if value:
            return pickle.loads(zlib.decompress(value))


    def get(self, key, default=None):
        """Get data at key and return default if not defined
        """
        try:
            value = self[key]
        except KeyError:
            value = default
        return value


    def meta(self, key, value=None, prefix='__meta__'):
        """Get / set meta for this value

        if value is passed then set the meta attribute for this key
        if not then get the existing meta data for this key
        """
        key = prefix + key
        if value is None:
            # get the meta data
            return self.get(key, {})
        else:
            # set the meta data
            self[key] = value


    def clear(self):
        """Clear all cached data
        """
        for key in self:
            del self[key]


    def merge(self, db, override=False):
        """Merge this databases content
        override determines whether to override existing keys
        """
        for key in db:
            if override or key not in self:
                self[key] = db[key]
