from zoundry.appframework.services.dnd.dndsource import ZUrlDnDSource
from zoundry.appframework.services.dnd.dndsource import ZCompositeDnDSource
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.actions.toolbaraction import ZDropDownToolBarAction
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarActionContext
from zoundry.appframework.ui.util.clipboardutil import setClipboardText
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlTableContext
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuModel
from zoundry.appframework.ui.widgets.dialogs.progress import ZAbstractRunnableProgress
from zoundry.appframework.ui.widgets.dialogs.progress import ZShowProgressDialog
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.blogeditorctrls.blogposteditcontrol import IZBlogPostEditControl
from zoundry.blogapp.ui.util.blogutil import getBlogFromBlogInfo
from zoundry.blogapp.ui.util.editorutil import ZCssStyleUiUtil
from zoundry.blogapp.ui.util.editorutil import ZFindReplaceUiUtil
from zoundry.blogapp.ui.util.editorutil import ZImageUiUtil
from zoundry.blogapp.ui.util.editorutil import ZLinkUiUtil
from zoundry.blogapp.ui.util.editorutil import ZSpellCheckUiUtil
from zoundry.blogapp.ui.util.editorutil import ZTableUiUtil
from zoundry.blogapp.ui.util.publisherutil import ZPublishEntryUiUtil

# ------------------------------------------------------------------------------
# The action context shared by both the toolbar and menu items.
# ------------------------------------------------------------------------------
class IZBlogPostEditorActionContext(IZActionContext):

    def getParentWindow(self):
        u"Returns the wx Window that is a parent the control." #$NON-NLS-1$
    # end getParentWindow()

    def getEditor(self):
        u"""getEditor() -> ZBlogPostEditor
        Returns the editor.""" #$NON-NLS-1$
    # end getEditor()

# end IZBlogPostEditorActionContext


# ------------------------------------------------------------------------------
# The action context passed to blog post editor's menu actions.
# ------------------------------------------------------------------------------
class ZBlogPostEditorMenuActionContext(ZMenuActionContext, IZBlogPostEditorActionContext):

    def __init__(self, editor):
        self.editor = editor
        ZMenuActionContext.__init__(self, editor)
    # end __init_()

    def getEditor(self):
        return self.editor
    # end getEditor()

# end ZBlogPostEditorMenuActionContext


# ------------------------------------------------------------------------------
# The action context passed to blog post editor's toolbar.
# ------------------------------------------------------------------------------
class ZBlogPostEditorToolBarActionContext(ZToolBarActionContext, IZBlogPostEditorActionContext):

    def __init__(self, editor):
        self.editor = editor
        ZToolBarActionContext.__init__(self, editor)
    # end __init_()

    def getEditor(self):
        return self.editor
    # end getEditor()

# end ZBlogPostEditorToolBarActionContext


# ------------------------------------------------------------------------------
# The base action classes for editor related operations - shared by both, the
# toolbar and menu items
# ------------------------------------------------------------------------------
class ZBlogPostEditorMenuItemAndToolbarActionBase(ZMenuAction, ZDropDownToolBarAction):

    def isVisible(self, context):
        # used by menu item
        return ZMenuAction.isVisible(self, context)
    # end isVisible()

    def isEnabled(self, context): #@UnusedVariable
        # common method for menu and toolbar
        return True
    # end isEnabled()

    def isBold(self, context):
        # used by menu item
        return ZMenuAction.isBold(self, context)
    # end isBold()

    def isChecked(self, context):
        # used by menu item
        return ZMenuAction.isChecked(self, context)
    # end isBold()

    def getParameters(self):
        # used by menu item
        return ZMenuAction.getParameters(self)
    # end getParameters()

    def setParameters(self, izParameters):
        ZMenuAction.setParameters(self, izParameters)
    # end setParameters()

    def runCheckAction(self, actionContext, checked): #@UnusedVariable
        # menu item action
        self.runAction(actionContext)
    # end runCheckAction()

    def isDepressed(self, context): #@UnusedVariable
        # used by toolbar
        return False
    # end isDepressed()

    def runToggleAction(self, toolBarActionContext, depressed): #@UnusedVariable
        self.runAction(toolBarActionContext)
    # end runToggleAction()

    def runDropDownAction(self, toolBarActionContext, toolPosition, toolSize):
        ZDropDownToolBarAction.runDropDownAction(self, toolBarActionContext, toolPosition, toolSize)
    # end runToggleAction()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        # runAction common to toolbar and to menu items
        pass
    # end runAction()

# end ZBlogPostEditorMenuItemAndToolbarActionBase()


# ------------------------------------------------------------------------------
# Not yet implemented action.
# ------------------------------------------------------------------------------
class ZBlogNotYetImplementedAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, actionContext): #@UnusedVariable
        return False
    # end isEnabled()

