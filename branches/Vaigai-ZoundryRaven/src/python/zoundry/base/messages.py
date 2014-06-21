from zoundry.base.constants import IZI18NConstants
from zoundry.base.util.i18n import ZBundleCollection
import os

# ------------------------------------------------------------------------------------------
# This class is the accessor to get at Zoundry Raven externalized strings.  It wraps a 
# collection of string bundles which it uses to provide the data.
# ------------------------------------------------------------------------------------------
class ZMessages:
    
    def __init__(self):
        self.bundle = None
    # end __init__()

    def _getBundlePath(self):
        # Dev default.  :)
        dirPath = os.path.join(os.path.dirname(__file__), u"../../../../bin/system/bundles") #$NON-NLS-1$
        if IZI18NConstants.BUNDLE_PATH_ENV_VAR in os.environ:
            dirPath = os.environ[IZI18NConstants.BUNDLE_PATH_ENV_VAR]

        return dirPath
    # end _getBundlePath()

    def _getBundleName(self):
        return u"zoundry.base.xml" #$NON-NLS-1$
    # end _getBundleName()

    def _getDefaultBundleFilename(self):
        return os.path.join(self._getBundlePath(), self._getBundleName())
    # end defaultBundleFilename()

    def _getBundle(self):
        if self.bundle is None:
            self.bundle = ZBundleCollection(self._getDefaultBundleFilename())
        return self.bundle
    # end _getBundle()

    def getString(self, key):
        return self._getBundle().getString(key)
    # end getString()

# end ZMessages

MESSAGES = ZMessages()

def _extstr(name):
    global MESSAGES
    val = MESSAGES.getString(name)
    if not val:
        val = u"!!%s!!" % name #$NON-NLS-1$
    return val
# end _extstr()
