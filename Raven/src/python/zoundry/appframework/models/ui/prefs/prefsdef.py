from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
import string

# ---------------------------------------------------------------------------------------
# An extension point def that wraps the preference page info from a plugin.
# ---------------------------------------------------------------------------------------
class ZPreferencePageDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def getParent(self):
        parent = self._getExtensionText(u"plg:prefpage/plg:parent") #$NON-NLS-1$
        if not parent:
            return None
        return parent
    # end getParent()

    def getName(self):
        name = self._getExtensionText(u"plg:prefpage/plg:name") #$NON-NLS-1$
        if not name:
            raise ZAppFrameworkException(u"No name was supplied for extension with id '%s'." % self.getId()) #$NON-NLS-1$
        return name
    # end getName()

    def getDescription(self):
        desc = self._getExtensionText(u"plg:prefpage/plg:description") #$NON-NLS-1$
        if not desc:
            raise ZAppFrameworkException(u"No description was supplied for extension with id '%s'." % self.getId()) #$NON-NLS-1$
        return desc
    # end getName()

    def getHeaderImage(self):
        headerImage = self._getExtensionText(u"plg:prefpage/plg:header-image") #$NON-NLS-1$
        if not headerImage:
            return u"" #$NON-NLS-1$
        return headerImage
    # end getHeaderImage()

    def getPriority(self):
        priority = self._getExtensionText(u"plg:prefpage/plg:priority") #$NON-NLS-1$
        if not priority:
            return 50
        return string.atoi(priority)
    # end getPriority()

    def getIcon(self):
        icon = self._getExtensionText(u"plg:prefpage/plg:icon") #$NON-NLS-1$
        if not icon:
            return None
        return icon
    # end getIcon()

    def getIconKey(self):
        return u"%s:%s" % (self.getId(), self.getIcon()) #$NON-NLS-1$
    # end getIconKey()

    def loadIcon(self):
        return self.getPlugin().getResourceRegistry().getBitmap(self.getIcon())
    # end loadIcon()
    
    def resolveHeaderImage(self):
        return self.getPlugin().getResourceRegistry().getImagePath(self.getHeaderImage())
    # end resolveHeaderImage()

# end ZPreferencePageDef
