from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.actions.link.linkactionctx import ZLinkActionContext
from zoundry.appframework.ui.menus.link.linkmenumodel import ZLinkMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.base.util.urlutil import decodeUri
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.indeximpl import ZLinkIDO
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
from zoundry.blogapp.ui.views.viewselimpl import ZLinkSelection
import wx

# ----------------------------------------------------------------------------------------
# The content provider used for the list of links in the post.
# ----------------------------------------------------------------------------------------
class ZLinkListViewContentProvider(IZListViewExContentProvider):

    def __init__(self):
        self.imageList = ZMappedImageList()
        self.links = []
    # end __init__()

    def getLink(self, index):
        return self.links[index]
    # end getLink()

    def setDocument(self, document):
        xhtmlDoc = document.getContent().getXhtmlDocument()
        self.links = xhtmlDoc.getLinks()
    # end setDocument()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.links)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        columnName = None
        if columnIndex == 0:
            columnName = _extstr(u"linkdetails.LinkURL") #$NON-NLS-1$
        return (columnName, None, 0, ZListViewEx.COLUMN_RELATIVE | ZListViewEx.COLUMN_LOCKED, 100)
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return decodeUri(self.links[rowIndex].getHref())
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

# end ZLinkListViewContentProvider


# ----------------------------------------------------------------------------------------
# A concrete impl of a blog post details panel.  This one shows 'links' information
# about the blog post.
# ----------------------------------------------------------------------------------------
class ZLinkBlogPostDetailsPanel(ZAbstractDetailsPanel):

    def __init__(self, parent):
        self.selectedLink = None
        self.document = None
        # FIXME (EPW) need to update the value of self.blog in onSelectionChanged()
        self.blog = None
        self.linkContentProvider = ZLinkListViewContentProvider()

        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.NO_BORDER
        self.linkListView = ZListViewEx(self.linkContentProvider, self, style = style)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected, self.linkListView)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onActivated, self.linkListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self.linkListView)

        wx.EVT_SET_FOCUS(self.linkListView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.linkListView, self.onUnFocus)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        linkSBSizer = wx.BoxSizer(wx.HORIZONTAL)
        linkSBSizer.Add(self.linkListView, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(linkSBSizer, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def onSelectionChanged(self, document):
        self.document = document
        self.selectedLink = None
        self.linkContentProvider.setDocument(document)
        self.linkListView.refresh()
    # end onSelectionChanged()

    def onSelected(self, event):
        link = self.linkContentProvider.getLink(event.GetIndex())
        self.selectedLink = link
        self._fireLinkSelectionEvent(link)
        event.Skip()
    # end onSelected()

    def onActivated(self, event):
        url = self.linkListView.GetItemText(event.GetIndex())
        if url:
            context = ZLinkActionContext(self, url)
            openLinkAction = getApplicationModel().getActionRegistry().findAction(IZAppActionIDs.OPEN_LINK_ACTION)
            openLinkAction.runAction(context)
        event.Skip
    # end onActivated()

    def onRightClick(self, event):
        url = self.linkListView.GetItemText(event.GetIndex())
        if url:
            context = ZLinkActionContext(self, url)
            menuModel = ZLinkMenuModel()
            menu = ZModelBasedMenu(menuModel, context, self)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onRightClick()

    def onFocus(self, event):
        self._fireLinkSelectionEvent(self.selectedLink)
        event.Skip()
    # end onFocus()

    def onUnFocus(self, event):
        fireViewUnselectionEvent()
        event.Skip()
    # end onUnFocus()

    def _fireLinkSelectionEvent(self, link):
        if link:
            linkIDO = ZLinkIDO(None, self.document.getId(), link.getHref())
            linkSelection = ZLinkSelection(linkIDO, self.blog)
            fireViewSelectionEvent(linkSelection, None)
    # end _fireLinkSelectionEvent()

# end ZLinkBlogPostDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a blog post details panel factory that creates a panel for "Link"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZLinkBlogPostDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZLinkBlogPostDetailsPanel(parent)
    # end createDetailsPanel()

# end ZLinkBlogPostDetailsPanelFactory
