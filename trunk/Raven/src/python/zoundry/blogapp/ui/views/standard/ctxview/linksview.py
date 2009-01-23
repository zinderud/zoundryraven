from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.models.ui.widgets.treemodel import ZTreeNodeBasedContentProvider
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.actions.link.linkactionctx import ZLinkIDOActionContext
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.splitterevents import ZEVT_SPLITTER_SASH_POS_CHANGED
from zoundry.appframework.ui.menus.link.linkmenumodel import ZLinkMenuModel
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.advanced.textbox import ZAdvancedTextBox
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.appframework.ui.widgets.controls.tree import ZTreeView
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.views.standard.ctxview.linksviewmodel import ZContextInfoLinksModel
from zoundry.blogapp.models.views.standard.ctxview.linksviewmodel import ZLinkIDONode
from zoundry.blogapp.services.docindex.index import IZLinkSearchFilter
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocumentIndexListener
from zoundry.blogapp.services.docindex.indeximpl import ZLinkSearchFilter
from zoundry.blogapp.ui.events.viewevents import VIEWLINKSFILTERCHANGEDEVENT
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.events.viewevents import ZViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.linksummaryview import ZLinkSummaryView
from zoundry.blogapp.ui.views.view import IZViewIds
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZLinkSelection
import wx

IMAGE_LIST_DATA = [
       (u"site", u"images/perspectives/standard/contextinfo/linksview/site.png"), #$NON-NLS-1$ #$NON-NLS-2$
       (u"link", u"images/perspectives/standard/contextinfo/linksview/link.png"), #$NON-NLS-1$ #$NON-NLS-2$
]

SEARCH_HOST = 0


# --------------------------------------------------------------------------------------
# Content provider for the links tree view.
# --------------------------------------------------------------------------------------
class ZLinkTreeContentProvider(ZTreeNodeBasedContentProvider):

    def __init__(self, model):
        self.model = model
        self.imageList = self._createImageList()

        ZTreeNodeBasedContentProvider.__init__(self, None, self.imageList)
    # end __init__()

    def _createImageList(self):
        imgList = ZMappedImageList()
        for (label, imagePath) in IMAGE_LIST_DATA:
            imgList.addImage(label, getResourceRegistry().getBitmap(imagePath))
        return imgList
    # end _createImageList()

    def getRootNode(self):
        return self.model.getRootNode()
    # end getRootNode()

# end ZLinkTreeContentProvider


# --------------------------------------------------------------------------------------
# Boxed view that shows the tree/list of links.
# --------------------------------------------------------------------------------------
class ZLinksView(ZBoxedView, IZDocumentIndexListener):

    def __init__(self, parent):
        self.link = None
        self.blog = None
        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.model = ZContextInfoLinksModel(ZLinkSearchFilter())
        self.openLinkAction = getApplicationModel().getActionRegistry().findAction(IZAppActionIDs.OPEN_LINK_ACTION)

        ZBoxedView.__init__(self, parent)

        self._registerAsIndexListener()

        self.validSelection = False
    # end __init__()

    def getViewId(self):
        return IZViewIds.LINKS_LIST_VIEW
    # end getViewId()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/links.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"linksview.Links") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        choices = self._getSearchBoxChoices()
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/contextinfo/linksview/search.png") #$NON-NLS-1$
        self.searchTextBox = ZAdvancedTextBox(parent, bitmap, choices, False)
        self.searchTextBox.setCurrentChoice(SEARCH_HOST)
        self.searchTextBox.SetSizeHints(220, -1)

        widgetList.append(self.searchTextBox)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        treeStyle = wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_HAS_BUTTONS | wx.NO_BORDER
        provider = ZLinkTreeContentProvider(self.model)
        self.linksTreeView = ZTreeView(provider, parent, style = treeStyle)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.linksTreeView, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onLinkActivated, self.linksTreeView)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onLinkRightClick, self.linksTreeView)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onLinkSelected, self.linksTreeView)
#        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onEntryBeginDrag, self.linksTreeView)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearchText, self.searchTextBox)
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
        wx.EVT_SET_FOCUS(self.linksTreeView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.linksTreeView, self.onUnFocus)
    # end _bindWidgetEvents()

    def refreshContent(self, selection):
        (accountId, blogId) = selection.getData()

        filter = ZLinkSearchFilter()
        if blogId is not None:
            account = self.accountStore.getAccountById(accountId)
            self.blog = account.getBlogById(blogId)
            filter.setAccountIdCriteria(accountId)
            filter.setBlogIdCriteria(blogId)
        else:
            self.blog = None
            filter.setAccountIdCriteria(IZLinkSearchFilter.UNPUBLISHED_ACCOUNT_ID)
            filter.setBlogIdCriteria(IZLinkSearchFilter.UNPUBLISHED_BLOG_ID)

        self.model = ZContextInfoLinksModel(filter)
        self.linksTreeView.setContentProvider(ZLinkTreeContentProvider(self.model))
        self.linksTreeView.refresh()
        self.linksTreeView.deselectAll()
        self.onInvalidSelection()
        fireViewUnselectionEvent()
    # end refreshContent()

    def onViewSelectionChanged(self, event):
        if event.getSelection().getType() == IZViewSelectionTypes.BLOG_LINKS_SELECTION:
            self.refreshContent(event.getSelection())
    # end onViewSelectionChanged()

    def onFocus(self, event):
        if self.link:
            fireViewSelectionEvent(ZLinkSelection(self.link, self.blog), self)
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end onFocus()

    def onUnFocus(self, event):
        fireViewUnselectionEvent()
        event.Skip()
    # end onUnFocus()

    def onSearchText(self, event):
        self.model.setHostCriteria(event.GetString())
        self.model.refresh()
        self.linksTreeView.clear()
        self.linksTreeView.refresh()
        self.linksTreeView.deselectAll()
        self.onInvalidSelection()
        
        fireViewEvent(ZViewEvent(VIEWLINKSFILTERCHANGEDEVENT, self))
        event.Skip()
    # end onSearchText()
