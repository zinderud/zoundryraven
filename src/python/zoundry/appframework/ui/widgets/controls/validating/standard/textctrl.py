from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZValidatingCtrl
import wx


# -------------------------------------------------------------------------------------
# A validating version of a wx TextCtrl.  This class is more or less identical in usage
# to the TextCtrl, except that it requires an IZValidator and throws additional events
# for when the value transitions from Valid->Invalid or vice versa.
# -------------------------------------------------------------------------------------
class ZValidatingTextCtrl(ZValidatingCtrl):

    def __init__(self, validator, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0, name = u"ZValidatingTextCtrl"): #$NON-NLS-1$ #$NON-NLS-2$
        self.initialValue = value
        self.initialSize = size
        self.widgetName = name
        self.widgetId = id
        self.style = style

        ZValidatingCtrl.__init__(self, validator, parent)
    # end __init__()

    def _createWidget(self):
        return wx.TextCtrl(self, self.widgetId, self.initialValue, size = self.initialSize, style = self.style, name = self.widgetName)
    # end _createWidget()

    def _bindWidgetEvent(self):
        self.Bind(wx.EVT_TEXT, self.onText, self.widget)
    # end _bindWidgetEvent()

    def _getWidgetValue(self):
        return self.widget.GetValue()
    # end _getWidgetValue()

    def onText(self, event): #@UnusedVariable
        self._validateWidget()

        # Propagate the EVT_TEXT event
        event = event.Clone()
        event.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)

        event.Skip()
    # end onText()

    # -----------------------------------------------------------------------------
    # Redefine some standard WX methods to pass them thru to the underlying widget.
    # -----------------------------------------------------------------------------

    def GetValue(self):
        return self.widget.GetValue()
    # end GetValue()

    def SetValue(self, value):
        self.widget.SetValue(value)
    # end SetValue()

    def ChangeValue(self, value):
        self.widget.ChangeValue(value)
    # end ChangeValue()

    def SetToolTipString(self, tooltip):
        self.widget.SetToolTipString(tooltip)
    # end SetToolTipString()

    def SetFocus(self):
        self.widget.SetFocus()
    # end SetFocus

    def SetInsertionPointEnd(self):
        self.widget.SetInsertionPointEnd()
    # end SetInsertionPointEnd

    def SetInsertionPoint(self, pos):
        self.widget.SetInsertionPoint(pos)
    # end SetInsertionPointEnd

    def SetSelection(self, start, end):
        self.widget.SetSelection(start, end)
    # end SetSelection

    def SetSizeHints(self, minW, minH, maxW=-1, maxH=-1, incW=-1, incH=-1):
        self.widget.SetSizeHints(minW, minH, maxW, maxH, incW, incH)
    # end SetSizeHints()

# end ZValidatingTextCtrl


# -------------------------------------------------------------------------------------
# A validating version of a password cntrol.
# -------------------------------------------------------------------------------------
class ZValidatingPasswordCtrl(ZValidatingTextCtrl):

    def __init__(self, validator, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0, name = u"ZValidatingPasswordCtrl"): #$NON-NLS-1$ #$NON-NLS-2$
        ZValidatingTextCtrl.__init__(self, validator, parent, id, value, size, style | wx.TE_PASSWORD, name)
    # end __init__()

# end ZValidatingTextCtrl
