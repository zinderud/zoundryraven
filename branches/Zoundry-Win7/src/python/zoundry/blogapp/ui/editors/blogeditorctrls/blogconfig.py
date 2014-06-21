from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.events.commonevents import ZEVT_CONTENT_MODIFIED
from zoundry.appframework.ui.events.datectrlevents import ZEVT_DATE_CHANGE
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.util.colorutil import getDefaultPopdownDialogBackgroundColor
from zoundry.appframework.ui.util.fontutil import getDefaultFontItalic
from zoundry.appframework.ui.widgets.controls.common.panel import ZSmartTransparentPanel
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPubMetaData
from zoundry.blogapp.ui.common.pubdatawidgets import ZCategoryListContentProvider
from zoundry.blogapp.ui.common.pubdatawidgets import ZCategoryMultiSelectListView
from zoundry.blogapp.ui.common.pubdatawidgets import ZCategorySingleSelectListView
from zoundry.blogapp.ui.common.pubdatawidgets import ZPingListContentProvider
from zoundry.blogapp.ui.common.pubdatawidgets import ZPubMetaDataView
from zoundry.blogapp.ui.common.pubdatawidgets import ZTagspaceListContentProvider
from zoundry.blogapp.ui.common.pubdatawidgets import ZTagspaceListView
from zoundry.blogapp.ui.common.pubdatawidgets import ZTrackbackListContentProvider
from zoundry.blogapp.ui.common.pubdatawidgets import ZTrackbackUrlsView
from zoundry.blogapp.ui.events.editors.blogeditorevents import firePublishingChangeEvent
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaDataForBlog
from zoundry.blogapp.ui.util.blogutil import isCapabilitySupportedByBlog
from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
import wx.combo
import wx.lib.flatnotebook as fnb

