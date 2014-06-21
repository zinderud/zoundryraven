from zoundry.appframework.util.osutil.osutil import ZOSUtilBase
import os

# -------------------------------------------------------------------------------------
# A Linux impl of a Zoundry Raven OS Util class.
# -------------------------------------------------------------------------------------
class ZLinuxOSUtil(ZOSUtilBase):

    def __init__(self):
        ZOSUtilBase.__init__(self)
    # end __init__()

    def getOperatingSystemId(self):
        return u"linux" #$NON-NLS-1$
    # end getOperatingSystemId()

    def _getApplicationDataDirectory(self):
        return os.path.join(u"~", u".zoundry", u"Raven") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
    # end _getApplicationDataDirectory()

# end ZLinuxOSUtil