# end ZBlogNotYetImplementedAction()


# ------------------------------------------------------------------------------
# This is the action implementation for the blog post editor's "Save" item.
# ------------------------------------------------------------------------------
class ZBlogPostSaveAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, actionContext):
        return actionContext.getEditor().isDirty()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().save()
    # end runAction()

# end ZBlogPostSaveAction


# ------------------------------------------------------------------------------
# The action impl for the blog post editor's 'Cut' item.
# ------------------------------------------------------------------------------
class ZBlogPostCutAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_CUT) \
                and context.getEditor().getActiveContentEditor().canCut()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().cut()
    # end runAction()

# end ZBlogPostCutAction


# ------------------------------------------------------------------------------
# The action impl for the blog post editor's 'Copy'  item.
# ------------------------------------------------------------------------------
class ZBlogPostCopyAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_COPY) \
                and context.getEditor().getActiveContentEditor().canCopy()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().copy()
    # end runAction()

# end ZBlogPostCopyAction


# ------------------------------------------------------------------------------
# The action impl for the blog post editor's 'Paste' item.
# ------------------------------------------------------------------------------
class ZBlogPostPasteAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_PASTE) \
                and context.getEditor().getActiveContentEditor().canPaste(False)
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().paste(False)
    # end runAction()

# end ZBlogPostPasteAction


# ------------------------------------------------------------------------------
# The action impl for the blog post editor's 'Paste Xhtml' item.
# ------------------------------------------------------------------------------
class ZBlogPostPasteXhtmlAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_PASTE_HTML) \
                and context.getEditor().getActiveContentEditor().canPaste(True)
    # end isEnabled()

    def isDepressed(self, izblogPostEditorActionContext): #@UnusedVariable
        # normally used by toolbar buttons.
        return False
    # end isDepressed()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().paste(True)
    # end runAction()

# end ZBlogPostPasteXhtmlAction


# ------------------------------------------------------------------------------
# Select All action
# ------------------------------------------------------------------------------
class ZBlogPostSelectAllAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_SELECT_ALL) \
                and context.getEditor().getActiveContentEditor().canSelectAll()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().selectAll()
    # end runAction()

# end ZBlogPostSelectAllAction


# ------------------------------------------------------------------------------
# Undo action
# ------------------------------------------------------------------------------
class ZBlogPostUndoAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_UNDO) \
                and context.getEditor().getActiveContentEditor().canUndo()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().undo()
    # end runAction()

# end ZBlogPostUndoAction


# ------------------------------------------------------------------------------
# Undo action
# ------------------------------------------------------------------------------
class ZBlogPostRedoAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        return context.getEditor().hasCapability(IZEditControl.ZCAPABILITY_REDO) \
                and context.getEditor().getActiveContentEditor().canRedo()
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().getActiveContentEditor().redo()
    # end runAction()

# end ZBlogPostRedoAction


# ------------------------------------------------------------------------------
# Publish action
# ------------------------------------------------------------------------------
class ZBlogPostPublishAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context):
        editor = context.getEditor()
        document = editor.getDocument()
        return document.isPublishable()
    # end isEnabled()

    def runAction(self, actionContext):
        window = actionContext.getParentWindow()
        editor = actionContext.getEditor()
        # save current document
        editor.save()
        zblog = None
        zblogDocument = editor.getDocument()
        metaDataList = zblogDocument.getPubMetaDataList()
        ZPublishEntryUiUtil().publishPost(window, zblog, zblogDocument, metaDataList)
    # end runAction()

# end ZBlogPostPublishAction


# ------------------------------------------------------------------------------
# View (online) action
# ------------------------------------------------------------------------------
class ZBlogPostViewOnlineAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def __init__(self, blogId = None):
        self.blogId = blogId
    # end __init__()

    def isEnabled(self, context):
        return self._findFirstBlogId(context) is not None
    # end isEnabled()

    def runAction(self, actionContext):
        blogId = self.blogId
        if blogId is None:
            blogId = self._findFirstBlogId(actionContext)
        if blogId is None:
            return

        url = None

        editor = actionContext.getEditor()
        zblogDocument = editor.getDocument()
        blogInfos = zblogDocument.getBlogInfoList()
        for blogInfo in blogInfos:
            if blogInfo.getBlogId() == blogId:
                pubInfo = blogInfo.getPublishInfo()
                url = pubInfo.getUrl()

        if url is not None:
            getOSUtil().openUrlInBrowser(url)
    # end runAction()

    def _findFirstBlogId(self, actionContext):
        editor = actionContext.getEditor()
        zblogDocument = editor.getDocument()
        blogInfos = zblogDocument.getBlogInfoList()
        if blogInfos:
            return blogInfos[0].getBlogId()
        return None
    # end _findFirstBlogId()

    def _createMenuModel(self, actionContext): #@UnusedVariable
        menuModel = ZMenuModel()
        editor = actionContext.getEditor()
        zblogDocument = editor.getDocument()
        blogInfos = zblogDocument.getBlogInfoList()
        for blogInfo in blogInfos:
            blog = getBlogFromBlogInfo(blogInfo)
            menuModel.addMenuItemWithAction(blog.getName(), 0, ZBlogPostViewOnlineAction(blog.getId()))
        return menuModel
    # end _createMenuModel()

# end ZBlogPostViewOnlineAction

# ------------------------------------------------------------------------------
# Base action class for links
# ------------------------------------------------------------------------------
class ZBlogPostLinkActionBase(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def _getLinkContext(self, actionContext):
        editor = actionContext.getEditor()
        # Get IZXHTMLEditControlLinkContext instance of the editor.
        linkContext = None
        if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
            linkContext = editor.getLinkContext()
        elif isinstance(actionContext, ZBlogPostEditorMenuActionContext):
            linkContext = editor.getActiveContentEditor().getLinkContext()
        return linkContext
    # end _getLinkContext

    def isEnabled(self, context):
        editor = context.getEditor()
        if not self._hasCapabilities(editor):
            return False
        # Get IZXHTMLEditControlLinkContext instance of the editor.
        linkContext = self._getLinkContext(context)
        return linkContext is not None and self._isEnabled(linkContext)
    # end isEnabled()

    def _hasCapabilities(self, editor):
        return editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_LINK)
    # end _hasCapabilities()

    def _isEnabled(self, linkContext):
        return linkContext.canCreateLink()
    # end _isEnabled()

# end ZBlogPostLinkActionBase

# ------------------------------------------------------------------------------
# base class for an editable link action
# ------------------------------------------------------------------------------
class ZBlogPostEditableLinkActionBase(ZBlogPostLinkActionBase):

    def _hasCapabilities(self, editor):
        return editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_EDIT_LINK)
    # end _hasCapabilities()

    def _isEnabled(self, linkContext):
        return linkContext.canEditLink()
    # end _isEnabled()

    def _getLinkUrl(self, context):
        url = None
        linkContext = self._getLinkContext(context)
        if linkContext and linkContext.canEditLink():
            attrs = linkContext.getLinkAttributes()
            if u"href" in attrs: #$NON-NLS-1$
                url = getNoneString(attrs[u"href"]) #$NON-NLS-1$
        return url
    # end _getLinkUrl()

# end ZBlogPostEditableLinkActionBase()

# ------------------------------------------------------------------------------
# Toolbar - Insert Link action.
# ------------------------------------------------------------------------------
class ZBlogPostToolbarLinksAction(ZBlogPostLinkActionBase):

    def __init__(self, menuModel):
        self.menuModel = menuModel
    # end __init__()

    def _hasCapabilities(self, editor):
        if not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_LINK) \
            and not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_EDIT_LINK):
            return False
        else:
            return True
    # end _hasCapabilities()

    def _isEnabled(self, linkContext):
        return linkContext.canCreateLink() or linkContext.canEditLink()
    # end _isEnabled()

    def runAction(self, actionContext):
        linkContext = self._getLinkContext(actionContext)
        ZLinkUiUtil().editLink(actionContext.getParentWindow(), linkContext)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()
# end ZBlogPostToolbarLinksAction()

# ------------------------------------------------------------------------------
# Insert Link action.
# ------------------------------------------------------------------------------
class ZBlogPostInsertLinkAction(ZBlogPostLinkActionBase):

    def runAction(self, actionContext):
        linkContext = self._getLinkContext(actionContext)
        ZLinkUiUtil().editLink(actionContext.getParentWindow(), linkContext)
    # end runAction()
# end ZBlogPostInsertLinkAction()

# ------------------------------------------------------------------------------
# Editor Context menu action for editing a link
# ------------------------------------------------------------------------------
class ZBlogPostEditLinkAction(ZBlogPostEditableLinkActionBase):

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        linkContext = self._getLinkContext(izblogPostEditorActionContext)
        ZLinkUiUtil().editLink(izblogPostEditorActionContext.getParentWindow(), linkContext)
    # end runAction()
# end ZBlogPostEditLinkAction

# ------------------------------------------------------------------------------
# Copy link location
# ------------------------------------------------------------------------------
class ZBlogPostCopyLinkLocationAction(ZBlogPostEditableLinkActionBase):

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        url = self._getLinkUrl(izblogPostEditorActionContext)
        if url:
            setClipboardText(url)
    # end runAction()
# end ZBlogPostCopyLinkLocationAction

# ------------------------------------------------------------------------------
# Create link from with out a ui.
# ------------------------------------------------------------------------------
class ZBlogPostCreateLinkNoUiAction(ZBlogPostLinkActionBase):

    def __init__(self, url, rel, ):
        self.url = url
        self.rel = rel
    # end __init__()

    def _createLinkUrl(self, linkText): #@UnusedVariable
        return self.url
    # end _getLinkUrl()

    def _getLinkRel(self):
        return self.rel
    # end _getLinkRel()

    def _getSelection(self, actionContext):
        # returns instance of IZXHTMLEditControlSelection
        editor = actionContext.getEditor()
        # Get IZXHTMLEditControlLinkContext instance of the editor.
        selection = None
        if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
            selection = editor.getCurrentSelection()
        elif isinstance(actionContext, ZBlogPostEditorMenuActionContext):
            selection = editor.getActiveContentEditor().getCurrentSelection()
        return selection
    # end _getSelection

    def runAction(self, actionContext):
        linkContext = self._getLinkContext(actionContext)
        selection = self._getSelection(actionContext)
        text = None
        if selection and not selection.isEmpty():
            text = selection.getSelectedText()
        url = self._createLinkUrl(text)
        attrs = {u"href" :url} #$NON-NLS-1$
        if ( getNoneString(self._getLinkRel()) ):
            attrs[u"rel"] = self._getLinkRel() #$NON-NLS-1$
        linkContext.setLinkAttributes(attrs)
    # end runAction()
# end ZBlogPostCreateLinkNoUiAction()

# ------------------------------------------------------------------------------
# Create link from formatter IZLinkFormatter.
# ------------------------------------------------------------------------------
class ZBlogPostCreateLinkFromFormatterAction(ZBlogPostCreateLinkNoUiAction):

    def __init__(self, linkFormatter):
        self.linkFormatter = linkFormatter
        ZBlogPostCreateLinkNoUiAction.__init__(self, None, None)
    # end __init__()

    def _createLinkUrl(self, linkText): #@UnusedVariable
        return self.linkFormatter.formatUrl(linkText)
    # end _getLinkUrl()

    def _getLinkRel(self):
        return self.linkFormatter.getRel()
    # end _getLinkRel()

# end ZBlogPostInsertLinkAction()


# ------------------------------------------------------------------------------
# Base class for image actions
# ------------------------------------------------------------------------------
class ZBlogPostImageActionBase(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def _getImageContext(self, actionContext):
        editor = actionContext.getEditor()
        # Get IZXHTMLEditControlLinkContext instance of the editor.
        imageContext = None
        if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
            imageContext = editor.getImageContext()
        elif isinstance(actionContext, ZBlogPostEditorMenuActionContext):
            imageContext = editor.getActiveContentEditor().getImageContext()
        return imageContext
    # end _getImageContext

    def isEnabled(self, context):
        editor = context.getEditor()
        # Editor is ZBlogPostWysiwygContentEditor
        if not self._hasCapabilities(editor):
            return False
        # Get IZXHTMLEditControlImageContext instance of the editor.
        imageContext = self._getImageContext(context)
        return imageContext is not None and self._isEnabled(imageContext)
    # end isEnabled()

    def _hasCapabilities(self, editor):
        if not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_IMAGE):
            return False
        else:
            return True
    # end _hasCapabilities()

    def _isEnabled(self, imageContext):
        return  imageContext.canCreateImage()
    # end _isEnabled()
# end  ZBlogPostImageActionBase

# ------------------------------------------------------------------------------
# Base action handler for img tags
# ------------------------------------------------------------------------------
class ZBlogPostEditableImageActionBase(ZBlogPostImageActionBase):

    def _hasCapabilities(self, editor):
        return editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_EDIT_IMAGE)
    # end _hasCapabilities()

    def _isEnabled(self, imageContext):
        return  imageContext.canEditImage()
    # end _isEnabled()

    def _getImageUrl(self, context):
        url = None
        imageContext = self._getImageContext(context)
        if imageContext and imageContext.canEditImage():
            attrs = imageContext.getImageAttributes()
            if attrs.has_key(u"src"): #$NON-NLS-1$
                url = getNoneString(attrs[u"src"]) #$NON-NLS-1$
        return url
    # end _getImageUrl
# end ZBlogPostEditableImageActionBase

# ------------------------------------------------------------------------------
# Insert/edit Image action
# ------------------------------------------------------------------------------
class ZBlogPostInsertImageAction(ZBlogPostImageActionBase):

    def runAction(self, actionContext):
        imageContext = self._getImageContext(actionContext)
        if imageContext.canEditImage():
            ZImageUiUtil().editImage(actionContext.getParentWindow(), imageContext)
        else:
            ZImageUiUtil().insertImageFile(actionContext.getParentWindow(), imageContext)
    # end runAction()

# end ZBlogPostInsertImageAction()

# ------------------------------------------------------------------------------
# Insert Image action (which shows drop down list for File or Tag
# ------------------------------------------------------------------------------
class ZBlogPostToolbarImagesAction(ZBlogPostInsertImageAction):

    def __init__(self, menuModel):
        self.menuModel = menuModel
    # end __init__()

    def _hasCapabilities(self, editor):
        if not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_IMAGE) \
            and not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_EDIT_IMAGE):
            return False
        else:
            return True
    # end _hasCapabilities()

    def _isEnabled(self, imageContext):
        return imageContext.canCreateImage() or imageContext.canEditImage()
    # end _isEnabled()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()

# end ZBlogPostToolbarImagesAction()

# ------------------------------------------------------------------------------
# Insert Img Tag action
# ------------------------------------------------------------------------------
class ZBlogPostInsertImgTagAction(ZBlogPostImageActionBase):

    def runAction(self, actionContext):
        imageContext = self._getImageContext(actionContext)
        ZImageUiUtil().insertImageTag(actionContext.getParentWindow(), imageContext)
    # end runAction()

# end ZBlogPostInsertImgTagAction

# ------------------------------------------------------------------------------
# Editor Context menu action for editing an image
# ------------------------------------------------------------------------------
class ZBlogPostEditImageAction(ZBlogPostEditableImageActionBase):

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        imageContext = self._getImageContext(izblogPostEditorActionContext)
        ZImageUiUtil().editImage(izblogPostEditorActionContext.getParentWindow(), imageContext)
    # end runAction()

# end ZBlogPostEditImageAction

# ------------------------------------------------------------------------------
# Copy image src location to clipboard
# ------------------------------------------------------------------------------
class ZBlogPostCopyImageLocationAction(ZBlogPostEditableImageActionBase):

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        url = self._getImageUrl(izblogPostEditorActionContext)
        if url:
            setClipboardText(url)
    # end runAction()
# end ZBlogPostCopyImageLocationAction

# ------------------------------------------------------------------------------
# Toolbar - Insert table action (which shows drop down list for table insertation and manipulation
# ------------------------------------------------------------------------------
class ZBlogPostInsertTableAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def __init__(self, menuModel):
        self.menuModel = menuModel
    # end __init__()

    def isEnabled(self, context):
        editor = context.getEditor()
        # Editor is ZBlogPostWysiwygContentEditor
        if not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_TABLE) \
            and not editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_EDIT_TABLE):
            return False

        # Get IZXHTMLEditControlTableContext instance of the editor.
        tableContext = editor.getTableContext()
        return tableContext is not None and ( tableContext.canInsertTable() or tableContext.canEditTable() )
    # end isEnabled()

    def runAction(self, actionContext):
        if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
            tableCtx = actionContext.getEditor().getTableContext()
            if tableCtx and tableCtx.canInsertTable():
                ZTableUiUtil().insertTable(actionContext.getParentWindow(), tableCtx)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()

# end ZBlogPostInsertTableAction()

# ------------------------------------------------------------------------------
# Table manipulation commands
# ------------------------------------------------------------------------------
class ZBlogPostTableCommandsAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def __init__(self, commandId):
        self.commandId = commandId
    # end __init__()

    def isEnabled(self, context):
        tableContext = None
        if isinstance(context, ZBlogPostEditorToolBarActionContext):
            # Get IZXHTMLEditControlTableContext instance of the editor.
            tableContext = context.getEditor().getTableContext()
        elif isinstance(context, ZBlogPostEditorMenuActionContext):
            tableContext = context.getEditor().getActiveContentEditor().getTableContext()
        return tableContext is not None and tableContext.isCommandEnabled(self.commandId)
    # end isEnabled()

    def runAction(self, actionContext):
        tableCtx = None
        if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
            tableCtx = actionContext.getEditor().getTableContext()
        elif isinstance(actionContext, ZBlogPostEditorMenuActionContext):
            tableCtx = actionContext.getEditor().getActiveContentEditor().getTableContext()

        if tableCtx:
            if IZXHTMLEditControlTableContext.INSERT_TABLE == self.commandId:
                ZTableUiUtil().insertTable(actionContext.getParentWindow(), tableCtx)
            elif IZXHTMLEditControlTableContext.EDIT_TABLE_ATTRS == self.commandId:
                ZTableUiUtil().editTable(actionContext.getParentWindow(), tableCtx)
            else:
                tableCtx.execCommand(self.commandId)
    # end runAction()

