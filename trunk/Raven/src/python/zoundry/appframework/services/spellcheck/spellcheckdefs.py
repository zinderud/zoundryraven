from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef

# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to the
# specific data of interest for this type of extension point (SpellCheck Provider).
# ----------------------------------------------------------------------------------
class ZSpellCheckProviderDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

# end ZSpellCheckProviderDef


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to the
# specific data of interest for this type of extension point (SpellCheck dictionary 
# handler).
# ----------------------------------------------------------------------------------
class ZSpellCheckDictionaryHandlerDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

# end ZSpellCheckDictionaryHandlerDef
