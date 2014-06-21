import wx

POPUPLISTEVENT = wx.NewEventType()
CHECKLISTCHANGEEVENT = wx.NewEventType()
ZEVT_POPUP_LIST_SELECTION = wx.PyEventBinder(POPUPLISTEVENT, 1)
ZEVT_CHECKBOX_LIST_CHANGE = wx.PyEventBinder(CHECKLISTCHANGEEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZPopupListSelectionEvent(wx.PyCommandEvent):

    def __init__(self, windowID, listId):
        self.listId = listId
        self.eventType = POPUPLISTEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getListId(self):
        return self.listId
    # end getList()

    def Clone(self):
        return self.__class__(self.GetId(), self.getListId())
    # end Clone()

# end ZPopupListSelectionEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZCheckBoxListChangeEvent(wx.PyCommandEvent):

    def __init__(self, windowID, listId, checked):
        self.listId = listId
        self.checked = checked
        self.eventType = CHECKLISTCHANGEEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__()

    def getListId(self):
        return self.listId
    # end getList()

    def isChecked(self):
        return self.checked
    # end isChecked()

    def Clone(self):
        return self.__class__(self.GetId(), self.getListId(), self.isChecked())
    # end Clone()

# end ZCheckBoxListChangeEvent
