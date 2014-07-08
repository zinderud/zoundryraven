from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.splitterevents import ZEVT_SPLITTER_SASH_POS_CHANGED
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.advanced.textbox import ZAdvancedTextBox
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.base.util.dateutil import getRangeForThisMonth
from zoundry.base.util.dateutil import getRangeForThisWeek
from zoundry.base.util.dateutil import getRangeForToday
from zoundry.base.util.dateutil import getRangeForYesterday
from zoundry.blogapp.constants import IZBlogAppAcceleratorIds
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.views.standard.ctxview.postsviewmodel import ZContextInfoPostsModel
from zoundry.blogapp.services.docindex.index import IZDocumentSearchFilter
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocumentIndexListener
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentSearchFilter
from zoundry.blogapp.ui.dnd.blogpostdnd import ZBlogPostDataObjectInternal
from zoundry.blogapp.ui.events.viewevents import VIEWBLOGPOSTSFILTERCHANGEDEVENT
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.events.viewevents import ZViewEvent
from zoundry.blogapp.ui.menus.blogpost.postmenu import ZBlogPostActionContext
from zoundry.blogapp.ui.menus.blogpost.postmenumodel import ZBlogPostMenuModel
from zoundry.blogapp.ui.util.dateformatutil import formatLocalDateAndTime
from zoundry.blogapp.ui.util.viewutil import fireViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.postsummaryview import ZBlogPostSummaryView
from zoundry.blogapp.ui.views.view import IZViewIds
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZDocumentSelection
from zoundry.blogapp.services.docindex.index import IZBlogBasedSearchFilter
import wx

SEARCH_TB_TITLE = 0
SEARCH_TB_TAG_HOST = 1

IMAGE_LIST_DATA = [
       (u"document", u"images/perspectives/standard/contextinfo/postsview/document.png"), #$NON-NLS-1$ #$NON-NLS-2$
       (u"draft", u"images/perspectives/standard/contextinfo/postsview/draft.png"), #$NON-NLS-1$ #$NON-NLS-2$
       (u"dirty", u"images/perspectives/standard/contextinfo/postsview/draft.png") #$NON-NLS-1$ #$NON-NLS-2$
]

VIEW_CHOICE_ALL = 0
VIEW_CHOICE_DRAFTS = 1
VIEW_CHOICE_PUBLISHED = 2
VIEW_CHOICE_TODAY = 3

VIEW_CHOICE_YESTERDAY = 5
VIEW_CHOICE_THISWEEK = 6
VIEW_CHOICE_THISMONTH = 7


