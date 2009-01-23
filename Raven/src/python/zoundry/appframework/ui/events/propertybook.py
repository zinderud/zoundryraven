import wx

PROPERTYTABSELECTIONEVENT = wx.NewEventType()
ZEVT_PB_TAB_SELECTION = wx.PyEventBinder(PROPERTYTABSELECTIONEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZPropertyBookTabSelectionEvent(wx.PyCommandEvent):

    def __init__(self, id, tabName):
        self.tabName = tabName
        self.eventType = PROPERTYTABSELECTIONEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, id)
    # end __init__()

    def getTabName(self):
        return self.tabName
    # end getTabName()

    def Clone(self):
        return self.__class__(self.GetId(), self.getTabName())
    #end Clone

#end ZPropertyBookTabSelectionEvent
