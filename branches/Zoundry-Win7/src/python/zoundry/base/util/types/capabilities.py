
# ---------------------------------------------------------------------------------------
# Common interface for all 'capabilities' classes.
# ---------------------------------------------------------------------------------------
class IZCapabilities:

    def hasCapability(self, capabilityKey):
        u"Returns True if the given capability exists." #$NON-NLS-1$
    # end hasCapability()
    
    def getCapabilityKeys(self):
        u"Returns a list of all the capability keys." #$NON-NLS-1$
    # end getCapabilityKeys()

    def clone(self):
        u"Called to make a copy of the capabilities." #$NON-NLS-1$
    # end clone()
    
    def override(self, capabilites, restrictOnly = True):
        u"Called to override the capabilities with another set of capabilities.  The flag indicates whether capabilities can only be restricted." #$NON-NLS-1$
    # end override()

# end IZCapabilities


# ---------------------------------------------------------------------------------------
# A simple base class for capabilities.
# ---------------------------------------------------------------------------------------
class ZCapabilities(IZCapabilities):

    def __init__(self, capabilityMap = {}):
        self.capabilityMap = capabilityMap
    # end __init__()

    def hasCapability(self, capabilityKey):
        if capabilityKey in self.capabilityMap:
            return self.capabilityMap[capabilityKey]
        return False
    # end hasCapability()

    def getCapabilityKeys(self):
        return self.capabilityMap.keys()
    # end getCapabilityKeys()

    def _addCapability(self, capabilityKey, enabled = True):
        self.capabilityMap[capabilityKey] = enabled
    # end _addCapability()

    def _removeCapability(self, capabilityKey):
        if capabilityKey in self.capabilityMap:
            del self.capabilityMap[capabilityKey]
    # end _removeCapability()

    def clone(self):
        capabilities = ZCapabilities( self.capabilityMap.copy() )
        return capabilities
    # end clone()
    
    def override(self, capabilites, restrictOnly = True):
        for key in capabilites.getCapabilityKeys():
            value = capabilites.hasCapability(key)
            # Add the capability (true or false) only if the value is False OR if the 
            # restrict only flag is not set.
            if not value or not restrictOnly:
                self._addCapability(key, value)
    # end override()

# end ZCapabilities
