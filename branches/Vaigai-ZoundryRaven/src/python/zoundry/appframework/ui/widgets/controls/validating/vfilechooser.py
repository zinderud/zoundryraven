from zoundry.appframework.ui.widgets.controls.common.filechooser import ZFileChooserCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZValidatingCtrl
import wx

# -----------------------------------------------------------------------------------------
# A validating version of a ZFileChooser.  This class is more or less identical in usage
# to the ZFileChooser, except that it requires an IZValidator and throws additional events
# for when the value transitions from Valid->Invalid or vice versa.
# -----------------------------------------------------------------------------------------
class ZValidatingFileChooserCtrl(ZValidatingCtrl):

    def __init__(self, validator, parent, type, dialogTitle): #$NON-NLS-1$
        self.type = type
        self.dialogTitle = dialogTitle

        ZValidatingCtrl.__init__(self, validator, parent)
    # end __init__()

    def setDefaultDirectory(self, defaultDirectory):
        self.widget.setDefaultDirectory(defaultDirectory)
    # end setDefaultDirectory()

    def setDefaultFile(self, defaultFile):
        self.widget.setDefaultFile(defaultFile)
    # end setDefaultFile()

    def setWildcard(self, wildcard):
        self.widget.setWildcard(wildcard)
    # end setWildcard()

    def getPath(self):
        return self.widget.getPath()
    # end getPath()

    def setPath(self, path):
        self.widget.setPath(path)
    # end setPath()

    def _createWidget(self):
        return ZFileChooserCtrl(self, self.type, self.dialogTitle)
    # end _createWidget()

    def _bindWidgetEvent(self):
        self.Bind(wx.EVT_TEXT, self.onText, self.widget)
    # end _bindWidgetEvent()

    def _getWidgetValue(self):
        return self.widget.getPath()
    # end _getWidgetValue()

    def onText(self, event): #@UnusedVariable
        self._validateWidget()

        # Propagate the EVT_TEXT event
        event = event.Clone()
        event.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)

        event.Skip()
    # end onText()

    def SetToolTipString(self, tooltip):
        self.widget.SetToolTipString(tooltip)
    # end SetToolTipString()

# end ZValidatingTextCtrl
