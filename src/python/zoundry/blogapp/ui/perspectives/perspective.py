from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.blogapp.messages import _extstr

# ----------------------------------------------------------------------------------
# The interface that all perspectives must implement.
# ----------------------------------------------------------------------------------
class IZPerspective:

    def createUIPanel(self, parent):
        u"This method is called by the main app window when a perspective's UI should be created." #$NON-NLS-1$
    # end createUI()

    def destroy(self):
        u"This method is called when the application switches to a different perspective.  The perspective that is being left should, at this point, destroy its UI." #$NON-NLS-1$
    # end destroy()

# end IZPerspective


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to 
# the specific data of interest for this type of extension point (Perspective).
# ----------------------------------------------------------------------------------
class ZPerspectiveDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def getName(self):
        name = self._getExtensionText(u"plg:perspective-info/plg:name") #$NON-NLS-1$
        if not name:
            return _extstr(u"perspective.Unknown") #$NON-NLS-1$
        return name
    # end getName()

    def getDescription(self):
        desc = self._getExtensionText(u"plg:perspective-info/plg:description") #$NON-NLS-1$
        if not desc:
            return u"" #$NON-NLS-1$
        return desc
    # end getName()

# end ZPerspectiveDef
