import wx

METADATATITLECHANGEDEVENT = wx.NewEventType()

ZEVT_META_DATA_TITLE_CHANGED = wx.PyEventBinder(METADATATITLECHANGEDEVENT, 0)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZMetaDataTitleChangedEvent(wx.PyCommandEvent):

    def __init__(self, title):
        self.title = title
        wx.PyCommandEvent.__init__(self, METADATATITLECHANGEDEVENT)
    # end __init__()

    def getTitle(self):
        return self.title
    # end getTitle()

    def Clone(self):
        return self.__class__(self.getTitle())
    # end Clone()

# end ZMetaDataTitleChangedEvent

# ----------------------------------------------------------------------------
# Convenience function for firing a title change event.
# ----------------------------------------------------------------------------
def fireMetaDataTitleChangedEvent(window, title):
    event = ZMetaDataTitleChangedEvent(title)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorTitleChangedEvent()
