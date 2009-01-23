import wx

TOOLBOOKSELECTINGEVENT = wx.NewEventType()
TOOLBOOKSELECTEDEVENT = wx.NewEventType()
ZEVT_TOOLBOOK_SELECTING = wx.PyEventBinder(TOOLBOOKSELECTINGEVENT, 1)
ZEVT_TOOLBOOK_SELECTED = wx.PyEventBinder(TOOLBOOKSELECTEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event base class.
# ----------------------------------------------------------------------------
class ZToolBookEvent(wx.PyCommandEvent):

    def __init__(self, eventType, id, toolId):
        self.toolId = toolId
        wx.PyCommandEvent.__init__(self, eventType, id)
    # end __init__()

    def getToolId(self):
        return self.toolId
    # end getToolId()

    def Clone(self):
        return self.__class__(self.GetId(), self.getToolId())
    #end Clone

#end ZToolBookEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolBookSelectedEvent(ZToolBookEvent):
    
    def __init__(self, id, toolId):
        ZToolBookEvent.__init__(self, TOOLBOOKSELECTEDEVENT, id, toolId)
    # end __init__()

# end ZToolBookSelectedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolBookSelectingEvent(ZToolBookEvent):

    def __init__(self, id, toolId):
        ZToolBookEvent.__init__(self, TOOLBOOKSELECTINGEVENT, id, toolId)
        self.vetoed = False
    # end __init__()
    
    def Veto(self):
        self.vetoed = True
    # end Veto()
    
    def isVetoed(self):
        return self.vetoed
    # end isVetoed()

# end ZToolBookSelectingEvent


# ----------------------------------------------------------------------------
# Convenience function for firing an event.
# ----------------------------------------------------------------------------
def fireToolBookSelectingEvent(window, toolId, sync = False):
    event = ZToolBookSelectingEvent(window.GetId(), toolId)
    if sync:
        window.GetEventHandler().ProcessEvent(event)
    else:
        window.GetEventHandler().AddPendingEvent(event)
    return event
# end fireToolBookSelectingEvent()


# ----------------------------------------------------------------------------
# Convenience function for firing an event.
# ----------------------------------------------------------------------------
def fireToolBookSelectedEvent(window, toolId):
    event = ZToolBookSelectedEvent(window.GetId(), toolId)
    window.GetEventHandler().AddPendingEvent(event)
# end fireToolBookSelectedEvent()