#
#    def onEntryBeginDrag(self, event):
#        index = event.GetIndex()
#        docIDO = self.model.getEntry(index)
#        docId = docIDO.getId()
#
#        # FIXME also add some sort of custom format for dragging to the Explorer/TextPad (use a composite data object)
#        data = ZBlogPostDataObjectInternal(docId)
#        dragSource = wx.DropSource(self)
#        dragSource.SetData(data)
#        dragSource.DoDragDrop(wx.Drag_CopyOnly)
#        event.Skip()
#    # end onEntryBeginDrag()

    def _updateModel(self, refreshData):
        (eventType, linkIDO) = refreshData
        shouldRefresh = False
        if eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD:
            shouldRefresh = self.model.addLink(linkIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE:
            shouldRefresh = self.model.removeLink(linkIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_UPDATE:
            shouldRefresh = self.model.updateLink(linkIDO)
        return shouldRefresh
    # end _updateModel()

    # This is the only method that can happen on a non-UI thread.  It will
    # gather up the needed data, then fire a "refresh ui" event.  That event
    # will get picked up by the UI thread and the view will refresh.
    def onIndexChange(self, event):
        if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_LINK:
            refreshData = (event.getEventType(), event.getLinkIDO())
            fireRefreshEvent(self, refreshData)
    # end onIndexChange()

    def onZoundryRefresh(self, event):
        if self._updateModel(event.getData()):
            self.linksTreeView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onLinkActivated(self, event):
        node = self.linksTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZLinkIDONode):
            link = node.getLinkIDO()
            context = ZLinkIDOActionContext(self, link)
            self.openLinkAction.runAction(context)
        event.Skip
    # end onLinkActivated()

    def onLinkRightClick(self, event):
        node = self.linksTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZLinkIDONode):
            link = node.getLinkIDO()
            context = ZLinkIDOActionContext(self, link)
            menuModel = ZLinkMenuModel()
            menu = ZModelBasedMenu(menuModel, context, self)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onLinkRightClick()

    def onLinkSelected(self, event):
        node = self.linksTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZLinkIDONode):
            self.link = node.getLinkIDO()

            if self.link:
                fireViewSelectionEvent(ZLinkSelection(self.link, self.blog), self)
            else:
                fireViewUnselectionEvent()
        event.Skip()
    # end onLinkSelected()

    def onInvalidSelection(self):
        self.link = None
    # end onInvalidSelection()

    def destroy(self):
        self._unregisterAsIndexListener()
    # end destroy()

    def _registerAsIndexListener(self):
        self.indexService.addListener(self)
    # end _registerAsIndexListener()

    def _unregisterAsIndexListener(self):
        self.indexService.removeListener(self)
    # end _unregisterAsIndexListener()

    def _getSearchBoxChoices(self):
        return [
                (u"Host", None, SEARCH_HOST), #$NON-NLS-1$
        ]
    # end _getSearchBoxChoices()

# end ZLinksView


# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected the "Links" sub-item of a Blog in the Navigator.  When that selection is
# made, the list of links for that blog needs to be shown.
# --------------------------------------------------------------------------------------
class ZContextInfoLinksView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.sashPosition = 0

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getViewId(self):
        return IZViewIds.LINKS_VIEW
    # end getViewId()

    def _createWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)

        self.linksView = ZLinksView(self.splitterWindow)
        self.linkSummaryView = ZLinkSummaryView(self.splitterWindow)

        self.splitterWindow.SplitHorizontally(self.linksView, self.linkSummaryView)
        self.splitterWindow.SetMinimumPaneSize(100)
        self.splitterWindow.SetSashSize(8)
        self.splitterWindow.SetSashGravity(0.0)
    # end _createWidgets()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.splitterWindow, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def _populateWidgets(self):
        self._restoreSashPosition()
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_SPLITTER_SASH_POS_CHANGED, self.onSashPosChanged, self.splitterWindow)
    # end _bindWidgetEvents

    def onSashPosChanged(self, event):
        self.sashPosition = self.splitterWindow.GetSashPosition()
        event.Skip()
    # end onSashPosChanged()

    def destroy(self):
        self._saveSashPosition()

        self.linksView.destroy()
        self.linkSummaryView.destroy()
    # end destroy()

    def _saveSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.LINKS_VIEW_SASH_POS, self.splitterWindow.GetSashPosition())
    # end _saveSashPosition()

    def _restoreSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.sashPosition = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.LINKS_VIEW_SASH_POS, 200)
        self.splitterWindow.SetSashPosition(self.sashPosition)
    # end _restoreSashPosition()

# end ZContextInfoLinksView
