from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.events.editcontrolevents import IZEditControlEvents
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOLBAR_RESIZE
from zoundry.appframework.ui.util.colorutil import getDefaultDialogBackgroundColor
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarEventHandler
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowNotYetImplementedMessage
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.constants import IZBlogAppAcceleratorIds
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditorToolBarActionContext
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertImageAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertImgTagAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertLinkAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSpellCheckAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogRichTextFormatAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZFocusOnTagwordsAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZFocusOnTitleAction
from zoundry.blogapp.ui.editors.blogeditorctrls.blogposteditcontrol import IZBlogPostEditControl
from zoundry.blogapp.ui.editors.blogeditorctrls.metadata import ZBlogPostMetaDataWidget
from zoundry.blogapp.ui.menus.blogeditor.blogcontenteditorcontextmenumodel import ZBlogContentEditorContextMenuModel
from zoundry.blogapp.ui.menus.blogeditor.blogeditortoolbarmodel import ZBlogContentEditorToolbarModel
import wx

# ------------------------------------------------------------------------------
# Interface that blog content editor controls must implement.
# ------------------------------------------------------------------------------
class IZBlogContentEditorControl:

    def refreshUI(self):
        u"""refreshUI() -> void
        Updates the UI as well editor content based on the model data
        """ #$NON-NLS-1$
    # end refreshUI()

    def updateModel(self):
        u"""updateModel() -> void
        Updates the model data (title, xhtml document etc) from the UI controls.
        """ #$NON-NLS-1$
    # end updateModel()

    def modelSaved(self):
        u"""modelSaved() -> void
        Invoked by the editor framework when the model data has been persisted.
        """ #$NON-NLS-1$
    # end modelSaved()

# end IZBlogContentEditorControl


# ------------------------------------------------------------------------------
# Implements the accelerator table for the blog post content editor.
# ------------------------------------------------------------------------------
class ZBlogPostContentEditorAcceleratorTable(ZAcceleratorTable):

    def __init__(self, context):
        self.context = context
        ZAcceleratorTable.__init__(self, IZBlogAppAcceleratorIds.ZID_BLOG_POST_EDITOR_CONTENT_ACCEL)
    # end __init__()

    def _createActionContext(self):
        return self.context
    # end _createActionContext()

    def _loadAdditionalEntries(self):
        return [
            # Bold, Italic, Underline, Strike
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'B'), ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_BOLD)), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'I'), ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ITALIC)), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'U'), ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_UNDERLINE)), #$NON-NLS-1$
            # create link
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'L'), ZBlogPostInsertLinkAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'K'), ZBlogPostInsertLinkAction()), #$NON-NLS-1$
            # insert image
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'M'), ZBlogPostInsertImageAction()), #$NON-NLS-1$,
            ZAcceleratorEntry(wx.ACCEL_CTRL + wx.ACCEL_SHIFT, ord(u'M'), ZBlogPostInsertImgTagAction()), #$NON-NLS-1$,
            # spell check
            ZAcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F7, ZBlogPostSpellCheckAction()),
            # Go to Title
            ZAcceleratorEntry(wx.ACCEL_ALT, ord(u'T'), ZFocusOnTitleAction()), #$NON-NLS-1$
            # Go to Tagwords
            ZAcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_TAB, ZFocusOnTagwordsAction()), #$NON-NLS-1$
        ]
    # end _loadAdditionalEntries()

# end ZBlogPostContentEditorAcceleratorTable


