from zoundry.blogapp.messages import _extstr
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.splitterevents import ZEVT_SPLITTER_SASH_POS_CHANGED
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.advanced.textbox import ZAdvancedTextBox
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.models.views.standard.ctxview.tagsviewmodel import ZContextInfoTagsModel
from zoundry.blogapp.services.docindex.index import IZTagSearchFilter
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocumentIndexListener
from zoundry.blogapp.services.docindex.indeximpl import ZTagSearchFilter
from zoundry.blogapp.ui.events.viewevents import VIEWTAGSFILTERCHANGEDEVENT
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.events.viewevents import ZViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewEvent
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.tagsummaryview import ZTagSummaryView
from zoundry.blogapp.ui.views.view import IZViewIds
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZTagSelection
import wx

SEARCH_TAG = 0

# --------------------------------------------------------------------------------------
# Tags view - shows a tag cloud.
# --------------------------------------------------------------------------------------
class ZTagsView(ZBoxedView, IZDocumentIndexListener):

    def __init__(self, parent):
        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.model = ZContextInfoTagsModel(ZTagSearchFilter())

        self.tagCloudsView = None
        self.searchTextBox = None

        ZBoxedView.__init__(self, parent)

        self._registerAsIndexListener()
    # end __init__()

    def getViewId(self):
        return IZViewIds.TAG_CLOUD_VIEW
    # end getViewId()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/tags.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"tagsview.Tags") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        choices = self._getSearchBoxChoices()
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/contextinfo/linksview/search.png") #$NON-NLS-1$
        self.searchTextBox = ZAdvancedTextBox(parent, bitmap, choices, False)
        self.searchTextBox.setCurrentChoice(SEARCH_TAG)
        self.searchTextBox.SetSizeHints(220, -1)

        widgetList.append(self.searchTextBox)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        self.tagCloudsView = ZInfoTagCloudPanel(parent, self.model)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.tagCloudsView, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)
        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearchText, self.searchTextBox)
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
    # end _bindWidgetEvents()

    def _getSearchBoxChoices(self):
        return [
                (u"Tag", None, SEARCH_TAG), #$NON-NLS-1$
        ]
    # end _getSearchBoxChoices()

    def onSearchText(self, event):
        self.model.setTagCriteria(event.GetString())
        self.model.refresh()
        self.tagCloudsView.refresh()
        self.onInvalidSelection()

        fireViewEvent(ZViewEvent(VIEWTAGSFILTERCHANGEDEVENT, self))
        event.Skip()
    # end onSearchText()

    def _updateModel(self, refreshData):
        (eventType, tagIDO) = refreshData
        shouldRefresh = False
        if eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD:
            shouldRefresh = self.model.addTag(tagIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE:
            shouldRefresh = self.model.removeTag(tagIDO)
        elif eventType == IZDocIndexEvent.DOCINDEX_EVENTTYPE_UPDATE:
            shouldRefresh = self.model.updateTag(tagIDO)
        return shouldRefresh
    # end _updateModel()

    def onIndexChange(self, event):
        if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_TAG:
            refreshData = (event.getEventType(), event.getTagIDO())
            fireRefreshEvent(self, refreshData)
    # end onIndexChange()

    def onZoundryRefresh(self, event): #@UnusedVariable
        if self._updateModel(event.getData()):
            self.tagCloudsView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onInvalidSelection(self):
        pass
    # end onInvalidSelection()

    def onViewSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.BLOG_TAGS_SELECTION:
            self.refreshContent(selection)
    # end onViewSelectionChanged()

    def refreshContent(self, selection):
        (accountId, blogId) = selection.getData()

        filter = ZTagSearchFilter()
        if blogId is not None:
            account = self.accountStore.getAccountById(accountId)
            self.blog = account.getBlogById(blogId)
            filter.setAccountIdCriteria(accountId)
            filter.setBlogIdCriteria(blogId)
        else:
            self.blog = None
            filter.setAccountIdCriteria(IZTagSearchFilter.UNPUBLISHED_ACCOUNT_ID)
            filter.setBlogIdCriteria(IZTagSearchFilter.UNPUBLISHED_BLOG_ID)

        self.model = ZContextInfoTagsModel(filter)
        self.tagCloudsView.setBlog(self.blog)
        self.tagCloudsView.setModel(self.model)
        self.tagCloudsView.refresh()
        fireViewUnselectionEvent()
    # end refreshContent()

    def destroy(self):
        self._unregisterAsIndexListener()
    # end destroy()

    def _registerAsIndexListener(self):
        self.indexService.addListener(self)
    # end _registerAsIndexListener()

    def _unregisterAsIndexListener(self):
        self.indexService.removeListener(self)
    # end _unregisterAsIndexListener()

# end ZTagsView


# --------------------------------------------------------------------------------------
# Tags view - shown when the user clicks on "Links" in the Navigator, for example.
# --------------------------------------------------------------------------------------
class ZContextInfoTagsView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.sashPosition = 0

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getViewId(self):
        return IZViewIds.TAGS_VIEW
    # end getViewId()

    def _createWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)

        self.tagsView = ZTagsView(self.splitterWindow)
        self.tagSummaryView = ZTagSummaryView(self.splitterWindow)

        self.splitterWindow.SplitHorizontally(self.tagsView, self.tagSummaryView)
        self.splitterWindow.SetMinimumPaneSize(100)
        self.splitterWindow.SetSashSize(8)
        self.splitterWindow.SetSashGravity(0.0)
    # end _createWidgets()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.splitterWindow, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)

        self._restoreSashPosition()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_SPLITTER_SASH_POS_CHANGED, self.onSashPosChanged, self.splitterWindow)
    # end _bindWidgetEvents()

    def onSashPosChanged(self, event):
        self.sashPosition = self.splitterWindow.GetSashPosition()
        event.Skip()
    # end onSashPosChanged()

    def destroy(self):
        self._saveSashPosition()
    # end destroy()

    def _saveSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.TAGS_VIEW_SASH_POS, self.splitterWindow.GetSashPosition())
    # end _saveSashPosition()

    def _restoreSashPosition(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.sashPosition = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.TAGS_VIEW_SASH_POS, 200)
        self.splitterWindow.SetSashPosition(self.sashPosition)
    # end _restoreSashPosition()

