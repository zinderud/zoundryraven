from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.pingsubpage import ZPingSitesPrefSubPage

# ------------------------------------------------------------------------------
# Implements the blog preferences sub-page for ping sites options.
# ------------------------------------------------------------------------------
class ZBlogPingSitesPrefSubPage(ZPingSitesPrefSubPage):

    def __init__(self, parent, session):
        ZPingSitesPrefSubPage.__init__(self, parent, session)
    # end __init__()

    def _getOverridePingSitesLabel(self):
        return _extstr(u"pingsubpage.OverrideAccountPingSitesSettings") #$NON-NLS-1$
    # end _getOverridePingSitesLabel()

# end ZBlogPingSitesPrefSubPage
