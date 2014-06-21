from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZTextEditControlSelection
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import ZBaseEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import ZTextEditControlSelection
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString

# ------------------------------------------------------------------------------
# Interface that all html edit controls must implement.  An edit control is a
# control that allows the user to edit the content of a IZDocument.  In the
# case of a XHTML edit control, the assumption is that the content of the
# IZDocument is xhtml based content.
# ------------------------------------------------------------------------------
class IZXHTMLEditControl(IZRichTextEditControl):

    ZCAPABILITY_PASTE_HTML = u"zoundry.xhtmleditcontrol.capability.paste-html" #$NON-NLS-1$
    ZCAPABILITY_INSERT_IMAGE = u"zoundry.xhtmleditcontrol.capability.insert-image" #$NON-NLS-1$
    ZCAPABILITY_EDIT_IMAGE = u"zoundry.xhtmleditcontrol.capability.edit-image" #$NON-NLS-1$
    ZCAPABILITY_INSERT_LINK = u"zoundry.xhtmleditcontrol.capability.insert-link" #$NON-NLS-1$
    ZCAPABILITY_EDIT_LINK = u"zoundry.xhtmleditcontrol.capability.edit-link" #$NON-NLS-1$
    ZCAPABILITY_INSERT_TABLE = u"zoundry.xhtmleditcontrol.capability.insert-table" #$NON-NLS-1$
    ZCAPABILITY_EDIT_TABLE = u"zoundry.xhtmleditcontrol.capability.edit-table" #$NON-NLS-1$
    ZCAPABILITY_INSERT_HTML = u"zoundry.xhtmleditcontrol.capability.insert-html" #$NON-NLS-1$
    ZCAPABILITY_VALIDATE_HTML = u"zoundry.xhtmleditcontrol.capability.validate-html" #$NON-NLS-1$
    ZCAPABILITY_TIDY_HTML = u"zoundry.xhtmleditcontrol.capability.tidy-html" #$NON-NLS-1$
    ZCAPABILITY_FORMAT_HTML = u"zoundry.xhtmleditcontrol.capability.format-html" #$NON-NLS-1$
    ZCAPABILITY_SCHEMA_AWARE = u"zoundry.xhtmleditcontrol.capability.schema-aware" #$NON-NLS-1$

    def setXhtmlDocument(self, xhtmlDoc):
        u"""setXhtmlDocument(ZXhtmlDocument) -> void
        Sets the xhtml content.""" #$NON-NLS-1$

    def getXhtmlDocument(self):
        u"""getXhtmlDocument()  -> ZXhtmlDocument
        Returns the xhtml content.""" #$NON-NLS-1$

    def canPasteXhtml(self):
        u"""canPasteXhtml()  -> bool
        Returns true  if xhtml content can be inserted or pasted to the current document model.""" #$NON-NLS-1$

    def pasteXhtml(self):
        u"""pasteXhtml()  -> void
        Content is inserted or pasted to the current document model.""" #$NON-NLS-1$
        
    def canInsertXhtml(self):
        u"""canInsertXhtml()  -> bool
        Returns true  if xhtml content can be inserted into the current document model.""" #$NON-NLS-1$

    def insertXhtml(self, xhtmlString):
        u"""insertXhtml(string)  -> void
        Content is inserted into the current document model.""" #$NON-NLS-1$
        
    def getCurrentSelection(self):
        u"""getCurrentSelection()  -> IZXHTMLEditControlSelection
        Returns current selection if available or None otherwise.""" #$NON-NLS-1$
    # end getCurrentSelection

    def getLinkContext(self):
        u"""getLinkContext()  -> IZXHTMLEditControlLinkContext
        Returns link creation and edit context if available or None otherwise.""" #$NON-NLS-1$
    # end getLinkContext

    def getImageContext(self):
        u"""getImageContext()  -> IZXHTMLEditControlImageContext
        Returns image creation and edit context if available or None otherwise.""" #$NON-NLS-1$
    # end getImageContext

    def getTableContext(self):
        u"""getTableContext()  -> IZXHTMLEditControlTableContext
        Returns table creation and edit context if capability is supported and available or None otherwise.""" #$NON-NLS-1$
    # end getTableContext()
    
    def schemaValidate(self):
        u"""schemaValidate() -> void
        Runs xhtml validation if ZCAPABILITY_VALIDATE_HTML supported""" #$NON-NLS-1$
        pass
    # end schemaValidate
    
    def clearValidation(self):
        u"""clearValidation() -> void
        Clears any xhtml validation messages if ZCAPABILITY_VALIDATE_HTML is supported""" #$NON-NLS-1$
        pass
    # end clearValidation    
    
    def runTidy(self):
        u"""runTidy() -> void
        Runs xhtml Tidy if ZCAPABILITY_TIDY_HTML is supported""" #$NON-NLS-1$
        pass
    # end runTidy    
    
