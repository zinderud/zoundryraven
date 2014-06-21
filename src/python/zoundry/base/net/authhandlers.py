from zoundry.base.util.text.textutil import getSafeString
import sha
import time
import base64
from zoundry.base.util.text.unicodeutil import convertToUtf8


#======================================
# Singleton to authetication manager.
#======================================

def ZAuthenticationManager():
    return _ZAuthenticationManager.getInstance()

class _ZAuthenticationManager:
    # --- singleton'ize
    _instance = None
    def getInstance():
        if not _ZAuthenticationManager._instance:
            # Create the account manager
            _ZAuthenticationManager._instance = _ZAuthenticationManager()
        return _ZAuthenticationManager._instance
    # --- static'ize
    getInstance = staticmethod(getInstance)
    def __init__(self):
        self.logger = None
        # list of tuples (scheme, handlerClass)
        self.handlerClases = []
        # map containing previously authorized header values.
        self.headerMap = {}
        self.registerHandler(ZHttpBasicAuthHandler.SCHEME, ZHttpBasicAuthHandler)
        self.registerHandler(ZXWsseUsernameAuthHandler.SCHEME, ZXWsseUsernameAuthHandler)
        
    def setLogger(self, logger):
        self.logger = logger
        
    def _debug(self, s):
        if self.logger:
            self.logger.debug(s)

    def registerHandler(self, scheme, handlerClazz):
        rval = False
        scheme = getSafeString(scheme).lower()
        if scheme and handlerClazz:
            newval = (scheme, handlerClazz)
            #if scheme already exist then replace id can be replaced
            for idx in range( len(self.handlerClases) ):
                (tmpScheme, tmpClazz) = self.handlerClases[idx] #@UnusedVariable
                if tmpScheme == scheme:
                    self.handlerClases[idx] = newval
                    rval = True
                    break
            # append new one if not replaced
            if not rval:
                self.handlerClases.append(newval)
                rval = True
        return rval

    def _listHandlerClasses(self):
        rval = []
        for (scheme, clazz) in self.handlerClases: #@UnusedVariable
            rval.append(clazz)
        return rval
    
    def _getHandlerClass(self, scheme):
        clazz = None
        scheme = getSafeString(scheme).lower()
        for (tmpScheme, tmpClazz) in self.handlerClases: #@UnusedVariable
            if tmpScheme == scheme:
                clazz = tmpClazz
                break
        return clazz

    def supportsScheme(self, scheme):
        rval = self._getHandlerClass(scheme) is not None
        return rval

    def getSchemeFromResponse(self, httpResp):
        rval = None
        for clazz in self._listHandlerClasses():
            handler = clazz()
            if handler.supported(httpResp):
                rval = handler.getScheme()
                break
        return rval

    def isInstalled(self, key):
        return self.headerMap.has_key(key)

    def getAuthHeaders(self, key):
        # return name/value map need for www request headers. (typically, the authorization header)
        rVal = None
        if self.headerMap.has_key(key):
            rVal = self.headerMap[key]
        else:
            rVal = {}
        return rVal

    def uninstall(self, key):
        if self.headerMap.has_key(key):
            del self.headerMap[key]

    def install(self, authType, key, httpResp, url, username, password):
        # Note: httpResp maybe None.
        if not authType:
            self._debug(u"Cannot install authentication handler for authtype=None") #$NON-NLS-1$
            return
        elif not self.supportsScheme(authType):
            self._debug(u"Cannot install unsupported authentication handler scheme %s"  % authType) #$NON-NLS-1$
            return
        if not key:
            self._debug(u"Cannot install %s authentication handler for key %s" % key) #$NON-NLS-1$
            return

        self._debug(u"Installing authentication handler type %s for %s" %(authType, url)) #$NON-NLS-1$

        clazz = self._getHandlerClass(authType)
        handler = clazz()
        handler.setLogger(self.logger)
        try:
            headers = handler.handleRequest(httpResp, url, username, password)
            self.headerMap[key] = headers
        except Exception, e:
            raise e