# ------------------------------------------------------------------------------
# A control that allows the user to configure information/meta data specific
# to a particular blog (for publishing purposes).  This popup window will allow
# the user to change date/time, draft, categories, etc...
# ------------------------------------------------------------------------------
class ZBlogConfigPopup(wx.combo.ComboPopup):

    def __init__(self, combo, blog):
        self.combo = combo
        self.blog = blog
        self.catListCtrl = None
        self.pdColor = getDefaultPopdownDialogBackgroundColor()
        wx.combo.ComboPopup.__init__(self)
    # end __init__()

    def Init(self):
        pass
    # end Init()

    def Create(self, parent):
        self.parent = parent
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end Create()

    def GetControl(self):
        return self.panel
    # end GetControl()

    def GetStringValue(self):
        return _extstr(u"blogconfig.Configure") #$NON-NLS-1$
    # end GetStringValue()

    def OnPopup(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        tabId = userPrefs.getUserPreferenceInt(IZAppUserPrefsKeys.BLOGPUB_CONFIG_POPUP + u".tab-id", 0) #$NON-NLS-1$
        if tabId >= 0 and tabId < self.notebook.GetPageCount():
            self.notebook.SetSelection(tabId)
    # end OnPopup()

    def OnDismiss(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        tabId = self.notebook.GetSelection()
        userPrefs.setUserPreference(IZAppUserPrefsKeys.BLOGPUB_CONFIG_POPUP + u".tab-id", tabId) #$NON-NLS-1$
    # end OnDismiss()

    def SetStringValue(self, value): #@UnusedVariable
        pass
    # end SetStringValue()

    def _createWidgets(self):
        self.panel = wx.Panel(self.parent, wx.ID_ANY, style = wx.SIMPLE_BORDER)
        self.panel.SetBackgroundColour(self.pdColor)
        self.notebook = fnb.FlatNotebook(self.panel, wx.ID_ANY, style = fnb.FNB_BOTTOM | fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_NO_X_BUTTON | fnb.FNB_NODRAG)
        self.notebook.SetBackgroundColour(self.pdColor)
        self.notebook.SetActiveTabColour(self.pdColor)
        self.notebook.AddPage(self._createCategoriesPage(), _extstr(u"blogconfig.Categories"), False, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createCommonPage(), _extstr(u"blogconfig.General"), True, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createPingPage(), _extstr(u"blogconfig.WeblogPing"), False, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createTagsPage(), _extstr(u"blogconfig.TagSites"), False, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createTrackbackPage(), _extstr(u"blogconfig.Trackbacks"), False, -1) #$NON-NLS-1$
    # end _createWidgets()

    def _createCommonPage(self):
        self.commonPanel = ZTransparentPanel(self.notebook, wx.ID_ANY)
        self.commonCtrls = ZPubMetaDataView(self.commonPanel)
        return self.commonPanel
    # end _createCommonPage()

    def _createCategoriesPage(self):
        self.categoriesPanel = ZSmartTransparentPanel(self.notebook, wx.ID_ANY)
        self.catListProvider = ZCategoryListContentProvider()
        self.catListCtrl = ZCategoryMultiSelectListView(self.categoriesPanel, self.catListProvider)
        return self.categoriesPanel
    # end _createCategoriesPage()

    def _createPingPage(self):
        self.pingPanel = ZSmartTransparentPanel(self.notebook, wx.ID_ANY)
        self.pingListProvider = ZPingListContentProvider()
        self.pingListCtrl = ZCheckBoxListViewWithButtons(self.pingListProvider, self.pingPanel)
        return self.pingPanel
    # end _createPingPage()

    def _createTrackbackPage(self):
        self.trackbackPanel = ZSmartTransparentPanel(self.notebook, wx.ID_ANY)
        self.trackbackListProvider = ZTrackbackListContentProvider()
        self.tracbackListView = ZTrackbackUrlsView(self.trackbackPanel, self.trackbackListProvider)
        return self.trackbackPanel
    # end _createTrackbackPage()

    def _createTagsPage(self):
        self.tagspacePanel = ZSmartTransparentPanel(self.notebook, wx.ID_ANY)
        self.tagspaceListProvider = ZTagspaceListContentProvider()
        self.tagspaceListCtrl = ZTagspaceListView(self.tagspacePanel, self.tagspaceListProvider)
        return self.tagspacePanel
    # end _createTagsPage()

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 0)

        self._layoutCommonPage()
        self._layoutPingPage()
        self._layoutTagsPage()
        self._layoutTrackbackPage()

        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(True)
        self.panel.Layout()
    # end _layoutWidgets()

    def _layoutCommonPage(self):
        spaceSizer = wx.BoxSizer(wx.VERTICAL)
        spaceSizer.Add(self.commonCtrls, 1, wx.EXPAND | wx.ALL, 5)
        self.commonPanel.SetSizer(spaceSizer)
        self.commonPanel.SetAutoLayout(True)
        self.commonPanel.Layout()
    # end _layoutCommonPage()

    def _layoutCategoriesPage(self):
        # 'Categories' section
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self.categoriesPanel, wx.ID_ANY, _extstr(u"blogconfig.Categories")), wx.HORIZONTAL) #$NON-NLS-1$
        sbSizer.Add(self.catListCtrl, 1, wx.EXPAND | wx.ALL, 3)
        spaceSizer = wx.BoxSizer(wx.VERTICAL)
        spaceSizer.AddSizer(sbSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.categoriesPanel.SetSizer(spaceSizer)
        self.categoriesPanel.SetAutoLayout(True)
        self.categoriesPanel.Layout()
    # end _layoutCategoriesPage()

    def _layoutPingPage(self):
        # 'Weblog Ping' section
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self.pingPanel, wx.ID_ANY, _extstr(u"blogconfig.WeblogPing")), wx.HORIZONTAL) #$NON-NLS-1$
        sbSizer.Add(self.pingListCtrl, 1, wx.EXPAND | wx.ALL, 3)

        spaceSizer = wx.BoxSizer(wx.VERTICAL)
        spaceSizer.AddSizer(sbSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.pingPanel.SetSizer(spaceSizer)
        self.pingPanel.SetAutoLayout(True)
        self.pingPanel.Layout()
    # end _layoutPingPage()

    def _layoutTagsPage(self):
        # 'Tagging section
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self.tagspacePanel, wx.ID_ANY, _extstr(u"blogconfig.TagSites")), wx.HORIZONTAL) #$NON-NLS-1$
        sbSizer.Add(self.tagspaceListCtrl, 1, wx.EXPAND | wx.ALL, 3)

        spaceSizer = wx.BoxSizer(wx.VERTICAL)
        spaceSizer.AddSizer(sbSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.tagspacePanel.SetSizer(spaceSizer)
        self.tagspacePanel.SetAutoLayout(True)
        self.tagspacePanel.Layout()
    # end _layoutTagsPage()

    def _layoutTrackbackPage(self):
        # 'Trackback section
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self.trackbackPanel, wx.ID_ANY, _extstr(u"blogconfig.Trackbacks")), wx.HORIZONTAL) #$NON-NLS-1$
        sbSizer.Add(self.tracbackListView, 1, wx.EXPAND | wx.ALL, 3)

        spaceSizer = wx.BoxSizer(wx.VERTICAL)
        spaceSizer.AddSizer(sbSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.trackbackPanel.SetSizer(spaceSizer)
        self.trackbackPanel.SetAutoLayout(True)
        self.trackbackPanel.Layout()
    # end _layoutTrackbackPage()

    def _bindWidgetEvents(self):
        # Events that will cause a 'publishing change' event
        self.commonPanel.Bind(wx.EVT_CHECKBOX, self.onPublishingChange)
        self.commonPanel.Bind(ZEVT_DATE_CHANGE, self.onPublishingChange)
        self.pingPanel.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onPublishingChange)
        self.tagspacePanel.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onPublishingChange)
        self.trackbackPanel.Bind(ZEVT_CONTENT_MODIFIED, self.onPublishingChange)
        self.categoriesPanel.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onPublishingChange)
    # end _bindWidgetEvents()

    def _createAndLayoutCategoriesControl(self):
        for child in self.categoriesPanel.GetChildren():
            self.categoriesPanel.RemoveChild(child)
        if self.catListCtrl:
            self.catListCtrl.Show(False)
            self.catListCtrl.Destroy()
            self.catListCtrl = None

        if self.catListProvider.isMultiselect():
            self.catListCtrl = ZCategoryMultiSelectListView(self.categoriesPanel, self.catListProvider)
        else:
            self.catListCtrl = ZCategorySingleSelectListView(self.categoriesPanel, self.catListProvider)
        self._layoutCategoriesPage()
        self.categoriesPanel.GetParent().Layout()
        self.categoriesPanel.GetParent().Refresh()
    # end _createAndLayoutCategoriesControl()

    def setBlog(self, blog):
        self.blog = blog
        if not blog:
            return
        self.catListProvider.setBlog(blog)
        self._createAndLayoutCategoriesControl()
        self.catListCtrl.refresh()
        self.commonCtrls.enableDraftCheckbox(self._blogSupportsDraft(blog))
    # end setBlog()

    def _blogSupportsDraft(self, blog):
        return isCapabilitySupportedByBlog(IZBlogApiCapabilityConstants.DRAFT_POSTS, blog)
    # end _blogSupportsDraft()

    def setPubMetaData(self, pubMetaData):
        if pubMetaData:
            self._populateWidgets(pubMetaData)
    # end setPubMetaData()

    def getPubMetaData(self):
        pubMetaData = ZPubMetaData()
        self.commonCtrls.updatePubMetaData(pubMetaData)

        # categories
        categories  = self.catListProvider.getSelectedCategories()
        pubMetaData.setCategories( categories )

        # weblog ping list
        pingSites  = self.pingListProvider.getSelectedPingSites()
        pubMetaData.setPingServices(pingSites)

        # tagspaces
        tagspaceUrls = self.tagspaceListProvider.getSelectedTagSpaceUrls()
        pubMetaData.setTagspaceUrls( tagspaceUrls )

        # trackbacks
        trackbacks = self.trackbackListProvider.getTrackbacks()
        pubMetaData.setTrackbacks(trackbacks)

        return pubMetaData
    # end getPubMetaData()

    def _populateWidgets(self, pubMetaData):
        self.commonCtrls.setPubMetaData(pubMetaData)
        self.catListProvider.setSelectedCategories( pubMetaData.getCategories() )
        self.catListCtrl.refresh()
        self.pingListProvider.setSelectedPingSites( pubMetaData.getPingServices())
        self.pingListCtrl.refresh()
        self.tagspaceListProvider.setSelectedTagSpaceUrls( pubMetaData.getTagspaceUrls() )
        self.tagspaceListCtrl.refresh()
        self.trackbackListProvider.setTrackbacks( pubMetaData.getTrackbacks() )
        self.tracbackListView.refresh()
    # end _populateWidgets()

    def getPreferredHeight(self):
        return self.notebook.GetBestSizeTuple()[1]
    # end getPreferredHeight()

    def onOverridePubTime(self, event):
        self.dateCtrl.Enable(event.IsChecked())
        self.commonPanel.Layout()
        event.Skip()
    # end onOverridePubTime()

    def onPublishingChange(self, event): #@UnusedVariable
        firePublishingChangeEvent(self.combo)
        event.Skip()
    # end onPublishingChange()