# end ZContextInfoTagsView


#----------------------------------------------------
# Tag clouds panel.
#----------------------------------------------------
class ZInfoTagCloudPanel(ZTransparentPanel):

    def __init__(self, parent, model):
        self.blog = None

        ZTransparentPanel.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        self.htmlWidget = None
        self.model = model
        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()

    def setBlog(self, blog):
        self.blog = blog
    # end setBlog()

    def setModel(self, model):
        self.model = model
    # end setModel()

    def _createWidgets(self):
        self.htmlWidget = ZHTMLViewControl(self, wx.ID_ANY)
        self.htmlWidget.setLinkCallback(self)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.htmlWidget, 1, wx.EXPAND)
        self.SetSizer(sizer)
    # end _layoutWidgets()

    def onTag(self, tagId):
        #Call back when tag link is clicked on
        tagId = convertToUnicode(tagId)
        tagIDO = self.model.getTagIDO(tagId)
        fireViewSelectionEvent(ZTagSelection(tagIDO, self.blog), self)
        return False
    # end onTag()

    def refresh(self):
        idx = 0
        colors = [u"black", u"blue", u"orange", u"red", u"green", u"magenta"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$
        s = u"" #$NON-NLS-1$
        idoHitCountTupleList = []
        idoHitCountTupleList.extend( self.model.getTagsMap().itervalues() )
        idoHitCountTupleList.sort( lambda x, y: cmp( x[0].getId(), y[0].getId() ) )
        for (tagIdo, hitCount) in idoHitCountTupleList:
            fz = u"3.0em"  #$NON-NLS-1$
            if hitCount < 9:
                fz = u"1.%dem" % (hitCount-1)  #$NON-NLS-1$
            elif hitCount < 20:
                fz = u"2.%dem" % (hitCount-10)  #$NON-NLS-1$
            color = colors[ idx % len(colors) ]
            idx = idx+1
            #tagstr = u"""<span style="font-size:%s;color:%s">%s<a href="py::onTag('%s')">(%d)</a></span>&nbsp;&nbsp; """ % (fz, color, tagIdo.getTagword(), tagIdo.getId(), hitCount) #$NON-NLS-1$
            tagstr = u"""<span><a style="font-size:%s;color:%s;text-decoration:none" href="py::onTag('%s')">%s</a>(%d)</span>&nbsp;&nbsp; """ % (fz, color, tagIdo.getId(), tagIdo.getTagword(), hitCount) #$NON-NLS-1$
            s = s + tagstr
        html = u"""<html><body><table border="0" cellspacing="5"><tr><td>%s</td></tr></table></body></html>""" %s #$NON-NLS-1$
        self.htmlWidget.setHtmlValue(html)
    # end refresh()

# end ZInfoTagCloudPanel
