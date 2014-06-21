from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.ui.actions.toolbaraction import IZToolBarAction
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import IZToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import IZToolBarEventHandler

# ------------------------------------------------------------------------------
# An interface that toolbar nodes should implement.  A toolbar node can be used
# when modeling a toolbar.
# ------------------------------------------------------------------------------
class IZToolBarNode:

    def getText(self):
        u"""getText() -> string
        Gets the node's text.""" #$NON-NLS-1$
    # end getText()

    def getDescription(self):
        u"""getDescription() -> string
        Gets the node's description.""" #$NON-NLS-1$
    # end getDescription()

    def getGravity(self):
        u"""getGravity() -> int
        Gets the node's gravity.""" #$NON-NLS-1$
    # end getGravity()

    def getBitmap(self, size):
        u"""getBitmap(int) -> wx.Bitmap
        Gets the node's bitmap of the given size.""" #$NON-NLS-1$
    # end getBitmap()

    def getDisabledBitmap(self, size):
        u"""getDisabledBitmap(int) -> wx.Bitmap
        Gets the node's disabled bitmap of the given size.""" #$NON-NLS-1$
    # end getDisabledBitmap()

    def getHoverBitmap(self, size):
        u"""getHoverBitmap(int) -> wx.Bitmap
        Gets the node's hover bitmap of the given size.""" #$NON-NLS-1$
    # end getHoverBitmap()

    def isSeparator(self):
        u"""isSeparator() -> boolean
        Returns True if this node represents a toolbar
        separator.""" #$NON-NLS-1$
    # end isSeparator()

    def isToggleTool(self):
        u"""isToggleTool() -> boolean
        Returns True if this node represents a
        toggle-style toolbar item.""" #$NON-NLS-1$
    # end isToggleTool()

    def isDropDownTool(self):
        u"""isDropDownTool() -> boolean
        Returns True if this node represents a
        toggle-style toolbar item.""" #$NON-NLS-1$
    # end isDropDownTool()

    def getDropDownMenuModel(self):
        u"""getDropDownMenuModel() -> ZMenuModel
        Returns the menu model to use when displaying the
        drop down menu (only valid for drop-down style
        tools).""" #$NON-NLS-1$
    # end getDropDownMenuModel()

# end IZToolBarNode


# ------------------------------------------------------------------------------
# A simple implementation of a IZToolBarNode.
# ------------------------------------------------------------------------------
class ZToolBarNode(IZToolBarNode):

    def __init__(self, text, description, gravity, isToggle = False, isDropDown = False):
        self.text = text
        self.description = description
        self.gravity = gravity
        self.bitmaps = {}
        self.disabledBitmaps = {}
        self.hoverBitmaps = {}
        self.isToggle = isToggle
        self.isDropDown = isDropDown
    # end __init__()

    def getText(self):
        return self.text
    # end getText()

    def setText(self, text):
        self.text = text
    # end setText()

    def getDescription(self):
        return self.description
    # end getDescription()

    def setDescription(self, description):
        self.description = description
    # end setDescription()

    def getGravity(self):
        return self.gravity
    # end getGravity()

    def getBitmap(self, size):
        if size in self.bitmaps:
            return self.bitmaps[size]
        return None
    # end getBitmap()

    def addBitmap(self, size, bitmap):
        self.bitmaps[size] = bitmap
    # end addBitmap()

    def getDisabledBitmap(self, size):
        if size in self.disabledBitmaps:
            return self.disabledBitmaps[size]
        return None
    # end getDisabledBitmap()

    def addDisabledBitmap(self, size, bitmap):
        self.disabledBitmaps[size] = bitmap
    # end addDisabledBitmap()

    def getHoverBitmap(self, size):
        if size in self.hoverBitmaps:
            return self.hoverBitmaps[size]
        return None
    # end getHoverBitmap()

    def addHoverBitmap(self, size, bitmap):
        self.hoverBitmaps[size] = bitmap
    # end addHoverBitmap()

    def isSeparator(self):
        return False
    # end isSeparator()

    def isToggleTool(self):
        return self.isToggle
    # end isToggleTool()

    def isDropDownTool(self):
        return self.isDropDown
    # end isDropDownTool()

    def getDropDownMenuModel(self):
        return self.dropDownMenuModel
    # end getDropDownMenuModel()

    def setDropDownMenuModel(self, menuModel):
        self.dropDownMenuModel = menuModel
    # end setDropDownMenuModel()

