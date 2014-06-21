from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.urlfetch.connresp import ZHttpConnectionRespInfo
from zoundry.appframework.services.urlfetch.urlcache import ZCachedHttpConnectionResp
from zoundry.appframework.services.urlfetch.urlcache import ZFileURLCache
from zoundry.appframework.services.urlfetch.urlcache import ZURLMetaData
from zoundry.appframework.services.urlfetch.urlfetchsvc import IZURLFetchListener
from zoundry.appframework.services.urlfetch.urlfetchsvc import IZURLFetchService
from zoundry.appframework.services.urlfetch.urlfetchsvc import IZURLFetcher
from zoundry.base.exceptions import ZException
from zoundry.base.net.http import IZHttpBinaryFileDownloadListener
from zoundry.base.net.http import ZHttpBinaryFileDownload
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.guid import generate
from zoundry.base.util.urlutil import decodeUri
from zoundry.base.util.zthread import ZThread
from zoundry.base.xhtml.xhtmltelements import ZUrl
import os
import string


# ------------------------------------------------------------------------------
# Listener interface that extends the binary file download listener interface
# in order to add an entry point for onConnect().
# ------------------------------------------------------------------------------
class IZURLFetchHttpBinaryFileDownloadListener(IZHttpBinaryFileDownloadListener):

    def transferConnected(self, response):
        u"Called when the connection is made." #$NON-NLS-1$
    # end transferConnected()

# end IZURLFetchHttpBinaryFileDownloadListener


# ------------------------------------------------------------------------------
# Extends the basic binary file downloader in order to add some additional
# processing of the response HTTP protocol information (code, message, headers).
# ------------------------------------------------------------------------------
class ZURLFetchHttpBinaryFileDownload(ZHttpBinaryFileDownload):

    def __init__(self, url, filename, listener, customHeaders = None):
        ZHttpBinaryFileDownload.__init__(self, url, filename, listener, customHeaders)
    # end __init__()

    # Called after the connection has been established.
    def _processResponse(self, response):
        self.listener.transferConnected(response)
        ZHttpBinaryFileDownload._processResponse(self, response)
    # end _processResponse()

    def _processError(self, response):
        self.listener.transferError(ZException(response.reason))
    # end _processError()

# end ZURLFetchHttpBinaryFileDownload


# ------------------------------------------------------------------------------
# Adapts a url fetch listener into a binary download listener.
# ------------------------------------------------------------------------------
class ZBinaryDownloadListenerAdapter(IZURLFetchHttpBinaryFileDownloadListener):

    def __init__(self, url, urlFetcher, urlFetchListener, cache, tempFile):
        self.url = url
        self.urlFetcher = urlFetcher
        self.urlFetchListener = urlFetchListener
        self.cache = cache
        self.tempFile = tempFile
    # end __init__()

    def transferConnected(self, response):
        code = response.status
        message = response.reason
        headers = {}
        for (name, val) in response.getheaders():
            headers[name] = val
        self.connectionRespInfo = ZHttpConnectionRespInfo(self.url.toString(), code, message, headers)
        if not self.urlFetcher.isCancelled():
            self.urlFetchListener.onConnect(self.urlFetcher, self.connectionRespInfo)
    # end transferConnected()

    def transferStarted(self, contentType, contentLength): #@UnusedVariable
        if not self.urlFetcher.isCancelled():
            self.urlFetchListener.onContentDownloadStart(self.urlFetcher, contentLength)
    # end transferStarted()

    def transferBlock(self, blockLength):
        if not self.urlFetcher.isCancelled():
            self.urlFetchListener.onContentDownload(self.urlFetcher, blockLength)
    # end transferBlock()

    def transferComplete(self):
        connectionResp = self.cache.put(self.connectionRespInfo, self.tempFile)
        if not self.urlFetcher.isCancelled():
            self.urlFetchListener.onContentDownloadComplete(self.urlFetcher, connectionResp)
    # end transferComplete()

    def transferError(self, zexception):
        if not self.urlFetcher.isCancelled():
            self.urlFetchListener.onContentDownloadError(self.urlFetcher, zexception)
    # end transferError()

    def transferCancelled(self):
        # Do nothing - onCancel callback happens immediately.
        pass
    # end transferCancelled()

# end ZBinaryDownloadListenerAdapter


