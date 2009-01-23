from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.pubsubpage import ZPublishingPrefSubPage

# ------------------------------------------------------------------------------
# Implements the blog preferences sub-page for publishing options.
# ------------------------------------------------------------------------------
class ZBlogPublishingPrefSubPage(ZPublishingPrefSubPage):

    def __init__(self, parent, session):
        ZPublishingPrefSubPage.__init__(self, parent, session)
    # end __init__()

    def _getOverrideLabel(self):
        return _extstr(u"pubsubpage.OverrideAccountPublishingSettings") #$NON-NLS-1$
    # end _getOverrideLabel()

# end ZBlogPublishingPrefSubPage
