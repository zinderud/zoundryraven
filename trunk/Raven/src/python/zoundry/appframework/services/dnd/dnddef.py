from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef

# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to
# the specific data of interest for this type of extension point (Accelerator).
# ----------------------------------------------------------------------------------
class ZDnDHandlerDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def createHandler(self):
        handlerClass = self.getClass()
        return handlerClass()
    # end createHandler()

# end ZDnDHandlerDef

