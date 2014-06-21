from zoundry.appframework.ui.widgets.controls.advanced.htmlviewimpl.win32 import ZIExploreHTMLViewControl
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.exceptions import ZNotYetImplementedException

# ------------------------------------------------------------------------------
# Factory that creates an instance of IZHTMLViewControl.  The concrete impl
# created depends on the operating system.
# ------------------------------------------------------------------------------
def ZHTMLViewControl(*args, **kw):
    osutil = getOSUtil()
    osId = osutil.getOperatingSystemId()
    if osId == u"win32": #$NON-NLS-1$
        return ZIExploreHTMLViewControl(*args, **kw)
    else:
        raise ZNotYetImplementedException()
# end ZHTMLViewControl