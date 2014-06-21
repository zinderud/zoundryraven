from shutil import move
from zoundry.appframework.services.urlfetch.connresp import ZHttpConnectionResp
from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.zdom.dom import ZDom
import os

# ------------------------------------------------------------------------------
# The interface for the URL cache.  Manages cached Http Connection Response
# objects.
# ------------------------------------------------------------------------------
class IZURLCache:

    def get(self, url):
        u"""get(string) -> IZHttpConnectionResp
        Gets the cached connection response for the given URL or
        None if the URL is not in the cache.""" #$NON-NLS-1$
    # end get()

    def put(self, connectionRespInfo, contentFilename):
        u"""put(IZHttpConnectionRespInfo, string) -> IZHttpConnectionResp
        Adds the given connection response to the cache.""" #$NON-NLS-1$
    # end put()

# end IZURLCache


# ------------------------------------------------------------------------------
# Interface used by the cached http connection response object.
# ------------------------------------------------------------------------------
class IZURLMetaData:

    def getURL(self):
        u"""getURL() -> string
        Returns the url.""" #$NON-NLS-1$
    # end getURL()

    def getResponseCode(self):
        u"""getResponseCode() -> string""" #$NON-NLS-1$
    # end getResponseCode()

    def getResponseMessage(self):
        u"""getResponseMessage() -> string""" #$NON-NLS-1$
    # end getResponseMessage()

    def getResponseHeaders(self):
        u"""getResponseHeaders() -> map""" #$NON-NLS-1$
    # end getResponseHeaders()

# end IZURLMetaData


# ------------------------------------------------------------------------------
# Simple container impl of url meta data.
# ------------------------------------------------------------------------------
class ZURLMetaData(IZURLMetaData):

    def __init__(self, url, respCode, respMessage, headers):
        self.url = url
        self.respCode = respCode
        self.respMessage = respMessage
        self.headers = headers
    # end __init__()

    def getURL(self):
        return self.url
    # end getURL()

    def getResponseCode(self):
        return self.respCode
    # end getResponseCode()

    def getResponseMessage(self):
        return self.respMessage
    # end getResponseMessage()

    def getResponseHeaders(self):
        return self.headers
    # end getResponseHeaders()

# end ZURLMetaData


# ------------------------------------------------------------------------------
# An impl of a connection response from cached information.
# ------------------------------------------------------------------------------
class ZCachedHttpConnectionResp(ZHttpConnectionResp):

    def __init__(self, urlMetaData, contentFilename):
        url = urlMetaData.getURL()
        code = urlMetaData.getResponseCode()
        message = urlMetaData.getResponseMessage()
        headers = urlMetaData.getResponseHeaders()

        ZHttpConnectionResp.__init__(self, url, code, message, headers, contentFilename)
    # end __init__()

# end ZCachedHttpConnectionResp


# ------------------------------------------------------------------------------
# A convenience class for reading information from the meta data file in the
# file url cache.
# ------------------------------------------------------------------------------
class ZURLMetaDataReader(IZURLMetaData):

    def __init__(self, dom):
        self.dom = dom
    # end __init__()

    def getURL(self):
        return self.dom.selectSingleNodeText(u"/http-connection-response/url") #$NON-NLS-1$
    # end getURL()

    def getDataFile(self):
        return self.dom.selectSingleNodeText(u"/http-connection-response/data-file") #$NON-NLS-1$
    # end getDataFile()

    def getResponseCode(self):
        return int(self.dom.selectSingleNodeText(u"/http-connection-response/response-code")) #$NON-NLS-1$
    # end getResponseCode()

    def getResponseMessage(self):
        return self.dom.selectSingleNodeText(u"/http-connection-response/response-message") #$NON-NLS-1$
    # end getResponseMessage()

    def getResponseHeaders(self):
        nodes = self.dom.selectNodes(u"/http-connection-response/response-headers/header") #$NON-NLS-1$
        rval = {}
        for node in nodes:
            rval[node.getAttribute(u"name")] = node.getText() #$NON-NLS-1$
        return rval
    # end getResponseHeaders()