# end IZXHTMLEditControl

# ------------------------------------------------------------------------------
# link edit contexts
# ------------------------------------------------------------------------------
class IZXHTMLEditControlLinkContext:

    def canCreateLink(self):
        u"""canCreateLink()  -> bool
        Returns true if a link can be created""" #$NON-NLS-1$
    # end canCreateLink()

    def canEditLink(self):
        u"""canEditLink()  -> bool
        Returns true if a link can be edited""" #$NON-NLS-1$
    # end canEditLink()

    def canRemoveLink(self):
        u"""canRemoveLink()  -> bool
        Returns true if a link can be removed""" #$NON-NLS-1$
    # end canRemoveLink()

    def removeLink(self):
        u"""removeLink()  -> bool
        Returns removes link and returns true on success""" #$NON-NLS-1$
    # end canRemoveLink()

    def getLinkAttributes(self):
        u"""getLinkAttributes()  -> Map
        Returns map containing link attributes such as href""" #$NON-NLS-1$
    # end getLinkAttributes()

    def setLinkAttributes(self, attrMap):
        u"""getLinkAttributes(Map)  -> bool
        Sets link properties and returns true on success.""" #$NON-NLS-1$
    # end setLinkAttributes()

# end IZXHTMLEditControlLinkContext

# ------------------------------------------------------------------------------
# image edit contexts
# ------------------------------------------------------------------------------
class IZXHTMLEditControlImageContext:

    def canCreateImage(self):
        u"""canCreateImage()  -> bool
        Returns true if a img can be created""" #$NON-NLS-1$
    # end canCreateLink()

    def canEditImage(self):
        u"""canEditImage()  -> bool
        Returns true if a img can be edited""" #$NON-NLS-1$
    # end canEditImage()

    def isThumbnail(self):
        u"""isThumbnail()  -> bool
        Returns true if the image is a thumbnail image (generated by Raven)""" #$NON-NLS-1$
    # end isThumbnail()

    def canCreateThumbnail(self):
        u"""canCreateThumbnail()  -> bool
        Returns true if a thumbnail image can be generated""" #$NON-NLS-1$
    # end canCreateThumbnail()

    def createThumbnail(self, width, height, options):
        u"""createThumbnail(int, int, map)  -> bool
        Generates a thumbnail image if the current image is not already an thumbnail. Returns true on success.""" #$NON-NLS-1$
    # end createThumbnail()


    def getImageAttributes(self):
        u"""getImageAttributes()  -> Map
        Returns map containing img attributes such as src""" #$NON-NLS-1$
    # end getImageAttributes()

    def setImageAttributes(self, attrMap):
        u"""setImageAttributes(Map)  -> bool
        Sets img properties and returns true on success.""" #$NON-NLS-1$
    # end setImageAttributes()

    def insertImage(self, attrMap):
        u"""insertImage(Map)  -> bool
        Inserts a new image and returns true on success.
        The image location attribute src is required.
        """ #$NON-NLS-1$
    # end insertImage()