#======================================
# Base class for a auth handler
#======================================
class ZAuthHandler:
    def __init__(self, scheme):
        self.scheme = scheme
        self.logger = None
        
    def setLogger(self, logger):
        self.logger = logger

    def getScheme(self):
        return self.scheme

    def _debug(self, s): #@UnusedVariable
        if self.logger:
            msg = u"AuthHandler[%s]: %s" % (self.getScheme(), s) #$NON-NLS-1$
            self.logger.debug(msg)
            
    # Gets a timestamp.
    def _getTimeStamp(self):
        u"Gets a timestamp." #$NON-NLS-1$
        return time.strftime(str(u"%Y-%m-%dT%H:%M:%SZ"), time.gmtime()) #$NON-NLS-1$
    # end _getTimeStamp()

    # Creates/gets an Nonce
    def _getNonce(self, tstamp):
        u"Creates an 'nonce'." #$NON-NLS-1$
        private = u"Just some private text" #$NON-NLS-1$
        timestamp = time.strftime(u"%Y-%m-%dT%H:%M:%SZ", tstamp) #$NON-NLS-1$
        noncePlain = u"%s %s" % (timestamp, sha.new(u"%s:%s" % (timestamp, private)).hexdigest()) #$NON-NLS-2$ #$NON-NLS-1$
        return base64.encodestring(noncePlain).replace(u"\n", u"") #$NON-NLS-2$ #$NON-NLS-1$
    # end _getNonce()

    def _getWWWAuthenticate(self, httpResp):
        wwwauth = getSafeString( httpResp.getheader(u"WWW-Authenticate") )  #$NON-NLS-1$
        return wwwauth
    # end  _getWWWAuthenticate

    def supported(self, httpResp):    #@UnusedVariable
        u"""Returns true if the handler supports the authentication scheme requested on the www-Authenticate header.""" #$NON-NLS-1$
        return False

    def handleRequest(self, httpResp, url, username, password): #@UnusedVariable
        u"""Creates the necessary authentication headers and returns the header map.""" #$NON-NLS-1$
        rVal = {}
        return rVal

    def handleResponse(self, httpResp, url, username, password): #@UnusedVariable
        u"""Creates the necessary authentication headers and returns the header map.""" #$NON-NLS-1$
        rVal = {}
        return rVal

#======================================
# WWW BASIC authentication
#======================================
class ZHttpBasicAuthHandler(ZAuthHandler):
    SCHEME = u"basic" #$NON-NLS-1$
    def __init__(self):
        ZAuthHandler.__init__(self, ZHttpBasicAuthHandler.SCHEME)

    def supported(self, httpResp):
        wwwauth = self._getWWWAuthenticate(httpResp)
        return wwwauth.lower().startswith(u"basic ") #$NON-NLS-1$

    def handleRequest(self, httpResp, url, username, password): #@UnusedVariable
        rVal = {}
        userPass = u"%s:%s" % (username, password) #$NON-NLS-1$
        userPass = convertToUtf8(userPass)
        auth = u'BASIC %s' % base64.encodestring(userPass) #$NON-NLS-1$
        rVal[u"Authorization"] = auth.rstrip() #$NON-NLS-1$
        return rVal

#======================================
# X-WSSE Username token authentication
#======================================

class ZXWsseUsernameAuthHandler(ZAuthHandler):
    SCHEME = u"xwsse" #$NON-NLS-1$

    def __init__(self):
        ZAuthHandler.__init__(self, ZXWsseUsernameAuthHandler.SCHEME)

    # Creates the Atom API authorization header.
    def _createWsseAuth(self, username, password):
        u"Creates the Atom API authorization header." #$NON-NLS-1$
        tstamp = time.gmtime()
        nonce = self._getNonce(tstamp)
        created = time.strftime(u"%Y-%m-%dT%H:%M:%SZ", tstamp) #$NON-NLS-1$
        pwdDigest = base64.encodestring(sha.new(nonce + created + password).digest()).replace(u"\n", u"") #$NON-NLS-2$ #$NON-NLS-1$
        authorizationHeader = u'UsernameToken Username="%s", PasswordDigest="%s", Created="%s", Nonce="%s"' % (username, pwdDigest, created, nonce) #$NON-NLS-1$
        return authorizationHeader

    def supported(self, httpResp):
        wwwauth = self._getWWWAuthenticate(httpResp)
        return wwwauth.lower().startswith(u"xwsse ") or wwwauth.lower().startswith(u"wsse ") #$NON-NLS-1$ #$NON-NLS-2$

    def handleRequest(self, httpResp, url, username, password): #@UnusedVariable
        rVal = {}
        auth = self._createWsseAuth(username, password)
        rVal[u"Authorization"] = u'WSSE profile="UsernameToken"' #$NON-NLS-2$ #$NON-NLS-1$
        rVal[u"X-WSSE"] = auth #$NON-NLS-1$
        return rVal

