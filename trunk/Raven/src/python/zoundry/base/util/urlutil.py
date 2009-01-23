import sys
from Ft.Lib.Uri import PercentDecode
from Ft.Lib.Uri import PercentEncode
from zoundry.base.util.text.unicodeutil import convertToUnicode
import os.path
import re
import string
import urllib

# Encoding used for encode/decode and quote/unquote methods.
DEFAULT_URI_ENC = u"utf-8" #$NON-NLS-1$
# Pattern to match http, https, ftp protocol
URL_RE_PATTERN = r"(^|[ \t\r\n])((ftp|http|https):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))" #$NON-NLS-1$
URL_RE = re.compile(URL_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Pattern to match http, https, ftp and file protocol
FILEURL_RE_PATTERN = r"(^|[ \t\r\n])((ftp|http|https|file):(([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%[A-Fa-f0-9]{2}){2,}(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?([A-Za-z0-9$_+!*();/?:~-]))" #$NON-NLS-1$
FILEURL_RE = re.compile(FILEURL_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


# Simple pattern to match local hard drive paths. Eg. C:/temp.
FILE_RE_PATTERN = r"(\w):([\\\/])[A-Za-z0-9]+"  #$NON-NLS-1$
FILE_RE = re.compile(FILE_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Pattern for file protocol
FILE_PROTOCOL_PATTERN = r"^file://[.]*" #$NON-NLS-1$
FILE_PROTOCOL_RE = re.compile(FILE_PROTOCOL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


def decodeUri(uri):
    u"""decodeUri(string) -> string
    Decodes(un-escape) the url. E.g %20 becomes a space. Supports UTF8.
    (basically decodes the provided uri for human readability)
    """ #$NON-NLS-1$
    rval = uri
    if uri:
        # Try and decode local file protocol
        rval = getFilePathFromUri(uri) #$NON-NLS-1$
        if not rval:
            # uri  is not a file. decode url components using 'unquote'.
            rval = unquote(uri)
            try:
                rval = decodeIDNA(rval)
            except:
                pass
    return rval
# end decodeUri

def encodeUri(uri):
    u"""encodeUri(string) -> string
    Encodes and returns the url. (e.g. - a space becomes %20)""" #$NON-NLS-1$
    rval = uri
    if uri:
        # check if file protocol.
        rval = getUriFromFilePath(uri, None)
        if not rval:
            uri = encodeIDNA(uri)
            uri = _internalEncodeUri(uri)
    return rval
# end encodeUri

def _internalEncodeUri(uri):
    rval = uri
    if uri:
        components = uri.split(u'/') #$NON-NLS-1$
        rval = u"" #$NON-NLS-1$
        for comp in components:
            if comp:
                rval = rval + u'/' + quote(comp) #$NON-NLS-1$
    return rval
# end _internalEncodeUri()    

def isLocalFile(uri):
    u"""isLocalFile(string) -> bool
    Returns true if the uri is a local file resource and the file exists.
    """ #$NON-NLS-1$
    return uri and FILE_PROTOCOL_RE.match(uri)
# end isLocalFile()

def getFilePathFromUri(uri):
    u"""getFilePathFromUri(string) -> string or None
    Returns the absolute local file path given the <a> href value
    or <img> src value. This method returns None if the URI protocol is
    not file:// .""" #$NON-NLS-1$

    rval = None
    if uri and FILE_PROTOCOL_RE.match(uri):
        uri = uri.strip()
        if uri.lower().startswith(u"file:///"): #$NON-NLS-1$
            uri = uri[8:]
        elif uri.lower().startswith(u"file://"): #$NON-NLS-1$
            uri = uri[7:]
        rval = url2pathname(uri)
    return rval
# end getFilePathFromUri()

def getUriFromFilePath(filePath, defaultPath=None):
    u"""getUriFromFilePath(string) -> string or None
    Returns the local file uri path (file://) given the <a> href value
    or <img> src value of local file name.""" #$NON-NLS-1$
    if not filePath:
        return filePath
    if defaultPath is None:
        defaultPath = filePath
    filename = None
    if os.path.exists(os.path.abspath(filePath)):
        # e.g: C:/path/to/file
        filename = filePath
    elif FILE_PROTOCOL_RE.match(filePath):
        # e.g: file://c:/path/to/file
        filename = getFilePathFromUri(filePath)
    else:
        # no change for http protocol etc.
        return defaultPath
    filename = filename.replace(u'\\', u'/') #$NON-NLS-1$ #$NON-NLS-2$
    rval = u"file:" + pathname2url(os.path.abspath(filename)) #$NON-NLS-1$
    return rval
# end getUriFromFilePath()

def urlencode(query,doseq=0):
    u"""Encode a sequence of two-element tuples or dictionary into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.    
    """ #$NON-NLS-1$
    
    # NOTE: function ported from Python's urllib::urlencode. This impl. supports unicode.

    if hasattr(query,u"items"): #$NON-NLS-1$
        # mapping objects
        query = query.items()
    else:
        # it's a bother at times that strings and string-like objects are
        # sequences...
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # zero-length sequences of all types will get here and succeed,
            # but that's a minor nit - since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty,va,tb = sys.exc_info() #@UnusedVariable
            raise TypeError, u"not a valid non-string sequence or mapping object", tb #$NON-NLS-1$

    l = []
    if not doseq:
        # preserve old behavior
        for k, v in query:
            k = quote_plus(unicode(k))
            v = quote_plus(unicode(v))
            l.append(k + u'=' + v) #$NON-NLS-1$
    else:
        for k, v in query:
            k = quote_plus(unicode(k))
            if isinstance(v, basestring):
                v = quote_plus(v)
                l.append(k + u'=' + v) #$NON-NLS-1$
            else:
                try:
                    # is this a sufficient test for sequence-ness?
                    x = len(v) #@UnusedVariable
                except TypeError:
                    # not a sequence
                    v = quote_plus(unicode(v))
                    l.append(k + u'=' + v) #$NON-NLS-1$
                else:
                    # loop over the sequence
                    for elt in v:
                        l.append(k + u'=' + quote_plus(unicode(elt))) #$NON-NLS-1$
    return u'&'.join(l) #$NON-NLS-1$

def quote(s, encoding = DEFAULT_URI_ENC):
    u"""Encodes a url path. Similar to urllib.quote but with support for unicode.""" #$NON-NLS-1$
    try:
        return PercentEncode(s, encoding) #$NON-NLS-1$
    except:

        try:
            return quote(s)
        except:
            return s
# end quote()

def quote_plus(s, encoding = DEFAULT_URI_ENC):
    u"""Encodes a url path. Similar to urllib.quote_plus but with support for unicode.""" #$NON-NLS-1$
    try:
        return PercentEncode(s, encoding, spaceToPlus=True)
    except:
        try:
            return urllib.quote_plus(s)
        except:
            return s
# end quote_plus()

def unquote(s, encoding = DEFAULT_URI_ENC, plusToSpace=False):
    u"""Decodes a url path. Similar to urllib.unquote but with support for unicode.""" #$NON-NLS-1$
    try:
        return PercentDecode(s, encoding)
    except:
        pass
    try:
        if plusToSpace:
            return urllib.unquote_plus(s)
        else:
            return urllib.unquote(s)
    except:
        return s
# end unquote()

def unquote_plus(s, encoding = DEFAULT_URI_ENC):
    u"""Decodes a url path. Similar to urllib.unquote but with support for unicode.""" #$NON-NLS-1$
    if s and u'+' in s: #$NON-NLS-1$
        s = u' '.join(s.split(u'+')) #$NON-NLS-1$ #$NON-NLS-2$
    return unquote(s, encoding, True)
# end unquote_plus()

def encodeIDNA(url):
    u"""Encodes url as IDNA form""" #$NON-NLS-1$
    return _internalEncodeIDNA(url, True)
# end encodeIDNA

def decodeIDNA(url):
    u"""Decodes IDNA""" #$NON-NLS-1$
    return _internalEncodeIDNA(url, False)
# end decodeIDNA


def _internalEncodeIDNA(url, encodeLabel):
    u"""Encodes url as IDNA form""" #$NON-NLS-1$
    if url and URL_RE.match(url):
        try:
            idx1 = url.find(u"://") #$NON-NLS-1$
            idx2 = url.find(u"/", idx1 + 3) #$NON-NLS-1$
            host = None
            if idx1 != -1 and idx2 != -1:
                host = url[idx1+3: idx2]
            elif idx1 != -1 :
                host = url[idx1+3:]
            if host:
                labels = host.split(u".") #$NON-NLS-1$
                for i in range( len(labels) ):
                    if encodeLabel:
                        labels[i] = labels[i].encode(u"idna") #$NON-NLS-1$
                    else:
                        # decode
                        labels[i] = labels[i].decode(u"idna") #$NON-NLS-1$
                host = u".".join(labels) #$NON-NLS-1$
                if idx2 != -1:
                    url = url[0:idx1+3] + host + url[idx2:]
                else:
                    url = url[0:idx1+3] + host
        except:
            pass
    return url
# end _internalEncodeIDNA

#====================================================
# Windows Specific. Modified version of nturl2path.py
#===================================================
def url2pathname(url):
    # e.g.
    # ///C|/foo/bar/spam.foo
    # becomes
    # C:\foo\bar\spam.foo
    # Windows itself uses ":" even in URLs.
    url = url.replace(u':', u'|') #$NON-NLS-1$ #$NON-NLS-2$
    if not u'|' in url: #$NON-NLS-1$
        # No drive specifier, just convert slashes
        if url[:4] == u'////':  #$NON-NLS-1$
            # path is something like ////host/path/on/remote/host
            # convert this to \\host\path\on\remote\host
            # (notice halving of slashes at the start of the path)
            url = url[2:]
        components = url.split(u'/')  #$NON-NLS-1$
        # make sure not to convert quoted slashes :-)
        return unquote(u'\\'.join(components))  #$NON-NLS-1$
    comp = url.split(u'|')  #$NON-NLS-1$
    if len(comp) != 2 or comp[0][-1] not in string.ascii_letters:
        error = u'Bad URL: ' + url  #$NON-NLS-1$
        raise IOError, error
    drive = comp[0][-1].upper()
    components = comp[1].split(u'/')  #$NON-NLS-1$
    path = drive + u':'  #$NON-NLS-1$
    for  comp in components:
        if comp:
            path = path + u'\\' + unquote(comp)  #$NON-NLS-1$
    return path
# end url2pathname()

def pathname2url(p):
    # e.g.
    # C:\foo\bar\spam.foo
    # becomes
    # ///C|/foo/bar/spam.foo
    if not u':' in p:  #$NON-NLS-1$
        # No drive specifier, just convert slashes and quote the name
        if p[:2] == u'\\\\':  #$NON-NLS-1$
        # path is something like \\host\path\on\remote\host
        # convert this to ////host/path/on/remote/host
        # (notice doubling of slashes at the start of the path)
            p = u'\\\\' + p  #$NON-NLS-1$
        components = p.split(u'\\')  #$NON-NLS-1$
        return quote(u'/'.join(components))  #$NON-NLS-1$
    comp = p.split(u':')  #$NON-NLS-1$
    if len(comp) != 2 or len(comp[0]) > 1:
        error = u'Bad path: ' + p  #$NON-NLS-1$
        raise IOError, error

    drive = quote(comp[0].upper())
    components = comp[1].split(u'\\')  #$NON-NLS-1$
    path = u'///' + drive + u'|' #$NON-NLS-1$ #$NON-NLS-2$
    for comp in components:
        if comp:
            path = path + u'/' + quote(comp)  #$NON-NLS-1$
    return path
# end pathname2url()

# ----------------------------------------------------------------------------------------
# getUrlFromShortcut(windowsShortCutFile)
# Extract the url embedded in a .url windows shortcut file
# ----------------------------------------------------------------------------------------
def getUrlFromShortcut(shortcutFile):
    u"""Returns tuple (url, name) given a IE shortcut file or (None,None) if failed.""" #$NON-NLS-1$
    url = None
    fname = None
    if not shortcutFile or not shortcutFile.lower().endswith(u".url"): #$NON-NLS-1$
        return (None,None)
    try :
        fname = shortcutFile.replace(u'\\', u'/').split(u'/')[-1] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        (fname, fExt) = os.path.splitext(fname) #@UnusedVariable
        file  = open(shortcutFile, u'r') #$NON-NLS-1$
        count = 0
        scFound = False
        for line in file.readlines():
            if not line or count > 25:
                break
            count = count + 1
            line = line.strip()
            if line == u"[InternetShortcut]": #$NON-NLS-1$
                scFound = True
                continue
            if scFound and line.lower().startswith(u"url="): #$NON-NLS-1$
                url = line[4:]
                break
        file.close()
    except Exception:
        pass
    if fname:
        fname = convertToUnicode(fname)
    return (url, fname)
# end getUrlFromShortcut()