# end IZXHTMLEditControlImageContext

# ------------------------------------------------------------------------------
# Returns the CSS style context of the current element or selection
# ------------------------------------------------------------------------------
class IZXHTMLEditControlStyleContext:

    def getFontInfo(self):
        u"""getFontInfo()  -> ZCssFontInfo
        Returns font info""" #$NON-NLS-1$
    # end getFontInfo()

    def setFontInfo(self, fontInfo):
        u"""setFontInfo(ZCssFontInfo)  -> void
        Sets the font info""" #$NON-NLS-1$
    # end setFontInfo()

    def getColor(self):
        u"""getColor() -> ZCssColor or None
        """ #$NON-NLS-1$
    # end getColor()

    def setColor(self, cssColor):
        u"""setColor(ZCssColor) -> void
        """ #$NON-NLS-1$
    # end setColor()

    def getBackgroundColor(self):
        u"""getBackgroundColor() -> ZCssColor or None
        """ #$NON-NLS-1$
    # end getBackgroundColor()

    def applyStyle(self, cssFontInfo, cssColor, cssBgColor):
        u"""applyStyle(ZCssFontInfo, ZCssColor, ZCssColor) -> void
        """ #$NON-NLS-1$
    # end applyStyle()

# end IZXHTMLEditControlStyleContext


# ------------------------------------------------------------------------------
# table create and  edit contexts
# ------------------------------------------------------------------------------
class IZXHTMLEditControlTableContext:
    # well known properties
    ATTR_ROWS = u"rows" #$NON-NLS-1$
    ATTR_COLS = u"cols" #$NON-NLS-1$
    ATTR_CELLPADDING = u"cellpadding" #$NON-NLS-1$
    ATTR_CELLSPACING = u"cellspacing" #$NON-NLS-1$
    ATTR_BORDER = u"border" #$NON-NLS-1$
    ATTR_WIDTH = u"width" #$NON-NLS-1$

    # commands
    INSERT_TABLE = u"insertTable" #$NON-NLS-1$
    EDIT_TABLE_ATTRS = u"editTableAttrs" #$NON-NLS-1$

    INSERT_HEADER = u"insertHeader" #$NON-NLS-1$
    INSERT_FOOTER = u"insertFooter" #$NON-NLS-1$
    INSERT_CAPTION = u"insertCaption" #$NON-NLS-1$
    
    INSERT_ROW_ABOVE = u"insertRowAbove" #$NON-NLS-1$
    INSERT_ROW_BELOW = u"insertRowBelow" #$NON-NLS-1$
    INSERT_COL_LEFT = u"insertColumnLeft" #$NON-NLS-1$
    INSERT_COL_RIGHT = u"insertColumnRight" #$NON-NLS-1$

    MOVE_ROW_ABOVE = u"moveRowAbove" #$NON-NLS-1$
    MOVE_ROW_BELOW = u"moveRowBelow" #$NON-NLS-1$
    MOVE_COL_LEFT = u"moveColumnLeft" #$NON-NLS-1$
    MOVE_COL_RIGHT = u"moveColumnRight" #$NON-NLS-1$

    DELETE_ROW = u"deleteRow" #$NON-NLS-1$
    DELETE_COL = u"deleteColumn" #$NON-NLS-1$
    CLEAR_CELL = u"clearCell" #$NON-NLS-1$

    def canInsertTable(self):
        u"""canInsertTable()  -> bool
        Returns true if a table can be created""" #$NON-NLS-1$
    # end canInsertTable()

    def canEditTable(self):
        u"""canEditTable()  -> bool
        Returns true if current selection is  table  and  it can be edited""" #$NON-NLS-1$
    # end canEditTable()

    def insertTable(self, attributes):
        u"""createTable()  -> void
        Creates and inserts a table""" #$NON-NLS-1$
    # end insertTable()

    def getTableAttributes(self):
        u"""getTableAttributes()  -> map
        Returns the table attributes""" #$NON-NLS-1$
    # end getTableAttributes()

    def setTableAttributes(self, attributes):
        u"""getTableAttributes(map)  -> void
        Sets the table attributes""" #$NON-NLS-1$
    # end setTableAttributes()

    def isCommandEnabled(self, commandId):
        u"""isCommandEnabled(string)  -> bool
        Returns true if a command can be applied. E.g. InsertRowBelow.""" #$NON-NLS-1$
    # end isCommandEnabled()

    def execCommand(self, commandId):
        u"""execCommand(string)  -> void
        Applies given table command. E.g. InsertRowBelow.""" #$NON-NLS-1$
    # end execCommand()