# end ZToolBarNode


# ------------------------------------------------------------------------------
# Implements a node that is a toolbar separator.
# ------------------------------------------------------------------------------
class ZToolBarSeparatorNode(ZToolBarNode):

    def __init__(self, gravity):
        ZToolBarNode.__init__(self, u"", u"", gravity) #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def isSeparator(self):
        return True
    # end isSeparator()

# end ZToolBarSeparatorNode


# ------------------------------------------------------------------------------
# Implements a toolbar content provider that uses a list of toolbar nodes as
# the content.
# ------------------------------------------------------------------------------
class ZNodeBasedToolBarContentProvider(IZToolBarContentProvider):

    def __init__(self, nodes, toolSize, supportedSizes):
        self.nodes = nodes
        self.toolSize = toolSize
        self.supportedSizes = supportedSizes
    # end _init__()

    def getToolBitmapSizes(self):
        return self.supportedSizes
    # end getToolBitmapSizes()

    def getToolBitmapSize(self):
        return self.toolSize
    # end getToolBitmapSize()

    def getToolBarNodes(self):
        return self.nodes
    # end getToolBarNodes()

    def getText(self, node):
        return node.getText()
    # end getText()

    def getDescription(self, node):
        return node.getDescription()
    # end getDescription()

    def getBitmap(self, node, size):
        return node.getBitmap(size)
    # end getBitmap()

    def getDisabledBitmap(self, node, size):
        return node.getDisabledBitmap(size)
    # end getDisabledBitmap()

    def getHoverBitmap(self, node, size):
        return node.getHoverBitmap(size)
    # end getHoverBitmap()

    def isSeparator(self, node):
        return node.isSeparator()
    # end isSeparator()

    def isToggleTool(self, node):
        return node.isToggleTool()
    # end isToggleTool()

    def isDropDownTool(self, node):
        return node.isDropDownTool()
    # end isDropDownTool()

    def getDropDownMenuModel(self, node):
        return node.getDropDownMenuModel()
    # end getDropDownMenuModel()

    def isEnabled(self, node): #@UnusedVariable
        return True
    # end isEnabled()

    def isDepressed(self, node): #@UnusedVariable
        return False
    # end isDepressed()

# end ZNodeBasedToolBarContentProvider


# ------------------------------------------------------------------------------
# Extends the standard toolbar node in order to define a node that also handles
# its own visual state and click action.
# ------------------------------------------------------------------------------
class IZActiveToolBarNode(IZToolBarNode):

    def isEnabled(self, toolBarActionContext):
        u"""isEnabled(IZToolBarActionContext) -> boolean
        Returns True if the toolbar node is currently
        enabled.""" #$NON-NLS-1$
    # end isEnabled()

    def isDepressed(self, toolBarActionContext):
        u"""isDepressed(IZToolBarActionContext) -> boolean
        Returns True if the toolbar node is currently
        depressed (only applicable for toggle-style toolbar
        nodes).""" #$NON-NLS-1$
    # end isDepressed()

    def runAction(self, toolBarActionContext):
        u"""runAction(IZToolBarActionContext) -> None
        Called when the user clicks on the toolbar
        button.""" #$NON-NLS-1$
    # end runAction()

    def runToggleAction(self, toolBarActionContext, depressed):
        u"""runToggleAction(IZToolBarActionContext, boolean) -> None
        Called when the user clicks on a toggle-style
        toolbar button.""" #$NON-NLS-1$
    # end runToggleAction()

    def runDropDownAction(self, toolBarActionContext, position, size):
        u"""runDropDownAction(IZToolBarActionContext, (int, int), (int, int)) -> None
        Called when the user clicks on a dropdown-style
        toolbar button.""" #$NON-NLS-1$
    # end runDropDownAction()

# end IZActiveToolBarNode


