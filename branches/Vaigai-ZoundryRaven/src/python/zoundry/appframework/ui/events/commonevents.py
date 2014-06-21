import wx

# Event for refreshing a UI (fired from a background thread to tell the main UI thread to refresh).
REFRESHEVENT = wx.NewEventType()
# Events for validating controls - event for REFRESH
ZEVT_REFRESH = wx.PyEventBinder(REFRESHEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZRefreshEvent(wx.PyCommandEvent):

    def __init__(self, windowID, data = None):
        self.eventType = REFRESHEVENT
        self.data = data
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getData(self):
        return self.data
    # end getData()

    def Clone(self):
        return self.__class__(self.GetId(), self.getData())
    # end Clone()

#end ZRefreshEvent


# Event for running some arbitrary code in the UI thread.
UIEXECEVENT = wx.NewEventType()
ZEVT_UIEXEC = wx.PyEventBinder(UIEXECEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZUIExecEvent(wx.PyCommandEvent):

    def __init__(self, windowID, runnable):
        self.runnable = runnable
        self.eventType = UIEXECEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId(), self.getRunnable())
    # end Clone()

    def getRunnable(self):
        return self.runnable
    # end getRunnable()

# end ZUIExecEvent

# General purpose event to notify that content has been modified
CONTENTMODIFIEDEVENT = wx.NewEventType()
ZEVT_CONTENT_MODIFIED = wx.PyEventBinder(CONTENTMODIFIEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZContentModifiedEvent(wx.PyCommandEvent):

    def __init__(self, windowID, data = None):
        self.eventType = CONTENTMODIFIEDEVENT
        self.data = data
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getData(self):
        return self.data
    # end getData()

    def Clone(self):
        return self.__class__(self.GetId(), self.getData())
    # end Clone()

#end ZContentModifiedEvent