# --------------------------------------------------------------------------------------
# The content provider for the list of blog entries.
# --------------------------------------------------------------------------------------
class ZBlogEntryListContentProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model
        self.imageList = self._createImageList()

        cstyle = wx.LIST_FORMAT_LEFT
        self.columnInfo = [
            (_extstr(u"postsview.Title"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 70), #$NON-NLS-1$
            (_extstr(u"postsview.Published"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30), #$NON-NLS-1$
            (_extstr(u"postsview.LastModified"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30) #$NON-NLS-1$
        ]
    # end __init__()

    def _createImageList(self):
        imgList = ZMappedImageList()
        for (label, imagePath) in IMAGE_LIST_DATA:
            imgList.addImage(label, getResourceRegistry().getBitmap(imagePath))
        return imgList
    # end _createImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 2
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getEntries())
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        columnInfo = self.columnInfo[columnIndex]
        blogId = self.model.getCurrentFilter().getBlogIdCriteria()
        if columnIndex == 1 and blogId == IZBlogBasedSearchFilter.UNPUBLISHED_BLOG_ID:
            columnInfo = self.columnInfo[2]
        return columnInfo
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        data = self.model.getEntries()[rowIndex]
        if columnIndex == 0:
            title = data.getTitle()
            if not title:
                title = u"(%s)" % _extstr(u"postsview.NoTitle") #$NON-NLS-1$ #$NON-NLS-2$
            return title
        if columnIndex == 1:
            blogId = self.model.getCurrentFilter().getBlogIdCriteria()
            pdIDO = data.getPubDataIDO(blogId)
            if pdIDO:
                return formatLocalDateAndTime( pdIDO.getPublishedTime() )
            else:
                return formatLocalDateAndTime( data.getLastModifiedTime())
        return u"" #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex):
        if columnIndex == 0:
            data = self.model.getEntries()[rowIndex]
            blogId = self.model.getCurrentFilter().getBlogIdCriteria()
            pdIDO = data.getPubDataIDO(blogId)
            if pdIDO is not None:
                if pdIDO.getDraft():
                    return self.imageList[u"draft"] #$NON-NLS-1$
                if pdIDO.getSynchTime() is not None and data.getLastModifiedTime() > pdIDO.getSynchTime():
                    return self.imageList[u"dirty"] #$NON-NLS-1$
            return self.imageList[u"document"] #$NON-NLS-1$
        return -1
    # end getRowImage()

# end ZBlogEntryListContentProvider


# ------------------------------------------------------------------------------
# Accelerator table for the list of blog posts.
# ------------------------------------------------------------------------------
class ZBlogPostsListAcceleratorTable(ZAcceleratorTable):

    def __init__(self, view):
        self.view = view
        ZAcceleratorTable.__init__(self, IZBlogAppAcceleratorIds.ZID_BLOG_POST_LIST_ACCEL)
    # end __init__()

    def _createActionContext(self):
        return self.view.createActionContext()
    # end _createActionContext()

    def _loadAdditionalEntries(self):
        return [
            ZAcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DELETE, getApplicationModel().getActionRegistry().findAction(IZBlogAppActionIDs.DELETE_BLOG_POST_ACTION))
        ]
    # end _loadAdditionalEntries()

# end ZBlogPostsListAcceleratorTable


# --------------------------------------------------------------------------------------
# Boxed view that shows a list of blog posts.  This view will change whenever a new
# "Posts" folder is selected in the Navigator.
# --------------------------------------------------------------------------------------
class ZBlogPostsView(ZBoxedView, IZDocumentIndexListener):

    def __init__(self, parent):
        filter = ZDocumentSearchFilter()
        filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)
        self.model = ZContextInfoPostsModel(filter)
        self.openAction = getApplicationModel().getActionRegistry().findAction(IZBlogAppActionIDs.OPEN_BLOG_POST_ACTION)
        self.blogPostContextMenu = ZBlogPostMenuModel()
        self.postsAccelTable = ZBlogPostsListAcceleratorTable(self)
        self.document = None
        self.blog = None
        self.hasFocus = False

        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        self.docStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)

        ZBoxedView.__init__(self, parent)

        self._registerAsIndexListener()
    # end __init__()

    def getViewId(self):
        return IZViewIds.POSTS_LIST_VIEW
    # end getViewId()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/posts.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"postsview.BlogPosts") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        self.viewLabel = wx.StaticText(parent, wx.ID_ANY, _extstr(u"postsview.Filter")) #$NON-NLS-1$
        choices = self._getViewChoices()
        self.viewCombo = wx.ComboBox(parent, wx.ID_ANY, _extstr(u"postsview.All"), style = wx.CB_READONLY, choices = choices) #$NON-NLS-1$
        choices = self._getSearchBoxChoices()
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/contextinfo/postsview/search.png") #$NON-NLS-1$
        self.searchTextBox = ZAdvancedTextBox(parent, bitmap, choices, False)
        self.searchTextBox.setCurrentChoice(SEARCH_TB_TITLE)
        self.searchTextBox.SetSizeHints(220, -1)

        widgetList.append(self.viewLabel)
        widgetList.append(self.viewCombo)
        widgetList.append(self.searchTextBox)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        provider = ZBlogEntryListContentProvider(self.model)
        style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER
        self.entriesListView = ZListViewEx(provider, parent, style = style)
        self.entriesListView.SetAcceleratorTable(self.postsAccelTable)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.entriesListView, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.postsAccelTable.bindTo(self.entriesListView)

        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEntryActivated, self.entriesListView)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onEntrySelected, self.entriesListView)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onEntryBeginDrag, self.entriesListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onEntryRightClick, self.entriesListView)
        self.Bind(wx.EVT_COMBOBOX, self.onViewCombo, self.viewCombo)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearchText, self.searchTextBox)
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
        wx.EVT_SET_FOCUS(self.entriesListView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.entriesListView, self.onUnFocus)
    # end _bindWidgetEvents()

    def refreshContent(self, selection):
        isUnselecting = False
        if self.entriesListView.getSelection():
            isUnselecting = True

        (accountId, blogId) = selection.getData()

        filter = ZDocumentSearchFilter()
        if blogId is not None:
            account = self.accountStore.getAccountById(accountId)
            self.blog = account.getBlogById(blogId)
            filter.setAccountIdCriteria(accountId)
            filter.setBlogIdCriteria(blogId)
        else:
            self.blog = None
            filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
            filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)

        self.model = ZContextInfoPostsModel(filter)
        self.entriesListView.setContentProvider(ZBlogEntryListContentProvider(self.model))
        self.entriesListView.refresh()
        self.entriesListView.deselectAll()
        self.onInvalidSelection()
        if isUnselecting:
            fireViewUnselectionEvent()
    # end refreshContent()

    def onViewSelectionChanged(self, event):
        if event.getSelection().getType() == IZViewSelectionTypes.BLOG_POSTS_SELECTION:
            self.refreshContent(event.getSelection())
        event.Skip()
    # end onViewSelectionChanged()

    def onFocus(self, event):
        if not self.hasFocus:
            if self.document:
                fireViewSelectionEvent(ZDocumentSelection(self.document, self.blog), self)
            else:
                fireViewUnselectionEvent()
            self.hasFocus = True
        event.Skip()
    # end onFocus()

    def onUnFocus(self, event):
        if self.hasFocus:
            fireViewUnselectionEvent()
            self.hasFocus = False
        event.Skip()
    # end onUnFocus()

    def onViewCombo(self, event):
        choice = event.GetSelection()
        self.model.clearDraftCriteria()
        self.model.clearDateRangeCriteria()
        if choice == VIEW_CHOICE_DRAFTS:
            self.model.setDraftCriteria()
        elif choice == VIEW_CHOICE_PUBLISHED:
            self.model.setDraftCriteria(False)
        elif choice == VIEW_CHOICE_TODAY:
            dateRange = getRangeForToday()
            self.model.setDateRangeCriteria(dateRange.getStartDate(), dateRange.getEndDate())
        elif choice == VIEW_CHOICE_YESTERDAY:
            dateRange = getRangeForYesterday()
            self.model.setDateRangeCriteria(dateRange.getStartDate(), dateRange.getEndDate())
        elif choice == VIEW_CHOICE_THISWEEK:
            dateRange = getRangeForThisWeek()
            self.model.setDateRangeCriteria(dateRange.getStartDate(), dateRange.getEndDate())
        elif choice == VIEW_CHOICE_THISMONTH:
            dateRange = getRangeForThisMonth()
            self.model.setDateRangeCriteria(dateRange.getStartDate(), dateRange.getEndDate())
        self.model.refresh()
        self.entriesListView.refresh()
        self.entriesListView.deselectAll()
        self.onInvalidSelection()

        fireViewEvent(ZViewEvent(VIEWBLOGPOSTSFILTERCHANGEDEVENT, self))
        event.Skip()
    # end onViewCombo()

    def onSearchText(self, event):
        self.model.setTitleCriteria(event.GetString())
        self.model.refresh()
        self.entriesListView.refresh()
        self.entriesListView.deselectAll()
        self.onInvalidSelection()

        fireViewEvent(ZViewEvent(VIEWBLOGPOSTSFILTERCHANGEDEVENT, self))
        event.Skip()
    # end onSearchText()

    def onEntryBeginDrag(self, event):
        index = event.GetIndex()
        docIDO = self.model.getEntry(index)
        docId = docIDO.getId()

        # FIXME (EPW) also add some sort of custom format for dragging to the Explorer/TextPad (use a composite data object)
        data = wx.DataObjectComposite()