# end ZURLMetaDataReader


# ------------------------------------------------------------------------------
# A file-based implementation of a URL cache.
# ------------------------------------------------------------------------------
class ZFileURLCache(IZURLCache):

    def __init__(self, cacheDir):
        self.cacheDir = cacheDir
    # end __init__()

    def get(self, url):
        urlHash = self._hashUrl(url)
        urlDir = os.path.join(self.cacheDir, urlHash)
        if not os.path.isdir(urlDir):
            return None
        urlMetaFile = os.path.join(urlDir, u"meta-data.xml") #$NON-NLS-1$
        if not os.path.isfile(urlMetaFile):
            return None
        urlMetaDom = ZDom()
        urlMetaDom.load(urlMetaFile)
        urlMetaData = ZURLMetaDataReader(urlMetaDom)
        if url != urlMetaData.getURL():
            return None
        dataFile = os.path.join(urlDir, urlMetaData.getDataFile())
        if not os.path.isfile(dataFile):
            return None
        return ZCachedHttpConnectionResp(urlMetaData, dataFile)
    # end get()

    def put(self, connectionRespInfo, contentFilename):
        urlHash = self._hashUrl(connectionRespInfo.getURL())
        urlDir = os.path.join(self.cacheDir, urlHash)
        if os.path.exists(urlDir):
            deleteDirectory(urlDir, False)
        else:
            os.makedirs(urlDir)
        urlMetaFile = os.path.join(urlDir, u"meta-data.xml") #$NON-NLS-1$
        dataFName = self._getContentFilename(contentFilename)
        self._serializeResponseInfo(urlMetaFile, connectionRespInfo, dataFName)
        dataFile = os.path.join(urlDir, dataFName)
        move(contentFilename, dataFile)

        # Now return a full IZHttpConnectionResp object based on the cached info.
        url = connectionRespInfo.getURL()
        code = connectionRespInfo.getCode()
        message = connectionRespInfo.getMessage()
        headers = connectionRespInfo.getHeaders()
        return ZHttpConnectionResp(url, code, message, headers, dataFile)
    # end put()

    def _getContentFilename(self, contentFilename):
        (root, ext) = os.path.splitext(contentFilename) #@UnusedVariable
        return u"data" + ext #$NON-NLS-1$
    # end _getContentFilename()

    def _serializeResponseInfo(self, metaFile, connectionRespInfo, dataFilename):
        dom = ZDom()
        dom.loadXML(u"""<http-connection-response />""") #$NON-NLS-1$
        rootElem = dom.documentElement
        urlElem = dom.createElement(u"url") #$NON-NLS-1$
        urlElem.setText(connectionRespInfo.getURL())
        rootElem.appendChild(urlElem)

        dataFileElem = dom.createElement(u"data-file") #$NON-NLS-1$
        dataFileElem.setText(dataFilename)
        rootElem.appendChild(dataFileElem)

        respCodeElem = dom.createElement(u"response-code") #$NON-NLS-1$
        respCodeElem.setText(unicode(connectionRespInfo.getCode()))
        rootElem.appendChild(respCodeElem)

        respMsgElem = dom.createElement(u"response-message") #$NON-NLS-1$
        respMsgElem.setText(unicode(connectionRespInfo.getMessage()))
        rootElem.appendChild(respMsgElem)

        headersElem = dom.createElement(u"response-headers") #$NON-NLS-1$
        rootElem.appendChild(headersElem)

        for headerName in connectionRespInfo.getHeaders():
            headerVal = connectionRespInfo.getHeader(headerName)
            headerElem = dom.createElement(u"header") #$NON-NLS-1$
            headerElem.setAttribute(u"name", headerName) #$NON-NLS-1$
            headerElem.setText(headerVal)
            headersElem.appendChild(headerElem)

        dom.save(metaFile, True)
    # end _serializeResponseInfo()

    def _hashUrl(self, url):
        return unicode(abs(hash(url)))
    # end _hashUrl()

# end ZFileURLCache