# end ZBlogConfigPopup


# ------------------------------------------------------------------------------
# A custom combo control that represents the "Configure..." button shown once
# the user makes a valid Blog selection.  When the user clicks the "Configure"
# button, a custom transient popup window is displayed, which lets the user
# configure the blog parameters.
# ------------------------------------------------------------------------------
class ZConfigureBlogCombo(wx.combo.ComboCtrl):

    def __init__(self, parent, blog):
        self.blog = blog

        wx.combo.ComboCtrl.__init__(self, parent, style = wx.CB_READONLY)

        self.SetFont(getDefaultFontItalic())
        self.UseAltPopupWindow(True)
        self.popupCtrl = self._createPopupControl()
        self.SetPopupControl(self.popupCtrl)
        self.SetPopupMaxHeight(self.popupCtrl.getPreferredHeight())
        self.SetValue(_extstr(u"blogconfig.Configure")) #$NON-NLS-1$
    # end __init__()

    def setPubMetaData(self, pubMetaData):
        self.popupCtrl.setPubMetaData(pubMetaData)
    # end setPubMetaData()

    def getPubMetaData(self):
        return self.popupCtrl.getPubMetaData()
    # end getPubMetaData()

    def _createPopupControl(self):
        return ZBlogConfigPopup(self, self.blog)
    # end _createPopupControl()

    def setExtent(self, lExtent):
        self.SetPopupExtents(lExtent, 0)
    # end setExtent()

    def setBlog(self, blog):
        # Normally called by the ZBlogInfoChooser when a blog is selected.
        self.blog = blog
        self.popupCtrl.setBlog(blog)

        # Create a new ZPubMetaData object and populate the UI
        pubMetaData = self._createPubMetaDataFromBlog()
        self.setPubMetaData(pubMetaData)
    # end setBlog()

    def _createPubMetaDataFromBlog(self):
        return createDefaultPubMetaDataForBlog(self.blog)
    # end _createPubMetaDataFromBlog()

# end ZConfigureBlogCombo
