import wx

VIEWSELECTIONEVENT = wx.NewEventType()
VIEWBLOGPOSTSFILTERCHANGEDEVENT = wx.NewEventType()
VIEWLINKSFILTERCHANGEDEVENT = wx.NewEventType()
VIEWIMAGESFILTERCHANGEDEVENT = wx.NewEventType()
VIEWTAGSFILTERCHANGEDEVENT = wx.NewEventType()

ZEVT_VIEW_SELECTION_CHANGED = wx.PyEventBinder(VIEWSELECTIONEVENT, 0)
ZEVT_VIEW_BLOG_POSTS_FILTER_CHANGED = wx.PyEventBinder(VIEWBLOGPOSTSFILTERCHANGEDEVENT, 0)
ZEVT_VIEW_LINKS_FILTER_CHANGED = wx.PyEventBinder(VIEWLINKSFILTERCHANGEDEVENT, 0)
ZEVT_VIEW_IMAGES_FILTER_CHANGED = wx.PyEventBinder(VIEWIMAGESFILTERCHANGEDEVENT, 0)
ZEVT_VIEW_TAGS_FILTER_CHANGED = wx.PyEventBinder(VIEWTAGSFILTERCHANGEDEVENT, 0)


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZViewEvent(wx.PyCommandEvent):

    def __init__(self, eventType, view):
        self.view = view
        self.eventType = eventType
        wx.PyCommandEvent.__init__(self, self.eventType)
    #end __init__()
    
    def getView(self):
        return self.view
    # end getView()

    def Clone(self):
        return self.__class__(self.GetEventType(), self.getView())
    #end Clone()

# end ZViewEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZViewSelectionEvent(ZViewEvent):

    def __init__(self, view, selection):
        self.selection = selection
        ZViewEvent.__init__(self, VIEWSELECTIONEVENT, view)
    #end __init__()

    def getSelection(self):
        return self.selection
    # end getSelection()

    def Clone(self):
        return self.__class__(self.getView(), self.getSelection())
    #end Clone()

# end ZViewSelectionEvent

