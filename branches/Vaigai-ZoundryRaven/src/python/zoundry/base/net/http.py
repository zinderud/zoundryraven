import zlib
import gzip
import StringIO
from zoundry.base.util.urlutil import urlencode
import base64
import stat
from zoundry.base.net.contrib.urllib2_file import send_data
from string import lower
from urlparse import urlparse
from urlparse import urlsplit
from zoundry.base.exceptions import ZException
from zoundry.base.net.authhandlers import ZAuthenticationManager
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.zdom.dom import ZDom
import httplib
import os
import re
import string
import mimetypes
import mimetools


# ------------------------------------------------------------------------------
# Constants for splitUrl()
#
# Pattern for splitting a URL into its component parts.
# Example URL:
#      http://www.zoundry.com:81/path/to/file.exe?query=12&blah=1
# Result Tuple:
#      ('http://', 'http', 'www.zoundry.com', ':81', '81', '/path/to/file.exe', '?', 'query=12&blah=1')
# Tuple: (dummy, scheme, host, dummy, port, path, dummy, query)
# Keys:
#   2 = scheme
#   3 = domain
#   5 = port
#   6 = path
#   8 = query
# ------------------------------------------------------------------------------
#                   (http://)    (host)    (port)    (path)       (query)
URL_PATTERN_STR = r"(([^:]+)://)?([^/:?]+)(:([0-9]+))?([^?]*)([?])?(.*)$" #$NON-NLS-1$
URL_PATTERN = re.compile(URL_PATTERN_STR)

DEFAULT_PORT_MAP = {
    u"http" : 80,  #$NON-NLS-1$
    u"https" : 443,  #$NON-NLS-1$
    u"ftp" : 21 #$NON-NLS-1$
}


