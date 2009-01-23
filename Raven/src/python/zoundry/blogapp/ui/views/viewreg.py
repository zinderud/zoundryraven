
# ------------------------------------------------------------------------------
# Interface for the view registry.  The view registry is a place where all 
# Views, when constructed, are registered.  Whenever a view is destroyed, it 
# is unregistered.  This registry allows parts of the application the ability 
# to manipulate, find, query, etc all currently active views.
# ------------------------------------------------------------------------------
class IZViewRegistry:

    # Called when a view is created.
    def registerView(self, view):
        u"""registerView(ZView) -> None
        Registers a view with the registry.""" #$NON-NLS-1$
    # end registerView()

    # Called when a view is destroyed.
    def unregisterView(self, view):
        u"""unregisterView(ZView) -> None
        Removes the view from the registry.""" #$NON-NLS-1$
    # end unregisterView()

    # Propagates a view event to all views.
    def fireViewEvent(self, event):
        u"""fireViewEvent(ZViewEvent) -> None
        Fires a view event to all views in the
        registry.""" #$NON-NLS-1$
    # end fireViewEvent()

    def findView(self, viewId):
        u"""findView(viewId) -> ZView
        Finds a view by its id.""" #$NON-NLS-1$
    # end findView()

# end IZViewRegistry


# ------------------------------------------------------------------------------
# The view registry is a place where all Views, when constructed, are
# registered.  Whenever a view is destroyed, it is unregistered.  This registry
# allows parts of the application the ability to manipulate, find, query, etc
# all currently active views.
# ------------------------------------------------------------------------------
class ZViewRegistry(IZViewRegistry):

    def __init__(self):
        self.activeViews = []
    # end __init__()

    # Called when a view is created.
    def registerView(self, view):
        self.activeViews.append(view)
    # end registerView()

    # Called when a view is destroyed.
    def unregisterView(self, view):
        self.activeViews.remove(view)
    # end unregisterView()

    # Propagates a view event to all views.
    def fireViewEvent(self, event):
        for view in self.activeViews:
            view.GetEventHandler().AddPendingEvent(event)
    # end fireViewEvent()

    def findView(self, viewId):
        for view in self.activeViews:
            if view.getViewId() == viewId:
                return view
        return None
    # end findView()

# end ZViewRegistry
