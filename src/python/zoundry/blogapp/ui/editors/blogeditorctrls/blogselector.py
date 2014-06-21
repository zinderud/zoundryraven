from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.events.listevents import ZEVT_POPUP_LIST_SELECTION
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.controls.listex import ZPopupListView
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.events.editors.blogeditorevents import ZBlogSelectorComboEvent
from zoundry.blogapp.ui.events.editors.blogeditorevents import ZEVT_BLOG_SELECTOR_COMBO
from zoundry.blogapp.ui.events.editors.blogeditorevents import firePublishingChangeEvent
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
import wx #@UnusedImport
import wx.combo #@Reimport


# ------------------------------------------------------------------------------
# Interface that models must implement if they want to be used as input to the
# blog selector control.
# ------------------------------------------------------------------------------
class IZBlogSelectorModel:

    def getAllAccounts(self):
        u"""getAllAccounts() -> IZAccount[]""" #$NON-NLS-1$
    # end getAllAccounts()
    
    def getAllBlogs(self):
        u"""getAllBlogs() -> IZBlogFromAccount[]""" #$NON-NLS-1$
    # end getAllBlogs()

# end IZBlogSelectorModel


# ------------------------------------------------------------------------------
# A content provider for showing the list of available blogs in a list control.
# ------------------------------------------------------------------------------
class ZBlogListContentProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model
        self.blogs = model.getAllBlogs()
        self.filteredBlogs = self.blogs
        self.blogNameFilter = None
        self.accountFilter = None

        self.imageList = self._createImageList()
    # end __init__()

    def _createImageList(self):
        imageList = ZMappedImageList()
        imageList.addImage(u"blog", getResourceRegistry().getBitmap(u"images/perspectives/standard/navigator/blog.png")) #$NON-NLS-1$ #$NON-NLS-2$
        return imageList
    # end _createImageList()

    def setBlogNameFilter(self, blogName):
        self.blogNameFilter = blogName
        self.filteredBlogs = self._getFilteredBlogs()
    # end setBlogNameFilter()

    def setAccountFilter(self, account):
        self.accountFilter = account
        self.filteredBlogs = self._getFilteredBlogs()
    # end setAccountFilter()

    def getBlogAtIdx(self, idx):
        return self.filteredBlogs[idx]
    # end getBlogAtIdx()

    def getBlogs(self):
        # FIXME (EPW) need a "<No Blog>" selection in the BlogSelector
        return self.blogs
    # end getBlogs()

    # FIXME (EPW) sort the result set
    def _getFilteredBlogs(self):
        if not self.blogNameFilter and self.accountFilter is None:
            return self.blogs

        blogs = []
        for blog in self.blogs:
            okToAdd = True
            if self.blogNameFilter and not self.blogNameFilter in blog.getName():
                okToAdd = False
            if self.accountFilter and blog.getAccount() != self.accountFilter:
                okToAdd = False
            if okToAdd:
                blogs.append(blog)

        return blogs
    # end _getFilteredBlogs()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.filteredBlogs)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (u"The Header", u"", 0, ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$ #$NON-NLS-2$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        blog = self.filteredBlogs[rowIndex]
        return blog.getName()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return self.imageList[u"blog"] #$NON-NLS-1$
    # end getRowImage()

# end ZBlogListContentProvider


