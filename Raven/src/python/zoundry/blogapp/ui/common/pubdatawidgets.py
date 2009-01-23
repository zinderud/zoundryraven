from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.events.commonevents import ZContentModifiedEvent
from zoundry.appframework.ui.widgets.controls.advanced.datectrl import ZDateTimeChooser
from zoundry.appframework.ui.widgets.controls.common.panel import ZSmartTransparentPanel
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.listex import IZCheckBoxListViewContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.controls.listex import ZRadioBoxListView
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import URL_RE
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZUrlSelectionValidator
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTrackback
from zoundry.blogapp.services.pubsystems.blog.blogpublisher import ZBlogPublisherUtil
from zoundry.blogapp.ui.util.blogutil import getCustomWPMetaDataAttribute
from zoundry.blogapp.ui.util.blogutil import isCapabilitySupportedByBlog
from zoundry.blogapp.ui.util.blogutil import setCustomWPMetaDataAttribute
from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
import wx

# FIXME use ZBlogPostMetaDataModel

# ------------------------------------------------------------------------------
# Content provider for the list of categories.
# ------------------------------------------------------------------------------
class ZCategoryListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self):
        self.multiselect = False
        self.usergenerated = False
        self.blogId = u"" #$NON-NLS-1$
        self.categories = []
        self.selectedCategories = []
        self.columns = [
                (u"Category", None, 0, ZListViewEx.COLUMN_RELATIVE, 50) #$NON-NLS-1$
        ]
    # end __init__()

    def _sort(self):
        self.categories.sort( lambda x, y: cmp(x.getName().lower(), y.getName().lower()) )
    # end _sort()

    def isUserGeneratedContent(self):
        return self.usergenerated
    # end isUserGeneratedContent()

    def isMultiselect(self):
        return self.multiselect
    # end isMultiSelect

    def setBlog(self, blog):
        self.blogId = blog.getId()
        self.categories = []
        self.selectedCategories = []
        self.categories.extend(blog.getCategories() )
        self._sort()
        self.multiselect = isCapabilitySupportedByBlog(IZBlogApiCapabilityConstants.MULTISELECT_CATEGORIES, blog)
        self.usergenerated = isCapabilitySupportedByBlog(IZBlogApiCapabilityConstants.USERGENERATED_CATEGORIES, blog)
    # end setBlog()

    def addCategoryByName(self, categoryName):
        if not self.usergenerated:
            return -1
        category = self._getByName(categoryName, self.categories)
        if not category:
            category = ZBlogPublisherUtil().createRavenCategoryByName(self.blogId, categoryName)
            self.categories.append(category)

        # append copy as selected
        selectedCat = self._getByName(categoryName, self.selectedCategories)
        if not selectedCat:
            self.selectedCategories.append(category)
        self._sort()
        idx = -1
        try:
            idx = self.categories.index(category)
        except:
            pass
        return idx
    # end addCategoryByName()

    def setSelectedCategories(self, categories):
        self.selectedCategories = categories
        if self.usergenerated:
            # for user generated content, add any categories not that not already in the list.
            for category in categories:
                if self._getByName(category.getName(), self.categories) is None:
                    self.categories.append(category)
            self._sort()
    # end setSelectedCategories()

    def getSelectedCategories(self):
        return self.selectedCategories
    # end getSelectedCategories()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return len(self.columns)
    # end getNumColumns()

    def getNumRows(self):
        return len( self.categories)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        rval = u"" #$NON-NLS-1$
        category = self._getCategory(rowIndex)
        if category:
            rval = category.getName()
        return rval
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex): #@UnusedVariable
        rval = False
        category = self._getCategory(rowIndex)
        # for user generated categories, compare using category name.
        if self.usergenerated and self._getByName(category.getName(), self.selectedCategories) is not None:
            rval = True
        elif self._getById(category.getId(), self.selectedCategories) is not None:
            rval = True
        return rval
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        category = self._getCategory(rowIndex)
        if checked:
            # for user generated categories, use compare using category name.
            if self.usergenerated and self._getByName(category.getName(), self.selectedCategories) is None:
                self.selectedCategories.append(category)
            elif self._getById(category.getId(), self.selectedCategories) is None:
                self.selectedCategories.append(category)
        else:
            if self.usergenerated and self._getByName(category.getName(), self.selectedCategories) is not None:
                self._removeByName(category.getName(), self.selectedCategories)
            elif self._getById(category.getId(), self.selectedCategories) is not None:
                self._removeById(category.getId(), self.selectedCategories)
    # end setChecked()

    def _getCategory(self, rowIndex):
        category = None
        if rowIndex >= 0 and self.categories and rowIndex < len(self.categories):
            category = self.categories[rowIndex]
        return category
    # end _getCategory()

    def _getByName(self, categoryName, categoryList):
        rval = None
        if categoryList:
            for cat in categoryList:
                if cat.getName().lower() == categoryName.lower():
                    rval = cat
                    break
        return rval
    # end _getByName()

    def _removeByName(self, categoryName, categoryList):
        if categoryList:
            tmpList = []
            tmpList.extend(categoryList)
            for cat in tmpList:
                if cat.getName().lower() == categoryName.lower():
                    categoryList.remove(cat)
    # end _removeByName()

    def _getById(self, categoryId, categoryList):
        rval = None
        if categoryList:
            for cat in categoryList:
                if cat.getId() == categoryId:
                    rval = cat
                    break
        return rval
    # end _getById()

    def _removeById(self, categoryId, categoryList):
        if categoryList:
            tmpList = []
            tmpList.extend(categoryList)
            for cat in tmpList:
                if cat.getId() == categoryId:
                    categoryList.remove(cat)
    # end _removeById()

# end ZCategoryListContentProvider


# ------------------------------------------------------------------------------
# Content provider for the list of ping services.
# ------------------------------------------------------------------------------
class ZTrackbackListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self):
        self.columns = [
                (_extstr(u"pubdatawidgets.URL"), None, 0, ZListViewEx.COLUMN_RELATIVE, 60), #$NON-NLS-1$
                (_extstr(u"pubdatawidgets.TrackbackSent"), None, 0, ZListViewEx.COLUMN_RELATIVE, 10), #$NON-NLS-1$
                (_extstr(u"pubdatawidgets.TrackbackDate"), None, 0, ZListViewEx.COLUMN_RELATIVE, 30) #$NON-NLS-1$
        ]

        self.data = [
             (u"http://Not-Yet-Implemented", u"Yes", u"Today"), #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        ]
        # list of IZTrackback
        self.trackbacks = []
    # end __init__()

    def setTrackbackUrlList(self, urlList):
        tbList = []
        for url in urlList:
            trackback = ZTrackback()
            trackback.setUrl(url)
            tbList.append(trackback)
        self.setTrackbacks(tbList)
    # end setTrackbackUrlList

    def setTrackbacks(self, izTrackbacks):
        if izTrackbacks:
            self.trackbacks = izTrackbacks
        else:
            self.trackbacks = []
    # end setTrackbacks()

    def getTrackbacks(self):
        return self.trackbacks
    # end getTrackbacks()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return len(self.columns)
    # end getNumColumns()

    def getNumRows(self):
        return len(self.data)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        return self.data[rowIndex][columnIndex]
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex): #@UnusedVariable
        return False
    # end isChecked()

# end ZTrackbackListContentProvider


# ------------------------------------------------------------------------------
# trackback list view control
# ------------------------------------------------------------------------------
class ZTrackbackListView(ZSmartTransparentPanel):

    def __init__(self, parent, provider):
        ZSmartTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.trackbackListProvider = provider
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgets()
    # end __init__()

    def _createWidgets(self):
        self.listCtrl = ZCheckBoxListViewWithButtons(self.trackbackListProvider, self)
#        self.catAddCategoryLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.AddCategory")) #$NON-NLS-1$
#        self.catAddCategoryTextCtrl = wx.TextCtrl(self, wx.ID_ANY, size = wx.Size(200, -1), style=wx.TE_PROCESS_ENTER )
#        self.catAddCategoryButton = wx.Button(self, wx.ID_ANY, _extstr(u"pubdatawidgets.Add")) #$NON-NLS-1$
    # end _createWidgets()


    def _layoutWidgets(self):
        listBox = wx.BoxSizer(wx.VERTICAL)
        listBox.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 3)
#        addCatBox = wx.BoxSizer(wx.HORIZONTAL)
#        addCatBox.Add(self.catAddCategoryLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
#        addCatBox.Add(self.catAddCategoryTextCtrl, 1, wx.LEFT, 3)
#        addCatBox.Add(self.catAddCategoryButton, 0, wx.LEFT, 5)
#        catListBox.AddSizer(addCatBox, 0, wx.ALL, 3)
        self.SetSizer(listBox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets

    def _bindWidgets(self):
        pass
#        self.Bind(wx.EVT_BUTTON, self.onAddCategory, self.catAddCategoryButton)
#        self.Bind(wx.EVT_TEXT_ENTER, self.onAddCategory, self.catAddCategoryTextCtrl)
    # end _bindWidgets()

    def refresh(self):
#        self.catAddCategoryTextCtrl.Clear()
        self.listCtrl.checkBoxListView.refreshItems()
    # end refresh
# end ZTrackbackListView

# ------------------------------------------------------------------------------
# Content provider for the list of ping services.
# ------------------------------------------------------------------------------
class ZTagspaceListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self):
        self.columns = [
                (u"Tag space", None, 0, ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
        ]
        linkService = getApplicationModel().getService(IZBlogAppServiceIDs.LINKS_SERVICE_ID)
        self.tagFormatters = []
        self.tagFormatters.extend( linkService.listFormattersByType(u"tag") )   #$NON-NLS-1$
        self.selectedTagSpaceUrls = []
    # end __init__()

    def getSelectedTagSpaceUrls(self):
        return self.selectedTagSpaceUrls
    # end getSelectedTagSpaceUrls

    def setSelectedTagSpaceUrls(self, urlList):
        if urlList is None:
            urlList = []
        self.selectedTagSpaceUrls = urlList
    # end setSelectedTagSpaceUrls()

    def _getFormatterByIndex(self, rowIndex):
        formatter = None
        if rowIndex >= 0 and rowIndex < len(self.tagFormatters):
            formatter = self.tagFormatters[rowIndex]
        return formatter
    # end _getFormatterByIndex()

    def _getFormatterByUrl(self, tagUrl):
        formatter = None
        for f in self.tagFormatters:
            if f.getUrl() == tagUrl:
                formatter = f
                break
        return formatter
    # end _getFormatterByUrl()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return len(self.columns)
    # end getNumColumns()

    def getNumRows(self):
        return len( self.tagFormatters )
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        formatter = self._getFormatterByIndex(rowIndex)
        if formatter:
            return formatter.getName()
        else:
            return u"NA" + rowIndex  #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex): #@UnusedVariable
        formatter = self._getFormatterByIndex(rowIndex)
        if not formatter:
            return False
        return formatter.getUrl() in self.getSelectedTagSpaceUrls()
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        formatter = self._getFormatterByIndex(rowIndex)
        if not formatter:
            return
        inlist = formatter.getUrl() in self.getSelectedTagSpaceUrls()
        if checked and not inlist:
            self.selectedTagSpaceUrls.append( formatter.getUrl() )
        elif not checked and inlist:
            try:
                self.selectedTagSpaceUrls.remove( formatter.getUrl())
            except:
                pass
    # end setChecked()

# end ZTagspaceListContentProvider

# ------------------------------------------------------------------------------
# Tag list view control
# ------------------------------------------------------------------------------
class ZTagspaceListView(ZSmartTransparentPanel):

    def __init__(self, parent, provider):
        ZSmartTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.tagListProvider = provider
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgets()
    # end __init__()

    def _createWidgets(self):
        self.listCtrl = ZCheckBoxListViewWithButtons(self.tagListProvider, self)
    # end _createWidgets()

    def _layoutWidgets(self):
        listBox = wx.BoxSizer(wx.VERTICAL)
        listBox.Add(self.listCtrl, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(listBox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets

    def _bindWidgets(self):
        pass
    # end _bindWidgets()

    def refresh(self):
        self.listCtrl.checkBoxListView.refreshItems()
    # end refresh
# end ZTagspaceListView

# ------------------------------------------------------------------------------
# Content provider for the list of ping services.
# ------------------------------------------------------------------------------
class ZPingListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self):
        self.columns = [
                (_extstr(u"pubdatawidgets.Service"), None, 0, ZListViewEx.COLUMN_RELATIVE, 40), #$NON-NLS-1$
                (_extstr(u"pubdatawidgets.URL"), None, 0, ZListViewEx.COLUMN_RELATIVE, 60) #$NON-NLS-1$
        ]
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        self.pingSites = publisherService.listWeblogPingSites()
        self.selectedPingSites = []
    # end __init__()

    def setSelectedPingSites(self, pingSites):
        u"""setSelectedPingSites(IZWeblogPingSite[]) -> void
        Sets the initial list of selected IZWeblogPingSite objects.""" #$NON-NLS-1$
        if pingSites is None:
            pingSites = []
        self.selectedPingSites = pingSites
    # end setSelectedPingSites()

    def getSelectedPingSites(self):
        return self.selectedPingSites
    # end getSelectedPingSites()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return len(self.columns)
    # end getNumColumns()

    def getNumRows(self):
        return len(self.pingSites)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        weblogpingSite = self._getWeblogpingSite(rowIndex)
        if weblogpingSite and columnIndex == 0:
            return weblogpingSite.getName()
        elif weblogpingSite and columnIndex == 1:
            return weblogpingSite.getUrl()
        return u"" #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex):
        pingSite = self._getWeblogpingSite(rowIndex)
        return pingSite and self._getByUrl(pingSite.getUrl(), self.selectedPingSites) is not None
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        pingSite = self._getWeblogpingSite(rowIndex)
        if pingSite and checked and self._getByUrl(pingSite.getUrl(), self.selectedPingSites) is None:
            self.selectedPingSites.append(pingSite)
        elif pingSite and not checked and self._getByUrl(pingSite.getUrl(), self.selectedPingSites) is not None:
            self._removeByUrl(pingSite.getUrl(), self.selectedPingSites)
    # end setChecked()

    def _getWeblogpingSite(self, rowIndex):
        weblogpingSite = None
        if rowIndex >= 0 and self.pingSites and rowIndex < len(self.pingSites):
            weblogpingSite = self.pingSites[rowIndex]
        return weblogpingSite
    # end _getWeblogpingSite()

    def _getByUrl(self, url, pingSiteList):
        for pingSite in pingSiteList:
            if url == pingSite.getUrl():
                return pingSite
        return None
    # end _getByUrl

    def _removeByUrl(self, url, pingSiteList):
        for pingSite in pingSiteList:
            if url == pingSite.getUrl():
                pingSiteList.remove(pingSite)
    # end _removeByUrl

# end ZPingListContentProvider


# ------------------------------------------------------------------------------
# Categories list view control
# ------------------------------------------------------------------------------
class ZAbstractCategoryListView(ZSmartTransparentPanel):

    def __init__(self, parent, provider):
        ZSmartTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.catListProvider = provider
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgets()
    # end __init__()

    def _createWidgets(self):
        self._createListControl()
        self.catAddCategoryLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.AddCategory")) #$NON-NLS-1$
        self.catAddCategoryTextCtrl = wx.TextCtrl(self, wx.ID_ANY, size = wx.Size(200, -1), style=wx.TE_PROCESS_ENTER )
        self.catAddCategoryButton = wx.Button(self, wx.ID_ANY, _extstr(u"pubdatawidgets.Add")) #$NON-NLS-1$
    # end _createWidgets()


    def _layoutWidgets(self):
        catListBox = wx.BoxSizer(wx.VERTICAL)
        catListBox.Add(self._getListControl(), 1, wx.EXPAND | wx.ALL, 3)
        addCatBox = wx.BoxSizer(wx.HORIZONTAL)
        addCatBox.Add(self.catAddCategoryLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        addCatBox.Add(self.catAddCategoryTextCtrl, 1, wx.LEFT, 3)
        addCatBox.Add(self.catAddCategoryButton, 0, wx.LEFT, 5)
        catListBox.AddSizer(addCatBox, 0, wx.ALL, 3)
        self.SetSizer(catListBox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets

    def _bindWidgets(self):
        self.Bind(wx.EVT_BUTTON, self.onAddCategory, self.catAddCategoryButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.onAddCategory, self.catAddCategoryTextCtrl)
    # end _bindWidgets()

    def onAddCategory(self, event): #@UnusedVariable
        text = getNoneString( self.catAddCategoryTextCtrl.GetValue())
        if text is not None:
            idx = self.catListProvider.addCategoryByName(text)
            self.refresh()
            if idx != -1:
                self._onAddCategory(idx, text)
        event.Skip()
    # end onAddCategory()

    def refresh(self):
        self.catAddCategoryTextCtrl.Clear()
        self.catAddCategoryLabel.Show( self.catListProvider.isUserGeneratedContent() )
        self.catAddCategoryTextCtrl.Show( self.catListProvider.isUserGeneratedContent() )
        self.catAddCategoryButton.Show( self.catListProvider.isUserGeneratedContent() )

        self.catAddCategoryLabel.Enable( self.catListProvider.isUserGeneratedContent() )
        self.catAddCategoryTextCtrl.Enable( self.catListProvider.isUserGeneratedContent() )
        self.catAddCategoryButton.Enable( self.catListProvider.isUserGeneratedContent() )
        self.Layout()
        self._refreshListControl()
    # end refresh()

    def _createListControl(self):
        return None
    # end _createListControl

    def _getListControl(self):
        return None
    # end _getListControl()

    def _onAddCategory(self, idx, text): #@UnusedVariable
        pass
    # end _addCategory()

    def _refreshListControl(self):
        pass
    # end _refreshListControl()

# end ZAbstractCategoryListView

# ------------------------------------------------------------------------------
# multi select list view control
# ------------------------------------------------------------------------------
class ZCategoryMultiSelectListView(ZAbstractCategoryListView):

    def __init__(self, parent, provider):
        self.catListCtrl = None
        ZAbstractCategoryListView.__init__(self, parent, provider)
    # end __init__

    def _createListControl(self):
        s = wx.LC_VRULES | wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_LIST
        self.catListCtrl = ZCheckBoxListViewWithButtons(self.catListProvider, self, style = s)
        return self.catListCtrl
    # end _createListControl

    def _getListControl(self):
        return self.catListCtrl
    # end _getListControl()

    def _addCategory(self, idx, text): #@UnusedVariable
        self.catListCtrl.checkBoxListView._fireCheckBoxListChangeEvent(idx)
    # end _addCategory()

    def _refreshListControl(self):
        self.catListCtrl.checkBoxListView.refreshItems()
    # end _refreshListControl()

# end  ZCategoryMultiSelectListView

# ------------------------------------------------------------------------------
# single select list view control
# ------------------------------------------------------------------------------
class ZCategorySingleSelectListView(ZAbstractCategoryListView):

    def __init__(self, parent, provider):
        self.catListCtrl = None
        ZAbstractCategoryListView.__init__(self, parent, provider)
    # end __init__

    def _createListControl(self):
        s = wx.LC_VRULES | wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_LIST
        self.catListCtrl = ZRadioBoxListView(self.catListProvider, self, style = s)
        return self.catListCtrl
    # end _createListControl

    def _getListControl(self):
        return self.catListCtrl
    # end _getListControl()

    def _addCategory(self, idx, text): #@UnusedVariable
        self.catListCtrl._fireCheckBoxListChangeEvent(idx)
    # end _addCategory()

    def _refreshListControl(self):
        self.catListCtrl.refreshItems()
    # end _refreshListControl()

# end  ZCategorySingleSelectListView


# ------------------------------------------------------------------------------
# publish meta data view control
# Contains draft status, date control, image upload attributes etc.
# ------------------------------------------------------------------------------
class ZPubMetaDataView(ZTransparentPanel):
    
    WP_PUBLISHED = 0
    WP_PENDING = 1
    WP_DRAFT = 2
    WP_PRIVATE = 3

    def __init__(self, parent):
        ZTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.wpPublishStatusValue = ZPubMetaDataView.WP_PUBLISHED
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.draftCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.PublishAsDraft")) #$NON-NLS-1$
        self.overridePubTimeCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.OverridePubTime")) #$NON-NLS-1$
        self.dateCtrl = ZDateTimeChooser(self, None)
        self.dateCtrl.Enable(False)
        self.thumbnailsOnlyCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.UploadOnlyTNs")) #$NON-NLS-1$
        self.forceUploadCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.ReUpload")) #$NON-NLS-1$
        self.lightboxCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.AddLightbox")) #$NON-NLS-1$
        self.poweredByZoundryCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.AddPoweredBy")) #$NON-NLS-1$
        self.wpPostSlugLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.WpPostSlug")) #$NON-NLS-1$
        self.wpPostSlugTextCtrl = wx.TextCtrl(self, wx.ID_ANY, size = wx.Size(200, -1), style=wx.TE_PROCESS_ENTER )
        self.wpPasswordLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.WpPostPassword")) #$NON-NLS-1$
        self.wpPasswordTextCtrl = wx.TextCtrl(self, wx.ID_ANY, size = wx.Size(200, -1), style=wx.TE_PROCESS_ENTER )
        self.wpPubStatusLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.WpPublishStatus")) #$NON-NLS-1$
        
        choices = self._getWpPublishChoices()
        self.wpPubStatusCombo = wx.ComboBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.WpPublishStatus_published"), style = wx.CB_READONLY, choices = choices) #$NON-NLS-1$
        
    # end _createWidgets()
    
    def _getWpPublishChoices(self):
        return [
                _extstr(u"pubdatawidgets.WpPublishStatus_published"), #$NON-NLS-1$
                _extstr(u"pubdatawidgets.WpPublishStatus_pending"), #$NON-NLS-1$
                _extstr(u"pubdatawidgets.WpPublishStatus_unpublished"), #$NON-NLS-1$
                _extstr(u"pubdatawidgets.WpPublishStatus_private")#$NON-NLS-1$
        ]
    # end _getWpPublishChoices()    

    def _layoutWidgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 'Publishing' section (draft, date/time override)
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.Publishing")), wx.VERTICAL) #$NON-NLS-1$
        sbSizer.Add(self.draftCB, 0, wx.ALL, 3)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.overridePubTimeCB, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        hbox.Add(self.dateCtrl, 0, wx.LEFT, 3)
        sbSizer.AddSizer(hbox, 0, wx.ALL, 3)
        vbox.AddSizer(sbSizer, 0, wx.ALL, 3)

        # 'Image Upload' section (thumbnails only, force upload)
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.ImageUpload")), wx.VERTICAL) #$NON-NLS-1$
        sbSizer.Add(self.thumbnailsOnlyCB, 0, wx.EXPAND | wx.ALL, 3)
        sbSizer.Add(self.forceUploadCB, 0, wx.EXPAND | wx.ALL, 3)
        sbSizer.Add(self.lightboxCB, 0, wx.EXPAND | wx.ALL, 3)
        vbox.AddSizer(sbSizer, 0, wx.ALL, 3)

        # 'Other' section (powered by Zoundry)
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.OtherOptions")), wx.VERTICAL) #$NON-NLS-1$
        sbSizer.Add(self.poweredByZoundryCB, 0, wx.EXPAND | wx.ALL, 3)
        vbox.AddSizer(sbSizer, 0, wx.ALL, 3)

        # 'WP' section
        sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _extstr(u"pubdatawidgets.WpOptions")), wx.VERTICAL) #$NON-NLS-1$
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.wpPubStatusLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        hbox.Add(self.wpPubStatusCombo, 1, wx.LEFT, 3)
        sbSizer.AddSizer(hbox, 0, wx.ALL, 3)        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.wpPostSlugLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        hbox.Add(self.wpPostSlugTextCtrl, 1, wx.LEFT, 3)
        sbSizer.AddSizer(hbox, 0, wx.ALL, 3)        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.wpPasswordLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        hbox.Add(self.wpPasswordTextCtrl, 1, wx.LEFT, 3)
        sbSizer.AddSizer(hbox, 0, wx.ALL, 3)        
        vbox.AddSizer(sbSizer, 0,wx.ALL, 3)

        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onOverridePubTime, self.overridePubTimeCB)
        self.Bind(wx.EVT_CHECKBOX, self.onDraftMode, self.draftCB)
        self.Bind(wx.EVT_COMBOBOX, self.onWpPubStatusCombo, self.wpPubStatusCombo)
    # end _bindWidgetEvents()

    def onWpPubStatusCombo(self, event):
        idx = self.wpPubStatusCombo.GetSelection()
        self.wpPublishStatusValue = idx
        self.draftCB.SetValue(idx == ZPubMetaDataView.WP_DRAFT)
        self.Layout()
        event.Skip()
    # end onWpPubStatusCombo()

    def onDraftMode(self, event):
        if not event.IsChecked() and self.wpPublishStatusValue == ZPubMetaDataView.WP_DRAFT:
            self.wpPublishStatusValue = ZPubMetaDataView.WP_PUBLISHED
            self.wpPubStatusCombo.SetSelection(self.wpPublishStatusValue)
        elif event.IsChecked() and self.wpPublishStatusValue != ZPubMetaDataView.WP_DRAFT:
            self.wpPublishStatusValue = ZPubMetaDataView.WP_DRAFT
            self.wpPubStatusCombo.SetSelection(self.wpPublishStatusValue)            
        self.Layout()
        event.Skip()
    # end onDraftMode(

    def onOverridePubTime(self, event):
        self.dateCtrl.Enable(event.IsChecked())
        self.Layout()
        event.Skip()
    # end onOverridePubTime()

    def enableDraftCheckbox(self, enabled):
        self.draftCB.Enable(enabled)
    # end enableDraftCheckbox()

    def setPubMetaData(self, pubMetaData):
        # Updates the UI controls based on the data in pubMetaData
        self.draftCB.SetValue(pubMetaData.isPublishAsDraft())
        pubTime = pubMetaData.getPublishTime()
        if pubTime is not None:
            self.overridePubTimeCB.SetValue(True)
            self.dateCtrl.Enable(True)
            self.dateCtrl.setDateTime(pubTime)
        self.thumbnailsOnlyCB.SetValue(pubMetaData.isUploadTNsOnly())
        self.forceUploadCB.SetValue(pubMetaData.isForceReUploadImages())
        self.lightboxCB.SetValue(pubMetaData.isAddLightbox())
        self.poweredByZoundryCB.SetValue(pubMetaData.isAddPoweredBy())

        # WP custom data
        slug = getSafeString( getCustomWPMetaDataAttribute(pubMetaData, u"wp_slug") ) #$NON-NLS-1$
        self.wpPostSlugTextCtrl.SetValue(slug)
        # WP password
        s = getSafeString( getCustomWPMetaDataAttribute(pubMetaData, u"wp_password") ) #$NON-NLS-1$
        self.wpPasswordTextCtrl.SetValue(s)

        # WP pub status
        self.wpPublishStatusValue = ZPubMetaDataView.WP_PUBLISHED
        s = getSafeString( getCustomWPMetaDataAttribute(pubMetaData, u"post_status") ) #$NON-NLS-1$

        if s == u"pending":  #$NON-NLS-1$
            self.wpPublishStatusValue = ZPubMetaDataView.WP_PENDING
        elif s == u"private":  #$NON-NLS-1$
            self.wpPublishStatusValue = ZPubMetaDataView.WP_PRIVATE
        elif s == u"draft" or pubMetaData.isPublishAsDraft():  #$NON-NLS-1$
            self.wpPublishStatusValue = ZPubMetaDataView.WP_DRAFT

        self.wpPubStatusCombo.SetSelection(self.wpPublishStatusValue)
    # end setPubMetaData

    def updatePubMetaData(self, pubMetaData):
        # Flushes the UI data to the pubMetaData object.
        pubMetaData.setAddPoweredBy(self.poweredByZoundryCB.IsChecked())
        pubMetaData.setForceReUploadImages(self.forceUploadCB.IsChecked())
        pubMetaData.setAddLightbox(self.lightboxCB.IsChecked())
        pubMetaData.setPublishAsDraft(self.draftCB.IsChecked())
        pubMetaData.setPublishTime(None)
        if self.overridePubTimeCB.IsChecked():
            pubTime = self.dateCtrl.getDateTime()
            pubMetaData.setPublishTime(pubTime)
        pubMetaData.setUploadTNsOnly(self.thumbnailsOnlyCB.IsChecked())

        # WP custom data
        slug = getNoneString(self.wpPostSlugTextCtrl.GetValue() )
        setCustomWPMetaDataAttribute(pubMetaData, u"wp_slug", slug) #$NON-NLS-1$
        # password
        pw = getNoneString(self.wpPasswordTextCtrl.GetValue() )
        setCustomWPMetaDataAttribute(pubMetaData, u"wp_password", pw) #$NON-NLS-1$

        pubstatus = None        
        if self.wpPublishStatusValue == ZPubMetaDataView.WP_PUBLISHED:
            pubstatus = u"publish" #$NON-NLS-1$
        elif self.wpPublishStatusValue == ZPubMetaDataView.WP_DRAFT:
            pubstatus = u"draft" #$NON-NLS-1$
        elif self.wpPublishStatusValue == ZPubMetaDataView.WP_PENDING:
            pubstatus = u"pending" #$NON-NLS-1$            
        elif self.wpPublishStatusValue == ZPubMetaDataView.WP_PRIVATE:
            pubstatus = u"private" #$NON-NLS-1$
                                    
        if pubstatus:
            setCustomWPMetaDataAttribute(pubMetaData, u"post_status", pubstatus) #$NON-NLS-1$
    # end updatePubMetaData())

# end ZPubMetaDataView

# ------------------------------------------------------------------------------
# Creates text area control with the validation icon and message shown at the bottom
# of the text area.
# ------------------------------------------------------------------------------
class ZValidatingUrlListCtrl(ZValidatingTextCtrl):

    def __init__(self, validator, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0, name = u"ZValidatingUrlListCtrl"): #$NON-NLS-1$ #$NON-NLS-2$
        ZValidatingTextCtrl.__init__(self, validator, parent, id, value, size, style, name)
    # end __init__()

    def _createWidgets(self):
        self.msgLabel = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        ZValidatingTextCtrl._createWidgets(self)
    # end _createWidgets()

    def _layoutWidgets(self):
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.warningImage, 0, wx.ALIGN_CENTER | wx.RIGHT, 2)
        boxSizer.Add(self.msgLabel, 1, wx.EXPAND)

        vboxSizer = wx.BoxSizer(wx.VERTICAL)
        vboxSizer.Add(self.widget, 1, wx.EXPAND)
        vboxSizer.AddSizer(boxSizer, 0, wx.ALL, 2)

        self.SetAutoLayout(True)
        self.SetSizer(vboxSizer)
        self.Layout()
    # end _layoutWidgets()

    def _validateWidget(self):
        ZValidatingTextCtrl._validateWidget(self)
        if not self.isValid:
            self.msgLabel.SetLabel(self.validator.getInvalidReason())
    # end _validateWidget()


    def _setImageVisibility(self):
        ZValidatingTextCtrl._setImageVisibility(self)
        self.msgLabel.Show(not self.isValid)
    # end _setImageVisibility()

# end ZValidatingUrlListCtrl

# ------------------------------------------------------------------------------
# Validates URLs in a multiline string
# ------------------------------------------------------------------------------
class ZMultilineUrlSelectionValidator(ZUrlSelectionValidator):

    def __init__(self):
        ZUrlSelectionValidator.__init__(self, u"") #$NON-NLS-1$
    # end __init__()

    def _validateProtocol(self, value, message):
        # value is  a string containing urls - one per line
        # report errors if a single invalid url is fouund.
        (validUrls, invalidUrls) = parseMultilineUrls(value) #@UnusedVariable
        valid = len(invalidUrls) == 0
        if not valid:
            message  = u"Invalid URL: '%s'" % invalidUrls[0] #$NON-NLS-1$
        return (valid, message)
    # end _validateProtocol()
#end ZMultilineUrlSelectionValidator

# ------------------------------------------------------------------------------
# Simple text area to list a  new line separated list of trackback URLS
# ------------------------------------------------------------------------------
class ZTrackbackUrlsView(ZTransparentPanel):

    def __init__(self, parent, provider):
        ZTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.orginalValue = u"" #$NON-NLS-1$
        self.trackbackListProvider = provider
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.trackbackLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"pubdatawidgets.Trackback.EnterUrlInNewLines")) #$NON-NLS-1$
        validator = ZMultilineUrlSelectionValidator()
        self.trackbackTextCtrl = ZValidatingUrlListCtrl(validator, self, style=wx.TE_MULTILINE )
        self.trackbackTextCtrl.SetToolTipString(_extstr(u"pubdatawidgets.Trackback.EnterUrlInNewLines")) #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.trackbackLabel, 0, wx.ALL, 3)
        vbox.Add(self.trackbackTextCtrl, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT, self.onText, self.trackbackTextCtrl)
    # end _bindWidgetEvents()

    def onText(self, event): #@UnusedVariable
        s = self.trackbackTextCtrl.GetValue()
        (validUrls, invalidUrls) = parseMultilineUrls(s) #@UnusedVariable
        self.trackbackListProvider.setTrackbackUrlList(validUrls)
        if self.orginalValue != s.strip():
            event = ZContentModifiedEvent(self.GetId())
            self.GetEventHandler().AddPendingEvent(event)
        #event.Skip()
    # end onText

    def refresh(self):
        s = u""; #$NON-NLS-1$
        for trackback in self.trackbackListProvider.getTrackbacks():
            s = s + trackback.getUrl() + u"\n" #$NON-NLS-1$
        self.orginalValue = s.strip()
        self.trackbackTextCtrl.SetValue(s)
    # end refresh
# end ZTrackbackUrlsView

# ------------------------------------------------------------------------------
# Function that returns tuple (validUrls, invalidUrls) given string of urls separated by a new line.
# ------------------------------------------------------------------------------
def parseMultilineUrls(multilineUrls):
    # returns tuple (validUrls, invalidUrls) given string of urls separated by a new line.
    validUrls = []
    invalidUrls = []
    urls = multilineUrls.split(u"\n") #$NON-NLS-1$
    for url in urls:
        url = getNoneString(url)
        if not url:
            continue
        if URL_RE.match(url) is not None:
            if url not in validUrls:
                validUrls.append(url)
        else:
            invalidUrls.append(url)
    return (validUrls, invalidUrls)
# end _parseUrls()

