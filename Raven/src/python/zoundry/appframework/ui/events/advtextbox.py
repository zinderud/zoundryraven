import wx

ZTEXTBOXOPTIONSELECTEDEVENT = wx.NewEventType()
ZEVT_ATB_OPTION_SELECTED = wx.PyEventBinder(ZTEXTBOXOPTIONSELECTEDEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZAdvTextBoxOptionEvent(wx.PyCommandEvent):

    def __init__(self, id, optionId):
        self.optionId = optionId
        self.eventType = ZTEXTBOXOPTIONSELECTEDEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, id)
    # end __init__()
    
    def getOptionId(self):
        return self.optionId
    # end getOptionId()

    def Clone(self):
        return self.__class__(self.GetId(), self.getOptionId())
    #end Clone

#end ZAdvTextBoxOptionEvent
