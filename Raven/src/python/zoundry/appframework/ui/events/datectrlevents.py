import wx

DATECHANGEEVENT = wx.NewEventType()
ZEVT_DATE_CHANGE = wx.PyEventBinder(DATECHANGEEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZDateChangeEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = DATECHANGEEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZDateChangeEvent
