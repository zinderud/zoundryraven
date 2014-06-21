from zoundry.appframework.ui.util.xhtmlvalidationutil import ZXhtmlSchemaUiUtil
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditorMenuItemAndToolbarActionBase
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControl
from zoundry.appframework.ui.actions.toolbaraction import ZDropDownToolBarAction
from zoundry.base.css.csscolor import ZCssColor
from zoundry.base.css.cssparse import parseCssBorderProperty
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditableImageActionBase

# ------------------------------------------------------------------------------
# Action for aligning images
# ------------------------------------------------------------------------------
class ZBlogPostImageAlignAction(ZBlogPostEditableImageActionBase):

    def __init__(self, align=u"none"): #$NON-NLS-1$
        self.align = align
    # end __init__()

    def _isEnabled(self, imageContext):
        en = ZBlogPostEditableImageActionBase._isEnabled(self, imageContext)
        if en:
            attrs = imageContext.getImageAttributes()
            return not attrs.has_key(u"align") or attrs[u"align"] != self.align #$NON-NLS-1$ #$NON-NLS-2$
        else:
            return False
    # end _isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        imageContext = self._getImageContext(izblogPostEditorActionContext)
        attrs = {u"align" : self.align} #$NON-NLS-1$
        imageContext.setImageAttributes(attrs)
    # end runAction()
# end ZBlogPostImageAlignAction

# ------------------------------------------------------------------------------
# Image align drop down toolbar action
# ------------------------------------------------------------------------------
class ZBlogPostImageAlignDropDownAction(ZDropDownToolBarAction):

    def __init__(self, menuModel): #$NON-NLS-1$
        self.menuModel = menuModel

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        # FIXME (PJ) create base class to share code with ZBlogPostImageAlignAction
        editor = izblogPostEditorActionContext.getEditor()
        # Get IZXHTMLEditControlImageContext instance of the editor.
        imageContext = editor.getImageContext()
        return imageContext is not None and imageContext.canEditImage()
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        delegate = ZBlogPostImageAlignAction()
        delegate.runAction(izblogPostEditorActionContext)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()
# end ZBlogPostImageAlignDropDownAction

# ------------------------------------------------------------------------------
# Action for setting image border
# ------------------------------------------------------------------------------
class ZBlogPostImageBorderAction(ZBlogPostEditableImageActionBase):

    def __init__(self, borderStyle=u"none"): #$NON-NLS-1$
        self.borderStyle = borderStyle
    # end __init__()

    def _isEnabled(self, imageContext):
        en = ZBlogPostEditableImageActionBase._isEnabled(self, imageContext)
        if en:
            attrs = imageContext.getImageAttributes()
            style = None
            if attrs.has_key(u"border"): #$NON-NLS-1$
                (width, style, zcssColor) = parseCssBorderProperty( getSafeString(attrs[u"border"]) ) #$NON-NLS-1$ @UnusedVariable
            return style is None or style != self.borderStyle
        else:
            return False
    # end _isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        imageContext = self._getImageContext(izblogPostEditorActionContext)
        (width, style, zcssColor) = (None, None, None) #@UnusedVariable
        attrs = imageContext.getImageAttributes()
        if attrs.has_key(u"border"): #$NON-NLS-1$
            (width, style, zcssColor) = parseCssBorderProperty( getSafeString(attrs[u"border"]) ) #$NON-NLS-1$ @UnusedVariable
        border = None
        if self.borderStyle and self.borderStyle != u"none": #$NON-NLS-1$
            if not width:
                width = u"1px" #$NON-NLS-1$
            if not zcssColor:
                zcssColor = ZCssColor()
            border = u"%s %s %s" % (width, self.borderStyle, zcssColor.getCssColor()) #$NON-NLS-1$
        attrs = {u"border" : border} #$NON-NLS-1$  +
        imageContext.setImageAttributes(attrs)
    # end runAction()
# end ZBlogPostImageBorderAction

# ------------------------------------------------------------------------------
class ZBlogPostImageBorderDropDownAction(ZDropDownToolBarAction):

    def __init__(self, menuModel): #$NON-NLS-1$
        self.menuModel = menuModel

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        # FIXME (PJ) create base class to share code with ZBlogPostImageBorderAction
        editor = izblogPostEditorActionContext.getEditor()
        # Get IZXHTMLEditControlImageContext instance of the editor.
        imageContext = editor.getImageContext()
        return imageContext is not None and imageContext.canEditImage()
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        # FIXME PJ instead of applying 'solid' border, apply the most recently used border action(e.g. dotted, dashed, solid etc).
        # (if possible, update the toolbar button icon image to reflect the last used border style)
        delegate = ZBlogPostImageBorderAction(u"solid") #$NON-NLS-1$
        delegate.runAction(izblogPostEditorActionContext)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()
