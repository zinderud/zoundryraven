import wx

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorEvent(wx.PyCommandEvent):

    def __init__(self, eventType, editor):
        self.editor = editor
        self.eventType = eventType
        wx.PyCommandEvent.__init__(self, self.eventType)
    #end __init__

    def getEditor(self):
        return self.editor
    # end getEditor()
    
    def _getEventType(self):
        return self.eventType
    # end _getEventType()

    def Clone(self):
        return self.__class__(self._getEventType(), self.getEditor())
    #end Clone

#end ZEditorEvent


EDITORCLOSEEVENT = wx.NewEventType()
EDITORTITLECHANGEDEVENT = wx.NewEventType()
EDITORDIRTYEVENT = wx.NewEventType()
EDITORSTATUSBARCHANGEDEVENT = wx.NewEventType()
EDITORMENUBARCHANGEDEVENT = wx.NewEventType()
EDITORTOOLBARCHANGEDEVENT = wx.NewEventType()

ZEVT_EDITOR_CLOSE = wx.PyEventBinder(EDITORCLOSEEVENT, 0)
ZEVT_EDITOR_TITLE_CHANGED = wx.PyEventBinder(EDITORTITLECHANGEDEVENT, 0)
ZEVT_EDITOR_DIRTY = wx.PyEventBinder(EDITORDIRTYEVENT, 0)
ZEVT_EDITOR_STATUS_BAR_CHANGED = wx.PyEventBinder(EDITORSTATUSBARCHANGEDEVENT, 0)
ZEVT_EDITOR_MENU_BAR_CHANGED = wx.PyEventBinder(EDITORMENUBARCHANGEDEVENT, 0)
ZEVT_EDITOR_TOOL_BAR_CHANGED = wx.PyEventBinder(EDITORTOOLBARCHANGEDEVENT, 0)

# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorCloseEvent(ZEditorEvent):

    def __init__(self, editor):
        ZEditorEvent.__init__(self, EDITORCLOSEEVENT, editor)
    #end __init__

    def Clone(self):
        return self.__class__(self.getEditor())
    #end Clone

#end ZEditorCloseEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorTitleChangedEvent(ZEditorEvent):

    def __init__(self, editor, title):
        self.title = title
        ZEditorEvent.__init__(self, EDITORTITLECHANGEDEVENT, editor)
    #end __init__

    def getTitle(self):
        return self.title
    # end getTitle()
    
    def Clone(self):
        return self.__class__(self.getEditor(), self.getTitle())
    #end Clone

#end ZEditorTitleChangedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorDirtyEvent(ZEditorEvent):

    def __init__(self, editor):
        ZEditorEvent.__init__(self, EDITORDIRTYEVENT, editor)
    #end __init__

    def Clone(self):
        return self.__class__(self.getEditor())
    #end Clone

#end ZEditorDirtyEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorStatusBarChangedEvent(ZEditorEvent):

    def __init__(self, editor):
        ZEditorEvent.__init__(self, EDITORSTATUSBARCHANGEDEVENT, editor)
    #end __init__

    def Clone(self):
        return self.__class__(self.getEditor())
    #end Clone

#end ZEditorStatusBarChangedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorMenuBarChangedEvent(ZEditorEvent):

    def __init__(self, editor):
        ZEditorEvent.__init__(self, EDITORMENUBARCHANGEDEVENT, editor)
    #end __init__

    def Clone(self):
        return self.__class__(self.getEditor())
    #end Clone

#end ZEditorMenuBarChangedEvent


# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZEditorToolBarChangedEvent(ZEditorEvent):

    def __init__(self, editor):
        ZEditorEvent.__init__(self, EDITORTOOLBARCHANGEDEVENT, editor)
    #end __init__

    def Clone(self):
        return self.__class__(self.getEditor())
    #end Clone

#end ZEditorToolBarChangedEvent


# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def fireEditorTitleChangedEvent(window, editor, title):
    event = ZEditorTitleChangedEvent(editor, title)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorTitleChangedEvent()

# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def fireEditorDirtyEvent(window, editor):
    event = ZEditorDirtyEvent(editor)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorDirtyEvent()

# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def fireEditorStatusBarChangedEvent(window, editor):
    event = ZEditorStatusBarChangedEvent(editor)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorStatusBarChangedEvent()

# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def fireEditorMenuBarChangedEvent(window, editor):
    event = ZEditorMenuBarChangedEvent(editor)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorMenuBarChangedEvent()

# ----------------------------------------------------------------------------
# Convenience function for firing a publishing change event.
# ----------------------------------------------------------------------------
def fireEditorToolBarChangedEvent(window, editor):
    event = ZEditorToolBarChangedEvent(editor)
    window.GetEventHandler().AddPendingEvent(event)
# end fireEditorToolBarChangedEvent()