# end ZBlogPostTableCommandsAction

# ------------------------------------------------------------------------------
# Content Editor Rich text formatting actions (bold, italic etc.)
# ------------------------------------------------------------------------------
class ZBlogRichTextFormatAction(ZBlogPostEditorMenuItemAndToolbarActionBase):
    #
    # Note: the ActionContext::getEditor() return the blog editor's content editor (IZBlogContentEditorControl -> wyswyg or xhtml)
    #

    def __init__(self, formattingCapabilityId):
        self.formattingCapabilityId = formattingCapabilityId
    # end __init__()

    def isEnabled(self, context):
        return context.getEditor().hasCapability(self.formattingCapabilityId) \
            and context.getEditor().isFormattingEnabled(self.formattingCapabilityId)
    # end isEnabled()

    def isDepressed(self, izblogPostEditorActionContext): #@UnusedVariable
        return izblogPostEditorActionContext.getEditor().getFormattingState(self.formattingCapabilityId)
    # end isDepressed()

    def runAction(self, actionContext):
        actionContext.getEditor().applyFormatting(self.formattingCapabilityId, None)
    # end runAction()

# end ZBlogRichTextFormatAction

# ------------------------------------------------------------------------------
# This is the action implementation for the blog post editor's "Save" item.
# ------------------------------------------------------------------------------
class ZBlogPostFontSettingsAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, actionContext):
        # get ZBlogPostWysiwygContentEditor instance from ZBlogPostEditorToolBarActionContext
        editor = actionContext.getEditor()
        # Editor is ZBlogPostWysiwygContentEditor
        if not editor.hasCapability(IZRichTextEditControl.ZCAPABILITY_FONT_NAME) \
            and not editor.hasCapability(IZRichTextEditControl.ZCAPABILITY_FONT_SIZE)\
            and not editor.hasCapability(IZRichTextEditControl.ZCAPABILITY_COLOR):
            return False
        selection = editor.getCurrentSelection()
        return selection and not selection.isEmpty()
    # end isEnabled()

    def runAction(self, actionContext):
        editor = actionContext.getEditor()
        selection = editor.getCurrentSelection()
        styleCtx = selection.getStyleContext()
        ZCssStyleUiUtil().setFontSettings(actionContext.getParentWindow(), styleCtx)
    # end runAction()
# end ZBlogPostFontSettingsAction

# ------------------------------------------------------------------------------
# Action for copy link location and copy image location to clipboard.
# ------------------------------------------------------------------------------
class ZBlogPostCopyURLContextMenuAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def __init__(self, url): #$NON-NLS-1$
        self.url = url
    # end __init__()

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        # This is a dynamic context menu action - always enabled since it appears only in link and image selection contexts.
        return True
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        setClipboardText(self.url)
    # end runAction()
# end ZBlogPostCopyURLContextMenuAction


# ------------------------------------------------------------------------------
# Action for removing a hyperlink (editor context menu)
# ------------------------------------------------------------------------------
class ZBlogPostRemoveLinkContextMenuAction(ZBlogPostEditableLinkActionBase):

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        linkContext = self._getLinkContext(izblogPostEditorActionContext)
        if linkContext is not None:
            linkContext.removeLink()
    # end runAction()

# end ZBlogPostRemoveLinkContextMenuAction


# ------------------------------------------------------------------------------
# Action for inserting a extended entry marker
# ------------------------------------------------------------------------------
class ZBlogPostInsertExtEntryMarkerContextMenuAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        return izblogPostEditorActionContext.getEditor().hasCapability(IZBlogPostEditControl.ZCAPABILITY_EXTENDED_ENTRY_MARKER)
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        izblogPostEditorActionContext.getEditor().insertExtendedEntryMarker()
    # end runAction()

# end ZBlogPostInsertExtEntryMarkerContextMenuAction


# ------------------------------------------------------------------------------
# Action for removing a extended entry marker (editor context menu)
# ------------------------------------------------------------------------------
class ZBlogPostRemoveExtEntryMarkerContextMenuAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        # This is a dynamic context menu action - always enabled since it appears only when a  extended entry marker is selected
        return True
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        izblogPostEditorActionContext.getEditor().getActiveContentEditor().removeExtendedEntryMarker()
    # end runAction()

# end ZBlogPostRemoveExtEntryMarkerContextMenuAction