# end ZBlogPostImageBorderDropDownAction


# ------------------------------------------------------------------------------
# Action for creating thumbnails
# ------------------------------------------------------------------------------
class ZBlogPostCreateThumbnailImageAction(ZBlogPostEditableImageActionBase):

    def __init__(self, width, height): #$NON-NLS-1$
        self.width = width
        self. height = height
    # end __init__()

    def _isEnabled(self, imageContext):
        en = ZBlogPostEditableImageActionBase._isEnabled(self, imageContext)
        if en:
            return imageContext.canCreateThumbnail()
        else:
            return False
    # end _isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        imageContext = self._getImageContext(izblogPostEditorActionContext)
        imageContext.createThumbnail(self.width, self.height)
    # end runAction()

# end ZBlogPostCreateThumbnailImageAction

# ------------------------------------------------------------------------------
# Drop down action handler to create image thumbnails
# ------------------------------------------------------------------------------
class ZBlogPostCreateThumbnailImageDropDownAction(ZDropDownToolBarAction):

    def __init__(self, menuModel): #$NON-NLS-1$
        self.menuModel = menuModel

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        # FIXME (PJ) create base class to share code with ZBlogPostCreateThumbnailImageAction
        editor = izblogPostEditorActionContext.getEditor()
        imageContext = editor.getImageContext()
        return imageContext is not None and imageContext.canCreateThumbnail()
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        # default case: generated a 250x250 tn
        editor = izblogPostEditorActionContext.getEditor()
        imageContext = editor.getImageContext()
        imageContext.createThumbnail(250, 250)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        return self.menuModel
    # end _createMenuModel()
# end ZBlogPostCreateThumbnailImageDropDownAction


# ------------------------------------------------------------------------------
# Drop down action handler to list html taga
# ------------------------------------------------------------------------------
class ZBlogPostFormatHtmlDropDownAction(ZDropDownToolBarAction):

    def __init__(self, zfFormatHtmlMenuModelBuilder, blockLevelOnly): #$NON-NLS-1$
        self.zfFormatHtmlMenuModelBuilder = zfFormatHtmlMenuModelBuilder
        self.blockLevelOnly = blockLevelOnly

    def isEnabled(self, izblogPostEditorActionContext): #@UnusedVariable
        editor = izblogPostEditorActionContext.getEditor()
        return editor.hasCapability(IZXHTMLEditControl.ZCAPABILITY_FORMAT_HTML)
    # end isEnabled()

    def runAction(self, izblogPostEditorActionContext): #@UnusedVariable
        #editor = izblogPostEditorActionContext.getEditor()
        pass
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        currentTagName = u"body" #$NON-NLS-1$
        if not self.blockLevelOnly:
            editor = toolBarActionContext.getParentWindow()
            selection = editor.getCurrentSelection()
            izXhtmlElement = selection.getElement()
            currentTagName = izXhtmlElement.getNodeName()
            if selection.isEmpty():
                if izXhtmlElement.getParent():
                    parentTag = izXhtmlElement.getParent().getNodeName()
                    if parentTag in  (u"body", u"html") and currentTagName in (u"p", u"div", u"blockquote"): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$
                        currentTagName = u"body" #$NON-NLS-1$       
        tagNames = ZXhtmlSchemaUiUtil().getChildElementNames(currentTagName)
        menuModel = self.zfFormatHtmlMenuModelBuilder.createHtmlTagMenuModel(tagNames)
        return menuModel
    # end _createMenuModel()
# end ZBlogPostFormatHtmlDropDownAction

# ------------------------------------------------------------------------------
# Format current selection
# ------------------------------------------------------------------------------
class ZBlogPostFormatHtmlAction(ZBlogPostEditorMenuItemAndToolbarActionBase):

    def __init__(self, tagName):
        self.tagName = tagName
    # end __init()__
    
    def isEnabled(self, context): #@UnusedVariable
        return True
    # end isEnabled()

    def runAction(self, actionContext):
        actionContext.getEditor().applyFormatting(IZXHTMLEditControl.ZCAPABILITY_FORMAT_HTML, self.tagName)
    # end runAction
# end ZBlogPostFormatHtmlAction
