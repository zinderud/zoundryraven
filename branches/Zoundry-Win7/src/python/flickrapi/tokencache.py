#@PydevCodeAnalysisIgnore

u'''Persistent token cache management for the Flickr API''' #$NON-NLS-1$

import os.path
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

__all__ = (u'TokenCache', u'SimpleTokenCache') #$NON-NLS-2$ #$NON-NLS-1$

class SimpleTokenCache(object):
    u'''In-memory token cache.''' #$NON-NLS-1$

    def __init__(self):
        self.token = None

    def forget(self):
        u'''Removes the cached token''' #$NON-NLS-1$

        self.token = None

class TokenCache(object):
    u'''On-disk persistent token cache for a single application.

    The application is identified by the API key used. Per
    application multiple users are supported, with a single
    token per user.
    ''' #$NON-NLS-1$

    def __init__(self, api_key, username=None):
        u'''Creates a new token cache instance''' #$NON-NLS-1$

        self.api_key = api_key
        self.username = username
        self.memory = {}

    def __get_cached_token_path(self):
        u"""Return the directory holding the app data.""" #$NON-NLS-1$
        return os.path.expanduser(os.path.join(u"~", u".flickr", self.api_key)) #$NON-NLS-2$ #$NON-NLS-1$

    def __get_cached_token_filename(self):
        u"""Return the full pathname of the cached token file.""" #$NON-NLS-1$

        if self.username:
            filename = u'auth-%s.token' % self.username #$NON-NLS-1$
        else:
            filename = u'auth.token' #$NON-NLS-1$

        return os.path.join(self.__get_cached_token_path(), filename)

    def __get_cached_token(self):
        u"""Read and return a cached token, or None if not found.

        The token is read from the cached token file.
        """ #$NON-NLS-1$

        # Only read the token once
        if self.username in self.memory:
            return self.memory[self.username]

        try:
            f = file(self.__get_cached_token_filename(), u"r") #$NON-NLS-1$
            token = f.read()
            f.close()

            return token.strip()
        except IOError:
            return None

    def __set_cached_token(self, token):
        u"""Cache a token for later use.""" #$NON-NLS-1$

        # Remember for later use
        self.memory[self.username] = token

        path = self.__get_cached_token_path()
        if not os.path.exists(path):
            os.makedirs(path)

        f = file(self.__get_cached_token_filename(), u"w") #$NON-NLS-1$
        print >>f, token
        f.close()

    def forget(self):
        u'''Removes the cached token''' #$NON-NLS-1$

        if self.username in self.memory:
            del self.memory[self.username]
        filename = self.__get_cached_token_filename()
        if os.path.exists(filename):
            os.unlink(filename)

    token = property(__get_cached_token, __set_cached_token, forget, u"The cached token") #$NON-NLS-1$
