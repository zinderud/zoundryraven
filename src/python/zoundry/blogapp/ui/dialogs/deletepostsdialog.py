from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.util.uiutil import getRootWindowOrDialog
from zoundry.appframework.ui.widgets.controls.listex import IZCheckBoxListViewContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZStandardDialog
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.messages import _extstr
import wx


# ------------------------------------------------------------------------------
# Content provider for a list of blogs.
# ------------------------------------------------------------------------------
class ZBlogListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self, blogs, blog):
        self.blogs = blogs
        self.blog = blog
        self.checked = []

        for listBlog in self.blogs:
            isChecked = listBlog == blog
            self.checked.append(isChecked)

        self.imageMap = ZMappedImageList()
    # end __init__()

    def getImageList(self):
        return self.imageMap
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.blogs)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (u"Blog Name", None, None, ZListViewEx.COLUMN_LOCKED | ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.blogs[rowIndex].getName()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex):
        return self.checked[rowIndex]
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        self.checked[rowIndex] = checked
    # end setChecked()

    def getCheckedBlogs(self):
        checkedBlogs = []
        for index in range(0, len(self.blogs)):
            if self.checked[index]:
                checkedBlogs.append(self.blogs[index])
        return checkedBlogs
    # end getCheckedBlogs()

    def allBlogsChecked(self):
        u"""Returns true if all blogs in the list are checked.""" #$NON-NLS-1$
        for checked in self.checked:
            if not checked:
                return False
        return True
    # end allBlogsChecked()

# end ZBlogListContentProvider


# ------------------------------------------------------------------------------
# Dialog to prompt the user to confirm deletion of a blog post.
# ------------------------------------------------------------------------------
class ZConfirmDeletePostFromMultipleBlogsDialog(ZStandardDialog):

    def __init__(self, parent, document, blog, blogs):
        self.document = document
        self.blog = blog
        self.blogs = blogs

        title = _extstr(u"deletepostsdialog.DeletePublishedPost") #$NON-NLS-1$
        caption = u"%s: '%s'\n%s:" % (_extstr(u"deletepostsdialog.DeleteBlogPost"), getSafeString(self.document.getTitle()), _extstr(u"deletepostsdialog.DeleteFromTheseBlogs")) #$NON-NLS-1$ #$NON-NLS-3$ #$NON-NLS-2$
        buttonMask = ZBaseDialog.YES_BUTTON | ZBaseDialog.NO_BUTTON
        ZStandardDialog.__init__(self, parent, title, caption, buttonMask, u"question") #$NON-NLS-1$

        (w, h) = self.GetBestSizeTuple()
        w = min(max(w, 500), 600)
        self.SetSize(wx.Size(w, h))
        self.Layout()
    # end __init__()

    def _createStandardDialogWidgets(self):
        ZStandardDialog._createStandardDialogWidgets(self)

        self.provider = ZBlogListContentProvider(self.blogs, self.blog)
        style = wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL
        self.blogsCheckList = ZCheckBoxListViewWithButtons(self.provider, self.topPanel, style = style)

        singleBlog = len(self.blogs) == 1
        self.localCopyCB = wx.CheckBox(self.topPanel, wx.ID_ANY, _extstr(u"deletepostsdialog.DeleteLocalCopy")) #$NON-NLS-1$
        self.localCopyCB.SetValue(singleBlog)
#        self.localCopyCB.Enable(singleBlog)
    # end _createStandardDialogWidgets()

    def _layoutTopPanel(self):
        # horizontal sizer holds the image and the caption
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        if self.image:
            hsizer.Add(self.image, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.captionText, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.blogsCheckList, 1, wx.EXPAND | wx.ALL, 3)
        hsizer.AddSizer(sizer, 1, wx.EXPAND | wx.ALL, 10)

        # vertical sizer has the horizontal sizer and the checkbox
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddSizer(hsizer, 1, wx.EXPAND | wx.ALL, 2)
        vsizer.Add(self.localCopyCB, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        return vsizer
    # end _layoutTopPanel()

    def _bindWidgetEvents(self):
        ZStandardDialog._bindWidgetEvents(self)

        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onCheckListChange, self.blogsCheckList)
    # end _bindWidgetEvents()

    def onCheckListChange(self, event):
        allBlogs = self.provider.allBlogsChecked()
        self.localCopyCB.SetValue(allBlogs)
        event.Skip()
    # end onCheckListChange()

    def _setInitialFocus(self):
        self._getNoButton().SetFocus()
    # end _setInitialFocus()

    def showDialog(self):
        result = self.ShowModal()
        return (result == wx.ID_YES, self.localCopyCB.IsChecked(), self.provider.getCheckedBlogs())
    # end showDialog()

# end ZConfirmDeletePostFromMultipleBlogsDialog


def ZShowConfirmDeletePostFromMultipleBlogsDialog(parent, document, blog, blogs):
    u"""Convenience function for opening the 'confirm delete post
    from multiple blogs dialog.  Returns a tuple:
    0 : wx.ID_*
    1 : alsoDeleteLocalCopy
    2 : list of blogs to delete from""" #$NON-NLS-1$

    parent = getRootWindowOrDialog(parent)
    dlg = ZConfirmDeletePostFromMultipleBlogsDialog(parent, document, blog, blogs)
    dlg.CenterOnParent()

    result = dlg.showDialog()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
    return result
# end ZShowConfirmDeletePostFromMultipleBlogsDialog()
