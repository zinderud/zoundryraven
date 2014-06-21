from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.models.ui.widgets.treemodel import ZTreeNodeBasedContentProvider
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.actions.image.imageactionctx import ZImageIDOActionContext
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.splitterevents import ZEVT_SPLITTER_SASH_POS_CHANGED
from zoundry.appframework.ui.menus.image.imagemenumodel import ZImageMenuModel
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.advanced.textbox import ZAdvancedTextBox
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.appframework.ui.widgets.controls.tree import ZTreeView
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.views.standard.ctxview.imgsviewmodel import ZContextInfoImagesModel
from zoundry.blogapp.models.views.standard.ctxview.imgsviewmodel import ZImageIDONode
from zoundry.blogapp.services.docindex.index import IZImageSearchFilter
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocumentIndexListener
from zoundry.blogapp.services.docindex.indeximpl import ZImageSearchFilter
from zoundry.blogapp.ui.events.viewevents import VIEWIMAGESFILTERCHANGEDEVENT
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.events.viewevents import ZViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.imagesummaryview import ZImageSummaryView
from zoundry.blogapp.ui.views.view import IZViewIds
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZImageSelection
import wx

IMAGE_LIST_DATA = [
       (u"site", u"images/perspectives/standard/contextinfo/imagesview/site.png"), #$NON-NLS-1$ #$NON-NLS-2$
       (u"image", u"images/perspectives/standard/contextinfo/imagesview/image.png"), #$NON-NLS-1$ #$NON-NLS-2$
]

SEARCH_HOST = 0


# --------------------------------------------------------------------------------------
# Content provider for the images tree view.
# --------------------------------------------------------------------------------------
class ZImageTreeContentProvider(ZTreeNodeBasedContentProvider):

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

# end ZImageTreeContentProvider


# --------------------------------------------------------------------------------------
# Boxed view that shows the tree/list of images.
# --------------------------------------------------------------------------------------
class ZImagesView(ZBoxedView, IZDocumentIndexListener):

    def __init__(self, parent):
        self.image = None
        self.blog = None
        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.model = ZContextInfoImagesModel(ZImageSearchFilter())
        self.openImageAction = getApplicationModel().getActionRegistry().findAction(IZAppActionIDs.OPEN_IMAGE_ACTION)

        ZBoxedView.__init__(self, parent)

        self._registerAsIndexListener()

        self.validSelection = False
    # end __init__()

    def getViewId(self):
        return IZViewIds.IMAGES_LIST_VIEW
    # end getViewId()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/images.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"imagesview.Images") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        choices = self._getSearchBoxChoices()
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/contextinfo/imagesview/search.png") #$NON-NLS-1$
        self.searchTextBox = ZAdvancedTextBox(parent, bitmap, choices, False)
        self.searchTextBox.setCurrentChoice(SEARCH_HOST)
        self.searchTextBox.SetSizeHints(220, -1)

        widgetList.append(self.searchTextBox)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        treeStyle = wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_HAS_BUTTONS | wx.NO_BORDER
        provider = ZImageTreeContentProvider(self.model)
        self.imagesTreeView = ZTreeView(provider, parent, style = treeStyle)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.imagesTreeView, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onImageActivated, self.imagesTreeView)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onImageRightClick, self.imagesTreeView)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onImageSelected, self.imagesTreeView)
