from zoundry.appframework.engine.service import IZService

#-------------------------------------------------------------------
# Schema version
#-------------------------------------------------------------------
class IZXhtmlSchemaVersion:
    XHTML_1_STRICT = u"xhtml1strict" #$NON-NLS-1$
    XHTML_1_TRANSITIONAL = u"xhtml1transitional" #$NON-NLS-1$
#end IZXhtmlSchemaVersion

#-------------------------------------------------------------------
# IZXhtmlValidator : interface to xhtml validation related
#-------------------------------------------------------------------
class IZXhtmlValidatorService(IZService):

    def getSchema(self, version):
        u"""getSchema(string) -> IZXhtmlSchema""" #$NON-NLS-1$
    # end getSchema()

    def getValidator(self, version):
        u"""getValidator(string) -> IZXhtmlValidator
        """ #$NON-NLS-1$
    # end getValidator()
    
    def tidyHtmlBody(self, htmlBody, izXhtmlValidationListener=None):
        u"""tidyHtmlBody(string, IZXhtmlValidationListener) -> (boolSuccess, tidyHtmlString, messageList)
        Runs Tidy on given xhtml body contents (i.e. children of <body> tag) as a string.
        This method returns the tuple (boolSuccess, htmlResultString, list of ZXhtmlValidationMessage items).
        """ #$NON-NLS-1$
    # end tidyHtmlBody()      

# end IZXhtmlValidatorService

# ------------------------------------------------------------
# XHTML validator interface
# ------------------------------------------------------------
class IZXhtmlValidator:

    def validateHtmlBody(self, htmlBody, izXhtmlValidationListener=None):
        u"""validateHtmlBody(string, IZXhtmlValidationListener) -> list
        Validates given xhtml body contents (i.e. children of <body> tag) as a string.
        This method returns a list of ZXhtmlValidationMessage items.
        """ #$NON-NLS-1$
    # end validateHtmlBody()

    def validateHtml(self, html, izXhtmlValidationListener=None):
        u"""validateHtml(string, IZXhtmlValidationListener) -> list
        Validates given xhtml contents as a string.
        This method returns a list of ZXhtmlValidationMessage items.
        """ #$NON-NLS-1$
    # end validateHtml()      

# end IZXhtmlValidator

#------------------------------------------------------------------------
# Validation listener
#------------------------------------------------------------------------
class IZXhtmlValidationListener:

    def onXhtmlValidationStart(self):
        u"""onXhtmlValidationStart() -> void
        Callback to indicate start of validation
        """ #$NON-NLS-1$
        pass
    # end onXhtmlValidationStart

    def onXhtmlValidationEnd(self, messageCount): #@UnusedVariable
        u"""onXhtmlValidationEnd(int) -> void
        Callback to indicate end of validation
        """ #$NON-NLS-1$
        pass
    # end onXhtmlValidationEnd

    def onXhtmlValidationMessage(self, zxhtmlValidationMessage): #@UnusedVariable
        u"""onXhtmlValidation(ZXhtmlValidationMessage) -> void
        Callback on validation events.
        """ #$NON-NLS-1$
        pass
    # end onXhtmlValidationMessage

    def onXhtmlValidationException(self, exception): #@UnusedVariable
        u"""onXhtmlValidationException(Exception) -> void
        Callback to indicate error or exception.
        """ #$NON-NLS-1$
        pass
    # end onXhtmlValidationException
# end IZXhtmlValidationListener

#------------------------------------------------------------------------
# Validation message
#------------------------------------------------------------------------
class ZXhtmlValidationMessage:
    # severities
    INFO = 0
    WARNING = 1
    ERROR = 2
    FATAL = 3
    SUCCESS = 4

    def __init__(self, severity, lineNumber, columnNumber, message):
        self.severity = severity
        self.lineNumber = lineNumber
        self.columnNumber = columnNumber
        self.message = message
    # end __init__()

    def __str__(self):
        return u"[%d]-[%03d,%03d]-[%s]" % (self.severity, self.lineNumber, self.columnNumber, self.message) #$NON-NLS-1$
    # end __str__()

    def getSeverity(self):
        return self.severity
    # end getSeverity()

    def getMessage(self):
        return self.message
    # end getMessage()

    def getLine(self):
        return self.lineNumber
    # end getLine()

    def getColumn(self):
        return self.columnNumber
    # end getColumn()
# end ZXhtmlValidationMessage


#------------------------------------------------------------
# Interface that represents xhtml XSD Schema document
# and util methods
#------------------------------------------------------------
class IZXhtmlSchema:

    def getDocument(self):
        u"""Returns the schema xsd ZDom.""" #$NON-NLS-1$
    # end getDocument()

    def getAllElementNames(self):
        u"""Returns list of element names.""" #$NON-NLS-1$
    # end getAllElementNames()

    def isMixedType(self, aElementName):
        u"""Returns true if the element supports mixed typed (e.g. characters and elements).""" #$NON-NLS-1$
    # end isMixedType()

    def getElementDocumentation(self, aElementName):
        u"""Returns documentation for element. """ #$NON-NLS-1$
    # end getElementDocumentation

    def getElementChildren(self, aParentElementName, bMixedTypeOnly=False):
        u"""Returns list of child element names given parent element name.""" #$NON-NLS-1$
    # end getElementChildren()

    def getElementAttributes(self, aElementName, bRequiredAttrOnly=False):
        u"""Returns list of attributes given element name.""" #$NON-NLS-1$
    # end getElementAttributes()

# end IZXhtmlSchema



