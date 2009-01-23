from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# The interface for a listener of a single URL fetch thread.  The listener 
# will get called back for various events in the life cycle of the fetch.
# ------------------------------------------------------------------------------
class IZURLFetchListener:
    
    def onCancel(self, fetcher):
        u"""onCancel(IZURLFetcher) -> None
        The URL fetch was cancelled.""" #$NON-NLS-1$
    # end onCancel()
    
    def onConnect(self, fetcher, connectionRespInfo):
        u"""onConnect(IZURLFetcher, IZHttpConnectionRespInfo) -> None
        Called when a connection is successfully made to the URL's
        host.""" #$NON-NLS-1$
    # end onConnect()
    
    def onConnectError(self, fetcher, error):
        u"""onConnectError(IZURLFetcher, error) -> None
        Called when there is an error when trying to make the initial
        connection to the host.""" #$NON-NLS-1$
    # end onConnectError()

    def onContentDownloadStart(self, fetcher, contentLength):
        u"""onContentDownloadStart(IZURLFetcher, int) -> None
        Called once the download of the content has begun.""" #$NON-NLS-1$
    # end onContentDownloadStart()
    
    def onContentDownload(self, fetcher, numBytes):
        u"""onContentDownload(IZURLFetcher, int) -> None
        Called (potentially multiple times) each time a block
        of data is downloaded.""" #$NON-NLS-1$
    # end onContentDownload()

    def onContentDownloadComplete(self, fetcher, connectionResp):
        u"""onContentDownloadComplete(IZURLFetcher, IZHttpConnectionResp) -> None
        Called once the content has been completely downloaded.""" #$NON-NLS-1$
    # end onContentDownloadComplete()
    
    def onContentDownloadError(self, fetcher, error):
        u"""onContentDownloadError(IZURLFetcher, error) -> None
        Called if there is an error while downloading the content.""" #$NON-NLS-1$
    # end onContentDownloadError()

# end IZURLFetchListener


# ------------------------------------------------------------------------------
# Interface for the URL fetcher.  This is the interface that is returned to the
# caller of IZURLFetchService::fetch().
# ------------------------------------------------------------------------------
class IZURLFetcher:
    
    def cancel(self):
        u"""cancel() -> None
        Cancels the fetch.""" #$NON-NLS-1$
    # end cancel()
    
    def isFetching(self):
        u"""isFetching() -> boolean
        Returns True if the fetcher is running.""" #$NON-NLS-1$
    # end isFetching()
    
    def isComplete(self):
        u"""isComplete() -> boolean
        Returns True if the fetch is complete.""" #$NON-NLS-1$
    # end isComplete()
    
    def isCancelled(self):
        u"""isCancelled() -> boolean
        Returns True if the fetcher has been cancelled.""" #$NON-NLS-1$
    # end isCancelled()

# end IZURLFetcher


# ------------------------------------------------------------------------------
# Interface for the URL fetch service.  This service is used to download the
# meta data and content for a single URL.  A listener is provided which is used
# to call back with the information about the URL (meta data, content).
# ------------------------------------------------------------------------------
class IZURLFetchService(IZService):

    def fetch(self, url, listener, useCache = True):
        u"""fetch(string, IZURLFetchListener, boolean) -> IZURLFetcher
        Begins fetching the information about the given URL.  This
        means making a (potentially remote) connection to the url's
        address and downloading the meta data and content found at
        that location.  Redirects are followed.""" #$NON-NLS-1$
    # end fetch()

# end IZURLFetchService