# ------------------------------------------------------------------------------
# Spell check action
# ------------------------------------------------------------------------------
class ZBlogPostSpellCheckAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context): #@UnusedVariable
        return context.getEditor().hasCapability(IZTextEditControl.ZCAPABILITY_SPELLCHECK)
    # end isEnabled()

    def runAction(self, actionContext):
        # check if support (if accel shortkey is pressed which by passes the above isEnabled().
        if not actionContext.getEditor().hasCapability(IZTextEditControl.ZCAPABILITY_SPELLCHECK):
            return
        window = actionContext.getParentWindow()
        spellcheckContext = actionContext.getEditor().createSpellCheckContext()
        ZSpellCheckUiUtil().runSpellCheck(window, spellcheckContext)
    # end runAction

# end ZBlogPostSpellCheckAction


# ------------------------------------------------------------------------------
# Find/Replace action
# ------------------------------------------------------------------------------
class ZBlogPostFindReplaceAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context): #@UnusedVariable
        return context.getEditor().hasCapability(IZTextEditControl.ZCAPABILITY_FINDREPLACE)
    # end isEnabled()

    def runAction(self, actionContext):
        # check if support (if accel shortkey is pressed which by passes the above isEnabled().
        if not actionContext.getEditor().hasCapability(IZTextEditControl.ZCAPABILITY_FINDREPLACE):
            return
        window = actionContext.getParentWindow()
        # Note: main window menu item action. Editor is ZBlogPostEditor.
        findReplaceContext = actionContext.getEditor().getActiveContentEditor().createFindReplaceContext()
        ZFindReplaceUiUtil().runFindReplace(window, findReplaceContext)
    # end runAction

# end ZBlogPostFindReplaceAction


# ------------------------------------------------------------------------------
# Sets the focus on the Title.
# ------------------------------------------------------------------------------
class ZFocusOnTitleAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def runAction(self, actionContext):
        editor = actionContext.getEditor()
        mdWidget = editor.getMetaDataWidget()
        mdWidget.titleText.SetFocus()
        mdWidget.titleText.SetSelection(-1, -1)
    # end runAction

# end ZFocusOnTitleAction


# ------------------------------------------------------------------------------
# Sets the focus on the Tagwords.
# ------------------------------------------------------------------------------
class ZFocusOnTagwordsAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def runAction(self, actionContext):
        editor = actionContext.getEditor()
        mdWidget = editor.getMetaDataWidget()
        mdWidget.tagwordsText.SetFocus()
    # end runAction()

# end ZFocusOnTitleAction


# ------------------------------------------------------------------------------
# Action called when the user chooses to convert an existing video (or similar) link into an
# embed source
# ------------------------------------------------------------------------------
class ZConvertLinkToEmbedAction(ZBlogPostEditableLinkActionBase):

    def __init__(self):
        self.dndService = getApplicationModel().getService(IZBlogAppServiceIDs.DND_SERVICE_ID)
    # end __init__

    def _getDnDHandler(self, context):
        url = self._getLinkUrl(context)
        return self.getDnDHandler(url)
    # end _getDnDHandler()

    def _createDnDSource(self, url):
        dndSource = ZCompositeDnDSource()
        dndSource.addSource(ZUrlDnDSource(url))
        return dndSource
    # end _createDnDSource()

    def getDnDHandler(self, url):
        handler = None
        if url:
            dndSource = self._createDnDSource(url)
            handlers = self.dndService.getMatchingHandlers(dndSource)
            if len(handlers) > 0:
                handler = handlers[0]
        return handler
    # end getDnDHandler()

    def getDnDHandlerName(self, url):
        handler = self.getDnDHandler(url)
        if handler:
            return handler.getName()
        else:
            return None
    # end getDnDHandlerName

#    def isEnabled(self, context):
#        return ZBlogPostEditableLinkActionBase.isEnabled(self, context) and \
#                context.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_INSERT_HTML)
#    # end isEnabled()

    def isVisible(self, context): #@UnusedVariable
        return self._getDnDHandler(context) is not None
    # end isVisible()

    def runAction(self, actionContext):
        editor = actionContext.getEditor()
        handler = self._getDnDHandler(actionContext)
        if handler:
            url = self._getLinkUrl(actionContext)
            dndSource = self._createDnDSource(url)
            xhtmlEmbedContent = handler.handle(dndSource, None)
            if isinstance(actionContext, ZBlogPostEditorToolBarActionContext):
                editor.insertXhtml(xhtmlEmbedContent)
            elif isinstance(actionContext, ZBlogPostEditorMenuActionContext):
                editor.getActiveContentEditor().insertXhtml(xhtmlEmbedContent)
    # end runAction()

# end ZConvertLinkToEmbedAction

