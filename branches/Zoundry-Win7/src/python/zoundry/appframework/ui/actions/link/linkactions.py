from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.util.clipboardutil import setClipboardText
from zoundry.appframework.util.osutilfactory import getOSUtil
import wx

# ------------------------------------------------------------------------------
# Implements the Open action for links (opens the link the browser).
# ------------------------------------------------------------------------------
class ZOpenLinkAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"linkactions._Open") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"linkactions.OpenDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        cursor = wx.BusyCursor()
        url = actionContext.getUrl()
        getOSUtil().openUrlInBrowser(url)
        del cursor
    # end runAction()
# end ZOpenLinkAction

# ------------------------------------------------------------------------------
# Implements the Copy link location
# ------------------------------------------------------------------------------
class ZCopyLinkLocationAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"linkactions._CopyLinkLocation") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"linkactions.CopyLinkLocationDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        url = actionContext.getUrl()
        setClipboardText(url)
    # end runAction()
# end ZCopyLinkLocationAction

