from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.util.clipboardutil import setClipboardText
from zoundry.appframework.util.osutilfactory import getOSUtil
import wx

# ------------------------------------------------------------------------------
# Implements the Open action for images (opens the image the browser).
# ------------------------------------------------------------------------------
class ZOpenImageAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"imageactions._Open") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"imageactions.OpenDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        cursor = wx.BusyCursor()
        url = actionContext.getUrl()
        getOSUtil().openUrlInBrowser(url)
        del cursor
    # end runAction()

# end ZOpenImageAction

# ------------------------------------------------------------------------------
# Implements the Copy Image URL
# ------------------------------------------------------------------------------
class ZCopyImageLocationAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"imageactions._CopyImageLocation") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"imageactions.CopyImageLocationDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        url = actionContext.getUrl()
        setClipboardText(url)
    # end runAction()
# end ZCopyImageLocationAction
