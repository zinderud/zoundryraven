# -*- encoding: utf-8 -*-
#@PydevCodeAnalysisIgnore

u'''Call result cache.

Designed to have the same interface as the `Django low-level cache API`_.
Heavily inspired (read: mostly copied-and-pasted) from the Django framework -
thanks to those guys for designing a simple and effective cache!


.. _`Django low-level cache API`: http://www.djangoproject.com/documentation/cache/#the-low-level-cache-api
''' #$NON-NLS-1$

import threading
import time

class SimpleCache(object):
    u'''Simple response cache for FlickrAPI calls.
    
    This stores max 50 entries, timing them out after 120 seconds:
    >>> cache = SimpleCache(timeout=120, max_entries=50)
    ''' #$NON-NLS-1$

    def __init__(self, timeout=300, max_entries=200):
        self.storage = {}
        self.expire_info = {}
        self.lock = threading.RLock()
        self.default_timeout = timeout
        self.max_entries = max_entries
        self.cull_frequency = 3

    def locking(method):
        u'''Method decorator, ensures the method call is locked''' #$NON-NLS-1$

        def locked(self, *args, **kwargs):
            self.lock.acquire()
            try:
                return method(self, *args, **kwargs)
            finally:
                self.lock.release()

        return locked

    @locking
    def get(self, key, default=None):
        u'''Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        ''' #$NON-NLS-1$

        now = time.time()
        exp = self.expire_info.get(key)
        if exp is None:
            return default
        elif exp < now:
            self.delete(key)
            return default

        return self.storage[key]

    @locking
    def set(self, key, value, timeout=None):
        u'''Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        ''' #$NON-NLS-1$
        
        if len(self.storage) >= self.max_entries:
            self.cull()
        if timeout is None:
            timeout = self.default_timeout
        self.storage[key] = value
        self.expire_info[key] = time.time() + timeout

    @locking
    def delete(self, key):
        u'''Deletes a key from the cache, failing silently if it doesn't exist.''' #$NON-NLS-1$

        if key in self.storage:
            del self.storage[key]
        if key in self.expire_info:
            del self.expire_info[key]

    @locking
    def has_key(self, key):
        u'''Returns True if the key is in the cache and has not expired.''' #$NON-NLS-1$
        return self.get(key) is not None

    @locking
    def __contains__(self, key):
        u'''Returns True if the key is in the cache and has not expired.''' #$NON-NLS-1$
        return self.has_key(key)

    @locking
    def cull(self):
        u'''Reduces the number of cached items''' #$NON-NLS-1$

        doomed = [k for (i, k) in enumerate(self.storage)
                if i % self.cull_frequency == 0]
        for k in doomed:
            self.delete(k)

    @locking
    def __len__(self):
        u'''Returns the number of cached items -- they might be expired
        though.
        ''' #$NON-NLS-1$

        return len(self.storage)
