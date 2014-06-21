from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.widgets.acceleratordefs import ZAcceleratorDef
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
import wx

ENUM_TO_WXACCEL_MAP = {
       u"alt" : wx.ACCEL_ALT, #$NON-NLS-1$
       u"cmd" : wx.ACCEL_CMD, #$NON-NLS-1$
       u"ctrl" : wx.ACCEL_CTRL, #$NON-NLS-1$
       u"shift" : wx.ACCEL_SHIFT, #$NON-NLS-1$
}

# ------------------------------------------------------------------------------
# Extends the wx accelerator entry to include the action to run when the
# accelerator fires.
# ------------------------------------------------------------------------------
class ZAcceleratorEntry(wx.AcceleratorEntry):

    def __init__(self, flags, keyCode, action):
        self.flags = flags
        self.keyCode = keyCode
        self.acceleratorId = wx.NewId()
        self.action = action

        wx.AcceleratorEntry.__init__(self, flags, keyCode, self.acceleratorId)
    # end __init__()

    def getAction(self):
        return self.action
    # end getAction()

    def getId(self):
        return self.acceleratorId
    # end getId()

# end ZAcceleratorEntry


# ------------------------------------------------------------------------------
# A version of an accelerator entry that gets constructed from extension info.
# ------------------------------------------------------------------------------
class ZPluginAcceleratorEntry(ZAcceleratorEntry):

    def __init__(self, acceleratorDef):
        flags = map(self._deserializeFlag, acceleratorDef.getFlags())
        flags = self._combineFlags(flags)
        keyCode = ord(acceleratorDef.getKeyCode())
        action = acceleratorDef.createAction()

        ZAcceleratorEntry.__init__(self, flags, keyCode, action)
    # end __init__()

    def _deserializeFlag(self, flag):
        return ENUM_TO_WXACCEL_MAP[flag]
    # end _deserializeFlag()

    def _combineFlags(self, flags):
        if not flags:
            return wx.ACCEL_NORMAL
        rval = 0
        for flag in flags:
            rval += flag
        return rval
    # end _combineFlags()

# end ZPluginAcceleratorEntry


# ------------------------------------------------------------------------------
# An accelerator table that knows how to load its data from the plugins.  In
# addition, this class exposes an 'abstract' method that can be taken over by
# subclasses that want to load hard-coded entries.
# ------------------------------------------------------------------------------
class ZAcceleratorTable(wx.AcceleratorTable):

    def __init__(self, pluginId):
        self.pluginId = pluginId
        self.wxidToActionMap = {}

        self.acceleratorEntries = self._loadAcceleratorEntries()
        for entry in self.acceleratorEntries:
            self.wxidToActionMap[entry.getId()] = entry.getAction()

        wx.AcceleratorTable.__init__(self, self.acceleratorEntries)
    # end __init__()

    def getAcceleratorEntries(self):
        return self.acceleratorEntries
    # end getAcceleratorEntries()

    def getAction(self, acceleratorId):
        if acceleratorId in self.wxidToActionMap:
            return self.wxidToActionMap[acceleratorId]
        else:
            return None
    # end getAction()

    def bindTo(self, window):
        for entry in self.acceleratorEntries:
            accelId = entry.getId()
            wx.EVT_MENU(window, accelId, self.onAccelerator)
    # end bindTo()

    def onAccelerator(self, event):
        action = self.getAction(event.GetId())
        action.runAction(self._createActionContext())
        event.Skip()
    # end onAccelerator()

    # Creates the action context.  This can be overridden by
    # subclasses - gets called each time an accelerator is 'fired'.
    def _createActionContext(self):
        return ZMenuActionContext(getApplicationModel().getTopWindow())
    # end _createActionContext()

    def _loadAcceleratorEntries(self):
        return self._loadPluginEntries() + self._loadAdditionalEntries()
    # end _loadAcceleratorEntries()

    def _loadPluginEntries(self):
        entries = []
        if self.pluginId:
            registry = getApplicationModel().getPluginRegistry()
            acceleratorExtensions = registry.getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_CORE_ACCELERATOR)
            accelExtensionDefs = map(ZAcceleratorDef, acceleratorExtensions)
            for accelDef in accelExtensionDefs:
                if self.pluginId == accelDef.getGroup():
                    entries.append(ZPluginAcceleratorEntry(accelDef))
        return entries
    # end _loadPluginEntries()

    # Loads any additional 'hard coded' entries - should be taken over
    # by subclasses.
    def _loadAdditionalEntries(self):
        return []
    # end _loadAdditionalEntries()

# end ZAcceleratorTable
