from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.util.types.parameters import ZParameters


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to
# the specific data of interest for this type of extension point (Accelerator).
# ----------------------------------------------------------------------------------
class ZAcceleratorDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.parameters = None
    # end __init__()

    def createAction(self):
        actionClass = self.getClass()
        return actionClass()
    # end createAction()

    def getGroup(self):
        return self._getExtensionText(u"plg:accelerator/plg:group") #$NON-NLS-1$
    # end getGroup()

    def getKeyCode(self):
        return self._getExtensionText(u"plg:accelerator/plg:keyCode") #$NON-NLS-1$
    # end getKeyCode()

    def getFlags(self):
        flags = []
        flagNodes = self._getExtensionNodes(u"plg:accelerator/plg:flags/plg:flag") #$NON-NLS-1$
        for flagNode in flagNodes:
            flags.append(flagNode.getText())
        return flags
    # end getFlags()

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZParameters.""" #$NON-NLS-1$
        if self.parameters is None:
            nodes = self._getExtensionNodes(u"plg:accelerator/plg:parameters/plg:parameter") #$NON-NLS-1$
            paramMap = {}
            for node in nodes:
                name = node.getAttribute(u"name") #$NON-NLS-1$
                if name:
                    paramMap[name] = node.getText()
            self.parameters = ZParameters(paramMap)
        return self.parameters
    # end getParameters()

# end ZAcceleratorDef
