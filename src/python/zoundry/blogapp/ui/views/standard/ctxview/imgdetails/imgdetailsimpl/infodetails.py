from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.urlfetch.urlfetchsvc import IZURLFetchListener
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.ui.common.blogpostswidgets import ZBlogPostsListByImageQueryModel
from zoundry.blogapp.ui.common.blogpostswidgets import ZWhereFoundBlogPostListView
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
from zoundry.blogapp.ui.views.standard.ctxview.imgdetails.imgdetailsimpl.infodetailswidgets import ZImagePreviewPanel
from zoundry.blogapp.ui.views.standard.ctxview.imgdetails.imgdetailsimpl.infodetailswidgets import ZImageSummaryPanel
import wx

# ----------------------------------------------------------------------------------------
# The model used by the "image info" details panel - the details panel that shows info
# about a selected image.
# ----------------------------------------------------------------------------------------
class ZInfoImageDetailsModel(ZBlogPostsListByImageQueryModel):

    def __init__(self):
        ZBlogPostsListByImageQueryModel.__init__(self)
        self.urlFetchService = getApplicationModel().getService(IZAppServiceIDs.URL_FETCH_SERVICE_ID)
        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
    # end __init__()

    def getUrlFetchService(self):
        return self.urlFetchService
    # end getUrlFetchService()

# end ZInfoImageDetailsModel


# ----------------------------------------------------------------------------------------
# A helper class for executing code that updates the details panel UI.  This class is
# needed because we want to run the code on the UI thread.
# ----------------------------------------------------------------------------------------
class ZInfoImageDetailsPanelUIUpdater(IZRunnable):

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
        if self.mode == ZInfoImageDetailsPanelUIUpdater.MODE_CONNECT:
            self.panel.updateFromConnectionRespInfo(self.data)
        elif self.mode == ZInfoImageDetailsPanelUIUpdater.MODE_CONNECT_ERROR:
            self.panel.updateFromConnectionError(self.data)
        elif self.mode == ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD_COMPLETE:
            self.panel.updateFromConnectionResp(self.data)
        elif self.mode == ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD_ERROR:
            self.panel.updateFromDownloadError(self.data)
    # end run()

# end ZInfoImageDetailsPanelUIUpdater


# ----------------------------------------------------------------------------------------
# A concrete impl of a image details panel.  This one shows 'general' information
# about the image.
# ----------------------------------------------------------------------------------------
class ZInfoImageDetailsPanel(ZAbstractDetailsPanel, IZURLFetchListener):

    def __init__(self, parent):
        self.model = ZInfoImageDetailsModel()
        self.fetcher = None
        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        self.imagePreview = ZImagePreviewPanel(self)
        self.summary = ZImageSummaryPanel(self)
        self.blogPostListView = ZWhereFoundBlogPostListView(self, self.model)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.summary, 0, wx.EXPAND | wx.BOTTOM, 5)
        vBox.Add(self.blogPostListView, 1, wx.EXPAND)

        hBox = wx.BoxSizer(wx.HORIZONTAL)
        hBox.Add(self.imagePreview, 0)
        hBox.AddSizer(vBox, 1, wx.EXPAND | wx.LEFT, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(hBox, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def destroy(self):
        # Cancel any Image fetching that might be going on
        if self.fetcher is not None and not self.fetcher.isDone():
            self.fetcher.cancel()
    # end destroy()

    def onSelectionChanged(self, data):
        (blog, imageIDO) = data #@UnusedVariable
        
        # Cancel any Image fetching that might be going on
        if self.fetcher is not None and not self.fetcher.isDone():
            self.fetcher.cancel()

        # Set the current imageIDO in the model
        self.model.setImageIDO(imageIDO)

        # Reset the UI for the widgets
        self.imagePreview.reset()
        self.summary.reset()
        self.Layout()

        # Refresh the list of blog posts
        self.blogPostListView.refresh()

        # Start fetching the image in the background - events will update the UI
        url = imageIDO.getUrl()
        self.fetcher = self.model.getUrlFetchService().fetch(url, self)
    # end onSelectionChanged()

    def updateFromConnectionError(self, error):
        self.imagePreview.updateFromError(error)
        self.summary.updateFromError(error)
        self.Layout()
    # end updateFromConnectionError()

    def updateFromConnectionRespInfo(self, connectionRespInfo):
        self.imagePreview.updateFromConnectionRespInfo(connectionRespInfo)
        self.summary.updateFromConnectionRespInfo(connectionRespInfo)
        self.Layout()
    # end updateFromConnectionRespInfo()

    def updateFromDownloadError(self, error):
        self.imagePreview.updateFromError(error)
        self.summary.updateFromError(error)
        self.Layout()
    # end updateFromDownloadError()

    def updateFromConnectionResp(self, connectionResp):
        self.imagePreview.updateFromConnectionResp(connectionResp)
        self.summary.updateFromConnectionResp(connectionResp)
        self.Layout()
    # end updateFromConnectionResp()

    def onCancel(self, fetcher):
        if self.fetcher == fetcher:
            self.fetcher = None
    # end onCancel()

    def onConnect(self, fetcher, connectionRespInfo): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, connectionRespInfo, ZInfoImageDetailsPanelUIUpdater.MODE_CONNECT)
        fireUIExecEvent(updater, self)
    # end onConnect()

    def onConnectError(self, fetcher, error): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, error, ZInfoImageDetailsPanelUIUpdater.MODE_CONNECT_ERROR)
        fireUIExecEvent(updater, self)
    # end onConnectError()

    def onContentDownloadStart(self, fetcher, contentLength): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, contentLength, ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD_START)
        fireUIExecEvent(updater, self)
    # end onContentDownloadStart()

    def onContentDownload(self, fetcher, numBytes): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, numBytes, ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD)
        fireUIExecEvent(updater, self)
    # end onContentDownload()

    def onContentDownloadComplete(self, fetcher, connectionResp): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, connectionResp, ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD_COMPLETE)
        fireUIExecEvent(updater, self)
    # end onContentDownloadComplete()

    def onContentDownloadError(self, fetcher, error): #@UnusedVariable
        updater = ZInfoImageDetailsPanelUIUpdater(self, error, ZInfoImageDetailsPanelUIUpdater.MODE_DOWNLOAD_ERROR)
        fireUIExecEvent(updater, self)
    # end onContentDownloadError()

# end ZInfoImageDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a image details panel factory that creates a panel for "Image Info"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZInfoImageDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZInfoImageDetailsPanel(parent)
    # end createDetailsPanel()

# end ZInfoImageDetailsPanelFactory
