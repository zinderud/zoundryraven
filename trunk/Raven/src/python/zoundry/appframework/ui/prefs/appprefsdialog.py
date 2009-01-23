from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.models.ui.prefs.prefsmodel import ZPreferencesModel
from zoundry.appframework.models.ui.widgets.treemodel import ZTreeNodeBasedContentProvider
from zoundry.appframework.ui.dialogs.mixins import ZPersistentPrefsDialogMixin
from zoundry.appframework.ui.dialogs.prefpage import IZUserPreferencePageSession
from zoundry.appframework.ui.dialogs.prefpage import ZUserPreferencePage
from zoundry.appframework.ui.dialogs.prefs import ZPreferencesDialog


# ------------------------------------------------------------------------------
# This wrapper is used by the user preferences/settings dialog.  It will wrap a
# ZUserPreferences object and prevent any actual changes (sets) on that object until
# the apply method is called.  It has the same interface as the ZUserPreferences, but
# keeps a map of changes that are going to be made to the user prefs.  Once the apply
# method is called, those changes are actually written.
# ------------------------------------------------------------------------------
class ZUserPreferencesSession(IZUserPreferencePageSession):

    def __init__(self, prefPage, prefs):
        self.prefPage = prefPage
        self.prefs = prefs
        self.changes = {}
    # end __init__()

    def getUserPreference(self, key, dflt = None):
        return self.prefs.getUserPreference(key, dflt)
    # end getUserPreference()

    def getUserPreferenceBool(self, key, dflt = None):
        return self.prefs.getUserPreferenceBool(key, dflt)
    # end getUserPreferenceBool()

    def getUserPreferenceInt(self, key, dflt = None):
        return self.prefs.getUserPreferenceInt(key, dflt)
    # end getUserPreferenceInt

    def setUserPreference(self, key, value):
        newValue = unicode(value)
        if value is None:
            newValue = None
        self.changes[key] = newValue

        currentValue = self.getUserPreference(key, None)
        if newValue == currentValue or (not newValue and currentValue is None):
            del self.changes[key]

        # Now notify the settings prefPage that something changed.
        self.prefPage.onSessionChange()
    # end setUserPreference()

    def isDirty(self):
        return len(self.changes) > 0
    # end isDirty()

    def apply(self):
        for key in self.changes:
            value = self.changes[key]
            self.prefs.setUserPreference(key, value)
        del self.changes
        self.changes = {}
    # end apply()

    def rollback(self):
        del self.changes
        self.changes = {}
    # end rollback()

# end ZUserPreferencesSession


# ------------------------------------------------------------------------------
# Base class for application preferences pages.
# ------------------------------------------------------------------------------
class ZApplicationPreferencesPrefPage(ZUserPreferencePage):
    
    def __init__(self, parent):
        ZUserPreferencePage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZUserPreferencesSession(self, getApplicationModel().getUserProfile().getPreferences())
    # end _createSession()

    def onSessionChange(self):
        u"""onSessionChange() -> None
        Called by the session whenever a change to the session's
        data is made.  Default behavior is to notify the dialog
        that something changed in the pref page, allowing the 
        dialog to alter button states, etc...""" #$NON-NLS-1$
        self._firePrefPageChangeEvent()
    # end onSessionChange()
    
# end ZApplicationPreferencesPrefPage


# ------------------------------------------------------------------------------
# Implements the user preferences dialog.  The user preferences dialog uses the
# prefpage extension point in order to create the various preference pages.  
# Extends the base validating dialog in order to conveniently add widgets that
# support input validation.
# ------------------------------------------------------------------------------
class ZApplicationPreferencesDialog(ZPreferencesDialog, ZPersistentPrefsDialogMixin):

    def __init__(self, parent, jumpToPageId = None):
        self.model = ZPreferencesModel()
        
        ZPreferencesDialog.__init__(self, parent, jumpToPageId)
        ZPersistentPrefsDialogMixin.__init__(self, IZAppUserPrefsKeys.USERPREFS_DIALOG, False)
    # end __init__()

    def _getHeaderTitle(self):
        if self.currentSelection is None:
            return _extstr(u"prefsdialog.ZoundryRavenSettings") #$NON-NLS-1$
        else:
            return self.currentSelection.getName()
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        if self.currentSelection is None:
            return _extstr(u"prefsdialog.SettingsDialogMessage") #$NON-NLS-1$
        else:
            return self.currentSelection.getDescription()
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        if self.currentSelection is None:
            return u"images/userprefs/preferences.png" #$NON-NLS-1$
        else:
            return self.currentSelection.getHeaderImagePath()
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

    def _resolveNodeId(self, treeNode):
        return treeNode.getId()
    # end _resolveNodeId()

    def _getDefaultPageId(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        return userPrefs.getUserPreference(IZAppUserPrefsKeys.USERPREFS_DIALOG + u".page-id", None) #$NON-NLS-1$
    # end _getDefaultPageId()

    def _getDialogTitle(self):
        return _extstr(u"prefsdialog.SettingsDialogTitle") #$NON-NLS-1$
    # end _getDialogTitle()
    
    def _createTreeProvider(self):
        return ZTreeNodeBasedContentProvider(self.model.getRootNode(), self.model.getImageList())
    # end _createTreeProvider()
    
    def _createPrefPage(self, parent, currentSelection):
        pageClass = self._getPrefPageClass(currentSelection)
        return pageClass(parent)
    # end _createPrefPage()

    def _getPrefPageClass(self, selectedNode):
        return selectedNode.getPreferencePageClass()
    # end _getPrefPageClass()
    
# end ZApplicationPreferencesDialog
