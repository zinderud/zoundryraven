import wx

SASHPOSCHANGEDEVENT = wx.NewEventType()
ZEVT_SPLITTER_SASH_POS_CHANGED = wx.PyEventBinder(SASHPOSCHANGEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZSplitterEvent(wx.PyCommandEvent):

    def __init__(self, eventType, splitterWindow):
        self.eventType = eventType
        self.splitterWindow = splitterWindow
        wx.PyCommandEvent.__init__(self, self.eventType, splitterWindow.GetId())
    # end __init__()

    def GetSashPosition(self):
        return self.splitterWindow.GetSashPosition()
    # end GetSashPosition()

    def Clone(self):
        return self.__class__(self.eventType, self.splitterWindow)
    # end Clone()

# end ZSplitterEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZSplitterSashPosChangedEvent(ZSplitterEvent):

    def __init__(self, splitterWindow):
        ZSplitterEvent.__init__(self, SASHPOSCHANGEDEVENT, splitterWindow)
    # end __init__()
    
# end ZSplitterSashPosChangedEvent
