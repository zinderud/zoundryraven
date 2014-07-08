from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.sizers.cardsizer import ZCardSizer
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.views.standard.ctxview.acctsummary import ZContextInfoAccountSummaryView
from zoundry.blogapp.ui.views.standard.ctxview.blogsummary import ZContextInfoBlogSummaryView
from zoundry.blogapp.ui.views.standard.ctxview.dashboard import ZDashboardView
from zoundry.blogapp.ui.views.standard.ctxview.imagesview import ZContextInfoImagesView
from zoundry.blogapp.ui.views.standard.ctxview.linksview import ZContextInfoLinksView
from zoundry.blogapp.ui.views.standard.ctxview.postsview import ZContextInfoPostsView
from zoundry.blogapp.ui.views.standard.ctxview.tagsview import ZContextInfoTagsView
from zoundry.blogapp.ui.views.standard.ctxview.postsview import ZContextInfoEditedView
from zoundry.blogapp.ui.views.standard.ctxview.welcome import ZWelcomeView
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
import wx

CONTEXT_TYPE_NONE = 0


# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View.  This view shows
# the user information about whatever they have selected in the Navigator View.
# --------------------------------------------------------------------------------------
class ZContextInfoView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self.currentState = CONTEXT_TYPE_NONE
        self.currentSelection = None

        self.stateMap = {
            CONTEXT_TYPE_NONE : self._showDashboardOrWelcomeView,
            IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION : self._showDashboardOrWelcomeView,
            IZViewSelectionTypes.ACCOUNT_SELECTION : self._showAccountSummary,
            IZViewSelectionTypes.BLOG_SELECTION : self._showBlogSummary,
            IZViewSelectionTypes.BLOG_POSTS_SELECTION : self._showPostsView,
            IZViewSelectionTypes.BLOG_TAGS_SELECTION : self._showTagsView,
            IZViewSelectionTypes.BLOG_IMAGES_SELECTION : self._showImagesView,
            IZViewSelectionTypes.BLOG_LINKS_SELECTION : self._showLinksView,
            IZViewSelectionTypes.BLOG_EDITED_SELECTION : self._showEditedView,

        }

        self._createViews()
        self._layoutViews()
        self.refreshWidgets()

        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
    # end __init__()

    def _createViews(self):
        self.welcomeView = ZWelcomeView(self)
        self.dashboardView = ZDashboardView(self)
        self.accountSummaryView = ZContextInfoAccountSummaryView(self)
        self.blogSummaryView = ZContextInfoBlogSummaryView(self)
        self.postsView = ZContextInfoPostsView(self)
        self.imagesView = ZContextInfoImagesView(self)
        self.linksView = ZContextInfoLinksView(self)
        self.tagsView = ZContextInfoTagsView(self)
        self.editedView = ZContextInfoEditedView(self)#pitchaimuthu

    # end _createViews()

    def _layoutViews(self):
        sizer = ZCardSizer()

        sizer.Add(self.welcomeView)
        sizer.Add(self.dashboardView)
        sizer.Add(self.accountSummaryView)
        sizer.Add(self.blogSummaryView)
        sizer.Add(self.postsView)
        sizer.Add(self.imagesView)
        sizer.Add(self.linksView)
        sizer.Add(self.tagsView)
        sizer.Add(self.editedView)#pitchaimuthu

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end _layoutViews()

    def onViewSelectionChanged(self, event):
        self._doSelectionChanged(event.getSelection())
        event.Skip()
    # end onViewSelectionChanged()

    # Called when the state changes.
    def refreshWidgets(self):
        showMethod = self._showDashboardOrWelcomeView
        if self.currentState in self.stateMap:
            showMethod = self.stateMap[self.currentState]

        self._hideAllViews()
        showMethod()
        self.Layout()
        self.Refresh()
    # end refreshWidgets()

    # Called when the user selects something in the Navigator.
    def _doSelectionChanged(self, selection):
        if selection.getType() in self.stateMap:
            newState = selection.getType()
            if newState != self.currentState:
                self.currentState = newState
                self.refreshWidgets()
    # end _doSelectionChanged()

    def _hideAllViews(self):
        self.welcomeView.Show(False)
        self.dashboardView.Show(False)
        self.accountSummaryView.Show(False)
        self.blogSummaryView.Show(False)
        self.postsView.Show(False)
        self.imagesView.Show(False)
        self.linksView.Show(False)
        self.tagsView.Show(False)
    # end _hideAllViews()

    def _showWelcomePage(self):
        self.welcomeView.Show(True)
    # end _showWelcomePage()

    def _showDashboardView(self):
        self.dashboardView.Show(True)
    # end _showDashboardView()

    def _showAccountSummary(self):
        self.accountSummaryView.Show(True)
    # end _showAccountSummary()

    def _showBlogSummary(self):
        self.blogSummaryView.Show(True)
    # end _showBlogSummary()

    def _showPostsView(self):
        self.postsView.Show(True)
    # end _showPostsView()

    def _showImagesView(self):
        self.imagesView.Show(True)
    # end _showImagesView()

    def _showLinksView(self):
        self.linksView.Show(True)
    # end _showLinksView()

    def _showEditedView(self):#pitchaimuthu
        self.editedView.Show(True)
    # end _showLinksView()


    def _showTagsView(self):
        self.tagsView.Show(True)
    # end _showLinksView()

    def _showDashboardOrWelcomeView(self):
        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accounts = accountStore.getAccounts()
        if accounts is None or len(accounts) == 0:
            self._showWelcomePage()
        else:
            self._showDashboardView()
    # end _showDashboardOrWelcomeView()

    def destroy(self):
        self.welcomeView.destroy()
        self.dashboardView.destroy()
        self.accountSummaryView.destroy()
        self.blogSummaryView.destroy()
        self.postsView.destroy()
        self.imagesView.destroy()
        self.linksView.destroy()
        self.tagsView.destroy()
    # end destroy()

# end ZContextInfoView