#        url = self._getUrlFromDocIDO(docIDO)
#        if url is not None:
#            data.Add(ZURLDataObject(url))
        data.Add(ZBlogPostDataObjectInternal(docId))
#        data.Add(wx.TextDataObject(str(convertToUtf8(u"Hello World"))))

        dragSource = wx.DropSource(self)
        dragSource.SetData(data)
        dragSource.DoDragDrop(wx.Drag_CopyOnly)
        event.Skip()
    # end onEntryBeginDrag()

    def _updateModel(self, refreshData):
        (eventType, documentIDO) = refreshData
        shouldRefresh = False
        if eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD:
            shouldRefresh = self.model.addEntry(documentIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE:
            shouldRefresh = self.model.removeEntry(documentIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_UPDATE:
            shouldRefresh = self.model.updateEntry(documentIDO)
        return shouldRefresh
    # end _updateModel()

    # This is the only method that can happen on a non-UI thread.  It will
    # gather up the needed data, then fire a "refresh ui" event.  That event
    # will get picked up by the UI thread and the view will refresh.
    def onIndexChange(self, event):
        if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_DOCUMENT:
            refreshData = (event.getEventType(), event.getDocumentIDO())
            fireRefreshEvent(self, refreshData)
    # end onIndexChange()

    def onZoundryRefresh(self, event): #@UnusedVariable
        if self._updateModel(event.getData()):
            self.entriesListView.refresh()
            selection = self.entriesListView.getSelection()
            if not selection:
                self.onInvalidSelection()
                fireViewUnselectionEvent()
            else:
                selIdx = selection[0]
                newDocIDO = self.model.getEntry(selIdx)
                newDoc = self.docStore.getDocument(newDocIDO.getId())
                self.document = newDoc
                fireViewSelectionEvent(ZDocumentSelection(self.document, self.blog), self)
        event.Skip()
    # end onZoundryRefresh()

    def onEntryRightClick(self, event):
        index = event.GetIndex()
        docIDO = self.model.getEntry(index)
        blogId = None
        if self.blog is not None:
            blogId = self.blog.getId()
        actionContext = ZBlogPostActionContext(self, docIDO, blogId)
        provider = ZModelBasedMenuContentProvider(self.blogPostContextMenu, actionContext)
        handler = ZModelBasedMenuEventHandler(self.blogPostContextMenu, actionContext)
        menu = ZMenu(self, self.blogPostContextMenu.getRootNode(), provider, handler)
        self.PopupMenu(menu)
        event.Skip()
    # end onEntryRightClick()

    def onEntryActivated(self, event):
        index = event.GetIndex()
        docIDO = self.model.getEntry(index)
        blogId = None
        if self.blog is not None:
            blogId = self.blog.getId()
        actionContext = ZBlogPostActionContext(self, docIDO, blogId)
        self.openAction.runAction(actionContext)
        event.Skip()
    # end onEntryActivated()

    def onEntrySelected(self, event):
        index = event.GetIndex()
        docIDO = self.model.getEntry(index)
        docId = docIDO.getId()
        self.document = self.docStore.getDocument(docId)

        if self.document:
            fireViewSelectionEvent(ZDocumentSelection(self.document, self.blog), self)
        else:
            fireViewUnselectionEvent()

        event.Skip()
    # end onEntrySelected()

    def onInvalidSelection(self):
        self.document = None
    # end onInvalidSelection()

    def createActionContext(self):
        docIDO = None
        blogId = None
        selection = self.entriesListView.getSelection()
        if selection:
            index = selection[0]
            docIDO = self.model.getEntry(index)
            if self.blog is not None:
                blogId = self.blog.getId()
        return ZBlogPostActionContext(self, docIDO, blogId)
    # end createActionContext()

    def destroy(self):
        self._unregisterAsIndexListener()
    # end destroy()

    def _getViewChoices(self):
        return [
                _extstr(u"postsview.All"), #$NON-NLS-1$
                _extstr(u"postsview.Drafts"), #$NON-NLS-1$
                _extstr(u"postsview.Published"), #$NON-NLS-1$
                _extstr(u"postsview.Today"), #$NON-NLS-1$
                u"-----------", #$NON-NLS-1$
                _extstr(u"postsview.Yesterday"), #$NON-NLS-1$
                _extstr(u"postsview.ThisWeek"), #$NON-NLS-1$
                _extstr(u"postsview.ThisMonth") #$NON-NLS-1$
        ]
    # end _getViewChoices()

    def _getSearchBoxChoices(self):
        return [
                (_extstr(u"postsview.Title"), None, SEARCH_TB_TITLE), #$NON-NLS-1$
        ]
    # end _getSearchBoxChoices()

    def _getUrlFromDocIDO(self, docIDO):
        url = None
        if self.blog is not None:
            pdIDO = docIDO.getPubDataIDO(self.blog.getId())
            if pdIDO is not None:
                url = pdIDO.getUrl()
        return url
    # end _getUrlFromDocIDO()

    def _registerAsIndexListener(self):
        self.indexService.addListener(self)
    # end _registerAsIndexListener()

    def _unregisterAsIndexListener(self):
        self.indexService.removeListener(self)
    # end _unregisterAsIndexListener()

# end ZBlogPostsView


# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected the "Posts" sub-item of a Blog in the Navigator.  When that selection is made,
# the list of posts for that blog need to be shown.
# --------------------------------------------------------------------------------------
class ZContextInfoPostsView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.sashPosition = 0

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getViewId(self):
        return IZViewIds.POSTS_VIEW
    # end getViewId()

    def _createWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)

        self.blogPostsView = ZBlogPostsView(self.splitterWindow)
        self.blogPostSummaryView = ZBlogPostSummaryView(self.splitterWindow)

        self.splitterWindow.SplitHorizontally(self.blogPostsView, self.blogPostSummaryView)
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
    # end _bindWidgetEvents()

    def onSashPosChanged(self, event):
        self.sashPosition = self.splitterWindow.GetSashPosition()
        event.Skip()
    # end onSashPosChanged()

    def destroy(self):
        self._saveSashPosition()
        self.blogPostsView.destroy()
        self.blogPostSummaryView.destroy()
    # end destroy()

    def _saveSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.POSTS_VIEW_SASH_POS, self.sashPosition)
    # end _saveSashPosition()

    def _restoreSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.sashPosition = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.POSTS_VIEW_SASH_POS, 200)
        self.splitterWindow.SetSashPosition(self.sashPosition)
    # end _restoreSashPosition()

# end ZContextInfoPostsView

#by pitchaimuthu
class ZContextInfoEditedView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.sashPosition = 0

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getViewId(self):
        return IZViewIds.POSTS_VIEW
    # end getViewId()

    def _createWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)

        self.blogPostsView = ZBlogPostsView(self.splitterWindow)
        self.blogPostSummaryView = ZBlogPostSummaryView(self.splitterWindow)

        self.splitterWindow.SplitHorizontally(self.blogPostsView, self.blogPostSummaryView)
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
    # end _bindWidgetEvents()

    def onSashPosChanged(self, event):
        self.sashPosition = self.splitterWindow.GetSashPosition()
        event.Skip()
    # end onSashPosChanged()

    def destroy(self):
        self._saveSashPosition()
        self.blogPostsView.destroy()
        self.blogPostSummaryView.destroy()
    # end destroy()

    def _saveSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.POSTS_VIEW_SASH_POS, self.sashPosition)
    # end _saveSashPosition()

    def _restoreSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.sashPosition = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.POSTS_VIEW_SASH_POS, 200)
        self.splitterWindow.SetSashPosition(self.sashPosition)
    # end _restoreSashPosition()

# end ZContextInfoEditedView

