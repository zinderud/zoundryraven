from wx.html import HW_NO_SELECTION #@UnresolvedImport
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.appframework.ui.widgets.controls.list import IZListViewContentProvider
from zoundry.appframework.ui.widgets.controls.list import ZListView
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
from zoundry.blogapp.ui.util.dateformatutil import formatLocalDateAndTime
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
import wx

# ----------------------------------------------------------------------------------------
# The content provider used for the list of publish information.
# ----------------------------------------------------------------------------------------
class ZBlogPostPropertiesListViewContentProvider(IZListViewContentProvider):

    def __init__(self):
        self.imageList = ZMappedImageList()
        self.document = None
    # end __init__()

    def setDocument(self, document):
        self.document = document
    # end setDocument()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 2
    # end getNumColumns()

    def getNumRows(self):
        if self.document is not None:
            return len(self.document.getBlogInfoList())
        return 0
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        columnName = None
        width = -2
        # FIXME (PJ) extern these
        if columnIndex == 0:
            columnName = u"Blog" #$NON-NLS-1$
            width = 250
        elif columnIndex == 1:
            columnName = u"Post Date" #$NON-NLS-1$
            width = 125
#        elif columnIndex == 2:
#            columnName = u"Post ID" #$NON-NLS-1$
#        elif columnIndex == 3:
#            columnName = u"Categories" #$NON-NLS-1$
#        elif columnIndex == 4:
#            columnName = u"Trackback Sent" #$NON-NLS-1$
        return (columnName, None, 0, width)
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        if self.document is not None and rowIndex < len(self.document.getBlogInfoList()) :
            blogInfo = self.document.getBlogInfoList()[rowIndex]
            pubData = blogInfo.getPublishInfo()
            blog = getBlogFromIds(blogInfo.getAccountId(), blogInfo.getBlogId())
            if columnIndex == 0 and blog is not None:
                return blog.getName()
            elif columnIndex == 1:
                issuedTime = pubData.getPublishedTime()
                return formatLocalDateAndTime(issuedTime)
            elif columnIndex == 2:
                return unicode(pubData.getBlogEntryId())
            elif columnIndex == 3:
                return u"" # FIXME impl this #$NON-NLS-1$
            elif columnIndex == 4:
                return u"False"  # FIXME impl this #$NON-NLS-1$
        return u"" #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

# end ZBlogPostPropertiesListViewContentProvider


# ----------------------------------------------------------------------------------------
# A concrete impl of a blog post details panel.  This one shows 'general' information
# about the blog post.
# ----------------------------------------------------------------------------------------
class ZGeneralBlogPostDetailsPanel(ZAbstractDetailsPanel):

    GENERAL_HTML_TEMPLATE = u"""
       <html>
         <body>
           <font size="-1">
           <table width="100%%" cellspacing="0" cellpadding="2">
             <tr><td width="1%%"><b>Title:  </b></td><td>%(title)s</td></tr>
             <tr><td><b>Modified:  </b></td><td>%(modified)s</td></tr>
             <tr><td><b>Created:  </b></td><td>%(created)s</td></tr>
             <tr><td><b>Entry ID:  </b></td><td>%(entryid)s</td></tr>
           </table>
           </font>
         </body>
       </html>
    """ #$NON-NLS-1$

    def __init__(self, parent):
        self.postPropsContentProvider = ZBlogPostPropertiesListViewContentProvider()

        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        self.generalHtmlBox = ZHTMLControl(self, style = wx.SIMPLE_BORDER | HW_NO_SELECTION)
        # FIXME (PJ / EPW) re-use ZWhereFoundBlogPostListView (and model).
        self.postPropertiesListView = ZListView(self.postPropsContentProvider, self)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        generalSBSizer = wx.BoxSizer(wx.HORIZONTAL)
        generalSBSizer.Add(self.generalHtmlBox, 1, wx.EXPAND)
        postPropertiesSBSizer = wx.BoxSizer(wx.HORIZONTAL)
        postPropertiesSBSizer.Add(self.postPropertiesListView, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(generalSBSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(postPropertiesSBSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def _formatHtml(self, document):
        title = document.getTitle()
        modified = document.getLastModifiedTime()
        created = document.getCreationTime()
        id = document.getId()
        args = {
            u"title" : title, #$NON-NLS-1$
            u"modified" : formatLocalDateAndTime(modified), #$NON-NLS-1$
            u"created" :  formatLocalDateAndTime(created), #$NON-NLS-1$
            u"entryid" :  id #$NON-NLS-1$
        }
        return ZGeneralBlogPostDetailsPanel.GENERAL_HTML_TEMPLATE % args
    # end _formatHtml()

    def onSelectionChanged(self, document):
        self.generalHtmlBox.SetPage(self._formatHtml(document))
        self.postPropsContentProvider.setDocument(document)
        self.postPropertiesListView.refresh()
    # end onSelectionChanged()

# end ZGeneralBlogPostDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a blog post details panel factory that creates a panel for "General"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZGeneralBlogPostDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZGeneralBlogPostDetailsPanel(parent)
    # end createDetailsPanel()

# end ZGeneralBlogPostDetailsPanelFactory