# ------------------------------------------------------------------------------
# This is the base class of the  blog post content area editor.
# Concrete implementations are WsyiWyg and XhtmlText content editors
# ------------------------------------------------------------------------------
class ZBlogPostContentEditorBase(wx.Panel, IZBlogContentEditorControl):

    def __init__(self, parentWindow, zblogPostEditor, zblogPostEditorModel):
        self.zblogPostEditor = zblogPostEditor
        self.zblogPostEditorModel = zblogPostEditorModel
        self.editor = None
        self.metaDataWidget = None
        self.contentEditCtrl = None
        # dirty: internally keep track if the editor (mshtml/scintilla) content has been modified.
        self.contentModified = False
        wx.Panel.__init__(self, parentWindow, wx.ID_ANY)
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        if self._getContentEditControl():
            self._bindContentEditCtrlEvents()
    # end __init__()

    def focusOnContent(self):
        self.contentEditCtrl.SetFocus()
    # end focusOnContent()

    def getMetaDataWidget(self):
        return self.metaDataWidget
    # end getMetaDataWidget()

    def _getModel(self):
        return self.zblogPostEditorModel
    # end _getModel

    def _getContentEditControl(self):
        return self.contentEditCtrl
    # end _getContentEditControl

    def _createWidgets(self):
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.metaDataWidget = ZBlogPostMetaDataWidget(self, self._getModel().getMetaDataModel() )
        self.metaDataWidget.SetBackgroundColour(getDefaultDialogBackgroundColor())
        self.contentEditCtrl = self._createContentEditCtrl(self)
        # Note: toolbar must be created only after the contentEditCtrl has been created (so that edit control capabilities can be determined)
        self.toolBar = self._createToolBar()
        self.tbStaticLine = wx.StaticLine(self, wx.ID_ANY)

        self.acceleratorTable = ZBlogPostContentEditorAcceleratorTable(ZBlogPostEditorToolBarActionContext(self))
        self.contentEditCtrl.SetAcceleratorTable(self.acceleratorTable)
    # end _createWidgets()

    def _createContentEditCtrl(self, parent):
        # sublcasses must create concrete IZBlogPostEditControl impl.
        raise ZAbstractMethodCalledException(self.__class__.__name__, u"_createContentEditCtrl") #$NON-NLS-1$
    # end _createContentEditCtrl()

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.metaDataWidget, 0, wx.EXPAND)
        self.sizer.Add(self.toolBar, 0, wx.EXPAND)
        self.sizer.Add(self.tbStaticLine, 0, wx.EXPAND)
        self.sizer.Add(self.contentEditCtrl, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_TOOLBAR_RESIZE, self.onToolBarResize, self.toolBar)
        wx.EVT_NAVIGATION_KEY(self.metaDataWidget, self.onMetaDataKeyboardNavigation)
        self.acceleratorTable.bindTo(self)
    # end _bindWidgetEvents()

    def _bindContentEditCtrlEvents(self):
        self.Bind(IZEditControlEvents.ZEVT_UPDATE_UI, self.onUpdateUI, self._getContentEditControl())
        self.Bind(IZEditControlEvents.ZEVT_SELECTION_CHANGE, self.onSelectionChange, self._getContentEditControl())
        self.Bind(IZEditControlEvents.ZEVT_CONTEXT_MENU, self.onContextMenu, self._getContentEditControl())
        self.Bind(IZEditControlEvents.ZEVT_CONTENT_MODIFIED, self.onContentModified, self._getContentEditControl())
    # end _bindContentEditCtrlEvents()

    def _createToolBar(self):
        self.toolBarModel = self._createToolBarModel()
        self.toolBarContext = ZBlogPostEditorToolBarActionContext(self)
        contentProvider = ZModelBasedToolBarContentProvider(self.toolBarModel, self.toolBarContext)
        eventHandler = ZModelBasedToolBarEventHandler(self.toolBarModel, self.toolBarContext)
        return ZToolBar(contentProvider, eventHandler, self)
    # end _createToolBar()

    def _createToolBarModel(self):
        toolbarModel = ZBlogContentEditorToolbarModel()
        return toolbarModel
    # end _createToolBarModel()

    def _isContentModified(self):
        return self.contentModified
    #end _isContentModified()

    def _setContentModified(self, modified):
        self.contentModified = modified

    def onUpdateUI(self, event): #@UnusedVariable
        self.zblogPostEditor._fireUpdateMenu()        
        self.toolBar.refresh()
        self._updateCaretPostionUI()
    # end onUIUpdate()
    
    def _updateCaretPostionUI(self):
        (row, col) = self._getContentEditControl().getCaretPosition()
        text = u"" #$NON-NLS-1$
        if row != -1 and col != -1:
            text = u"%d : %d" % (row, col) #$NON-NLS-1$
        self.zblogPostEditor.statusBarModel.setPaneText(u"rowcol", text) #$NON-NLS-1$
        self.zblogPostEditor._fireStatusBarChangedEvent()
    # end _updateCaretPostionUI()

    def onContentModified(self, event): #@UnusedVariable
        # This is the event handler for mshtml/stc content modified/dirty indicator.
        # Notify the blog post editor just one time
        if not self._isContentModified():
            self.zblogPostEditor.setDirty(True)
        self._setContentModified(True)
    # end onContentModified()

    def onSelectionChange(self, event): #@UnusedVariable
        pass
    # end onSelectionChange()

    def onContextMenu(self, event):
        linkCtx = self.getLinkContext()
        imageCtx = self.getImageContext()
        tableCtx = self.getTableContext()
        removeExtMarker = False
        if self.hasCapability(IZBlogPostEditControl.ZCAPABILITY_EXTENDED_ENTRY_MARKER) \
            and self._getContentEditControl().canRemoveExtendedEntryMarker():
            removeExtMarker = True

        menuModel = ZBlogContentEditorContextMenuModel()
        menuModel.initialize(linkCtx, imageCtx, tableCtx, removeExtMarker)

        menuContext = self.zblogPostEditor.getMenuActionContext()
        contentProvider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        menu = ZMenu(event.getParentWindow(), menuModel.getRootNode(), contentProvider, eventHandler)
        try:
            event.getParentWindow().PopupMenu(menu, event.getXYPoint())
        except Exception, e:
            getLoggerService().exception(e)
        menu.Destroy()
    # end onContextMenu()

    def refreshUI(self):
        document = self.zblogPostEditorModel.getDocument()
        # refresh title, tags, blog data etc.
        self.metaDataWidget.refreshUI()
        # get xhtml content and set it in the edit control.
        if document.getContent() is not None:
            xhtmlDoc = document.getContent().getXhtmlDocument()
            self._getContentEditControl().setXhtmlDocument(xhtmlDoc)
    # end refreshUI()

    def modelSaved(self):
        # model was saved to data store.
        # Clear dirty flag so that onContentModified() handler can set the flag in the model
        self._setContentModified(False)
        # Clear flags (such as 'content modified') in the content editor (eg. ZMSHTMLBlogPostEditControl via ZBlogPostWysiwygContentEditor)
        self._getContentEditControl().clearState()
        # Refresh widget UI.
        self.metaDataWidget.refreshUI()
    # end modelSaved()

    def updateModel(self):
        document = self.zblogPostEditorModel.getDocument()
        # Flush title, tags, blog meta data etc. from UI controls to zmetadata model.
        self.metaDataWidget.updateModel()
        #  Next copy title, tags etc. from meta data model to the document.
        self.zblogPostEditorModel.getMetaDataModel().updateDocument(document)

        # Finally, get the Xhtml content from the editor and set it in the document
        xhtmlDoc = self._getContentEditControl().getXhtmlDocument()
        xhtmlContent = ZXhtmlContent()
        xhtmlContent.setXhtmlDocument(xhtmlDoc)
        document.setContent(xhtmlContent)
    # end updateModel()

    def onTool(self, ctx): #@UnusedVariable
        ZShowNotYetImplementedMessage(self)
    # end onTool()

    def onToolBarResize(self, event):
        self.Layout()
        event.Skip()
    # end onToolBarResize()

    # This is a bit hack-y - when tabbing from the tagwords text control, in
    # the forward direction, the focus does not get properly set to the
    # content editor.  I'm not really sure where it goes, actually.  This
    # method will listen for keyboard nav events in the meta data widget and
    # re-route a forward direction Tab event so that it sets the focus
    # explicitly on the content editor.
    def onMetaDataKeyboardNavigation(self, event):
        focusWidget = self.metaDataWidget.FindFocus()
        if event.GetDirection() and event.IsFromTab() and focusWidget == self.metaDataWidget.tagwordsText:
            self.focusOnContent()
        else:
            event.Skip()
    # end onMetaDataKeyboardNavigation()

    def hasCapability(self, capabilityId):
        return self._getContentEditControl().getCapabilities().hasCapability(capabilityId)
    # end hasCapability()

    def canCut(self):
        return self._getContentEditControl().canCut()
    # end canCut()

    def cut(self):
        self._getContentEditControl().cut()
    # end cut()

    def canCopy(self):
        return self._getContentEditControl().canCopy()
    # end canCopy()

    def copy(self):
        self._getContentEditControl().copy()
    # end copy()

    def canPaste(self, xhtmlFormat):
        if xhtmlFormat:
            return self._getContentEditControl().canPasteXhtml()
        else:
            return self._getContentEditControl().canPaste()
    # end canPaste()

    def paste(self, xhtmlFormat):
        if xhtmlFormat:
            self._getContentEditControl().pasteXhtml()
        else:
            self._getContentEditControl().paste()
    # end paste()

    def canInsertXhtml(self):
        return self._getContentEditControl().canInsertXhtml()
    # end canInsertXhtml

    def insertXhtml(self, xhtmlString): #@UnusedVariable
        self._getContentEditControl().insertXhtml(xhtmlString)
    # end insertXhtml

    def canSelectAll(self):
        return self._getContentEditControl().canSelectAll()
    # end canSelectAll()

    def selectAll(self):
        self._getContentEditControl().selectAll()
    # end selectAll()

    def canUndo(self):
        return self._getContentEditControl().canUndo()
    # end canUndo()

    def undo(self):
        self._getContentEditControl().undo()
    # end undo()

    def canRedo(self):
        return self._getContentEditControl().canRedo()
    # end canRedo()

    def redo(self):
        self._getContentEditControl().redo()
    # end redo()

    # ---------------------------------------------
    # RichTextEdit formatting commands. Eg. Bold, Italic.
    # ---------------------------------------------

    def isFormattingEnabled(self, capabilityId):
        return self._getContentEditControl().isFormattingEnabled(capabilityId)
    # end isFormattingEnabled()

    def getFormattingState(self, capabilityId):
        return self._getContentEditControl().getFormattingState(capabilityId)
    # end getFormattingState()

    def applyFormatting(self, capabilityId, customData):
        self._getContentEditControl().applyFormatting(capabilityId, customData)
    # end applyFormatting()

    def getLinkContext(self):
        u"""getLinkContext()  -> IZXHTMLEditControlLinkContext
        Returns link creation and edit context if available or None otherwise.""" #$NON-NLS-1$
        return self._getContentEditControl().getLinkContext()
    # end getLinkContext

    def getImageContext(self):
        u"""getImageContext()  -> IZXHTMLEditControlImageContext
        Returns image creation and edit context if available or None otherwise.""" #$NON-NLS-1$
        return self._getContentEditControl().getImageContext()
    # end getImageContext

    def getTableContext(self):
        u"""getTableContext()  -> IZXHTMLEditControlTableContext
        Returns table insertion and edit context if available or None otherwise.""" #$NON-NLS-1$
        return self._getContentEditControl().getTableContext()
    # end getTableContext

    def getCurrentSelection(self):
        u"""getCurrentSelection() -> IZXHTMLEditControlSelection
        """ #$NON-NLS-1$
        return self._getContentEditControl().getCurrentSelection()
    # end getCurrentSelection()

    # ---------------------------------------------
    # Extended entry
    # ---------------------------------------------

    def insertExtendedEntryMarker(self):
        self._getContentEditControl().insertExtendedEntryMarker()
    # end insertExtendedEntryMarker()

    def removeExtendedEntryMarker(self):
        self._getContentEditControl().removeExtendedEntryMarker()
    # removeExtendedEntryMarker()

    # ---------------------------------------------
    # Spellcheck
    # ---------------------------------------------
    def createSpellCheckContext(self):
        u"""createSpellCheckContext() -> IZEditControlSpellCheckContext
        Returns IZEditControlSpellCheckContext if spellcheck is supported or None otherwise.
        """ #$NON-NLS-1$
        return self._getContentEditControl().createSpellCheckContext()
    # end createSpellCheckContext()

    # ---------------------------------------------
    # Find and Find/Replace
    # ---------------------------------------------
    def createFindReplaceContext(self):
        u"""createFindReplaceContext() -> IZEditControlFindReplaceTextContext
        Returns IZEditControlFindReplaceTextContext if find/replace is supported or None otherwise.
        """ #$NON-NLS-1$
        return self._getContentEditControl().createFindReplaceContext()
    # end createFindReplaceContext()
    
    # ---------------------------------------------
    # Validate and Tidy
    # ---------------------------------------------
    def schemaValidate(self):
        self._getContentEditControl().schemaValidate()
    # end schemaValidate
    
    def clearValidation(self):
        self._getContentEditControl().clearValidation()
    # end clearValidation    
    
    def runTidy(self):
        self._getContentEditControl().runTidy()
    # end runTidy      
    

# end ZBlogPostContentEditorBase