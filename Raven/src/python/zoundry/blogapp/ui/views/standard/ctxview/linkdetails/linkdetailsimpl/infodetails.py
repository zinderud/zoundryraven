from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.urlfetch.urlfetchsvc import IZURLFetchListener
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.ui.common.blogpostswidgets import ZBlogPostsListByLinkQueryModel
from zoundry.blogapp.ui.common.blogpostswidgets import ZWhereFoundBlogPostListView
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
from zoundry.blogapp.ui.views.standard.ctxview.linkdetails.linkdetailsimpl.infodetailswidgets import ZLinkSummaryPanel
import wx

# ----------------------------------------------------------------------------------------
# The model used by the "link info" details panel - the details panel that shows info
# about a selected link.
# ----------------------------------------------------------------------------------------
class ZInfoLinkDetailsModel(ZBlogPostsListByLinkQueryModel):

    def __init__(self):
        ZBlogPostsListByLinkQueryModel.__init__(self)
        self.urlFetchService = getApplicationModel().getService(IZAppServiceIDs.URL_FETCH_SERVICE_ID)
    # end __init__()

    def getUrlFetchService(self):
        return self.urlFetchService
    # end getUrlFetchService()

# end ZInfoLinkDetailsModel



# ----------------------------------------------------------------------------------------
# A helper class for executing code that updates the details panel UI.  This class is
# needed because we want to run the code on the UI thread.
# ----------------------------------------------------------------------------------------
class ZInfoLinkDetailsPanelUIUpdater(IZRunnable):

    MODE_CONNECT = 0
    MODE_CONNECT_ERROR = 1
    MODE_DOWNLOAD_START = 2
    MODE_DOWNLOAD = 3
    MODE_DOWNLOAD_COMPLETE = 4
    MODE_DOWNLOAD_ERROR = 5

    def __init__(self, panel, data, mode):
        self.panel = panel
        self.data = data
        self.mode = mode
    # end __init__()

    def run(self):
        if self.mode == ZInfoLinkDetailsPanelUIUpdater.MODE_CONNECT:
            self.panel.updateFromConnectionRespInfo(self.data)
        elif self.mode == ZInfoLinkDetailsPanelUIUpdater.MODE_CONNECT_ERROR:
            self.panel.updateFromConnectionError(self.data)
        elif self.mode == ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD_COMPLETE:
            self.panel.updateFromConnectionResp(self.data)
        elif self.mode == ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD_ERROR:
            self.panel.updateFromDownloadError(self.data)
    # end run()

# end ZInfoLinkDetailsPanelUIUpdater

# ----------------------------------------------------------------------------------------
# A concrete impl of a link details panel.  This one shows 'general' information
# about the link.
# ----------------------------------------------------------------------------------------
class ZInfoLinkDetailsPanel(ZAbstractDetailsPanel, IZURLFetchListener):

    def __init__(self, parent):
        self.model = ZInfoLinkDetailsModel()
        self.fetcher = None
        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        self.summary = ZLinkSummaryPanel(self)
        self.blogPostListView = ZWhereFoundBlogPostListView(self, self.model)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.summary, 0, wx.EXPAND | wx.BOTTOM, 5)
        vBox.Add(self.blogPostListView, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(vBox, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def destroy(self):
        # Cancel any Link fetching that might be going on
        if self.fetcher is not None and not self.fetcher.isDone():
            self.fetcher.cancel()
    # end destroy()

    def onSelectionChanged(self, data):
        (blog, linkIDO) = data #@UnusedVariable

        # Cancel any Link fetching that might be going on
        if self.fetcher is not None and not self.fetcher.isDone():
            self.fetcher.cancel()

        # Set the current linkIDO in the model
        self.model.setLinkIDO(linkIDO)

        # Reset the UI for the widgets
        self.summary.reset()
        self.Layout()

        # Refresh the list of blog posts
        self.blogPostListView.refresh()

        # Start fetching the link in the background - events will update the UI
        url = linkIDO.getUrl()
        self.fetcher = self.model.getUrlFetchService().fetch(url, self)
    # end onSelectionChanged()

    def updateFromConnectionError(self, error):
        self.summary.updateFromError(error)
        self.Layout()
    # end updateFromConnectionRespInfo()

    def updateFromConnectionRespInfo(self, connectionRespInfo):
        self.summary.updateFromConnectionRespInfo(connectionRespInfo)
        self.Layout()
    # end updateFromConnectionRespInfo()

    def updateFromDownloadError(self, error):
        self.summary.updateFromError(error)
        self.Layout()
    # end updateFromDownloadError()

    def updateFromConnectionResp(self, connectionResp):
        self.summary.updateFromConnectionResp(connectionResp)
        self.Layout()
    # end updateFromConnectionResp()

    def onCancel(self, fetcher):
        if self.fetcher == fetcher:
            self.fetcher = None
    # end onCancel()

    def onConnect(self, fetcher, connectionRespInfo): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, connectionRespInfo, ZInfoLinkDetailsPanelUIUpdater.MODE_CONNECT)
        fireUIExecEvent(updater, self)
    # end onConnect()

    def onConnectError(self, fetcher, error): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, error, ZInfoLinkDetailsPanelUIUpdater.MODE_CONNECT_ERROR)
        fireUIExecEvent(updater, self)
    # end onConnectError()

    def onContentDownloadStart(self, fetcher, contentLength): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, contentLength, ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD_START)
        fireUIExecEvent(updater, self)
    # end onContentDownloadStart()

    def onContentDownload(self, fetcher, numBytes): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, numBytes, ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD)
        fireUIExecEvent(updater, self)
    # end onContentDownload()

    def onContentDownloadComplete(self, fetcher, connectionResp): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, connectionResp, ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD_COMPLETE)
        fireUIExecEvent(updater, self)
    # end onContentDownloadComplete()

    def onContentDownloadError(self, fetcher, error): #@UnusedVariable
        updater = ZInfoLinkDetailsPanelUIUpdater(self, error, ZInfoLinkDetailsPanelUIUpdater.MODE_DOWNLOAD_ERROR)
        fireUIExecEvent(updater, self)
    # end onContentDownloadError()

# end ZInfoLinkDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a link details panel factory that creates a panel for "Link Info"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZInfoLinkDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZInfoLinkDetailsPanel(parent)
    # end createDetailsPanel()

# end ZInfoLinkDetailsPanelFactory
