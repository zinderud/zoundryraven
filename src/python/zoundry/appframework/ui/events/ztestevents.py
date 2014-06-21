import wx

# Events for validating controls - event for VALID and event for INVALID.
ZTESTCOMPLETEDEVENT = wx.NewEventType()
ZTESTFAILEDEVENT = wx.NewEventType()

# Events for validating controls - event for VALID and event for INVALID.
ZEVT_ZTEST_COMPLETED = wx.PyEventBinder(ZTESTCOMPLETEDEVENT, 1)
ZEVT_ZTEST_FAILED = wx.PyEventBinder(ZTESTFAILEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZTestCompletedEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = ZTESTCOMPLETEDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZTestCompletedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZTestFailedEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = ZTESTFAILEDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZTestFailedEvent
