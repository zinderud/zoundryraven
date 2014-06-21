import wx

# Events for the standard Progress Dialog.
PROGRESSSTARTEDEVENT = wx.NewEventType()
PROGRESSWORKDONEEVENT = wx.NewEventType()
PROGRESSCOMPLETEEVENT = wx.NewEventType()
PROGRESSCANCELEVENT = wx.NewEventType()
PROGRESSERROREVENT = wx.NewEventType()
PROGRESSEXCEPTIONEVENT = wx.NewEventType()

# Events for the standard Progress Dialog.
ZEVT_PROGRESS_STARTED = wx.PyEventBinder(PROGRESSSTARTEDEVENT, 1)
ZEVT_PROGRESS_WORKDONE = wx.PyEventBinder(PROGRESSWORKDONEEVENT, 1)
ZEVT_PROGRESS_COMPLETE = wx.PyEventBinder(PROGRESSCOMPLETEEVENT, 1)
ZEVT_PROGRESS_CANCEL = wx.PyEventBinder(PROGRESSCANCELEVENT, 1)
ZEVT_PROGRESS_ERROR = wx.PyEventBinder(PROGRESSERROREVENT, 1)
ZEVT_PROGRESS_EXCEPTION = wx.PyEventBinder(PROGRESSEXCEPTIONEVENT, 1)


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressStartedEvent(wx.PyCommandEvent):

    def __init__(self, windowID, workAmount):
        self.eventType = PROGRESSSTARTEDEVENT
        self.workAmount = workAmount
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getWorkAmount(self):
        return self.workAmount
    # end getWorkAmount()

    def Clone(self):
        return self.__class__(self.GetId(), self.getWorkAmount())
    # end Clone()

#end ZProgressStartedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressWorkDoneEvent(wx.PyCommandEvent):

    def __init__(self, windowID, amount, text):
        self.amount = amount
        self.text = text
        self.eventType = PROGRESSWORKDONEEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__

    def getAmount(self):
        return self.amount
    # end getAmount()

    def getText(self):
        return self.text
    # end getText()

    def Clone(self):
        return self.__class__(self.GetId(), self.getAmount(), self.getText())
    #end Clone

#end ZProgressWorkDoneEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressCompleteEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = PROGRESSCOMPLETEEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__

    def Clone(self):
        return self.__class__(self.GetId())
    #end Clone

#end ZProgressCompleteEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressCancelEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = PROGRESSCANCELEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__

    def Clone(self):
        return self.__class__(self.GetId())
    #end Clone

#end ZProgressCancelEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressErrorEvent(wx.PyCommandEvent):

    def __init__(self, windowID, error):
        self.error = error
        self.eventType = PROGRESSERROREVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__

    def getError(self):
        return self.error
    # end getError()

    def Clone(self):
        return self.__class__(self.GetId(), self.getError())
    #end Clone

#end ZProgressErrorEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZProgressExceptionEvent(wx.PyCommandEvent):

    def __init__(self, windowID, exception):
        self.exception = exception
        self.eventType = PROGRESSEXCEPTIONEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    #end __init__

    def getException(self):
        return self.exception
    # end getException()

    def Clone(self):
        return self.__class__(self.GetId(), self.getException())
    #end Clone

#end ZProgressExceptionEvent