# ------------------------------------------------------------------------------
# Implements the fetcher interface.  This is a concrete implementation of a
# fetcher that actually does the work of connecting to a remove host and
# downloading the content.
# FIXME (EPW) support multiple listeners
# ------------------------------------------------------------------------------
class ZURLFetcher(ZThread, IZURLFetcher):

    def __init__(self, cache, url, listener, useCache, tempDir):
        self.cache = cache
        self.url = url
        self.listener = listener
        self.useCache = useCache
        self.tempDir = tempDir
        self.cancelled = False
        self.downloader = None

        ZThread.__init__(self, name = u"ZURLFetcher", daemonic = True) #$NON-NLS-1$
    # end __init__()

    def _run(self):
        connectionResp = None
        if self.useCache:
            connectionResp = self.cache.get(self.url)

        if connectionResp is not None:
            self._runFromCache(connectionResp)
        else:
            self._runLive()
    # end _run()

    def _runFromCache(self, connectionResp):
        if self.cancelled:
            return
        self.listener.onConnect(self, connectionResp)
        cl = connectionResp.getContentLength()
        self.listener.onContentDownloadStart(self, cl)
        self.listener.onContentDownload(self, cl)
        self.listener.onContentDownloadComplete(self, connectionResp)
    # end _runFromCache()

    def _runLive(self):
        if self.cancelled:
            return
        url = ZUrl(self.url)
        protocol = string.lower(url.getProtocol())
        if protocol == u"http" or protocol == u"https": #$NON-NLS-1$ #$NON-NLS-2$
            self._runLiveHttp(url)
        elif protocol == u"file": #$NON-NLS-1$
            self._runLiveFile(self.url)
        else:
            self.listener.onConnectError(self, ZAppFrameworkException(u"Unsupported protocol.")) #$NON-NLS-1$
    # end _runLive

    def _runLiveHttp(self, url):
        if self.cancelled:
            return
        try:
            tempFile = os.path.join(self.tempDir, generate() + u".bin") #$NON-NLS-1$
            listener = ZBinaryDownloadListenerAdapter(url, self, self.listener, self.cache, tempFile)
            self.downloader = ZURLFetchHttpBinaryFileDownload(url.toString(), tempFile, listener)
            self.downloader.send()
        except Exception, e:
            self.listener.onConnectError(self, e)
    # end _runLiveHttp()

    def _runLiveFile(self, url):
        if self.cancelled:
            return
        try:
            path = decodeUri(url)
            if not os.path.exists(path):
                raise ZAppFrameworkException(u"File does not exist.") #$NON-NLS-1$

            (shortFileName, absFileName, fileSize, timestamp) = getFileMetaData(path) #@UnusedVariable
            fileExt = os.path.splitext(path)[1][1:]
            mimeService = getApplicationModel().getService(IZAppServiceIDs.MIMETYPE_SERVICE_ID)
            mimeType = mimeService.getMimeType(fileExt)
            headers = {
                    u"content-type" : mimeType.toString(), #$NON-NLS-1$
                    u"Content-Type" : mimeType.toString(), #$NON-NLS-1$
                    u"content-length" : unicode(fileSize), #$NON-NLS-1$
                    u"Content-Length" : unicode(fileSize) #$NON-NLS-1$
            }
            urlMetaData = ZURLMetaData(url, 200, u"OK", headers) #$NON-NLS-1$
            response = ZCachedHttpConnectionResp(urlMetaData, path)
            self._runFromCache(response)
        except Exception, e:
            self.listener.onConnectError(self, e)
    # end _runLiveFile()

    def cancel(self):
        # Note: clear out the listener
        oldListener = self.listener
        self.listener = IZURLFetchListener()
        oldListener.onCancel(self)

        self.cancelled = True
        if self.downloader is not None:
            self.downloader.cancel()
    # end cancel()

    def isFetching(self):
        return not self.isDone()
    # end isFetching()

    def isComplete(self):
        return self.isDone()
    # end isComplete()

    def isCancelled(self):
        return self.cancelled
    # end isCancelled()

# end ZURLFetcher


# ------------------------------------------------------------------------------
# The implementation of the URL Fetch Service.
# ------------------------------------------------------------------------------
class ZURLFetchService(IZURLFetchService):

    def __init__(self):
        self.cacheDir = None
        self.cache = None
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.cacheDir = applicationModel.getUserProfile().getDirectory(u"url-cache") #$NON-NLS-1$
        self.tempDir = applicationModel.getUserProfile().getTempDirectory()
        self.cache = ZFileURLCache(self.cacheDir)
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)

        self.logger.debug(u"URL Fetch Service started.") #$NON-NLS-1$
    # end start()

    def stop(self):
        self.cacheDir = None
        self.cache = None
    # end stop()

    def fetch(self, url, listener, useCache = True):
        fetcher = ZURLFetcher(self.cache, url, listener, useCache, self.tempDir)
        fetcher.start()
        return fetcher
    # end fetch()

# end ZURLFetchService
