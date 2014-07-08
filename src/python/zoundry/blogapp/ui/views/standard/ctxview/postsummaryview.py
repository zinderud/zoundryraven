from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.views.standard.ctxview.postdetails.postdetails import ZBlogPostDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.summaryview import ZSummaryView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_BLOG_POSTS_FILTER_CHANGED


# ------------------------------------------------------------------------------
# A view that shows summary information about a blog post.  When a blog post/
# document is selected, this view should be visible and will show summary/
# preview information about the blog post.
# ------------------------------------------------------------------------------
class ZBlogPostSummaryView(ZSummaryView):

    def __init__(self, parent):
        ZSummaryView.__init__(self, parent)

        self.clearEventTypes = [
            IZViewSelectionTypes.BLOG_POSTS_SELECTION,
            IZViewSelectionTypes.ACCOUNT_SELECTION,
            IZViewSelectionTypes.BLOG_SELECTION,
            IZViewSelectionTypes.BLOG_IMAGES_SELECTION,
            IZViewSelectionTypes.BLOG_LINKS_SELECTION,
            IZViewSelectionTypes.BLOG_TAGS_SELECTION,
            IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION,
            IZViewSelectionTypes.BLOG_EDITED_SELECTION,
        ]
    # end __init__()

    def _getHeaderLabel(self):
        return _extstr(u"postsummaryview.BlogPostSummary") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createDetailsContainer(self, parent):
        return ZBlogPostDetailsPanelContainer(parent)
    # end _createDetailsContainer()

    def _bindWidgetEvents(self):
        ZSummaryView._bindWidgetEvents(self)

        self.Bind(ZEVT_VIEW_BLOG_POSTS_FILTER_CHANGED, self.onBlogPostsFilterChanged)
    # end _bindWidgetEvents()

    def onViewSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.DOCUMENT_SELECTION:
            (blog, document) = selection.getData() #@UnusedVariable
            self.detailsContainer.onBlogPostSelectionChanged(document)
            self.enableSelection()
        elif selection.getType() in self.clearEventTypes:
            self.clearSelection()
        event.Skip()
    # end onViewSelectionChanged()

    def onBlogPostsFilterChanged(self, event):
        self.clearSelection()
        event.Skip()
    # end onBlogPostsFilterChanged()

# end ZBlogPostSummaryView
