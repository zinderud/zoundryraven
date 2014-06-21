import wx

DETAILSPANELEXPANDEDEVENT = wx.NewEventType()
DETAILSPANELCOLLAPSEDEVENT = wx.NewEventType()
ZEVT_DP_EXPANDED = wx.PyEventBinder(DETAILSPANELEXPANDEDEVENT, 1)
ZEVT_DP_COLLAPSED = wx.PyEventBinder(DETAILSPANELCOLLAPSEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZDetailsPanelExpandedEvent(wx.PyCommandEvent):

    def __init__(self, id):
        self.eventType = DETAILSPANELEXPANDEDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, id)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    #end Clone

#end ZDetailsPanelExpandedEvent

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZDetailsPanelCollapsedEvent(wx.PyCommandEvent):

    def __init__(self, id):
        self.eventType = DETAILSPANELCOLLAPSEDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, id)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    #end Clone

#end ZDetailsPanelCollapsedEvent
