from zoundry.appframework.ui.events.validation import ZEVT_INVALID
from zoundry.appframework.ui.events.validation import ZEVT_VALID
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
import wx

# --------------------------------------------------------------------------------------
# An extension of the Zoundry HTML Header Dialog that provides a standard validation
# mechanism.
# --------------------------------------------------------------------------------------
class ZValidatingHeaderDialog(ZHeaderDialog):

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE, name = u"ZValidatingDialog"): #$NON-NLS-1$):
        self.validatingWidgets = {}
        self.isValid = True

        ZHeaderDialog.__init__(self, parent, id, title, pos, size, style, name)
    # end __init__()

    def _bindValidatingWidget(self, widget):
        self.Bind(ZEVT_VALID, self.onValid, widget)
        self.Bind(ZEVT_INVALID, self.onInvalid, widget)
        widget.validate()
    # end _bindValidatingWidget()
    
    def onValid(self, event):
        self.validatingWidgets[event.GetId()] = True
        self._validate()
        event.Skip()
    # end onValid()

    def onInvalid(self, event):
        self.validatingWidgets[event.GetId()] = False
        self._validate()
        event.Skip()
    # end onInvalid()

    def _validate(self):
        oldValid = self.isValid
        newValid = True

        # All validating widgets need to be valid.
        for key in self.validatingWidgets:
            newValid = newValid and self.validatingWidgets[key]
        
        self.isValid = newValid
        
        # If the state transitioned, do the appropriate thing.
        if oldValid != newValid:
            if self.isValid:
                self._doValid()
            else:
                self._doInvalid()
    # end _validate()

    def _doValid(self):
        self._enableOkButton(True)
    # end _doValid()

    def _doInvalid(self):
        self._enableOkButton(False)
    # end _doInvalid()

# end ZValidatingHeaderDialog
