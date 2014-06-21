
# --------------------------------------------------------------------------------------
# A model that wraps the user properties object and presents a simpler facade interface
# for getting and setting User Preferences.
# --------------------------------------------------------------------------------------
class ZUserPreferencesModel:

    def __init__(self, userProperties):
        self.userProperties = userProperties
    # end __init__()

    def getUserPreference(self, key):
        xpath = self._convertKeyToXPath(key)
        return self.userProperties.getPropertyString(xpath)
    # end getUserPreference()

    def setUserPreference(self, key, value):
        xpath = self._convertKeyToXPath(key)
        self.userProperties.setProperty(xpath, value)
    # end setUserPreference()
    
    def removeUserPreference(self, key):
        xpath = self._convertKeyToXPath(key)
        self.userProperties.removeProperty(xpath)
    # end removeUserPreference()

    def _convertKeyToXPath(self, key):
        return u"/user-properties/user-preferences/%s" % key.replace(u".", u"/") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
    # end _convertKeyToXPath()

# end ZUserPreferencesModel
