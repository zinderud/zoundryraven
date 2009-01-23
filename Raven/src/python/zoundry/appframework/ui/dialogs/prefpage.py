from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.appframework.ui.widgets.controls.validating.validatingpanel import ZValidatingPanel

# ------------------------------------------------------------------------------
# An interface that defines a user preference page session.  The session object
# is used by the page to set all of its data.  A session is created with some
# initial state and typically provides specific getters/setters for its data.
# This interface exposes generic methods to determine if the session is dirty
# or clean, and to commit or rollback any changes that have been made by the
# user.
# ------------------------------------------------------------------------------
class IZUserPreferencePageSession:

    def isDirty(self):
        u"""isDirty() -> boolean
        Returns True if the session is dirty.""" #$NON-NLS-1$
    # end isDirty()

    def apply(self):
        u"""apply() -> None
        Commits any changes in the session (i.e. save
        current state).""" #$NON-NLS-1$
    # end apply()

    def rollback(self):
        u"""rollback() -> None
        Discards any changes made to the session, reverting
        its internal state back to its creation state.""" #$NON-NLS-1$
    # end rollback()

# end IZUserPreferencePageSession


# ------------------------------------------------------------------------------
# Interface/base class needed to implement a single user preference page.
# ------------------------------------------------------------------------------
class ZUserPreferencePage(ZValidatingPanel):

    def __init__(self, parent):
        ZValidatingPanel.__init__(self, parent)

        self.session = self._createSession()
        self.prefsDialog = None
    # end __init__()

    def destroy(self):
        u"Called when the page is destroyed (when the dialog is closed)." #$NON-NLS-1$
    # end destroy()

    def setPrefsDialog(self, dialog):
        self.prefsDialog = dialog
    # end setPrefsDialog()

    def getPrefsDialog(self):
        return self.prefsDialog
    # end getPrefsDialog()

    def createWidgets(self):
        u"Called to create the page's widgets." #$NON-NLS-1$
    # end createWidgets()

    def bindWidgetEvents(self):
        u"Called to bind the page's widget events." #$NON-NLS-1$
    # end bindWidgetEvents()

    def populateWidgets(self):
        u"Called to populate the widgets with data." #$NON-NLS-1$
    # end populateWidgets()

    def layoutWidgets(self):
        u"Called to layout the page's widgets." #$NON-NLS-1$
    # end layoutWidgets()

    def _createSession(self):
        u"Creates the IZUserPreferencePageSession to use for this page." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_createSession") #$NON-NLS-1$
    # end _createSession()
    
    def _getSession(self):
        return self.session
    # end _getSession()

    def _firePrefPageChangeEvent(self):
        u"""_firePrefPageChangeEvent() -> None
        Internal convenience method - called when something on
        the pref page changes.""" #$NON-NLS-1$
        if self.prefsDialog:
            fireUIExecEvent(ZMethodRunnable(self.prefsDialog.onPrefPageChange), self.prefsDialog)
    # end _firePrefPageChangeEvent()

    def isDirty(self):
        return self.session.isDirty()
    # end isDirty()

    def isValid(self):
        return ZValidatingPanel.isValid(self)
    # end isValid()

    def apply(self):
        self.session.apply()
        return True
    # end apply()

    def rollback(self):
        self.session.rollback()
        self.populateWidgets()
    # end rollback()

# end ZUserPreferencePage