# ------------------------------------------------------------------------------
# Constants for content-type manipulation functions.
# ------------------------------------------------------------------------------
META_CT_TAG_PATTERN = u'(<meta[^>.]*http-equiv\s*=\s*"Content-Type"[^>.]*\/>)' #$NON-NLS-1$
META_CT_TAG_RE = re.compile(META_CT_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

META_CT_ATTR_PATTERN = u'(.*content\s*=\s*"?)([^"]*)(["\s].*>)(.*)' #$NON-NLS-1$
META_CT_ATTR_RE = re.compile(META_CT_ATTR_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# eg: text/html; charset=utf-8
CT_VALUE1_PATTERN = u"""(\s*)([\w^/]+)/([\w^\+\s\*]+)(\s*;?\s*)(charset\s*=\s*['"]?)([^\s^"']+)(['"]?\s*)""" #$NON-NLS-1$
CT_VALUE1_RE = re.compile(CT_VALUE1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# eg: text/html;
CT_VALUE2_PATTERN = u'(\s*)([\w^/]+)/([\w^\+\s\*]+)(\s*\;?)' #$NON-NLS-1$
CT_VALUE2_RE = re.compile(CT_VALUE2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


# ------------------------------------------------------------------------------
# Constants for HTTP connection classes
# ------------------------------------------------------------------------------
IE_ACCEPT = u"text/html, text/plain, text/xml, image/gif, image/x-xbitmap, image/x-icon,image/jpeg, image/pjpeg, application/vnd.ms-powerpoint, application/vnd.ms-excel, application/msword, */*" #$NON-NLS-1$
IE_LANGUAGE = u"en-us" #$NON-NLS-1$
IE_USERAGENT = u"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;)" #$NON-NLS-1$

DEFAULT_HEADERS = { u"Accept" : IE_ACCEPT, #$NON-NLS-1$
                    u"Accept-Language" : IE_LANGUAGE, #$NON-NLS-1$
                    #u"Accept-Encoding" : "gzip,deflate", #$NON-NLS-1$
                    u"User-Agent" : IE_USERAGENT } #$NON-NLS-1$

HTTP_GET = u"GET" #$NON-NLS-1$
HTTP_POST = u"POST" #$NON-NLS-1$
HTTP_PUT = u"PUT" #$NON-NLS-1$
HTTP_DELETE = u"DELETE" #$NON-NLS-1$
HTTP_CONNECT = u"CONNECT" #$NON-NLS-1$

# Gobal variables for proxy
_gHTTP_PROXY_ENABLED =False
_gHTTP_PROXY_HOST = u"localhost" #$NON-NLS-1$
_gHTTP_PROXY_PORT = 8080
_gHTTP_PROXY_USERNAME = None
_gHTTP_PROXY_PASSWORD = None
#---------------------------------
# Accessor to http proxy settings
#---------------------------------
class ZHttpProxyConfiguration:

    def isProxyEnabled(self):
        global _gHTTP_PROXY_ENABLED, _gHTTP_PROXY_HOST, _gHTTP_PROXY_PORT
        return _gHTTP_PROXY_ENABLED and _gHTTP_PROXY_HOST and _gHTTP_PROXY_PORT
    # end isProxyEnabled()
    
    def setEnable(self, enable):
        global _gHTTP_PROXY_ENABLED
        _gHTTP_PROXY_ENABLED = enable
    # end setEnable()
    
    def setHost(self, host):
        global _gHTTP_PROXY_HOST
        _gHTTP_PROXY_HOST = host
    # end setHost
    
    def getHost(self):
        global _gHTTP_PROXY_HOST
        return _gHTTP_PROXY_HOST
    # end getHost    
    
    def setPort(self, port):
        global _gHTTP_PROXY_PORT
        _gHTTP_PROXY_PORT  = port
    # end set port  
    
    def getPort(self):
        global _gHTTP_PROXY_PORT
        return _gHTTP_PROXY_PORT
    # end get port       
    
    def getProxyUrl(self):
        global _gHTTP_PROXY_HOST, _gHTTP_PROXY_PORT
        return u"http://%s:%d" % (_gHTTP_PROXY_HOST, _gHTTP_PROXY_PORT) #$NON-NLS-1$
    # end getProxyUrl()
    
    def setProxyAuthorization(self, username, password):
        global _gHTTP_PROXY_USERNAME, _gHTTP_PROXY_PASSWORD
        _gHTTP_PROXY_USERNAME = username
        _gHTTP_PROXY_PASSWORD = password
    # end setProxyAuthorization
    
    def hasAuthorization(self):
        global _gHTTP_PROXY_USERNAME, _gHTTP_PROXY_PASSWORD
        return _gHTTP_PROXY_USERNAME and _gHTTP_PROXY_PASSWORD
    # end hasAuthorization()
    
    def getAuthorization(self):
        if self.hasAuthorization():
            global _gHTTP_PROXY_USERNAME, _gHTTP_PROXY_PASSWORD
            userPass = u"%s:%s" % (_gHTTP_PROXY_USERNAME, _gHTTP_PROXY_PASSWORD) #$NON-NLS-1$
            userPass = convertToUtf8(userPass)
            auth = u'BASIC %s' % base64.encodestring(userPass) #$NON-NLS-1$
            return auth            
        else:
            None
    # end getAuthorization()

    # end hasAuthorization()
# end ZHttpProxyConfiguration

#---------------------------------
# generate mime boundry string
#---------------------------------
def generateMimeMultipartBoundry():
    return mimetools.choose_boundary()
# end generateMimeMultipartBoundry

#---------------------------------
# guess content type.
#---------------------------------
def getContentTypeFromFilename(filename):
    return mimetypes.guess_type(filename)[0] or u'application/octet-stream' #$NON-NLS-1$
# end getContentTypeFromFilename


# ------------------------------------------------------------------------------
# The http connection factory is responsible for creating the HTTP connection object given
# a URL, method, body, and headers.  It will also allow us to hook in proxy support at some
# point.
# ------------------------------------------------------------------------------
class ZHttpConnectionFactory:

    def __init__(self):
        pass
    # end __init__()

    def createHttpConnection(self, url = None, method = HTTP_GET, body = None, headers = DEFAULT_HEADERS):
        proxyConfig = ZHttpProxyConfiguration()
        if proxyConfig.isProxyEnabled():
            # connect to proxy server instead of url.
            (conn, scheme, netloc, path, query, fragment) = self._internalCreateHttpLibConnection( proxyConfig.getProxyUrl() ) #@UnusedVariable
            if not self._setupSSLTunnel(conn, proxyConfig, url):
                # standard http auth (non-ssl)
                if proxyConfig.hasAuthorization():
                    headers[u"Proxy-authorization"] = proxyConfig.getAuthorization() #$NON-NLS-1$            
            # change path to be teh dest URL
            path = url
        else:
            (conn, scheme, netloc, path, query, fragment) = self._internalCreateHttpLibConnection(url) #@UnusedVariable
        if body and method and path:
            conn.request(method, path, body, headers)
        elif method and path:
            conn.request(method, path, headers = headers)
        return conn
    # end createHttpConnection()

    def createRawConnection(self, url, method = HTTP_GET):
        proxyConfig = ZHttpProxyConfiguration()
        if proxyConfig.isProxyEnabled():
            (conn, scheme, netloc, path, query, fragment) = self._internalCreateHttpLibConnection( proxyConfig.getProxyUrl() ) #@UnusedVariable
            if not self._setupSSLTunnel(conn, proxyConfig, url):
                # standard http auth (non-ssl)
                if proxyConfig.hasAuthorization():
                    conn.putheader(u"Proxy-authorization", proxyConfig.getAuthorization()) #$NON-NLS-1$
            conn.putrequest(method, url)
        else:
            (conn, scheme, netloc, path, query, fragment) = self._internalCreateHttpLibConnection(url) #@UnusedVariable
            conn.putrequest(method, path)
        return conn
    # end _createConnection
    
    def _setupSSLTunnel(self, connection, proxyConfig, destURL): 
        # set up SSL tunnelling if needed and return true else return false       
        (scheme, netloc, path, query, fragment) = urlsplit(destURL, u"http") #$NON-NLS-1$ @UnusedVariable
        if scheme == u"https": #$NON-NLS-1$
            self._internalCreateSSLTunnel(connection, proxyConfig, netloc)
            return True
        else:
            return False
    # end _setupSSLTunnel()
    
    def _internalCreateSSLTunnel(self, connection, proxyConfig, desHostColonPort):
        import socket
        # desHostColonPort => host:port
        desHostPort = desHostColonPort.split(u":") #$NON-NLS-1$
        host = desHostPort[0]
        port = u"443" #$NON-NLS-1$
        if len(desHostPort) == 2:
            port = desHostPort[1]
            
        proxy_authorization = u"" #$NON-NLS-1$
        if proxyConfig.hasAuthorization():
            proxy_authorization = u"Proxy-authorization: %s\r\n" % proxyConfig.getAuthorization() #$NON-NLS-1$
        # based on John Nielsen's code snippet @ http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/301740
        proxy_user_agent= u'User-Agent: %s\r\n' % IE_USERAGENT  #$NON-NLS-1$
        proxy_connect= u'CONNECT %s:%s HTTP/1.0\r\n' % (host, port) #$NON-NLS-1$
        proxy_tunnel_request = proxy_connect + proxy_authorization + proxy_user_agent + u'\r\n' #$NON-NLS-1$

        #now connect, very simple recv and error checking
        proxy= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        proxy.connect( (proxyConfig.getHost(),proxyConfig.getPort()) )
        proxy.sendall(proxy_tunnel_request)
        response=proxy.recv(8192) 
        status=response.split()[1]
        if status!=str(200):
            ex = ZException(u"SSL Tunnel handshake error: %s" % unicode(status) ) #$NON-NLS-1$
            raise ex
        #trivial setup for ssl socket
        ssl = socket.ssl(proxy, None, None)
        sock = httplib.FakeSocket(proxy, ssl)                        
        connection.sock = sock
    # end _internalCreateSSLTunnel()

    def _internalCreateHttpLibConnection(self, url):
        (scheme, netloc, path, query, fragment) = urlsplit(url, u"http") #$NON-NLS-1$ @UnusedVariable
        if not path:
            path = u"/" #$NON-NLS-1$
        if query:
            path = u"%s?%s" % (path, query) #$NON-NLS-1$

        conn = None
        if (scheme == u"https"): #$NON-NLS-1$
            conn = httplib.HTTPSConnection(netloc)
        else:
            conn = httplib.HTTPConnection(netloc)
        return (conn, scheme, netloc, path, query, fragment)
    # end _internalCreateHttpLibConnection

# end ZHttpConnectionFactory()


# ------------------------------------------------------------------------------
# A cookie registry.  This class is used by the HTTP connection classes to manage a list of
# cookies that have been set by the HTTP response.  If the same registry is used for multiple
# HTTP calls, then cookies set by the response will be re-sent in subsequent requests.
# ------------------------------------------------------------------------------
class ZCookieReg:

    def __init__(self):
        self.cookies = []
    # end __init__()

    def addCookie(self, cookie):
        self.removeCookie(cookie)
        self.cookies.append(cookie)
    # end addCookie()

    def removeCookie(self, cookie):
        if self.cookies.count(cookie) > 0:
            self.cookies.remove(cookie)
    # end removeCookie()

    def addCookies(self, cookies):
        for cookie in cookies:
            self.addCookie(cookie)
    # end addCookies()

    def getCookiesForURL(self, url):
        (scheme, host, port, path, filename, query, url) = splitUrl(url) #@UnusedVariable
        if path is None:
            path = u"" #$NON-NLS-1$
        cookies = self.getCookiesForDomain(host)
        rval = []
        for cookie in cookies:
            if path.startswith(cookie.getPath()):
                rval.append(cookie)
        return rval
    # end getCookiesForURL()

    def getCookieStrForURL(self, url):
        cookies = self.getCookiesForURL(url)
        thecookies = []
        for cookie in cookies:
            thecookies.append(u"%s=%s" % cookie.getKeyValue()) #$NON-NLS-1$
        return string.join(thecookies, u", ") #$NON-NLS-1$
    # end getCookieStrForURL()

    def getCookiesForDomain(self, domain):
        rval = []
        for cookie in self.cookies:
            if cookie.getDomain() and domain.endswith(cookie.getDomain()):
                rval.append(cookie)
        return rval
    # end getCookiesForDomain()

# end ZCookieReg


# ------------------------------------------------------------------------------
# A single Cookie set by an HTTP response and re-sent by an HTTP request (potentially).
# ------------------------------------------------------------------------------
class ZCookie:
    def __init__(self, cookieStr, defaultDomain = None):
        self.cookieStr = cookieStr
        self.domain = None
        self.path = None
        self.expires = None
        self.key = u"" #$NON-NLS-1$
        self.value = None
        self._parseCookieString(cookieStr)
        if self.path is None:
            self.path = u"/" #$NON-NLS-1$
        if not self.domain and defaultDomain:
            self.domain = defaultDomain
    # end __init__()

    def __cmp__(self, other):
        if self.key == other.key:
            return 0
        elif self.key < other.key:
            return -1
        else:
            return 1
    # end __cmp__()

    def _parseCookieString(self, cookieStr):
        strs = cookieStr.split(u";") #$NON-NLS-1$
        for str in strs:
            kv = str.strip().split(u"=") #$NON-NLS-1$
            k = kv[0].strip()
            if len(kv) > 1:
                v = kv[1].strip()
                self._processCookieSpec(k, v)
    # end _parseCookieString()

    def _processCookieSpec(self, key, val):
        if key.lower() == u"path": #$NON-NLS-1$
            self.path = val
        elif key.lower() == u"domain": #$NON-NLS-1$
            self.domain = val
        elif key.lower() == u"expires": #$NON-NLS-1$
            self.expires = val
        else:
            self.key = key
            self.value = val
    # end _parseCookieString()

    def getKey(self):
        return self.key
    # end getKey()

    def getValue(self):
        return self.value
    # end getValue()

    def getKeyValue(self):
        return (self.key, self.value)
    # end getKeyValue()

    def getDomain(self):
        return self.domain
    # end getDomain()

    def getPath(self):
        return self.path
    # end getPath()

    def getExpires(self):
        return self.expires
    # end getExpires()

# end ZCookie

# ------------------------------------------------------------------------------
# A simple HTTP request class.  This class supports making very simple and straightforward
# HTTP calls to servers.  The class supports http redirects and also cookies.
# ------------------------------------------------------------------------------
class ZSimpleHTTPRequest:

    def __init__(self, url, customHeaders = {}, cookieReg = None):
        self.url = url
        self.customHeaders = customHeaders
        self.postData = None
        self.method = None
        self._setMethod(HTTP_GET)
        self.httpStatusCode = u"" #$NON-NLS-1$
        self.httpStatusMessage =  u"" #$NON-NLS-1$
        self.cookies = []
        self.cookieReg = cookieReg
        self.rawRval = None
        self.rval = None
        self.rawData = None
        # authorization username, password and scheme credentials
        self.username = None
        self.password = None
        self.authscheme = None
        # true if the request required authorization.
        self.auth401Requested = False
        # authorization uri key - unique key that identifies the url, username and password
        self.authUriKey = None
        self._createAuthUriKey()

        if not cookieReg:
            self.cookieReg = ZCookieReg()
    # end __init__()

    def _setMethod(self, method):
        self.method = method

    def setMethod(self, method):
        self._setMethod(method)

    def getMethod(self):
        return self.method

    def _createAuthUriKey(self):
        # create unique request key for this location to store/cache authorization information
        self.authUriKey = self.url
        (scheme, netloc, path, params, query, fragment) = urlparse(self.url, u"http") #$NON-NLS-1$ @UnusedVariable
        if netloc:
            self.authUriKey = netloc
        if self.username:
            self.authUriKey = self.authUriKey + u":" + self.username #$NON-NLS-1$
        if self.password:
            self.authUriKey = self.authUriKey + u":" + self.password #$NON-NLS-1$
        if self.authscheme:
            self.authUriKey = self.authUriKey + u":" + self.authscheme #$NON-NLS-1$
    # end _createAuthUriKey()

    def _getAuthUriKey(self):
        if not self.authUriKey:
            self._createAuthUriKey()
        return self.authUriKey
    # end _getAuthUriKey()

    def setAuthorization(self, username, password):
        self.username = username
        self.password = password
        # update uri lookup key
        self._createAuthUriKey()
    # end setAuthorization()

    def setAuthenticationScheme(self, scheme):
        if scheme:
            self.authscheme = scheme.lower().strip()
        else:
            self.authscheme = None
        # update uri lookup key
        self._createAuthUriKey()
    # end setAuthenticationScheme()

    def getAuthenticationScheme(self):
        return self.authscheme
    # end getAuthenticationScheme()

    def getUsername(self):
        return self.username
    # end getUsername()

    def getPassword(self):
        return self.password
    # end getPassword()

    def hasAuthorizationCredentials(self):
        return self.getUsername() is not None and self.getPassword() is not None
    # end hasAuthorizationCredentials()

    def getUrl(self):
        # returns url - which may be different from the original url due to redirects.
        return self.url
    # end getUrl()

    def getHttpStatusCode(self):
        return self.httpStatusCode
    # end getHttpStatusCode()

    def getHttpStatusMessage(self):
        return self.httpStatusMessage
    # end getHttpStatusMessage()

    def getHeader(self, name, dflt = u""): #$NON-NLS-1$
        if self.response and name:
            return self.response.getheader(name)
        else:
            return dflt
    # end getHeader()

    def getContentType(self):
        return self.getHeader(u"Content-Type") #$NON-NLS-1$
    # end getContentType()

    def getContentLength(self):
        try:
            return int(self.getHeader(u"Content-Length", u"0")) #$NON-NLS-1$ #$NON-NLS-2$
        except:
            return 0
    # end getContentLength()

    # Sends the request to the server.
    def send(self, postData = None):
        self.postData = self._processPostData(postData)
        self.rval = self._sendRequest()
        return not self.rval is None
    # end send()

    def _processPostData(self, postData):
        return postData
    # end _processPostData()

    def getResponse(self):
        return self.rval
    # end getResponse()

    def getRawResponseData(self):
        return self.rawData
    # end getRawResponseData()

    def getCookies(self):
        return self.cookies
    # end getCookies()

    def getCookieReg(self):
        return self.cookieReg
    # end getCookieReg()

    # Returns True if the request was successful.
    def requestSucceeded(self):
        return not self.rval == None
    # end requestSucceeded

    def isAuthorizationRequired(self):
        # true if the last request failed due to 401 code.
        return self.auth401Requested
    # end isAuthorizationRequired

    def _preAuthorize(self):
        # if auth info is known, then pre-authenticate instead of waiting for a 401.
        # (i.e send known credentials with the initial request)
        if self.hasAuthorizationCredentials() and self.getAuthenticationScheme():
            # install handler if not already installed
            if not ZAuthenticationManager().isInstalled( self._getAuthUriKey() ):
                self._installAuthorization(None, self.getAuthenticationScheme() )
    # end _preAuthorize()

    def _installAuthorization(self, httpResponse, authscheme): #@UnusedVariable
        # installs the auth into the auth manager and returns true
        rval = False
        schemeSupported = ZAuthenticationManager().supportsScheme( authscheme )
        if schemeSupported and self.hasAuthorizationCredentials():
            ZAuthenticationManager().install(authscheme, self._getAuthUriKey(), httpResponse, self.url, self.getUsername(), self.getPassword() )
            rval = True
        return rval
    # end _installAuthorization

    # Sends the request to the configured server.
    def _sendRequest(self):
        # clear 401 requested flag
        self.auth401Requested = False
        # if auth type is known, then pre-authenticate instead of waiting for a 401.
        # (i.e send known credentials with the initial request)
        self._preAuthorize()
        # attempt to get the response
        rVal = self._internalSendRequest()
        # rval is not None for successful request.
        # it is False if the request failed due to a 401 auth required.
        if rVal:
            # response is ok.
            return rVal
        elif not self.auth401Requested:
            # the response was a failure unrelated to authorization.
            return None
        # Resend request with authentication information.
        rVal = self._internalSendRequest()
        if not rVal and self.auth401Requested:
            # If response failed, then remove username/pass from authmanager so that it won't be re-used.
            ZAuthenticationManager().uninstall( self._getAuthUriKey() )
        return rVal

    def _setAuthorizationRequestHeaders(self, headers):
        # if there is a auth handler for the given url,username password combo, then copy them to request header.
        if ZAuthenticationManager().isInstalled( self._getAuthUriKey() ):
            # copy over 'cached' authroization headers.
            authHeaders = ZAuthenticationManager().getAuthHeaders(  self._getAuthUriKey() )
            for n,v in authHeaders.iteritems():
                headers[n] = v
    # end _setAuthorizationRequestHeaders

    def _internalSendRequest(self):
        # FIXME (PJ) catch and throw well known/typed exceptions for socket errors such as timeout. (and use this information to display a friendly message on UI i.e. autodiscovery, downbload posts etc
        try:
            headers = {}
            for n in DEFAULT_HEADERS:
                headers[n] = DEFAULT_HEADERS[n]

            # Add custom headers
            if self.customHeaders:
                for n in self.customHeaders:
                    headers[n] = self.customHeaders[n]
            # set auth headers
            self._setAuthorizationRequestHeaders(headers)

            body = None
            # Get current content-type if any and update/modify if needed.
            contentType = None
            if headers.has_key(u"Content-Type"):  #$NON-NLS-1$
                contentType = headers[u"Content-Type"].strip() #$NON-NLS-1$
            elif headers.has_key(u"content-type"):  #$NON-NLS-1$
                contentType = headers[u"content-type"].strip() #$NON-NLS-1$

            fileUpload = False # using multipart/form-data or raw  upload of a single file.
            fileDescriptor  = None # FD of a single file to be uploaded
            boundary = None # file upload boundry in multipart/form-data
            multipartMimeLength = -1
            v_files = []
            v_vars = []
            if self.postData:
                if isinstance(self.postData, dict):
                    # data is form-data (name value dictionary)
                    for (k, v) in self.postData.iteritems():
                        # get list of files and vars - adapted from urllib2_file.py
                        if hasattr(v, u'read'): #$NON-NLS-1$
                            v_files.append((k, v))
                        else:
                            v_vars.append( (k, v) )
                    # Case: no files. just plain string data
                    if len(v_vars) > 0 and len(v_files) == 0:
                        # update content-type
                        contentType = u"application/x-www-form-urlencoded; charset=utf-8" #$NON-NLS-1$
                        # url-encode form data
                        body = convertToUtf8( urlencode(self.postData) )
                        headers[u"Content-Length"] = u"%d" % len(body) #$NON-NLS-1$ #$NON-NLS-2$
                    elif len(v_files) > 0:
                        # Case: has one or more files
                        boundary = generateMimeMultipartBoundry()
                        fileUpload = True
                        # calculate length
                        multipartMimeLength = self._calculateMultipartFormData(v_vars, v_files, boundary)
                        headers[u"Content-Length"] = u"%d" % multipartMimeLength #$NON-NLS-1$ #$NON-NLS-2$
                        contentType = u'multipart/form-data; boundary=%s' % boundary #$NON-NLS-1$

                elif hasattr(self.postData, u'read'): #$NON-NLS-1$
                    # post data is a file handle
                    fileUpload = True
                    fileDescriptor = self.postData
                    fname = fileDescriptor.name.split(u'/')[-1] #$NON-NLS-1$
                    contentType = getContentTypeFromFilename(fname)
                    destName = os.path.basename(os.path.abspath(fname))
                    # Add file name as HTTP entity-header to associate meta data with a Atom POST. (e.g. currently used when uploading to picasa)
                    # See http://bitworking.org/projects/atom/draft-ietf-atompub-protocol-13.html#rfc.section.9.6
                    headers[u"Slug"] = destName #$NON-NLS-1$
                    file_size = os.fstat( fileDescriptor.fileno() )[stat.ST_SIZE]
                    headers[u"Content-Length"] = u"%d" % file_size #$NON-NLS-1$ #$NON-NLS-2$
                else:
                    # body could be binary or text data
                    body = self.postData
                    (ct_primary_type, ct_sub_type, ct_enc) = splitContentTypeField(contentType) #@UnusedVariable)
                    # if the body is of type text/* or application/xml or application/atom+xml, and does not have charset encoding, set encoding to utf-8
                    if not ct_enc and ( contentType.startswith(u"text/") or contentType == u"application/xml"  or contentType == u"application/atom+xml"): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
                        ct_enc = u"utf-8" #$NON-NLS-1$
                        contentType = ct_primary_type + u"/" + ct_sub_type + u"; charset=utf-8" #$NON-NLS-1$ #$NON-NLS-2$
                    # if enc is UTF8, then convert content to utf8
                    if body and ct_enc and (ct_enc == u"utf-8" or ct_enc == u"utf8"): #$NON-NLS-1$ #$NON-NLS-2$
                        body = convertToUtf8(body)
                    # add content-length
                    headers[u"Content-Length"] = u"%d" % len(body) #$NON-NLS-1$ #$NON-NLS-2$
                # update content-type
                if contentType:
                    headers[u"Content-Type"] =  contentType #$NON-NLS-1$
                # Switch to POST if the type is currently set to GET
                if self.getMethod() == HTTP_GET: #$NON-NLS-1$
                    self._setMethod(HTTP_POST) #$NON-NLS-1$
            # end if has post data
            numRedirects = 0

            while (numRedirects < 5):
                # Connect to the server
                (scheme, netloc, path, params, query, fragment) = urlparse(self.url, u"http") #$NON-NLS-1$ @UnusedVariable
                if query:
                    path = u"%s?%s" % (path, query) #$NON-NLS-1$

                # Get the cookie for this url.
                cookie = self.cookieReg.getCookieStrForURL(self.url)
                if cookie:
                    headers[u"Cookie"] = cookie #$NON-NLS-1$

                # Get the connection object from the factory.
                if fileUpload:
                    conn = ZHttpConnectionFactory().createRawConnection(self.url, self.getMethod() ) #@UnusedVariable
                    for (n,v) in headers.iteritems():
                        conn.putheader(n,v)
                    conn.endheaders()
                    if contentType.startswith(u"multipart/form-data"): #$NON-NLS-1$
                        # send multipart formdata along with 1 or more files
                        self._sendMultipartFormData(v_vars, v_files, boundary, conn)
                    else:
                        # send raw file. postData is a file descriptor
                        self._sendRawFile( fileDescriptor, conn )
                else:
                    conn = ZHttpConnectionFactory().createHttpConnection(self.url, self.getMethod(), body, headers)

                # Get the http response object
                self.response = conn.getresponse()

                self.httpStatusCode = self.response.status
                self.httpStatusMessage =  self.response.reason
                self.cookies = self._parseCookies(self.response.getheader(u"Set-cookie")) #$NON-NLS-1$
                self.cookieReg.addCookies(self.cookies)

                if self._responseIsRedirect(self.response):
                    self.url = getAbsoluteUrl( self.response.getheader(u"Location"), self.url ) #$NON-NLS-1$
                    numRedirects = numRedirects + 1
                else:
                    break
            # end while (numRedirects < 5)

            # Check for www-authenticate response
            if not self.auth401Requested and self._responseIsAuthenticate(self.response):
                self.auth401Requested = True
                self._processAuthorizationData(self.response)
                return None

            # If the response is not 'good', then process the error.
            if not self._responseIsGood(self.response):
                self._processError(self.response)
                return None
            
            # Otherwise, process the response to get its data, then post-process the data into
            # some response object (might be a ZDom, for example).
            responseFile = self._ungzipResponseContent(self.response)
            self.rawData = self._processResponse(responseFile)
            return self._processResponseData(self.response, self.rawData)
        except Exception, e:
            ze = ZException(rootCause = e)
            raise ze
    # end _sendRequest()
    
    def _ungzipResponseContent(self, httpResponse):
        # un gzip or unzip encoded content and return interface that implements the file.read().
        responseFile = None
        encoding = httpResponse.getheader(u"Content-Encoding") #$NON-NLS-1$
        if encoding and encoding in (u'gzip', u'x-gzip', u'deflate'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            try:
                content = httpResponse.read()
                if encoding == u'deflate': #$NON-NLS-1$
                    responseFile = StringIO.StringIO(zlib.decompress(content))
                else:
                    responseFile = gzip.GzipFile(u'', u'rb', 9, StringIO.StringIO(content)) #$NON-NLS-1$ #$NON-NLS-2$
            except:
                pass
        if responseFile:
            return responseFile
        else:
            # the httpResponse object also implements the read()
            return httpResponse
    # end _ungzipResponseContent()

    def _calculateMultipartFormData(self, v_vars, v_files, boundary):
        return self. _sendMultipartFormData(v_vars, v_files, boundary, None)
    # end _calculateMultipartFormData

    def _sendMultipartFormData(self, v_vars, v_files, boundary, connection):
        contentLength = send_data(v_vars, v_files, boundary, sock=connection)
        return contentLength
    # end _sendMultipartFormData()

    def _sendRawFile(self, fileDescriptor, connection):
        CHUNK_SIZE = 10 * 1024
        if hasattr(fileDescriptor, u'seek'): #$NON-NLS-1$
            fileDescriptor.seek(0)
        while True:
            chunk = fileDescriptor.read(CHUNK_SIZE)
            if not chunk:
                break
            connection.send(chunk)
    # end _sendRawFile()

    # Returns the data found in the http response.
    def _processResponse(self, resp):
        self.response = resp
        return resp.read()
    # end _processResponse()

    def _processError(self, resp): #@UnusedVariable
        # Note: resp.reason will give the reason for the error, resp.status will give the status.
        pass
    # end _processError()

    def _parseCookies(self, cookieStr):
        cookies = []
        if cookieStr:
            defaultDomain = getDomain(self.url)
            cstrs = cookieStr.split(u",") #$NON-NLS-1$
            for cstr in cstrs:
                cookies.append(ZCookie(cstr, defaultDomain))
        return cookies
    # end _parseCookies()

    def _processResponseData(self, resp, data): #@UnusedVariable
        return data
    # end _processResponseData()

    def _processAuthorizationData(self, httpResponse):
        authscheme = self._getAuthSchemeFromResponse(httpResponse)
        if authscheme:
            self._installAuthorization(httpResponse, authscheme )

    def _getAuthSchemeFromResponse(self, httpResponse):
        #  Delegate to auth handlers to determine if they can handle the scheme
        authscheme = ZAuthenticationManager().getSchemeFromResponse(httpResponse)
        return authscheme
    # end _getAuthSchemeFromResponse()

    # Tests the response object to make sure the request succeeded.
    def _responseIsGood(self, resp):
        return resp.status >= 200 and resp.status <= 299
    # end _responseIsGood()

    def _responseIsRedirect(self, resp):
        return resp.status == 301 or resp.status == 302
    # end _responseIsRedirect()

    def _responseIsAuthenticate(self, resp):
        return resp.status == 401
    # end _responseIsAuthenticate()

# end ZSimpleHTTPRequest


# ------------------------------------------------------------------------------
# A simple HTTP request class that just deals with text.  This class can handle multiple
# text encodings.  A flag to the constructor indicates whether the content-type character
# encoding should be handled (or attempt to be handled).
# ------------------------------------------------------------------------------
class ZSimpleTextHTTPRequest(ZSimpleHTTPRequest):

    def __init__(self, url, customHeaders = {}, handleEncoding = False, cookieReg = None):
        self.handleEncoding = handleEncoding

        ZSimpleHTTPRequest.__init__(self, url, customHeaders, cookieReg)
    # end __init__()

    def _processResponseData(self, resp, txt):
        # Determine encoding if required.
        enc = None
        if self.handleEncoding:
            # get the encoding from the header. This may be None if not specifed in the header.
            rawCt = resp.getheader(u"Content-Type") #$NON-NLS-1$
            (ctMain, ctSub, enc) = splitContentTypeField(rawCt) #@UnusedVariable

        if self.handleEncoding and not enc:
            # we did not find the enc in the content-type header. So, search the html body.
            metaTagList = findMetaContentTypeTags(txt)
            if metaTagList:
                (ctMain, ctSub, enc) = splitContentTypeField(metaTagList[0]) #@UnusedVariable

        txt = convertToUnicode(txt, enc)
        return txt
    # end _processResponseData()

# end SimpleTextHTTPRequest


# ------------------------------------------------------------------------------
# An extension of the simple text http request that handles XML input and output.
# ------------------------------------------------------------------------------
class ZSimpleXmlHTTPRequest(ZSimpleTextHTTPRequest):

    def __init__(self, url, customHeaders = {}, handleEncoding = False, cookieReg = None):
        ZSimpleTextHTTPRequest.__init__(self, url, customHeaders, handleEncoding, cookieReg)
    # end __init__()

    def _processPostData(self, postData):
        if postData and isinstance(postData, ZDom):
            return postData.serialize()
        else:
            return ZSimpleTextHTTPRequest._processPostData(self, postData)
    # end _processPostData()

    def _processResponseData(self, resp, txt):
        txt = ZSimpleTextHTTPRequest._processResponseData(self, resp, txt)
        # FIXME (PJ) check resp content-type. If text/plain, then return txt as is isstead of a zdom.
        return ZDom(txt)
    # end _processResponseData()

# end ZSimpleXmlHTTPRequest


# ------------------------------------------------------------------------------
# An interface for the binary file downloader listener.  An instance of this
# interface is given to the binary file downloader, which will call back the
# listener at for various reasons.
# ------------------------------------------------------------------------------
class IZHttpBinaryFileDownloadListener:

    def transferStarted(self, contentType, contentLength):
        u"Called when the file transfer has started." #$NON-NLS-1$
    # end transferStarted()

    def transferBlock(self, blockLength):
        u"Called when some data has been transferred." #$NON-NLS-1$
    # end transferBlock()

    def transferComplete(self):
        u"Called when the file transfer has completed." #$NON-NLS-1$
    # end transferComplete()

    def transferError(self, zexception):
        u"Called if there is an error during transfer." #$NON-NLS-1$
    # end transferError()

    def transferCancelled(self):
        u"Called if the file transfer has cancelled." #$NON-NLS-1$
    # end transferCancelled()

# end IZHttpBinaryFileDownloadListener


# ------------------------------------------------------------------------------
# This class provides a simple way to download a binary file.  A listener may
# optionally be provided that will be called back when the transfer starts,
# stops, 8k blocks are downloaded etc...
# ------------------------------------------------------------------------------
class ZHttpBinaryFileDownload(ZSimpleHTTPRequest):

    u"""Convenience class to download the http binary (e.g. image) content to a given file.""" #$NON-NLS-1$
    def __init__(self, url = None, filename = None, listener = None, customHeaders = None):
        self.filename = filename
        self.listener = listener
        if not self.listener:
            self.listener = IZHttpBinaryFileDownloadListener()
        self.stopped = False
        ZSimpleHTTPRequest.__init__(self, url, customHeaders)
    # end __init__()

    def cancel(self):
        self.stopped = True
    # end cancel()

    def getFilename(self):
        return self.filename
    # end getFilename()

    # Called after the connection has been established.  The method reads the raw response
    # content data and saves it to the given file.
    def _processResponse(self, response):
        rval = -1
        if response and self.filename:
            try:
                tfp = self._openOutputFile()
                try:
                    blockSize = 1024 * 8
                    done = False
                    totalSize = 0
                    while not done and not self.stopped:
                        block = self._readBlock(response, blockSize)
                        if block:
                            tfp.write(block)
                            totalSize = totalSize + len(block)
                        else:
                            done = True
                    rval = totalSize
                finally:
                    tfp.close()
                if self.stopped:
                    self.listener.transferCancelled()
                else:
                    self.listener.transferComplete()
            except Exception, e:
                ze = ZException(rootCause = e)
                self.listener.transferError(ze)
                raise ze
        return rval
    # end _processResponse()

    def _openOutputFile(self):
        self.listener.transferStarted(self.getContentType(), self.getContentLength())
        return open(self.filename, u'wb') #$NON-NLS-1$
    # end _openOutputFile()

    def _readBlock(self, response, blockSize):
        block = response.read(blockSize)
        if block:
            self.listener.transferBlock(len(block))
        return block
    # end _readBlock()

# end ZHttpBinaryFileDownload


# ------------------------------------------------------------------------------
# A simple extension of the base http binary file download that supports
# resumable downlaods via the standard HTTP "Range" request header.
# ------------------------------------------------------------------------------
class ZResumableHttpBinaryFileDownload(ZHttpBinaryFileDownload):

    def __init__(self, url, filename, startByte = 0, listener = None):
        u"""__init__(string, string, int, IZHttpBinaryFileDownloadListener)""" #$NON-NLS-1$
        self.startByte = startByte
        customHeaders = {}
        if startByte > 0:
            rangeHeader = u"bytes=%d-" % startByte #$NON-NLS-1$
            customHeaders[u"Range"] = rangeHeader #$NON-NLS-1$
        ZHttpBinaryFileDownload.__init__(self, url, filename, listener, customHeaders)
    # end __init__()

    def _openOutputFile(self):
        self.listener.transferStarted(self.getContentType(), self.getContentLength() + self.startByte)
        if self.startByte > 0 and os.path.exists(self.filename):
            self.listener.transferBlock(self.startByte)
            return open(self.filename, u'ab') #$NON-NLS-1$
        else:
            return open(self.filename, u'wb') #$NON-NLS-1$
    # end _openOutputFile()

# end ResumableHttpBinaryFileDownload


# ------------------------------------------------------------------------------
# Convenience method to return the filename (name.ext) specified in the url.
# Returns None if the last item in the url path did not have the pattern
# 'name.ext'.
# ------------------------------------------------------------------------------
def getFilenameFromUrl(url):
    return splitUrl(url)[4]
# end getFilenameFromUrl()


# ------------------------------------------------------------------------------
# Returns tuple (host, path) from url or (None, None) if failed.
# ------------------------------------------------------------------------------
def getHostAndPath(url):
    l = splitUrl(url)
    return (l[1], l[3])
# end getHostAndPath()


# ------------------------------------------------------------------------------
# Returns base url. http://www.myhost.com/path/to/something returns
# http://www.myhost.com/
# ------------------------------------------------------------------------------
def getBaseUrl(url):
    l = splitUrl(url)
    if l[0] and l[1] and l[2]:
        url = l[0] + u"://" + l[1] #$NON-NLS-1$
        p = l[2]
        if u"http" == l[0] and p != 80: #$NON-NLS-1$
            url = url + u":" + unicode(p) #$NON-NLS-1$
        elif u"https" == l[0] and p != 443: #$NON-NLS-1$
            url = url + u":" + unicode(p) #$NON-NLS-1$
    return url
# end getBaseUrl()


# ------------------------------------------------------------------------------
# Returns domain. http://www.myhost.com/path/to/something returns www.myhost.com
# ------------------------------------------------------------------------------
def getDomain(url):
    l = splitUrl(url)
    rval = l[1]
    return rval
# end getDomain()


# ------------------------------------------------------------------------------
# Returns the absolute url given a relative url and the reference/base url.
# For example getAbsoluteUrl("test1.html", "http://zoundry.com/dir/") => http://zoundry.com/dir/test1.html
# ------------------------------------------------------------------------------
def getAbsoluteUrl(relativeUrl, refUrl):
    rval = relativeUrl
    if rval and refUrl and not rval.startswith(u"http"): #$NON-NLS-1$
        parts = splitUrl(refUrl)
        scheme = parts[0]
        host = parts[1]
        port = parts[2]
        if parts[3]:
            path = parts[3].rstrip(u"/") + u"/" + relativeUrl.lstrip(u"/") #$NON-NLS-1$ #$NON-NLS-2$#$NON-NLS-3$
        else:
            path = u"/" + relativeUrl.lstrip(u"/") #$NON-NLS-1$ #$NON-NLS-2$
        rval = joinUrl(scheme, host, port, path)
    return rval
# end getAbsoluteUrl()

# ------------------------------------------------------------------------------
# Returns a tuple containing (scheme, host, port_integer, path, resource_name,
# query_string, url)
#
#    For example:
#        http://www.mydomain.com/pj/docs/readme.html?section=2
#    would return,
#        0. scheme = http
#        1. host = mydomain.com
#        2. port = 80 (integer value)
#        3. path = /pj/docs/
#        4. resource_name = readme.html (basically after trying to match a 'name.ext' pattern).
#        5. query_string = section=2
#        6. url = http://www.mydomain.com/pj/docs/readme.html?section=2 (the url is rebuilt
#           from the params)
#    If the sheme, host (for relative urls), or port is not specified in the URL,
#    then the default arguments will be used.
# ------------------------------------------------------------------------------
def splitUrl(url, defaultHost = u"", defaultScheme = u"http"): #$NON-NLS-1$ #$NON-NLS-2$
    matcher = URL_PATTERN.match(url)
    (_dummy, scheme, host, _dummy, port, path, _dummy, query) = matcher.groups()

    if not scheme:
        scheme = defaultScheme
    if not host:
        host = defaultHost
    if not query:
        query = None
    if port:
        port = int(port)
    elif DEFAULT_PORT_MAP.has_key(scheme):
        port = DEFAULT_PORT_MAP[scheme]
    else:
        port = 80

    filename = None
    fullPath = path
    if path:
        filename = os.path.basename(path)
        if not u"." in filename: #$NON-NLS-1$
            filename = None
        else:
            path = os.path.dirname(path)
    else:
        path = None

    url = joinUrl(scheme, host, port, fullPath, query)
    return (scheme, host, port, path, filename, query, url)
# end splitUrl()


# ------------------------------------------------------------------------------
# Takes the scheme, host, port, path, and query components of a URL and joins
# them together into a standard URL string.
# ------------------------------------------------------------------------------
def joinUrl(scheme, host, portNumber, path, query = None):
    if not host or len(host) == 0:
        return host
    port = int(portNumber)
    tempScheme = None
    if host and len(host) > 7 and host.lower().startswith(u"http://"):#$NON-NLS-1$
        tempScheme = u"http" #$NON-NLS-1$
        host = host[7:]
    elif host and len(host) > 8 and host.lower().startswith(u"https://"):#$NON-NLS-1$
        tempScheme = u"https" #$NON-NLS-1$
        host = host[8:]
    if not scheme and tempScheme:
        scheme = tempScheme

    tempHost = host
    if scheme == u"http" and port != 80: #$NON-NLS-1$
        tempHost = host + u":" + unicode(port) #$NON-NLS-1$
    elif scheme == u"https" and port != 443: #$NON-NLS-1$
        tempHost = host + u":" + unicode(port) #$NON-NLS-1$

    url = scheme + u"://" + tempHost#$NON-NLS-1$
    if path:
        url = url + u"/" + path.lstrip(u"/")  #$NON-NLS-1$  #$NON-NLS-2$
    if query:
        url = url + u"?" + query #$NON-NLS-1$
    return url
# end joinUrl()


# ------------------------------------------------------------------------------
# Returns list of the content-type attribute values found in the html <meta>
# tag for.
#
#    http-equiv=.Content-Type. For example:
#         <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
#
#         returns the list ["text/html; charset=UTF-8"]
#    Returns an empty list if meta tags were not found.
# ------------------------------------------------------------------------------
def findMetaContentTypeTags(htmlContent):
    metaTagList = META_CT_TAG_RE.findall(htmlContent)
    ctList = []
    for metaTag in metaTagList:
        ct = u"" #$NON-NLS-1$
        m = META_CT_ATTR_RE.match(metaTag)
        if m:
            ct= m.group(2)
            ct = ct.replace(u'\n', u' ') #$NON-NLS-1$ #$NON-NLS-2$
            ct = ct.replace(u'\r', u' ') #$NON-NLS-1$ #$NON-NLS-2$
            ctList.append(ct.strip())
    return ctList
# end findMetaContentTypeTags()


# ------------------------------------------------------------------------------
# Splits the HTTP content-type value into a tuple (ct_primary_type,ct_sub_type,
# encoding).
#    For example, "text/html; charset=UTF-8" returns ("text", "html", "utf-8").
#    Note the return tuple value maybe None if a match was not found.
# ------------------------------------------------------------------------------
def splitContentTypeField(ctValue):
    if not ctValue:
        return (None, None, None)

    rCtMain = None
    rCtSub = None
    rEnc = None

    m = CT_VALUE1_RE.match(ctValue)
    if m:
        rCtMain = lower(m.group(2).strip())
        rCtSub = lower(m.group(3).strip())
        rEnc = lower(m.group(6).strip())
    else:
        m = CT_VALUE2_RE.match(ctValue)
        if m:
            rCtMain = lower(m.group(2).strip())
            rCtSub = lower(m.group(3).strip())

    return (rCtMain, rCtSub, rEnc)
# end splitContentTypeField()



