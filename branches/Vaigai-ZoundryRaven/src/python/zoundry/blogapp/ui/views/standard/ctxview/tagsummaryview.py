from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_TAGS_FILTER_CHANGED
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.summaryview import ZSummaryView
from zoundry.blogapp.ui.views.standard.ctxview.tagdetails.tagdetails import ZTagDetailsPanelContainer
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes

# ------------------------------------------------------------------------------
# A view that shows summary information about a tag.  When a image is selected,
# this view should be visible and will show summary information about the tag.
# ------------------------------------------------------------------------------
class ZTagSummaryView(ZSummaryView):

    def __init__(self, parent):
        ZBoxedView.__init__(self, parent)

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
        return _extstr(u"tagsummaryview.TagSummary") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createDetailsContainer(self, parent):
        return ZTagDetailsPanelContainer(parent)
    # end _createDetailsContainer()

    def _bindWidgetEvents(self):
        ZSummaryView._bindWidgetEvents(self)

        self.Bind(ZEVT_VIEW_TAGS_FILTER_CHANGED, self.onTagsFilterChanged)
    # end _bindWidgetEvents()

    def onViewSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.TAG_SELECTION:
            self.detailsContainer.onTagSelectionChanged(selection.getData())
            self.enableSelection()
        elif selection.getType() in self.clearEventTypes:
            self.clearSelection()
        event.Skip()
    # end onViewSelectionChanged()

    def onTagsFilterChanged(self, event):
        self.clearSelection()
        event.Skip()
    # end onTagsFilterChanged()

# end ZTagSummaryView
