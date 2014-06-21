import wx

TOOLBUTTONEVENT = wx.NewEventType()
TOOLTOGGLEEVENT = wx.NewEventType()
TOOLDROPDOWNEVENT = wx.NewEventType()
TOOLRIGHTCLICKEVENT = wx.NewEventType()
TOOLRESIZEEVENT = wx.NewEventType()

ZEVT_TOOL_BUTTON = wx.PyEventBinder(TOOLBUTTONEVENT, 1)
ZEVT_TOOL_TOGGLE_BUTTON = wx.PyEventBinder(TOOLTOGGLEEVENT, 1)
ZEVT_TOOL_DROPDOWN_BUTTON = wx.PyEventBinder(TOOLDROPDOWNEVENT, 1)
ZEVT_TOOL_RIGHT_CLICK = wx.PyEventBinder(TOOLRIGHTCLICKEVENT, 1)
ZEVT_TOOLBAR_RESIZE = wx.PyEventBinder(TOOLRESIZEEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolEvent(wx.PyCommandEvent):

    def __init__(self, eventType, windowID, toolNode):
        self.toolNode = toolNode
        wx.PyCommandEvent.__init__(self, eventType, windowID)
    #end __init__

    def getToolNode(self):
        return self.toolNode
    # end getToolNode()

    def Clone(self):
        return self.__class__(self.GetEventType(), self.GetId(), self.getToolNode())
    # end Clone()

# end ZToolEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolButtonEvent(ZToolEvent):

    def __init__(self, windowID, toolNode):
        ZToolEvent.__init__(self, TOOLBUTTONEVENT, windowID, toolNode)
    # end __init__()

# end ZToolButtonEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolToggleEvent(ZToolEvent):

    def __init__(self, windowID, toolNode, toggled):
        self.toggled = toggled

        ZToolEvent.__init__(self, TOOLTOGGLEEVENT, windowID, toolNode)
    # end __init__()

    def isToggled(self):
        return self.toggled
    # end isToggled()

    def Clone(self):
        return self.__class__(self.GetId(), self.getToolNode(), self.isToggled())
    # end Clone()

# end ZToolToggleEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolDropDownEvent(ZToolEvent):

    def __init__(self, windowID, toolNode, position, size):
        self.position = position
        self.size = size
        ZToolEvent.__init__(self, TOOLDROPDOWNEVENT, windowID, toolNode)
    # end __init__()

    def getPosition(self):
        return self.position
    # end getPosition()

    def getSize(self):
        return self.size
    # end getSize()

    def Clone(self):
        return self.__class__(self.GetEventType(), self.GetId(), self.getToolNode(), self.getPosition(), self.getSize())
    # end Clone()

# end ZToolDropDownEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolRightClickEvent(ZToolEvent):

    def __init__(self, windowID, toolNode):
        ZToolEvent.__init__(self, TOOLRIGHTCLICKEVENT, windowID, toolNode)
    # end __init__()

# end ZToolRightClickEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZToolBarResizeEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        wx.PyCommandEvent.__init__(self, TOOLRESIZEEVENT, windowID)
    # end __init__()

    def Clone(self):
        self.__class__(self.GetId())
    # end Clone()

# end ZToolBarResizeEvent
