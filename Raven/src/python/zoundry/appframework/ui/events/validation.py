import wx

# Events for validating controls - event for VALID and event for INVALID.
WIDGETVALIDEVENT = wx.NewEventType()
WIDGETINVALIDEVENT = wx.NewEventType()

# Events for validating controls - event for VALID and event for INVALID.
ZEVT_VALID = wx.PyEventBinder(WIDGETVALIDEVENT, 1)
ZEVT_INVALID = wx.PyEventBinder(WIDGETINVALIDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZWidgetValidEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = WIDGETVALIDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

#end ZWidgetValidEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZWidgetInvalidEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = WIDGETINVALIDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

#end ZWidgetInvalidEvent
