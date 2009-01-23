import wx

TABSELECTEDEVENT = wx.NewEventType()
TABCLOSEDEVENT = wx.NewEventType()
ZEVT_TAB_SELECTED = wx.PyEventBinder(TABSELECTEDEVENT, 1)
ZEVT_TAB_CLOSED = wx.PyEventBinder(TABCLOSEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event base class.
# ----------------------------------------------------------------------------
class ZTabEvent(wx.PyCommandEvent):

    def __init__(self, eventType, id, tabId):
        self.tabId = tabId
        self.vetoed = False
        wx.PyCommandEvent.__init__(self, eventType, id)
    # end __init__()

    def getTabId(self):
        return self.tabId
    # end getTabId()

    def Clone(self):
        return self.__class__(self.GetId(), self.getTabId())
    #end Clone
    
    def Veto(self):
        self.vetoed = True
    # end Veto()
    
    def isVetoed(self):
        return self.vetoed
    # end isVetoed()

#end ZTabEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZTabSelectedEvent(ZTabEvent):
    
    def __init__(self, id, tabId):
        ZTabEvent.__init__(self, TABSELECTEDEVENT, id, tabId)
    # end __init__()

# end ZTabSelectedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZTabClosedEvent(ZTabEvent):
    
    def __init__(self, id, tabId):
        ZTabEvent.__init__(self, TABCLOSEDEVENT, id, tabId)
    # end __init__()

# end ZTabClosedEvent
