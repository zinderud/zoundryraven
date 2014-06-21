from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.action import ZActionContext
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.base.exceptions import ZAbstractMethodCalledException

# ------------------------------------------------------------------------------------
# The interface that all toolbar action contexts must implement.
# ------------------------------------------------------------------------------------
class IZToolBarActionContext(IZActionContext):

    def getParentWindow(self):
        u"Returns the wx Window that is a parent to the toolbar." #$NON-NLS-1$
    # end getParentWindow()

# end IZToolBarAction


# ------------------------------------------------------------------------------------
# An implementation of a toolbar action context.
# ------------------------------------------------------------------------------------
class ZToolBarActionContext(ZActionContext, IZToolBarActionContext):

    def __init__(self, window):
        self.window = window

        ZActionContext.__init__(self)
    # end __init__()

    def getParentWindow(self):
        return self.window
    # end getParentWindow()

# end ZToolBarActionContext()


# ------------------------------------------------------------------------------------
# The interface that all toolbar actions must implement.
# ------------------------------------------------------------------------------------
class IZToolBarAction(IZAction):

    def isEnabled(self, context):
        u"""isEnabled(IZToolBarActionContext) -> boolean
        Returns True if the toolbar item should be enabled
        when displaying the toolbar.""" #$NON-NLS-1$
    # end isEnabled()

    def isDepressed(self, context):
        u"""isDepressed(IZToolBarActionContext) -> boolean
        Returns True if the toolbar item should be depressed
        when displaying the toolbar.""" #$NON-NLS-1$
    # end isDepressed()

    def runToggleAction(self, toolBarActionContext, depressed):
        u"""runToggleAction(IZToolBarActionContext, boolean) -> None
        Called when the user clicks on a toggle-style toolbar
        button.""" #$NON-NLS-1$
    # end runToggleAction()

    def runDropDownAction(self, toolBarActionContext, toolPosition, toolSize):
        u"""runDropDownAction(IZToolBarActionContext, (int, int), (int, int)) -> None
        Called when the user clicks on a dropdown-style toolbar
        button.""" #$NON-NLS-1$
    # end runToggleAction()

# end IZToolBarAction


# ------------------------------------------------------------------------------------
# Simple base class for toolbar action impls.
# ------------------------------------------------------------------------------------
class ZToolBarAction(IZToolBarAction):

    def isEnabled(self, context): #@UnusedVariable
        return True
    # end isEnabled()

    def isDepressed(self, context): #@UnusedVariable
        return False
    # end isDepressed()

# end ZToolBarAction


# ------------------------------------------------------------------------------
# Base class for drop down actions.  This base class offers the ability to
# override the "runDropDownAction", or the ability to override the creation
# of a menu model used as the result of the drop down action.
# ------------------------------------------------------------------------------
class ZDropDownToolBarAction(ZToolBarAction):

    def runDropDownAction(self, toolBarActionContext, toolPosition, toolSize):
        menuModel = self._createMenuModel(toolBarActionContext)
        menuContext = self._createContext(toolBarActionContext)
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        handler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        menu = ZMenu(toolBarActionContext.getParentWindow(), menuModel.getRootNode(), provider, handler)
        menu.refresh()
        parentWindow = toolBarActionContext.getParentWindow()
        (x, y) = self._getPopupPosition(toolPosition, toolSize, parentWindow)
        toolBarActionContext.getParentWindow().PopupMenuXY(menu, x, y)
    # end runToggleAction()

    def _createContext(self, toolBarActionContext):
        return toolBarActionContext
    # end _createContext()

    def _createMenuModel(self, toolBarActionContext):
        raise ZAbstractMethodCalledException(self.__class__, u"_createMenuModel") #$NON-NLS-1$
    # end _createMenuModel()

    def _getPopupPosition(self, toolPosition, toolSize, window):
        (x, y) = toolPosition
        h = toolSize[1]
        y = y + h - 1
        (px, py) = window.GetScreenPositionTuple()
        return (x - px, y - py)
    # end _getPopupPosition()

# end ZDropDownToolBarAction


# ------------------------------------------------------------------------------
# Implementation of a toolbar action that delegates to some other action.  This
# is a base class used for drop-down actions that simply want to implement the
# behavior for "runDropDownAction".  This base class offers the ability to
# override just the "runDropDownAction", or the ability to override the creation
# of a menu model used as the result of the drop down action.
# ------------------------------------------------------------------------------
class ZDelegatingDropDownToolBarAction(ZDropDownToolBarAction):

    def __init__(self, toolbarAction):
        ZToolBarAction.__init__(self)

        self.toolbarAction = toolbarAction
    # end __init__()

    def isEnabled(self, context):
        return self.toolbarAction.isEnabled(context)
    # end isEnabled()

    def isDepressed(self, context):
        return self.toolbarAction.isDepressed(context)
    # end isDepressed()

# end ZDelegatingDropDownToolBarAction

