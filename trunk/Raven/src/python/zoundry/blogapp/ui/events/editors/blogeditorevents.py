import wx

BLOGSELECTORCOMBOEVENT = wx.NewEventType()
BLOGPUBLISHINGCHANGEEVENT = wx.NewEventType()
ZEVT_BLOG_SELECTOR_COMBO = wx.PyEventBinder(BLOGSELECTORCOMBOEVENT, 1)
ZEVT_PUBLISHING_CHANGE = wx.PyEventBinder(BLOGPUBLISHINGCHANGEEVENT, 1)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZBlogSelectorComboEvent(wx.PyCommandEvent):

    def __init__(self, windowID, blog):
        self.blog = blog
        self.eventType = BLOGSELECTORCOMBOEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getBlog(self):
        return self.blog
    # end getBlog()

    def Clone(self):
        return self.__class__(self.GetId(), self.getBlog())
    # end Clone()

# end ZBlogSelectorComboEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZBlogEditorEvent(wx.PyCommandEvent):

    def __init__(self, eventType, windowID):
        wx.PyCommandEvent.__init__(self, eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetEventType(), self.GetId())
    # end Clone()

# end ZBlogEditorEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZBlogPublishingChangeEvent(ZBlogEditorEvent):

    def __init__(self, windowID):
        ZBlogEditorEvent.__init__(self, BLOGPUBLISHINGCHANGEEVENT, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZBlogPublishingChangeEvent


# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def firePublishingChangeEvent(window):
    event = ZBlogPublishingChangeEvent(window.GetId())
    window.GetEventHandler().AddPendingEvent(event)
# end firePublishingChangeEvent()
