from zoundry.blogapp.services.docindex.index import IZTagSearchFilter
from zoundry.blogapp.ui.common.blogpostswidgets import ZBlogPostsListByTagQueryModel
from zoundry.blogapp.ui.common.blogpostswidgets import ZWhereFoundBlogPostListView
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
import wx


# ----------------------------------------------------------------------------------------
# A concrete impl of a tag details panel.  This one shows 'general' information
# about the tag.
# ----------------------------------------------------------------------------------------
class ZInfoTagDetailsPanel(ZAbstractDetailsPanel):

    def __init__(self, parent):
        self.model = ZBlogPostsListByTagQueryModel()
        self.blogPostListView = None

        ZAbstractDetailsPanel.__init__(self, parent)
    # end __init__()

    def _createWidgets(self):
        self.blogPostListView = ZWhereFoundBlogPostListView(self, self.model)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.Add(self.blogPostListView, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(vBox)
    # end _layoutWidgets()

    def onSelectionChanged(self, data):
        (blog, tagIDO) = data

        # first set the tag
        self.model.setTagIDO(tagIDO)
        if blog is not None:
            self.model.setBlogIdCriteria(blog.getId())
        else:
            self.model.setBlogIdCriteria(IZTagSearchFilter.UNPUBLISHED_BLOG_ID)
        # Refresh the list of blog posts
        self.blogPostListView.refresh()
    # end onTagSelectionChanged()

# end ZInfoTagDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a link details panel factory that creates a panel for "Link Info"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZInfoTagDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZInfoTagDetailsPanel(parent)
    # end createDetailsPanel()

# end ZInfoTagDetailsPanelFactory
