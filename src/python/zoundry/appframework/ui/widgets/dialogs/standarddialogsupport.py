from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
import wx

# ------------------------------------------------------------------------------
# Action run when the user types 'Y' in the standard dialog when the Yes button
# is available.
# ------------------------------------------------------------------------------
class ZYesButtonAction(IZAction):

    def runAction(self, actionContext):
        dialog = actionContext.getParentWindow()
        dialog.onYes(wx.CommandEvent(0, 0))
    # end runAction()

# end ZYesButtonAction


# ------------------------------------------------------------------------------
# Action run when the user types 'N' in the standard dialog when the Yes button
# is available.
# ------------------------------------------------------------------------------
class ZNoButtonAction(IZAction):

    def runAction(self, actionContext):
        dialog = actionContext.getParentWindow()
        dialog.onNo(wx.CommandEvent(0, 0))
    # end runAction()

# end ZNoButtonAction


# ------------------------------------------------------------------------------
# Accelerator table installed on the standard dialog.
# ------------------------------------------------------------------------------
class ZStandardDialogAcceleratorTable(ZAcceleratorTable):

    def __init__(self, dialog, buttonMask):
        self.dialog = dialog
        self.buttonMask = buttonMask

        ZAcceleratorTable.__init__(self, None)
    # end __init__()

    def _createActionContext(self):
        return ZMenuActionContext(self.dialog)
    # end _createActionContext()

    def _loadAdditionalEntries(self):
        entries = []
        # If I have a No button without a Cancel button, then map ESC to "No"
        if ((self.buttonMask & ZBaseDialog.NO_BUTTON) > 0) and ((self.buttonMask & ZBaseDialog.CANCEL_BUTTON) == 0):
            entries.append(ZAcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, ZNoButtonAction())) #$NON-NLS-1$
        return entries
    # end _loadAdditionalEntries()

# end ZStandardDialogAcceleratorTable

