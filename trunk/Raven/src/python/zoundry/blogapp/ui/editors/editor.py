from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarActionContext
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorCloseEvent
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorDirtyEvent
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorMenuBarChangedEvent
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorStatusBarChangedEvent
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorTitleChangedEvent
from zoundry.blogapp.ui.events.editors.editorevents import ZEditorToolBarChangedEvent
import wx

# ------------------------------------------------------------------------------
# Interface that all editors must implement.
#
# Events
# ------
#   Instances of IZEditor can throw any of the following events which are used
#   by windows that contain the editor.
#
#   ZEVT_EDITOR_TITLE_CHANGED: event fired when the editor's title changes
#   ZEVT_EDITOR_DIRTY: event fired when the editor's content goes from
#            not dirty->dirty or dirty->not dirty
#   ZEVT_EDITOR_STATUS_BAR_CHANGED: event fired when the editor's status bar
#            changes in some way
#   ZEVT_EDITOR_MENU_BAR_CHANGED: event fired when the editor's menu bar changes
#            in some way
#   ZEVT_EDITOR_TOOL_BAR_CHANGED: event fired when the editor's tool bar changes
#            in some way
# ------------------------------------------------------------------------------
class IZEditor:

    def getTitle(self):
        u"""getTitle() -> string
        Returns the title of the editor.""" #$NON-NLS-1$
    # end getTitle()

    def getDocument(self):
        u"""getDocument() -> IZDocument
        Returns the document that this editor is editing.""" #$NON-NLS-1$
    # end getDocument()

    def getDocumentId(self):
        u"""getDocumentId() -> string
        Returns the ID of the document that this editor is
        editing.""" #$NON-NLS-1$
    # end getDocumentId()

    def getBitmap(self):
        u"""getBitmap() -> wx.Bitmap
        Returns a bitmap representing the editor or document
        being edited.""" #$NON-NLS-1$
    # end getBitmap()

    def getMenuBarModel(self):
        u"""getMenuBarModel() -> ZMenuBarModel
        Returns the menu bar model that should be used to
        populate the editor window's menu bar when this
        editor is active.""" #$NON-NLS-1$
    # end getMenuBarModel()

    def getToolBarModel(self):
        u"""getToolBarModel() -> ZToolBarModel
        Returns the tool bar model that should be used to
        populate the editor window's main tool bar when
        this editor is active.""" #$NON-NLS-1$
    # end getToolBarModel()

    def getStatusBarModel(self):
        u"""getStatusBarModel() -> ZStatusBarModel
        Returns the status bar model that should be used to
        populate the editor window's status bar when this
        editor is active.""" #$NON-NLS-1$
    # end getStatusBarModel()

    def getToolBarActionContext(self):
        u"""getToolBarActionContext() -> IZToolBarActionContext
        Returns the action context to use for the toolbar.""" #$NON-NLS-1$
    # end getToolBarActionContext()

    def getMenuActionContext(self):
        u"""getMenuActionContext() -> IZMenuActionContext
        Returns the action context to use for the menu items.""" #$NON-NLS-1$
    # end getMenuActionContext()

    def isDirty(self):
        u"""isDirty() -> boolean
        Returns True if the editor is dirty.""" #$NON-NLS-1$
    # end isDirty()

    def save(self):
        u"""save() -> None
        Called when the editor needs to be saved.""" #$NON-NLS-1$
    # end save()

    def close(self):
        u"""close() -> None
        Closes the editor.""" #$NON-NLS-1$
    # end close()

    def hasCapability(self, capabilityKey):
        u"""hasCapability() -> bool
        Returns true if the editor supports the given capability.""" #$NON-NLS-1$
    # end hasCapability()

    def destroy(self):
        u"""destroy() -> None
        Called when the editor is destroyed.""" #$NON-NLS-1$
    # end destroy()

# end IZEditor


# ------------------------------------------------------------------------------
# Base class for editor implementations.  (abstract)
# ------------------------------------------------------------------------------
class ZEditor(IZEditor, wx.Panel):

    def __init__(self, parent):
        self.dirty = False

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._initEditor()
    # end __init__()

    def getToolBarActionContext(self):
        return ZToolBarActionContext(self)
    # end getToolBarActionContext()

    def getMenuActionContext(self):
        return ZMenuActionContext(self)
    # end getMenuActionContext

    def hasCapability(self, capabilityKey): #@UnusedVariable
        return False
    # end hasCapability()

    def _initEditor(self):
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        self._setInitialFocus()
    # end _initEditor()

    def _createWidgets(self):
        self._createEditorWidgets()
    # end _createWidgets()

    def _populateWidgets(self):
        self._populateEditorWidgets()
    # end _populateWidgets()

    def _layoutWidgets(self):
        # Subclass should layout its content into a sizer
        sizer = self._layoutEditorWidgets()

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end _layoutWidgets()

    def _createEditorWidgets(self, parent):
        u"Creates the widgets for this window." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_createEditorWidgets") #$NON-NLS-1$
    # end _createEditorWidgets()

    def _populateEditorWidgets(self):
        pass
    # end _populateEditorWidgets()

    def _layoutEditorWidgets(self):
        u"Lays out the window's widgets and returns a sizer (should be implemented by subclasses)." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_layoutEditorWidgets") #$NON-NLS-1$
    # end _layoutEditorWidgets()

    def _bindWidgetEvents(self):
        u"Binds widget events for this window." #$NON-NLS-1$
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        u"Sets the initial user focus for the window." #$NON-NLS-1$
    # end _setInitialFocus()

    def setDirty(self, dirty):
        if self.dirty != dirty:
            self.dirty = dirty
            self._fireDirtyEvent()
    # end setDirty()

    def isDirty(self):
        return self.dirty
    # end isDirty()

    def _fireDirtyEvent(self):
        event = ZEditorDirtyEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireDirtyEvent();

    def _fireMenuBarChangedEvent(self):
        event = ZEditorMenuBarChangedEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireMenuBarChangedEvent();

    def _fireToolBarChangedEvent(self):
        event = ZEditorToolBarChangedEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireToolBarChangedEvent();

    def _fireStatusBarChangedEvent(self):
        event = ZEditorStatusBarChangedEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireStatusBarChangedEvent();

    def _fireCloseEvent(self):
        event = ZEditorCloseEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireCloseEvent()

    def _fireTitleChangedEvent(self):
        event = ZEditorTitleChangedEvent(self, self.getTitle())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireTitleChangedEvent()

# end ZEditor
