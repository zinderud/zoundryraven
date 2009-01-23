from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZValidatingCtrl
import wx #@UnusedImport
import wx.combo #@Reimport

# -------------------------------------------------------------------------------------
# A validating version of a wx ComboBox.  This class is more or less identical in usage
# to the ComboBox, except that it requires an IZValidator and throws additional events
# for when the value transitions from Valid->Invalid or vice versa.
# -------------------------------------------------------------------------------------
class ZValidatingComboBox(ZValidatingCtrl):

    def __init__(self, validator, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0): #$NON-NLS-1$
        self.initialValue = value
        self.initialSize = size
        self.widgetId = id
        self.style = style

        ZValidatingCtrl.__init__(self, validator, parent)
    # end __init__()

    def _createWidget(self):
        return wx.ComboBox(self, self.widgetId, self.initialValue, size = self.initialSize, style = self.style)
    # end _createWidget()

    def _bindWidgetEvent(self):
        self.Bind(wx.EVT_TEXT, self.onEvent, self.widget)
        self.Bind(wx.EVT_COMBOBOX, self.onEvent, self.widget)
    # end _bindWidgetEvent()

    def _getWidgetValue(self):
        return self.widget.GetValue()
    # end _getWidgetValue()

    def onEvent(self, event):
        self._validateWidget()
        self._propagateEvent(event)
        event.Skip()
    # end onEvent()

    # -----------------------------------------------------------------------------
    # Redefine some standard WX methods to pass them thru to the underlying widget.
    # -----------------------------------------------------------------------------

    def GetValue(self):
        return self.widget.GetValue()
    # end GetValue()

    def SetValue(self, value):
        self.widget.SetValue(value)
    # end SetValue()

    def SetToolTipString(self, tooltip):
        self.widget.SetToolTipString(tooltip)
    # end SetToolTipString()

    def Append(self, item, clientData = None):
        self.widget.Append(item, clientData)
    # end Append()

    def AppendItems(self, items):
        self.widget.AppendItems(items)
    # end AppendItems()

    def Clear(self):
        self.widget.Clear()
    # end Clear()

    def Select(self, index):
        self.widget.Select(index)
    # end Select()

    def Insert(self, item, position, clientData = None):
        self.widget.Insert(item, position, clientData)
    # end Insert()

    def IsEmpty(self):
        return self.widget.IsEmpty()
    # end IsEmpty()

    def GetCount(self):
        return self.widget.GetCount()
    # end GetCount()

    def Delete(self, index):
        self.widget.Delete(index)
    # end Delete()

    def GetClientData(self, index):
        return self.widget.GetClientData(index)
    # end GetClientData()

    def GetSelection(self):
        return self.widget.GetSelection()
    # end GetSelection()

    def GetString(self):
        return self.widget.GetString()
    # end GetString()

    def SetSelection(self, idx):
        return self.widget.SetSelection(idx)
    # end GetSelection()

# end ZValidatingComboBox

# -----------------------------------------------------------------------------
# Implementation of validating bitmap combo box.
# Use method Append(item, clientData, bitmap)
# -----------------------------------------------------------------------------
class ZValidatingBitmapComboBox(ZValidatingComboBox):

    def __init__(self, validator, parent, id = wx.ID_ANY, value = u"", size = wx.DefaultSize, style = 0): #$NON-NLS-1$
        ZValidatingComboBox.__init__(self, validator, parent, id, value, size, style)
    # end __init__()

    def _createWidget(self):
        return wx.combo.BitmapComboBox(self, self.widgetId, self.initialValue, size = self.initialSize, style = self.style)
    # end _createWidget()

    def Append(self, item, clientData = None, bitmap = None):
        if not bitmap:
            bitmap = wx.NullBitmap
        self.widget.Append(item, bitmap, clientData)

    # end Append()

    def AppendItems(self, items):
        self.widget.AppendItems(items)
    # end AppendItems()

    def Insert(self, item, position, clientData = None, bitmap = None):
        if not bitmap:
            bitmap = wx.NullBitmap
        self.widget.Insert(item, bitmap, position, clientData)
    # end Insert()

# end ZValidatingBitmapComboBox