# ------------------------------------------------------------------------------
# Action called when the user chooses to convert an existing link into an
# affiliate link.
# ------------------------------------------------------------------------------
class ZConvertProductLinkAction(ZBlogPostEditableLinkActionBase):

    def isVisible(self, context): #@UnusedVariable
        url = self._getLinkUrl(context)
        if url:
            service = getApplicationModel().getService(IZBlogAppServiceIDs.PRODUCTS_SERVICE_ID)
            productMD = service.findProductByUrl(url)
            return productMD is not None
        return False
    # end isVisible()

    def runAction(self, actionContext):
        url = self._getLinkUrl(actionContext)
        linkContext = self._getLinkContext(actionContext)
        if url:
            self._doConvertLink(actionContext, url, linkContext)
    # end runAction()

    def _doConvertLink(self, actionContext, url, linkContext):
        runnable = ZConvertProductLinkRunnable(actionContext, url, linkContext)
        ZShowProgressDialog(actionContext.getParentWindow(), _extstr(u"blogeditoractions.Converting_Link"), runnable) #$NON-NLS-1$
        newUrl = runnable.getZoundryProductUrl()
        if newUrl:
            attrs = linkContext.getLinkAttributes()
            attrs[u"href"] = newUrl #$NON-NLS-1$
            linkContext.setLinkAttributes(attrs)
    # end _doConvertLink()

# end ZConvertProductLinkAction


# ------------------------------------------------------------------------------
# This runnable is used to actually convert the link into a product link.
# ------------------------------------------------------------------------------
class ZConvertProductLinkRunnable(ZAbstractRunnableProgress):

    def __init__(self, actionContext, url, linkContext):
        self.actionContext = actionContext
        self.url = url
        self.linkContext = linkContext
        self.zoundryProductUrl = None
        self.logger = getLoggerService()

        ZAbstractRunnableProgress.__init__(self)
    # end __init__()

    def getZoundryProductUrl(self):
        return self.zoundryProductUrl
    # end getZoundryProductUrl()

    def _calculateWork(self):
        return 2
    # end _calculateWork()

    def _doRun(self):
        service = getApplicationModel().getService(IZBlogAppServiceIDs.PRODUCTS_SERVICE_ID)

        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        zoundryId = userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.ZOUNDRY_ID, None)
        if not zoundryId:
            zoundryId = u"zoundry@zoundry.com" #$NON-NLS-1$

        self.logger.debug(u"Converting link %s using zoundry id %s." % (unicode(self.url), unicode(zoundryId))) #$NON-NLS-1$

        self._fireWorkDoneEvent(1, _extstr(u"blogeditoractions.Invoking_Zoundry_Service")) #$NON-NLS-1$
        newUrl = service.convertProductLink(self.url, zoundryId)

        if newUrl:
            self.logger.debug(u"Link successfully converted to %s" % unicode(newUrl)) #$NON-NLS-1$
            self._fireWorkDoneEvent(1, _extstr(u"blogeditoractions.SuccessfullyConvertedLink")) #$NON-NLS-1$

            if not self.isCancelled():
                self.zoundryProductUrl = newUrl
        else:
            raise ZException(_extstr(u"blogeditoractions.FailedToConvertLink")) #$NON-NLS-1$
    # end _doRun()

    def stop(self):
        ZAbstractRunnableProgress.stop(self)
        self._fireCancelEvent()
    # end stop()
# end ZConvertProductLinkRunnable


# ------------------------------------------------------------------------------
# Run Xhtml Validation
# ------------------------------------------------------------------------------
class ZBlogPostXhtmlValidationAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context): #@UnusedVariable
        return context.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_VALIDATE_HTML)
    # end isEnabled()

    def runAction(self, actionContext):
        if not actionContext.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_VALIDATE_HTML):
            return
        actionContext.getEditor().schemaValidate()
    # end runAction
# end ZBlogPostXhtmlValidationAction

# ------------------------------------------------------------------------------
# Clear Xhtml Validation Messages
# ------------------------------------------------------------------------------
class ZBlogPostXhtmlClearValidationMessagesAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context): #@UnusedVariable
        return context.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_VALIDATE_HTML)
    # end isEnabled()

    def runAction(self, actionContext):
        if not actionContext.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_VALIDATE_HTML):
            return
        actionContext.getEditor().clearValidation()
    # end runAction
# end ZBlogPostXhtmlClearValidationMessagesAction

# ------------------------------------------------------------------------------
# Xhtml Tidy
# ------------------------------------------------------------------------------
class ZBlogPostXhtmlTidyAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def isEnabled(self, context): #@UnusedVariable
        return context.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_TIDY_HTML)
    # end isEnabled()

    def runAction(self, actionContext):
        if not actionContext.getEditor().hasCapability(IZXHTMLEditControl.ZCAPABILITY_TIDY_HTML):
            return
        actionContext.getEditor().runTidy()
    # end runAction

# end ZBlogPostXhtmlTidyAction

