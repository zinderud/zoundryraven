from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.base.util.fileutil import getFileMetaData
import os

# ------------------------------------------------------------------------------
# The interface for connection response information.  This object contains the
# meta information about the connection response (code, message, headers).
# ------------------------------------------------------------------------------
class IZHttpConnectionRespInfo:
    
    def getURL(self):
        u"""getURL() -> string
        Returns the URL that this response represents.""" #$NON-NLS-1$
    # end getURL()
    
    def getCode(self):
        u"""getCode() -> int
        Returns the HTTP response code.""" #$NON-NLS-1$
    # end getCode()
    
    def getMessage(self):
        u"""getMessage() -> string
        Returns the HTTP response message.""" #$NON-NLS-1$
    # end getMessage()
    
    def getHeaders(self):
        u"""getHeaders() -> map<string, string>
        Returns a map of HTTP response header (map of header
        key to header value).""" #$NON-NLS-1$
    # end getHeaders()
    
    def getHeader(self, name):
        u"""getHeader(string) -> string
        Returns the value of the header with the given name.""" #$NON-NLS-1$
    # end getHeader()
    
    def getContentType(self):
        u"""getContentType() -> string
        Returns the content type of the response.""" #$NON-NLS-1$
    # end getContentType()
    
    def getContentLength(self):
        u"""getContentLength() -> int
        Returns the content length of the response.""" #$NON-NLS-1$
    # end getContentLength()

# end IZHttpConnectionRespInfo


# ------------------------------------------------------------------------------
# Extends the IZHttpConnectionRespInfo by adding accessors to get at the actual
# response content.
# ------------------------------------------------------------------------------
class IZHttpConnectionResp(IZHttpConnectionRespInfo):
    
    def getContentStream(self):
        u"""getContentStream() -> stream
        Returns a file-like object for the content for this
        response.""" #$NON-NLS-1$
    # end getContentStream
    
    def getContent(self):
        u"""getContent() -> data[]
        Returns the content data for this response.""" #$NON-NLS-1$
    # end getContent()
    
    def getContentFilename(self):
        u"""getContentFilename() -> string
        Returns the filename where the content for this response
        is stored.""" #$NON-NLS-1$
    # end getContentFilename()

# end IZHttpConnectionResp


# ------------------------------------------------------------------------------
# A simple implementation of a connection response info.
# ------------------------------------------------------------------------------
class ZHttpConnectionRespInfo(IZHttpConnectionRespInfo):

    def __init__(self, url, code, message, headers):
        self.url = url
        self.code = code
        self.message = message
        self.headers = headers
    # end __init__()
    
    def getURL(self):
        return self.url
    # end getURL()

    def getCode(self):
        return self.code
    # end getCode()
    
    def getMessage(self):
        return self.message
    # end getMessage()
    
    def getHeaders(self):
        return self.headers
    # end getHeaders()
    
    def getHeader(self, name):
        if name in self.headers:
            return self.headers[name]
        return None
    # end getHeader()
    
    def getContentType(self):
        return self.getHeader(u"content-type") #$NON-NLS-1$
    # end getContentType()
    
    def getContentLength(self):
        cl = self.getHeader(u"content-length") #$NON-NLS-1$
        if cl is not None:
            return long(cl)
        return None
    # end getContentLength()

# end ZHttpConnectionRespInfo


# ------------------------------------------------------------------------------
# A simple implementation of a connection response.
# ------------------------------------------------------------------------------
class ZHttpConnectionResp(ZHttpConnectionRespInfo, IZHttpConnectionResp):

    def __init__(self, url, code, message, headers, contentFilename):
        ZHttpConnectionRespInfo.__init__(self, url, code, message, headers)

        self.contentFilename = contentFilename
    # end __init__()

    def getContentLength(self):
        if os.path.isfile(self.contentFilename):
            return getFileMetaData(self.contentFilename)[2]

        return ZHttpConnectionRespInfo.getContentLength(self)
    # end getContentLength()

    def getContentStream(self):
        if not os.path.isfile(self.contentFilename):
            raise ZAppFrameworkException(u"%s: '%s'." % (_extstr(u"connresp.NoContentFoundError"), self.contentFilename)) #$NON-NLS-1$ #$NON-NLS-2$
        return open(self.contentFilename)
    # end getContentStream
    
    def getContent(self):
        file = self.getContentStream()
        try:
            return file.read()
        finally:
            file.close()
    # end getContent()
    
    def getContentFilename(self):
        return self.contentFilename
    # end getContentFilename()

# end ZHttpConnectionResp
