from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx


# ------------------------------------------------------------------------------
# The IDs of the built-in views.
# ------------------------------------------------------------------------------
class IZViewIds:

    LINKS_VIEW = u"zoundry.blogapp.ui.core.views.links" #$NON-NLS-1$
    LINKS_LIST_VIEW = u"zoundry.blogapp.ui.core.views.list-links" #$NON-NLS-1$
    IMAGES_VIEW = u"zoundry.blogapp.ui.core.views.images" #$NON-NLS-1$
    IMAGES_LIST_VIEW = u"zoundry.blogapp.ui.core.views.list-images" #$NON-NLS-1$
    POSTS_VIEW = u"zoundry.blogapp.ui.core.views.posts" #$NON-NLS-1$
    POSTS_LIST_VIEW = u"zoundry.blogapp.ui.core.views.list-posts" #$NON-NLS-1$
    BLOG_POST_SUMMARY_VIEW = u"zoundry.blogapp.ui.core.views.post-summary" #$NON-NLS-1$
    TAGS_VIEW = u"zoundry.blogapp.ui.core.views.tags" #$NON-NLS-1$
    TAG_CLOUD_VIEW = u"zoundry.blogapp.ui.core.views.tag-cloud" #$NON-NLS-1$
    NAVIGATOR_VIEW = u"zoundry.blogapp.ui.core.views.navigator" #$NON-NLS-1$
# end IZViewIds


# ------------------------------------------------------------------------------
# UI Views should implement this interface.
# ------------------------------------------------------------------------------
class IZView:

    def getViewId(self):
        u"Gets the view's id." #$NON-NLS-1$
    # end getViewId()

    def destroy(self):
        u"Called when the view is destroyed." #$NON-NLS-1$
    # end destroy()

# end IZView


# ------------------------------------------------------------------------------
# A common base class for views to share some functionality.  Note that classes
# that extend this class should also extend a wx.Window of some sort.  Some
# methods in this base class assume that.
# ------------------------------------------------------------------------------
class ZView(wx.Panel, IZView):

    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)

        getApplicationModel().getViewRegistry().registerView(self)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy, self)
    # end __init__()

    def getViewId(self):
        raise ZAbstractMethodCalledException(self.__class__, u"getViewId") #$NON-NLS-1$
    # end getViewId()

    def onDestroy(self, event):
        getApplicationModel().getViewRegistry().unregisterView(self)
        event.Skip()
    # end onDestroy()

    def _bindRefreshEvent(self, callback):
        self.Bind(ZEVT_REFRESH, callback)
    # end _bindRefreshEvent()

# end ZView
