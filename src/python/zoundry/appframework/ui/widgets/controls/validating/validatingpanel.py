from zoundry.appframework.ui.events.validation import ZEVT_INVALID
from zoundry.appframework.ui.events.validation import ZEVT_VALID
from zoundry.appframework.ui.events.validation import ZWidgetInvalidEvent
from zoundry.appframework.ui.events.validation import ZWidgetValidEvent
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import IZValidatingCtrl
import wx

# --------------------------------------------------------------------------------------
# A simple extension of a WX Panel that propagates the validation events of any of its
# child widgets.
#
# FIXME (EPW) share code with ZValidatingHeaderDialog
# --------------------------------------------------------------------------------------
class ZValidatingPanel(wx.Panel, IZValidatingCtrl):

    def __init__(self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL):
        self.validatingWidgets = {}
        self.valid = True

        wx.Panel.__init__(self, parent, id = id, style = style)
    # end __init__()

    def validate(self):
        pass
    # end validate()

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
        oldValid = self.valid
        newValid = True

        # All validating widgets need to be valid.
        for key in self.validatingWidgets:
            newValid = newValid and self.validatingWidgets[key]
        
        self.valid = newValid
        
        # If the state transitioned, do the appropriate thing.
        if oldValid != newValid:
            if self.valid:
                self._fireValidEvent()
                self._doValid()
            else:
                self._fireInvalidEvent()
                self._doInvalid()
    # end _validate()

    def _fireValidEvent(self):
        event = ZWidgetValidEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireValidEvent()

    def _fireInvalidEvent(self):
        event = ZWidgetInvalidEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireInvalidEvent

    def _doValid(self):
        u"Called when the panel transitions to a valid state.  Subclasses can override." #$NON-NLS-1$
    # end _doValid()

    def _doInvalid(self):
        u"Called when the panel transitions to an invalid state.  Subclasses can override." #$NON-NLS-1$
    # end _doInvalid()

    def DestroyChildren(self):
        self.validatingWidgets = {}
        wx.Panel.DestroyChildren(self)
    # end DestroyChildren()

    def isValid(self):
        return self.valid
    # end isValid()

# end ZValidatingPanel