#        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onEntryBeginDrag, self.imagesTreeView)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearchText, self.searchTextBox)
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
        wx.EVT_SET_FOCUS(self.imagesTreeView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.imagesTreeView, self.onUnFocus)
    # end _bindWidgetEvents()

    def refreshContent(self, selection):
        (accountId, blogId) = selection.getData()

        filter = ZImageSearchFilter()
        if blogId is not None:
            account = self.accountStore.getAccountById(accountId)
            self.blog = account.getBlogById(blogId)
            filter.setAccountIdCriteria(accountId)
            filter.setBlogIdCriteria(blogId)
        else:
            self.blog = None
            filter.setAccountIdCriteria(IZImageSearchFilter.UNPUBLISHED_ACCOUNT_ID)
            filter.setBlogIdCriteria(IZImageSearchFilter.UNPUBLISHED_BLOG_ID)

        self.model = ZContextInfoImagesModel(filter)
        self.imagesTreeView.setContentProvider(ZImageTreeContentProvider(self.model))
        self.imagesTreeView.refresh()
        self.imagesTreeView.deselectAll()
        self.onInvalidSelection()
        fireViewUnselectionEvent()
    # end refreshContent()

    def _getSearchBoxChoices(self):
        return [
                (u"Host", None, SEARCH_HOST), #$NON-NLS-1$
        ]
    # end _getSearchBoxChoices()

    def onViewSelectionChanged(self, event):
        if event.getSelection().getType() == IZViewSelectionTypes.BLOG_IMAGES_SELECTION:
            self.refreshContent(event.getSelection())
    # end onViewSelectionChanged()

    def onFocus(self, event):
        if self.image:
            fireViewSelectionEvent(ZImageSelection(self.image, self.blog), self)
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
        self.imagesTreeView.clear()
        self.imagesTreeView.refresh()
        self.imagesTreeView.deselectAll()
        self.onInvalidSelection()
        
        fireViewEvent(ZViewEvent(VIEWIMAGESFILTERCHANGEDEVENT, self))
        event.Skip()
    # end onSearchText()

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
        (eventType, imageIDO) = refreshData
        shouldRefresh = False
        if eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD:
            shouldRefresh = self.model.addImage(imageIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE:
            shouldRefresh = self.model.removeImage(imageIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_UPDATE:
            shouldRefresh = self.model.updateImage(imageIDO)
        return shouldRefresh
    # end _updateModel()

    # This is the only method that can happen on a non-UI thread.  It will
    # gather up the needed data, then fire a "refresh ui" event.  That event
    # will get picked up by the UI thread and the view will refresh.
    def onIndexChange(self, event):
        if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_IMAGE:
            refreshData = (event.getEventType(), event.getImageIDO())
            fireRefreshEvent(self, refreshData)
    # end onIndexChange()

    def onZoundryRefresh(self, event): #@UnusedVariable
        if self._updateModel(event.getData()):
            self.imagesTreeView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onImageActivated(self, event):
        node = self.imagesTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZImageIDONode):
            image = node.getImageIDO()
            context = ZImageIDOActionContext(self, image)
            self.openImageAction.runAction(context)
        event.Skip
    # end onImageActivated()

    def onImageRightClick(self, event):
        node = self.imagesTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZImageIDONode):
            link = node.getImageIDO()
            context = ZImageIDOActionContext(self, link)
            menuModel = ZImageMenuModel()
            menu = ZModelBasedMenu(menuModel, context, self)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onImageRightClick()

    def onImageSelected(self, event):
        node = self.imagesTreeView.GetPyData(event.GetItem())
        if isinstance(node, ZImageIDONode):
            self.image = node.getImageIDO()
            if self.image:
                fireViewSelectionEvent(ZImageSelection(self.image, self.blog), self)
            else:
                fireViewUnselectionEvent()
        event.Skip()
    # end onImageSelected()

    def onInvalidSelection(self):
        self.image = None
    # end onInvalidSelection()

    def _registerAsIndexListener(self):
        self.indexService.addListener(self)
    # end _registerAsIndexListener()

    def _unregisterAsIndexListener(self):
        self.indexService.removeListener(self)
    # end _unregisterAsIndexListener()

    def destroy(self):
        self._unregisterAsIndexListener()
    # end destroy()

# end ZImagesView


# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected the "Images" sub-item of a Blog in the Navigator.  When that selection is
# made, the list of images for that blog needs to be shown.
# --------------------------------------------------------------------------------------
class ZContextInfoImagesView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.sashPosition = 0

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getViewId(self):
        return IZViewIds.IMAGES_VIEW
    # end getViewId()

    def _createWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)

        self.imagesView = ZImagesView(self.splitterWindow)
        self.imageSummaryView = ZImageSummaryView(self.splitterWindow)

        self.splitterWindow.SplitHorizontally(self.imagesView, self.imageSummaryView)
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
        self.imagesView.destroy()
        self.imageSummaryView.destroy()
    # end destroy()

    def _saveSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.IMAGES_VIEW_SASH_POS, self.splitterWindow.GetSashPosition())
    # end _saveSashPosition()

    def _restoreSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.sashPosition = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.IMAGES_VIEW_SASH_POS, 200)
        self.splitterWindow.SetSashPosition(self.sashPosition)
    # end _restoreSashPosition()

# end ZContextInfoImagesView