# ------------------------------------------------------------------------------
# An implementation of an active toolbar node (IZActiveToolBarNode).
# ------------------------------------------------------------------------------
class ZActiveToolBarNode(ZToolBarNode, IZActiveToolBarNode):

    def __init__(self, text, description, gravity, isToggle = False, isDropDown = False, action = None):
        self.action = action

        ZToolBarNode.__init__(self, text, description, gravity, isToggle, isDropDown)
    # end __init__()

    def isEnabled(self, toolBarActionContext):
        return self.action.isEnabled(toolBarActionContext)
    # end isEnabled()

    def isDepressed(self, toolBarActionContext):
        return self.action.isDepressed(toolBarActionContext)
    # end isDepressed()

    def runAction(self, toolBarActionContext):
        self.action.runAction(toolBarActionContext)
    # end runAction()

    def runToggleAction(self, toolBarActionContext, depressed):
        self.action.runToggleAction(toolBarActionContext, depressed)
    # end runToggleAction()

    def runDropDownAction(self, toolBarActionContext, position, size):
        self.action.runDropDownAction(toolBarActionContext, position, size)
    # end runDropDownAction()

# end ZActiveToolBarNode


# ------------------------------------------------------------------------------
# An implementation of an active toolbar node (IZActiveToolBarNode) that adapts
# a simple callback method to an action.
# ------------------------------------------------------------------------------
class ZActiveCallbackToolBarNode(ZActiveToolBarNode):

    # --------------------------------------------------------------------------
    # Inner class used to adapt the callback to an action.
    # --------------------------------------------------------------------------
    class ZCallbackRunner(IZToolBarAction):

        def __init__(self, callback, enabled):
            self.callback = callback
            self.enabled = enabled
        # end __init__()

        def isEnabled(self, context): #@UnusedVariable
            return self.enabled
        # end isEnabled()

        def isDepressed(self, context): #@UnusedVariable
            return False
        # end isDepressed()

        def runAction(self, actionContext):
            if self.callback is not None:
                self.callback(actionContext)
        # end runAction()

        def runToggleAction(self, toolBarActionContext, depressed):
            raise ZAppFrameworkException(u"Toggle style toolbar items not supported by ZActiveCallbackToolBarNode") #$NON-NLS-1$
        # end runToggleAction()

        def runDropDownAction(self, toolBarActionContext, position, size):
            raise ZAppFrameworkException(u"Drop-down style toolbar items not supported by ZActiveCallbackToolBarNode") #$NON-NLS-1$
        # end runDropDownAction()

    # end ZCallbackRunner

    def __init__(self, text, description, gravity, isToggle = False, isDropDown = False, enabled = True, callback = None):
        action = ZActiveCallbackToolBarNode.ZCallbackRunner(callback, enabled)

        ZActiveToolBarNode.__init__(self, text, description, gravity, isToggle, isDropDown, action)
    # end __init__()

# end ZActiveCallbackToolBarNode


# ------------------------------------------------------------------------------
# Implements a toolbar content provider that uses a list of toolbar nodes as
# the content.
# ------------------------------------------------------------------------------
class ZActiveNodeBasedToolBarContentProvider(ZNodeBasedToolBarContentProvider):

    def __init__(self, nodes, toolSize, supportedSizes, actionContext):
        self.actionContext = actionContext

        ZNodeBasedToolBarContentProvider.__init__(self, nodes, toolSize, supportedSizes)
    # end _init__()
    
    def isEnabled(self, node): #@UnusedVariable
        return node.isEnabled(self.actionContext)
    # end isEnabled()

    def isDepressed(self, node): #@UnusedVariable
        return node.isDepressed(self.actionContext)
    # end isDepressed()

# end ZNodeBasedToolBarContentProvider


# ------------------------------------------------------------------------------
# An implementation of a toolbar event handler based on active toolbar nodes.
# ------------------------------------------------------------------------------
class ZActiveNodeBasedToolBarEventHandler(IZToolBarEventHandler):

    def __init__(self, toolBarContext):
        self.toolBarContext = toolBarContext
    # end __init__()

    def onToolClick(self, toolNode):
        toolNode.runAction(self.toolBarContext)
    # end onToolClick()

    def onToggleToolClick(self, toolNode, depressed):
        toolNode.runToggleAction(self.toolBarContext, depressed)
    # end onToggleToolClick()

    def onDropDownToolClick(self, toolNode, toolPosition, toolSize):
        toolNode.runDropDownAction(self.toolBarContext, toolPosition, toolSize)
    # end onToggleToolClick()

# end ZActiveNodeBasedToolBarEventHandler
