from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.appframework.ui.widgets.controls.progress import ZProgressLabelCtrl
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.util.zthread import ZThread
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.dialogs.accountsynchmodel import ZAccountSynchModel
from zoundry.blogapp.ui.common.publisher import ZBlogCheckboxListContentProvider
import wx

# --------------------------------------------------------------------------------
# Account synch/refresh dialog.
#
# Show accName
# Show check list control of blog list
# show 'refresh blog list' button - use bg task with progress meter to get blog list
# show ok , cancel buttons.
# if ok, then download selected blogs.
# --------------------------------------------------------------------------------
class ZSynchronizeAccountBlogsDialog(ZHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent, account):
        self.account = account
        self.model = ZAccountSynchModel(self.account)
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"synchronizeaccountdialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZSynchronizeAccountBlogsDialog") #$NON-NLS-2$ #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.SYNCH_DIALOG)
        self.Layout()
    # end __init__()

    def _getAccount(self):
        return self.account
    # end _getAccount()

    def _createNonHeaderWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"accountblogs.BlogList")) #$NON-NLS-1$
        self.blogListProvider = ZBlogCheckboxListContentProvider()
        self.blogListControl = ZCheckBoxListViewWithButtons(self.blogListProvider, self)
        self.blogListControl.SetSizeHints(-1, 150)
        self.refreshButton = wx.Button(self, wx.ID_ANY, _extstr(u"synchronizeaccountdialog.RefreshBlogList")) #$NON-NLS-1$
        self.animateControl = ZProgressLabelCtrl(self)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self._showBusy(False)
        blogs = []
        blogs.extend(self._getAccount().getBlogs())
        self._populateProvider(blogs)
    # end _populateNonHeaderWidgets()

    def _populateProvider(self, blogs):
        self.animateControl.setLabel(_extstr(u"synchronizeaccountdialog.FetchingBlogList")) #$NON-NLS-1$
        self.blogListProvider.setBlogList(blogs)
        self.blogListControl.checkBoxListView.refreshItems()
    # end _populateProvider()

    def _layoutNonHeaderWidgets(self):

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.refreshButton, 0 , wx.LEFT | wx.ALL, 5)
        box.Add(self.animateControl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.ALL, 5)

        sizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sizer.Add(self.blogListControl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.AddSizer(box, 0, wx.LEFT | wx.BOTTOM, 5)
        return sizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onRefreshBlogList, self.refreshButton)
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onBlogCheckedEvent, self.blogListControl)
        self.Bind(ZEVT_REFRESH, self.onRefreshEvent, self)
    # end _bindWidgetEvents()

    def _getHeaderTitle(self):
        return _extstr(u"synchronizeaccountdialog.HeaderTitle") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"synchronizeaccountdialog.HeaderMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/mediastorage/manage/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _showBusy(self, enable): #$NON-NLS-1$
        self.animateControl.Show(enable)
    # _showBusy()

    def onRefreshEvent(self, event):
        data = event.getData()
        if u"begin-list-blogs" == data: #$NON-NLS-1$
            self._showBusy(True)
        elif u"end-list-blogs" == data: #$NON-NLS-1$
            self._showBusy(False)
    # onRefreshEvent()

    def _refreshBlogList(self):
        # called via runnable ZListBlogsTasks
        fireRefreshEvent(self, u"begin-list-blogs") #$NON-NLS-1$
        blogs = self.model.listAllBlogs()
        self._populateProvider(blogs)
        fireRefreshEvent(self, u"end-list-blogs") #$NON-NLS-1$
    # _refreshBlogList()

    def onRefreshBlogList(self, event): #@UnusedVariable
        thread = ZThread(ZListBlogsTasks(self), u"ZSynchronizeAccountBlogsDialog.ZListBlogsTasks", True) #$NON-NLS-1$
        thread.start()

    # end onRefreshBlogList()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def getSelectedBlogList(self):
        rval = self.blogListProvider.getSelectedBlogList()
        return rval
    # end _getSelectedBlogList

    def onBlogCheckedEvent(self, event): #@UnusedVariable
        pass
# end ZSynchronizeAccountBlogsDialog

# --------------------------------
# Runnable callback to fetch list of blogs from online server.
# --------------------------------
class ZListBlogsTasks(IZRunnable):

    def __init__(self, owner):
        self.owner = owner

    def run(self):
        self.owner._refreshBlogList()



