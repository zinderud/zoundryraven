
# -----------------------------------------------------------
# A class that implements a set of in memory properties.
# -----------------------------------------------------------
class ZProperties:
    u"""Basic in memory properties class.""" #$NON-NLS-1$

    def __init__(self):
        self.properties = {}
    # end __init__()

    def _getPropertyKey(self, name):
        if name:
            name = name.lower().strip()
        if name:
            return name
        else:
            return None
    # end _getPropertyKey()

    def getProperties(self):
        u"""Returns the properies dictionary object.""" #$NON-NLS-1$
        return self.properties
    # end getProperties()

    def getProperty(self, name, defaultValue = None):
        u"""Returns the named property.""" #$NON-NLS-1$
        key = self._getPropertyKey(name)
        if key and self.properties.has_key(key):
            return self.properties[key]
        else:
            return defaultValue
    # end getProperty()

    def setProperty(self, name, value):
        u"""Sets the property.""" #$NON-NLS-1$
        key = self._getPropertyKey(name)
        if key and value:
            self.properties[key] = unicode(value)
    # end ()

    def removeProperty(self, name):
        u"""Removes the property.""" #$NON-NLS-1$
        key = self._getPropertyKey(name)
        if key and self.properties.has_key[key]:
            del self.properties[key]
    # end removeProperty()
         
    def getIntProperty(self, name, defaultValue = 0):
        u"""Convenience method that returns the property value as integer.""" #$NON-NLS-1$
        s = self.getProperty(name)
        if not s:
            return defaultValue
        try:
            return int(s)
        except:
            return defaultValue
    # end getIntProperty()

    def getBoolProperty(self, name, defaultValue = False):
        u"""Convenience method that returns the property value as boolean.""" #$NON-NLS-1$
        s = self.getProperty(name)
        if not s:
            return defaultValue
        try:
            s = s.strip().lower()
            if s == u"true" or s == u"yes": #$NON-NLS-1$ #$NON-NLS-2$
                return True
            else:
                return False
        except:
            return defaultValue
    # end getBoolProperty()

# end ZProperties
