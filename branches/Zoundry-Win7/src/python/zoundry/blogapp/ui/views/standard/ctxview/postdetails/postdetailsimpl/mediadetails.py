from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.actions.image.imageactionctx import ZImageActionContext
from zoundry.appframework.ui.menus.image.imagemenumodel import ZImageMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.appframework.ui.widgets.controls.list import IZListViewContentProvider
from zoundry.base.util.urlutil import decodeUri
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
import wx

# ----------------------------------------------------------------------------------------
# The content provider used for the list of images in the post.
# ----------------------------------------------------------------------------------------
class ZMediaListViewContentProvider(IZListViewContentProvider):

    def __init__(self):
        self.imageList = ZMappedImageList()
        self.images = []
    # end __init__()

    def setDocument(self, document):
        xhtmlDoc = document.getContent().getXhtmlDocument()
        self.images = xhtmlDoc.getImages()
    # end setDocument()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.images)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        columnName = None
        if columnIndex == 0:
            columnName = _extstr(u"mediadetails.MediaSource") #$NON-NLS-1$
        return (columnName, None, 0, ZListViewEx.COLUMN_RELATIVE | ZListViewEx.COLUMN_LOCKED, 100)
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return decodeUri(self.images[rowIndex].getSrc())
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

# end ZMediaListViewContentProvider


# ----------------------------------------------------------------------------------------
# A concrete impl of a blog post details panel.  This one shows 'media' information
# about the blog post.
# ----------------------------------------------------------------------------------------
class ZMediaBlogPostDetailsPanel(ZAbstractDetailsPanel):

    def __init__(self, parent):
        self.imageContentProvider = ZMediaListViewContentProvider()

        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.NO_BORDER
        self.imageListView = ZListViewEx(self.imageContentProvider, self, style = style)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onActivated, self.imageListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self.imageListView)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        imageSBSizer = wx.BoxSizer(wx.HORIZONTAL)
        imageSBSizer.Add(self.imageListView, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(imageSBSizer, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def onSelectionChanged(self, document):
        self.imageContentProvider.setDocument(document)
        self.imageListView.refresh()
    # end onSelectionChanged()

    def onActivated(self, event):
        url = self.imageListView.GetItemText(event.GetIndex())
        if url:
            context = ZImageActionContext(self, url)
            openAction = getApplicationModel().getActionRegistry().findAction(IZAppActionIDs.OPEN_IMAGE_ACTION)
            openAction.runAction(context)
        event.Skip
    # end onActivated()

    def onRightClick(self, event):
        url = self.imageListView.GetItemText(event.GetIndex())
        if url:
            context = ZImageActionContext(self, url)
            menuModel = ZImageMenuModel()
            menu = ZModelBasedMenu(menuModel, context, self)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onRightClick()

# end ZMediaBlogPostDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a blog post details panel factory that creates a panel for "Media"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZMediaBlogPostDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZMediaBlogPostDetailsPanel(parent)
    # end createDetailsPanel()

# end ZMediaBlogPostDetailsPanelFactory