# ------------------------------------------------------------------------------
# The blog selector popup is the transient window that gets displayed when the
# user clicks the little down arrow on the BlogSelector widget.  This popup
# window displays the available blogs in a list for the user to select.
# ------------------------------------------------------------------------------
class ZBlogSelectorPopup(wx.combo.ComboPopup):

    def __init__(self, model, combo):
        self.model = model
        self.combo = combo

        wx.combo.ComboPopup.__init__(self)
    # end __init__()

    def Init(self):
        self.blog = None
    # end Init()

    def Create(self, parent):
        self.parent = parent
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end Create()

    def GetControl(self):
        return self.panel
    # end GetControl()

    def GetStringValue(self):
        if self.blog:
            return self.blog.getName()
        return u"" #$NON-NLS-1$
    # end GetStringValue()

    def OnPopup(self):
        self.blogListView._resizeColumns()
        self.filterTextBox.SetFocus()
    # end OnPopup()

    def SetStringValue(self, value): #@UnusedVariable
        pass
    # end SetStringValue()

    def setBlog(self, blog):
        self.blog = blog
    # end setBlog()

    def _createWidgets(self):
        self.panel = wx.Panel(self.parent, wx.ID_ANY, style = wx.SIMPLE_BORDER)
        self.panel.SetBackgroundColour(u"#FFFFE6") #$NON-NLS-1$
        self.filterLabel = wx.StaticText(self.panel, wx.ID_ANY, _extstr(u"blogselector.BlogName")) #$NON-NLS-1$
        self.filterTextBox = wx.TextCtrl(self.panel, wx.ID_ANY, style = wx.TE_PROCESS_ENTER)
        self.filterTextBox.SetSizeHints(-1, getTextDimensions(u"Zoundry", self.filterTextBox)[1]) #$NON-NLS-1$
        self.filterAcctLabel = wx.StaticText(self.panel, wx.ID_ANY, _extstr(u"blogselector.Account")) #$NON-NLS-1$
        self.filterAccountCombo = wx.ComboBox(self.panel, wx.ID_ANY, style = wx.CB_READONLY)
        self.separator = wx.StaticLine(self.panel, wx.HORIZONTAL)

        self.contentProvider = ZBlogListContentProvider(self.model)
        self.blogListView = ZPopupListView(self.contentProvider, self.panel, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER | wx.LC_NO_HEADER)
        self.blogListView.SetBackgroundColour(u"#FFFFE6") #$NON-NLS-1$
    # end _createWidgets()

    def _populateWidgets(self):
        self.filterAccountCombo.Append(_extstr(u"blogselector._AllAccounts_"), None) #$NON-NLS-1$
        for account in self.model.getAllAccounts():
            self.filterAccountCombo.Append(account.getName(), account)
    # end _populateWidgets()

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        filterBarSizer = wx.BoxSizer(wx.HORIZONTAL)
        filterBarSizer.Add(self.filterLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        filterBarSizer.Add(self.filterTextBox, 1, wx.EXPAND | wx.RIGHT, 5)
        filterBarSizer.Add(self.filterAcctLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        filterBarSizer.Add(self.filterAccountCombo, 0, wx.EXPAND | wx.RIGHT, 5)

        self.sizer.AddSizer(filterBarSizer, 0, wx.EXPAND | wx.ALL, 3)
        self.sizer.Add(self.separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        self.sizer.Add(self.blogListView, 1, wx.EXPAND | wx.ALL, 2)

        self.blogListView.SetSizeHints(-1, self._getNumBlogListItems() * 17)

        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(True)
        self.panel.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.panel.Bind(ZEVT_POPUP_LIST_SELECTION, self.onBlogSelection, self.blogListView)
        self.panel.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onBlogSelection, self.blogListView)
        self.panel.Bind(wx.EVT_TEXT, self.onBlogNameFilter, self.filterTextBox)
        self.panel.Bind(wx.EVT_COMBOBOX, self.onAccountFilter, self.filterAccountCombo)
    # end _bindWidgetEvents()

    def _getNumBlogListItems(self):
        return self.contentProvider.getNumRows()
    # end _getNumBlogListItems()

    def onBlogNameFilter(self, event):
        self.contentProvider.setBlogNameFilter(self.filterTextBox.GetValue())
        self.blogListView.refresh()
        event.Skip()
    # end onBlogNameFilter()

    def onAccountFilter(self, event):
        selId = self.filterAccountCombo.GetCurrentSelection()
        account = self.filterAccountCombo.GetClientData(selId)
        self.contentProvider.setAccountFilter(account)
        self.blogListView.refresh()
        event.Skip()
    # end onAccountFilter()

    def onBlogSelection(self, event): #@UnusedVariable
        selectionIdx = self.blogListView.getSelection()[0]
        self.blog = self.contentProvider.getBlogAtIdx(selectionIdx)
        self.Dismiss()
        event = ZBlogSelectorComboEvent(self.combo.GetId(), self.blog)
        self.combo.GetEventHandler().AddPendingEvent(event)
        event.Skip()
    # end onBlogSelection()

    def getPreferredHeight(self):
        return self.panel.GetBestSizeTuple()[1]
    # end getPreferredHeight()

# end ZBlogSelectorPopup


# ------------------------------------------------------------------------------
# A control that lets the user select a blog from the list of blogs configured
# in the application.  This widget is a custom combo control that shows all of
# the blogs in a list view.
# ------------------------------------------------------------------------------
class ZBlogSelectorCombo(wx.combo.ComboCtrl):

    def __init__(self, parent, model):
        self.model = model
        self.blog = None

        wx.combo.ComboCtrl.__init__(self, parent, style = wx.CB_READONLY)

        self.SetFont(getDefaultFontBold())
        self.UseAltPopupWindow(True)
        self.popupCtrl = self._createPopupControl()
        self.SetPopupControl(self.popupCtrl)
        self.SetPopupMaxHeight(min(self.popupCtrl.getPreferredHeight(), 250))
        self.SetValue(u"") #$NON-NLS-1$

        self.Bind(ZEVT_BLOG_SELECTOR_COMBO, self.onSelection, self)
    # end __init__()

    def getBlog(self):
        return self.blog
    # end getBlog()

    def selectBlog(self, accountId, blogId):
        self.blog = getBlogFromIds(accountId, blogId)
        if self.blog is not None:
            self.popupCtrl.setBlog(self.blog)
            self.SetValue(self.blog.getName())
    # end selectBlog()

    def onSelection(self, event):
        self.blog = event.getBlog()
        firePublishingChangeEvent(self)
        event.Skip()
    # end onSelection()

    def setExtent(self, rExtent):
        self.SetPopupExtents(0, rExtent)
    # end setExtent()

    def _createPopupControl(self):
        return ZBlogSelectorPopup(self.model, self)
    # end _createPopupControl()

    def PaintComboControl(self, dc, rect):
        # FIXME (EPW) override to paint the Icon AND the text in the Combo
        wx.combo.ComboPopup.PaintComboControl(self, dc, rect)
    # end PaintComboControl()

# end ZBlogSelectorCombo
