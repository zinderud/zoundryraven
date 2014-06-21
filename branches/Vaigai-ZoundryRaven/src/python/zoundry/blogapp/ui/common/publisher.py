from zoundry.appframework.ui.widgets.controls.listex import IZCheckBoxListViewContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.messages import _extstr
# ------------------------------------------------------------------------------
# Content provider for blog list checkboxes
# ------------------------------------------------------------------------------
class ZBlogCheckboxListContentProvider(IZCheckBoxListViewContentProvider):

    def __init__(self):

        self.columns = [
            (_extstr(u"accountblogs.BlogName"), None, 0, ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
        ]
        self.blogList = []
        self.seletedBlogList = []
    # end __init__()

    def setBlogList(self, blogList):
        blogList.sort( lambda x, y: cmp( x.getName().lower(), y.getName().lower() ) )
        self.blogList = blogList
        self.seletedBlogList = []
    # end setBlogList()

    def getSelectedBlogList(self):
        return self.seletedBlogList
    # end getSelectedBlogList()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return len(self.columns)
    # end getNumColumns()

    def getNumRows(self):
        return len(self.blogList)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        if len(self.blogList) > 0 and rowIndex < len(self.blogList):
            blog = self.blogList[rowIndex]
            if columnIndex == 0:
                return getSafeString(blog.getName())
            elif columnIndex == 1:
                return getSafeString(blog.getUrl())
        return u"NA-r%d-c%d" % (rowIndex, columnIndex) #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex): #@UnusedVariable
        return False
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        if len(self.blogList) > 0 and rowIndex < len(self.blogList):
            blog = self.blogList[rowIndex]
            if checked and not (blog in self.seletedBlogList):
                self.seletedBlogList.append(blog)
            elif not checked and blog in self.seletedBlogList:
                self.seletedBlogList.remove(blog)
    # end setChecked
