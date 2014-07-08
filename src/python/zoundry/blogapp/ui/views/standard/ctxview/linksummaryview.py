from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.standard.ctxview.linkdetails.linkdetails import ZLinkDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.summaryview import ZSummaryView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_LINKS_FILTER_CHANGED

# ------------------------------------------------------------------------------
# A view that shows summary information about a link.  When a link is selected,
# this view should be visible and will show summary information about the link.
# ------------------------------------------------------------------------------
class ZLinkSummaryView(ZSummaryView):

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
        return _extstr(u"linksummaryview.LinkSummary") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createDetailsContainer(self, parent):
        return ZLinkDetailsPanelContainer(parent)
    # end _createDetailsContainer()

    def _bindWidgetEvents(self):
        ZSummaryView._bindWidgetEvents(self)

        self.Bind(ZEVT_VIEW_LINKS_FILTER_CHANGED, self.onLinksFilterChanged)
    # end _bindWidgetEvents()

    def onViewSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.LINK_SELECTION:
            self.detailsContainer.onLinkSelectionChanged(selection.getData())
            self.enableSelection()
        elif selection.getType() in self.clearEventTypes:
            self.clearSelection()
        event.Skip()
    # end onViewSelectionChanged()

    def onLinksFilterChanged(self, event):
        self.clearSelection()
        event.Skip()
    # end onLinksFilterChanged()

# end ZLinkSummaryView
