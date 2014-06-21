from zoundry.appframework.global_services import getApplicationModel
import wx

# ------------------------------------------------------------------------------
# A mixin that can be used to make any dialog 'persistent'.  That means that
# the dialog's size will be saved in the user prefs.
# ------------------------------------------------------------------------------
class ZPersistentDialogMixin:

    def __init__(self, persistentId, defaultToBestSize = True, defaultToCentreOnParent = False):
        self.persistentId = persistentId
        self.defaultToBestSize = defaultToBestSize
        self.defaultToCentreOnParent = defaultToCentreOnParent
        self.wasMoved = False
        self.wasResized = False

        self._restoreLayout()

        self.Bind(wx.EVT_BUTTON, self.onPersistDialogMixinClose, self.FindWindowById(wx.ID_CANCEL))
        self.Bind(wx.EVT_CLOSE, self.onPersistDialogMixinClose, self)
        self.Bind(wx.EVT_SIZE, self.onPersistDialogMixinResize, self)
        self.Bind(wx.EVT_MOVE, self.onPersistDialogMixinMove, self)
    # end __init__()

    def onPersistDialogMixinResize(self, event):
        self.wasResized = True
        event.Skip()
    # end onPersistDialogMixinResize()

    def onPersistDialogMixinMove(self, event):
        self.wasMoved = True
        event.Skip()
    # end onPersistDialogMixinMove()

    def onPersistDialogMixinClose(self, event):
        self._saveLayout()
        event.Skip()
    # end onPersistDialogMixinClose()

    def _saveLayout(self):
        if not self.IsMaximized():
            (width, height) = self.GetSizeTuple()
            (x, y) = self.GetPositionTuple()
            userPrefs = getApplicationModel().getUserProfile().getPreferences()
            if self.wasResized:
                userPrefs.setUserPreference(self.persistentId + u".width", width) #$NON-NLS-1$
                userPrefs.setUserPreference(self.persistentId + u".height", height) #$NON-NLS-1$
            if self.wasMoved:
                userPrefs.setUserPreference(self.persistentId + u".x", x) #$NON-NLS-1$
                userPrefs.setUserPreference(self.persistentId + u".y", y) #$NON-NLS-1$
    # end _saveLayout()

    def _restoreLayout(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        width = userPrefs.getUserPreferenceInt(self.persistentId + u".width", -1) #$NON-NLS-1$
        height = userPrefs.getUserPreferenceInt(self.persistentId + u".height", -1) #$NON-NLS-1$
        posX = userPrefs.getUserPreferenceInt(self.persistentId + u".x", -1) #$NON-NLS-1$
        posY = userPrefs.getUserPreferenceInt(self.persistentId + u".y", -1) #$NON-NLS-1$

        # Bound the size
        if width < 100:
            width = -1
        if height < 100:
            width = -1

        # Bound the window position
        if posX < 0:
            posX = -1
        if posY < 0:
            posY = -1
        displaySize = wx.GetDisplaySize()
        if posX >= displaySize.GetWidth() - 50:
            posX = -1
        if posY >= displaySize.GetHeight() - 50:
            posY = -1

        if width != -1 and height != -1:
            self.SetSize(wx.Size(width, height))
        elif self.defaultToBestSize:
            self.SetSize(self.GetBestSize())
        if posX != -1 and posY != -1:
            self.SetPosition(wx.Point(posX, posY))
        elif self.defaultToCentreOnParent:
            self.CentreOnParent()
        else:
            # FIXME (EPW) this might be problematic for multi-screen setups
            self.CentreOnScreen()
    # end _restoreLayout()

# end ZPersistentDialogMixin


# ------------------------------------------------------------------------------
# Extends the persistent dialog mixin to add save/restore logic for preferences
# dialogs (saves the sash position and the current page id).
# ------------------------------------------------------------------------------
class ZPersistentPrefsDialogMixin(ZPersistentDialogMixin):

    def __init__(self, persistentId, defaultToBestSize = True, defaultToCentreOnParent = False):
        ZPersistentDialogMixin.__init__(self, persistentId, defaultToBestSize, defaultToCentreOnParent)
    # end __init__()

    def _saveLayout(self):
        ZPersistentDialogMixin._saveLayout(self)

        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        if self.currentPageId:
            userPrefs.setUserPreference(self.persistentId + u".page-id", self.currentPageId) #$NON-NLS-1$

        sashPos = self.splitterWindow.GetSashPosition()
        userPrefs.setUserPreference(self.persistentId + u".sash-pos", sashPos) #$NON-NLS-1$
    # end _saveLayout()

    def _restoreLayout(self):
        ZPersistentDialogMixin._restoreLayout(self)

        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        sashPos = userPrefs.getUserPreferenceInt(self.persistentId + u".sash-pos", -1) #$NON-NLS-1$
        if sashPos != -1:
            self.splitterWindow.SetSashPosition(sashPos)
    # end _restoreLayout()

# end ZPersistentPrefsDialogMixin
