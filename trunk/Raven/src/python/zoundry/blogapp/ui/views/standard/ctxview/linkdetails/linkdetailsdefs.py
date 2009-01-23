from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef

# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to the
# specific data of interest for this type of extension point (link details panel).
# ----------------------------------------------------------------------------------
class ZLinkDetailsPanelDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def getName(self):
        return self._getExtensionText(u"plg:link-details-panel-info/plg:name") #$NON-NLS-1$
    # end getName()

# end ZLinkDetailsPanelDef
