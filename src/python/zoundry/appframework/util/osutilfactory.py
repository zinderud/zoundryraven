from zoundry.appframework.util.osutil.linux import ZLinuxOSUtil
from zoundry.appframework.util.osutil.macosx import ZMacOSXOSUtil
import platform

_OS_UTIL_INSTANCE = None


# -------------------------------------------------------------------------------------
# The OSUtil factory - responsible for creating the proper version of the IZOSUtil
# class.
# -------------------------------------------------------------------------------------
class ZOSUtilFactory:

    def createOSUtil(self):
        if self._isLinux():
            return ZLinuxOSUtil()
        elif self._isMacOSX():
            return ZMacOSXOSUtil()
        else:
            # import this on-demand because there may be missing imports on other systems.
            from zoundry.appframework.util.osutil.win32 import ZWindowsOSUtil
            return ZWindowsOSUtil()
    # end createOSUtil()
    
    def _isLinux(self):
        return platform.system() == u"Linux" #$NON-NLS-1$
    # end _isLinux
    
    def _isMacOSX(self):
        return platform.system() == u"MacOSX" #$NON-NLS-1$
    # end _isMacOSX()

    def _isWin32(self):
        return platform.system() == u"Windows" #$NON-NLS-1$
    # end _isWin32()

# end ZOSUtilFactory


# Getter for the OSUtil instance.
def getOSUtil():
    global _OS_UTIL_INSTANCE
    if not _OS_UTIL_INSTANCE:
        _OS_UTIL_INSTANCE = ZOSUtilFactory().createOSUtil()
    return _OS_UTIL_INSTANCE
# end getOSUtil()
