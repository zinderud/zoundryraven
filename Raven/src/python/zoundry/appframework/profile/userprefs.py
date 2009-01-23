from zoundry.appframework.models.profile.userprefsmodel import ZUserPreferencesModel
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.base.util.collections import ZListenerSet
import string

# ------------------------------------------------------------------------------
# Listener interface for listening to user prefs changes.
# ------------------------------------------------------------------------------
class IZUserPreferencesListener:

    def onUserPreferenceChange(self, key, newValue):
        u"""
        This method is called whenever a user preference is changed.
        
        @param key:
        @param newValue:
        """ #$NON-NLS-1$
    # end onUserPreferenceChange()

# end IZUserPreferencesListener


# ------------------------------------------------------------------------------
# Interface for the user preferences objects.
# ------------------------------------------------------------------------------
class IZUserPreferences:

    def addListener(self, listener):
        u"""
        Adds a listener to the user prefs.  The listener will get called
        back whenever the user preferences change.
        
        @param listener: IZUserPreferencesListener
        """ #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"""
        Removes a listener from the user prefs.
        
        @param listener:
        """ #$NON-NLS-1$
    # end removeListener()

    def getUserPreference(self, key, dflt = None):
        u"Gets the given user preference.  Returns the given default value if the preference does not exist." #$NON-NLS-1$
    # end getUserPreference()

    def getUserPreferenceBool(self, key, dflt = None):
        u"Gets the given user preference as a boolean.  Returns the given default value if the preference does not exist." #$NON-NLS-1$
    # end getUserPreferenceBool()

    def getUserPreferenceInt(self, key, dflt = None):
        u"Gets the given user preference as an integer.  Returns the given default value if the preference does not exist." #$NON-NLS-1$
    # end getUserPreferenceInt

    def setUserPreference(self, key, value):
        u"Sets the given user preference to the given value." #$NON-NLS-1$
    # end setUserPreference()

    def removeUserPreference(self, key):
        u"""removeUserPreference(string) -> None
        Removes the given user preference.""" #$NON-NLS-1$
    # end removeUserPreference()

# end IZUserPreferences


# ------------------------------------------------------------------------------
# A base class for user preferences implementations.  This class calls an abstract method
# in order to get/set the preference.  It provides implementations of the Bool and Int
# methods.
# ------------------------------------------------------------------------------
class ZUserPreferencesBase(IZUserPreferences):

    def __init__(self):
        self.listeners = ZListenerSet()
    # end __init__()

    def addListener(self, listener):
        self.listeners.addListener(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.removeListener(listener)
    # end removeListener()

    def getUserPreference(self, key, dflt = None):
        rval = self._getUserPreference(key)
        if rval is None:
            rval = dflt
        return rval
    # end getUserPreference()

    def getUserPreferenceBool(self, key, dflt = None):
        value = self.getUserPreference(key, None)
        if value is None:
            return dflt
        return value == u"True" or value == u"true" #$NON-NLS-2$ #$NON-NLS-1$
    # end getUserPreferenceBool()

    def getUserPreferenceInt(self, key, dflt = None):
        value = self.getUserPreference(key, None)
        if value is None:
            return dflt
        try:
            return string.atoi(value)
        except:
            return dflt
    # end getUserPreferenceInt

    def setUserPreference(self, key, value):
        self.listeners.doCallback(u"onUserPreferenceChange", [key, value]) #$NON-NLS-1$
        if value is not None:
            value = unicode(value)
        self._setUserPreference(key, value)
    # end setUserPreference()

    def removeUserPreference(self, key):
        self._removeUserPreference(key)
    # end removeUserPreference()

    def _getUserPreference(self, key):
        u"Internal method to get the value of the user preference.  If it does not exist, this should return None." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_getUserPreference") #$NON-NLS-1$
    # end _getUserPreference()

    def _setUserPreference(self, key, value):
        u"Internal method to set the value of the user preference." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_setUserPreference") #$NON-NLS-1$
    # end _setUserPreference()

    def _removeUserPreference(self, key):
        u"Internal method to remove the value of the user preference." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_removeUserPreference") #$NON-NLS-1$
    # end _removeUserPreference()

# end ZUserPreferences


# ------------------------------------------------------------------------------
# This class provides a way for user preferences to be read and stored.  This 
# is really just a facade in front of the system/user properties.
# ------------------------------------------------------------------------------
class ZUserPreferences(ZUserPreferencesBase):

    def __init__(self, userProperties):
        self.model = ZUserPreferencesModel(userProperties)
        
        ZUserPreferencesBase.__init__(self)
    # end __init__()

    def _getUserPreference(self, key):
        return self.model.getUserPreference(key)
    # ene _getUserPreference()

    def _setUserPreference(self, key, value):
        self.model.setUserPreference(key, value)
    # ene _setUserPreference()

    def _removeUserPreference(self, key):
        self.model.removeUserPreference(key)
    # end _removeUserPreference()

# end ZUserPreferences