# end IZXHTMLEditControlTableContext


# ------------------------------------------------------------------------------
# xhtml selection context
# ------------------------------------------------------------------------------
class IZXHTMLEditControlSelection(IZTextEditControlSelection):

    def getElement(self):
        u"""getElement() -> IZXhtmlElement
        Returns currently selected element or element under caret.""" #$NON-NLS-1$
        pass
    # end getElement()

    def getStyleContext(self):
        u"""getStyleContext() -> IZXHTMLEditControlStyleContext or None
        Returns CSS style context of current selection or None if not available.""" #$NON-NLS-1$
        pass
    # end getStyleContext()
# end IZXHTMLEditControlSelection

# ------------------------------------------------------------------------------
# base implementation of a html element selection.
# ------------------------------------------------------------------------------
class ZXHTMLEditControlSelection(ZTextEditControlSelection, IZXHTMLEditControlSelection):

    def __init__(self, text, izelement):
        self.izelement = izelement
        ZTextEditControlSelection.__init__(self, text)
    # end __init__()

    def getElement(self):
        return self.izelement
    # end getElement()

    def getStyleContext(self):
        return None
    # end getStyleContext()

# end clasd ZXHTMLEditControlSelection
# ------------------------------------------------------------------------------
# A base class for edit controls that support editing XHTML content.  This class
# extends the base edit control class and adds convenience methods useful for
# xhtml editing controls (such as convenience methods that help fire certain
# xhtml edit control specific events).
# ------------------------------------------------------------------------------


class ZBaseXHTMLEditControl(ZBaseEditControl, IZXHTMLEditControl):

    def __init__(self, *args, **kw):
        ZBaseEditControl.__init__(self, *args, **kw)
        self.noneSelection = ZXHTMLEditControlSelection(None, None)
    # end __init__()

    def setXhtmlDocument(self, xhtmlDoc):
        body = xhtmlDoc.getBody()
        xhtmlString = body.serialize()
        self.setValue(xhtmlString)
    # end setXhtmlDocument()

    def getXhtmlDocument(self):
        htmlString = self.getValue()
        xhtmlDocument = loadXhtmlDocumentFromString(htmlString)
        return xhtmlDocument
    # end getXhtmlDocument()

    def canPasteXhtml(self):
        return False
    # end canPasteXhtml()

    def pasteXhtml(self):
        pass
    # end pasteXhtml()
    
    def canInsertXhtml(self):
        return False
    # end canInsertXhtml
    
    def insertXhtml(self, xhtmlString): #@UnusedVariable
        pass
    # end insertXhtml

    def getCurrentSelection(self):
        return self.noneSelection
    # end getCurrentSelection

    def getLinkContext(self):
        return None
    # end getLinkContext

    def getImageContext(self):
        return None
    # end getImageContext

    def getTableContext(self):
        return None
    # end getTableContext()
    
    def schemaValidate(self):
        pass
    # end schemaValidate
    
    def clearValidation(self):
        pass
    # end clearValidation    
    
    def runTidy(self):
        pass
    # end runTidy        

# end ZXHTMLBaseEditControl
