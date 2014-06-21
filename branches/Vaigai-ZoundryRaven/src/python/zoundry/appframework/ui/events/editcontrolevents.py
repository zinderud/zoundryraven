import wx

# FIXME need contentModified event
# LINK_CLICKED event method:  getLink
# DRAG_N_DROP event method: getFIles(), getHtml(), getText() depending on subclass.

CONTENT_MODIFIED = wx.NewEventType()
UPDATE_UI = wx.NewEventType()
SELECTION_CHANGE = wx.NewEventType()
CONTEXT_MENU = wx.NewEventType()
CLICK_EVENT = wx.NewEventType()
DBL_CLICK_EVENT = wx.NewEventType()

# ------------------------------------------------------------------------------
# Interface used to access edit control related events.
# ------------------------------------------------------------------------------
class IZEditControlEvents:

    ZEVT_CONTENT_MODIFIED = wx.PyEventBinder(CONTENT_MODIFIED, 1)
    ZEVT_UPDATE_UI = wx.PyEventBinder(UPDATE_UI, 1)
    ZEVT_SELECTION_CHANGE = wx.PyEventBinder(SELECTION_CHANGE, 1)
    ZEVT_CONTEXT_MENU = wx.PyEventBinder(CONTEXT_MENU, 1)
    ZEVT_CLICK = wx.PyEventBinder(CLICK_EVENT, 1)
    ZEVT_DBL_CLICK = wx.PyEventBinder(DBL_CLICK_EVENT, 1)

# end IZEditControlEvents

# ----------------------------------------------------------------------------
# baseevent class.
# ----------------------------------------------------------------------------
class ZEditControlEvent(wx.PyCommandEvent):

    def __init__(self, eventType, windowID, editor):
        self.editor = editor
        self.eventType = eventType
        wx.PyCommandEvent.__init__(self, eventType, windowID)
    #end __init__

    def getEditor(self):
        return self.editor

    def Clone(self):
        return self.__class__(self.GetEventType(), self.GetId(), self.getEditor())
    #end Clone
#end ZEditControlEvent

#-------------------------------------------------
# UI Updated event to notify  toolbars etc.
#-------------------------------------------------
class ZEditControlUpdateUIEvent(ZEditControlEvent):

    def __init__(self, windowID, editor):
        ZEditControlEvent.__init__(self, UPDATE_UI, windowID, editor)
    # end __init__()
# end ZEditControlUpdateUIEvent

#-------------------------------------------------
# UI Updated event to notify  toolbars etc.
#-------------------------------------------------
class ZEditControlClickEvent(ZEditControlEvent):

    def __init__(self, windowID, editor):
        ZEditControlEvent.__init__(self, CLICK_EVENT, windowID, editor)
    # end __init__()
# end ZEditControlClickEvent

#-------------------------------------------------
# UI Updated event to notify  toolbars etc.
#-------------------------------------------------
class ZEditControlDoubleClickEvent(ZEditControlEvent):

    def __init__(self, windowID, editor):
        ZEditControlEvent.__init__(self, DBL_CLICK_EVENT, windowID, editor)
    # end __init__()
# end ZEditControlDoubleClickEvent

#-------------------------------------------------
# Event to notify that the content has been modified.
#-------------------------------------------------
class ZEditControlContentModifiedEvent(ZEditControlEvent):

    def __init__(self, windowID, editor):
        ZEditControlEvent.__init__(self, CONTENT_MODIFIED, windowID, editor)

#-------------------------------------------------
# Selection change event
#-------------------------------------------------
class ZEditControlSelectionChangeEvent(ZEditControlEvent):

    def __init__(self, windowID, editor, selection):
        self.selection = selection
        ZEditControlEvent.__init__(self, SELECTION_CHANGE, windowID, editor)

    def getSelection(self):
        u"""getSelection() -> IZEditControlSelection
        Returns current selection.""" #$NON-NLS-1$
        return self.selection

    def Clone(self):
        return self.__class__(self.GetId(), self.getEditor(), self.getSelection())
    #end Clone

#-------------------------------------------------
# Context menu operation
#-------------------------------------------------
class ZEditControlContextMenuEvent(ZEditControlEvent):

    def __init__(self, windowID, editor, parentWindow, xyPoint):
        self.parentWindow = parentWindow
        self.xyPoint = xyPoint
        ZEditControlEvent.__init__(self, CONTEXT_MENU, windowID, editor)

    def getParentWindow(self):
        u"""getParentWindow() -> wxWindow or its derivative
        Returns window owner of the context menu.""" #$NON-NLS-1$
        return self.parentWindow

    def getXYPoint(self):
        u"""getXYPoint() -> wxPoint
        Returns location of the context menu action with respect to the parent window.""" #$NON-NLS-1$
        return self.xyPoint

    def Clone(self):
        self.__class__(self.GetId(), self.getEditor(), self.getParentWindow(), self.getXYPoint())
    # end Clone()
