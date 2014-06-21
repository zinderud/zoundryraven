from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.tagsubpage import ZTagSitesPrefSubPage

# ------------------------------------------------------------------------------
# Implements the blog preferences sub-page for tag sites options.
# ------------------------------------------------------------------------------
class ZBlogTagSitesPrefSubPage(ZTagSitesPrefSubPage):

    def __init__(self, parent, session):
        ZTagSitesPrefSubPage.__init__(self, parent, session)
    # end __init__()

    def _getOverrideTagSitesLabel(self):
        return _extstr(u"tagsubpage.OverrideAccountTagSitesSettings") #$NON-NLS-1$
    # end _getOverrideTagSitesLabel()

# end ZBlogTagSitesPrefSubPage
