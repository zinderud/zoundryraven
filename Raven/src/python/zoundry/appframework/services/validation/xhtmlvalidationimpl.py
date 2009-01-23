from zoundry.base.zdom.tidyutil import ZTidyError
from zoundry.base.zdom.tidyutil import SOURCE_OPTIONS
from zoundry.base.zdom.tidyutil import runTidy
from zoundry.base.util.text.texttransform import ZTextToXhtmlTransformer
from zoundry.base.xhtml import xhtmlutil
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlValidator
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlValidatorService
from zoundry.appframework.services.validation.xhtmlvalidation import ZXhtmlValidationMessage
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlSchemaVersion
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.zdom.dom import ZDom
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlSchema
from zoundry.base.util.urlutil import getUriFromFilePath
from xml.parsers.xmlproc import xmlproc #@UnresolvedImport
from xml.parsers.xmlproc import xmlval  #@UnresolvedImport


#------------------------------------------------------------
# Class that represents xhtml XSD Schema document
# with some supporting methods.
#------------------------------------------------------------
class ZXhtmlSchema(IZXhtmlSchema):

    XS_NSS_MAP = {
        u"xs" : u"http://www.w3.org/2001/XMLSchema" #$NON-NLS-1$ #$NON-NLS-2$
    }

    def __init__(self, xsdFile):
        self.xsdFile = xsdFile
        self.dom = None
        self.elementMap = {}
        self.complexTypesMap = {}
        self.simpleTypesMap = {}
        self.groupsMap = {}
        self.attributeGroupsMap = {}

        try:
            self.dom = ZDom()
            self.dom.load(self.xsdFile)
            self.dom.setNamespaceMap(ZXhtmlSchema.XS_NSS_MAP)
            self._initMaps()
        except:
            pass

    def getSchemaFile(self):
        u"""Returns the schema xsd filename.""" #$NON-NLS-1$
        return self.xsdFile
    # end getSchemaFile

    def getDocument(self):
        u"""Returns the schema xsd ZDom.""" #$NON-NLS-1$
        return self.dom
    # end getDocument()

    def getAllElementNames(self):
        u"""Returns list of element names.""" #$NON-NLS-1$
        return self.elementMap.keys()
    # end getAllElementNames()

    def isMixedType(self, aElementName):
        u"""Returns true if the element supports mixed typed (e.g. characters and elements).""" #$NON-NLS-1$
        rVal = False
        ele = self._getElement(aElementName)
        if ele:
            complexEle = ele.selectSingleNode(u"descendant::xs:complexType") #$NON-NLS-1$
            if complexEle:
                mixed = complexEle.getAttribute(u"mixed")#$NON-NLS-1$
                rVal = mixed is not None and mixed.lower() == u"true" #$NON-NLS-1$
        return rVal
    # end isMixedType()

    def getElementDocumentation(self, aElementName):
        u"""Returns documentation for element. """ #$NON-NLS-1$
        rVal = None
        ele = self._getElement(aElementName)
        if ele:
            dEle = ele.selectSingleNode(u"descendant::xs:documentation") #$NON-NLS-1$
            if dEle:
                rVal = dEle.getText()
        return rVal
    # end getElementDocumentation

    def getElementChildren(self, aParentElementName, bMixedTypeOnly=False):
        u"""Returns list of child element names given parent element name.""" #$NON-NLS-1$
        rList = []
        parentEle = self._getElement(aParentElementName)
        if parentEle:
            eleList = parentEle.selectNodes(u"descendant::xs:element") #$NON-NLS-1$
            for ele in eleList:
                eleName = ele.getAttribute(u"ref")  #$NON-NLS-1$
                if not bMixedTypeOnly or (bMixedTypeOnly and self.isMixedType(eleName)):
                    rList.append(eleName)
            # complex tytpe extensions
            extList = parentEle.selectNodes(u"descendant::xs:extension") #$NON-NLS-1$
            for ext in extList:
                rList.extend( self._getChildrenForComplexType(ext.getAttribute(u"base"), bMixedTypeOnly) ) #$NON-NLS-1$
        return rList
    # end getElementChildren()

    def _getChildrenForComplexType(self, aComplexTypeName, bMixedTypeOnly=False):
        u"""Returns list of child element names given complexType name.""" #$NON-NLS-1$
        rList = []
        if self.complexTypesMap.has_key(aComplexTypeName):
            complexEle = self.complexTypesMap[aComplexTypeName]
            eleList = complexEle.selectNodes(u"descendant::xs:element") #$NON-NLS-1$
            for ele in eleList:
                eleName = ele.getAttribute(u"ref")  #$NON-NLS-1$
                if not bMixedTypeOnly or (bMixedTypeOnly and self.isMixedType(eleName)):
                    rList.append(eleName)
            groupList = complexEle.selectNodes(u"descendant::xs:group") #$NON-NLS-1$
            for group in groupList:
                rList.extend( self._getChildrenForGroup(group.getAttribute(u"ref"), bMixedTypeOnly) )  #$NON-NLS-1$
        return rList
    # end _getChildrenForComplexType()

    def _getChildrenForGroup(self, aGroupName, bMixedTypeOnly=False):
        u"""Returns list of child element names given group name.""" #$NON-NLS-1$
        rList = []
        groupEle = self._getGroup(aGroupName)
        if groupEle:
            eleList = groupEle.selectNodes(u"descendant::xs:element") #$NON-NLS-1$
            for ele in eleList:
                eleName = ele.getAttribute(u"ref")  #$NON-NLS-1$
                if not bMixedTypeOnly or (bMixedTypeOnly and self.isMixedType(eleName)):
                    rList.append(eleName)
            groupList = groupEle.selectNodes(u"descendant::xs:group") #$NON-NLS-1$
            for group in groupList:
                rList.extend( self._getChildrenForGroup(group.getAttribute(u"ref"), bMixedTypeOnly) )  #$NON-NLS-1$
        return rList
    # end _getChildrenForGroup()

    def getElementAttributes(self, aElementName, bRequiredAttrOnly=False):
        u"""Returns list of attributes given element name.""" #$NON-NLS-1$
        rList = []
        ele = self._getElement(aElementName)
        if ele:
            rList.extend( self._getAttributesForElement(ele, bRequiredAttrOnly) )
        return rList
    # end getElementAttributes()

    def _getAttributesForElement(self, aElement, bRequiredAttrOnly=False):
        rList = []
        # top level attributes
        attList = aElement.selectNodes(u"descendant::xs:attribute") #$NON-NLS-1$
        for att in attList:
            if self._isSupportAttribute(att, bRequiredAttrOnly):
                rList.append(att.getAttribute(u"name"))#$NON-NLS-1$

        # groups
        attList = aElement.selectNodes(u"descendant::xs:attributeGroup") #$NON-NLS-1$
        for att in attList:
            rList.extend( self._getAttributesForGroup(att.getAttribute(u"ref"), bRequiredAttrOnly) ) #$NON-NLS-1$
        return rList
    # _getAttributesForElement()

    def _getAttributesForGroup(self, aAttrGroupName, bRequiredAttrOnly=False):
        rList = []
        attGroupEle = self._getAttributeGroup(aAttrGroupName)
        if attGroupEle:
            # top level attributes
            attList = attGroupEle.selectNodes(u"descendant::xs:attribute") #$NON-NLS-1$
            for att in attList:
                if self._isSupportAttribute(att, bRequiredAttrOnly):
                    rList.append(att.getAttribute(u"name")) #$NON-NLS-1$

            # groups
            attList = attGroupEle.selectNodes(u"descendant::xs:attributeGroup") #$NON-NLS-1$
            for att in attList:
                rList.extend( self._getAttributesForGroup(att.getAttribute(u"ref"), bRequiredAttrOnly) )    #$NON-NLS-1$
        return rList
    # end _getAttributesForGroup()

    def _isRequiredAttribute(self, aAttrElement):
        # Returns true if required.
        return aAttrElement.getAttribute(u"use").lower() == u"required"  #$NON-NLS-1$  #$NON-NLS-2$
    # end _isRequiredAttribute()

    def _isSupportAttribute(self, aAttrElement, bRequiredAttrOnly=False):
        # skip Script type attributes (onBlur, onFocus) for the Joey editor.
        if bRequiredAttrOnly and not self._isRequiredAttribute(aAttrElement):
            return False
        return aAttrElement.getAttribute(u"type").lower() != u"script"  #$NON-NLS-1$  #$NON-NLS-2$
        # FIXME (PJ) : also skip for Coords, shape,
    # end _isSupportAttribute()

    def _isSupportedAttrGroup(self, aAttrGroupName):
        # skip events group (mouse up, onClick etc) for the Joey editor.
        return  aAttrGroupName != u"events"  #$NON-NLS-1$
    # end _isSupportedAttrGroup()

    def _getElement(self, aElementName):
        # returns the element given name or None if not found.
        rVal = None
        if aElementName:
            aElementName = aElementName.strip().lower()
            if self.elementMap.has_key(aElementName):
                rVal = self.elementMap[aElementName]
        return rVal
    # end _getElement()

    def _getGroup(self, aGroupName):
        # returns the group element given name or None if not found.
        rVal = None
        if self.groupsMap.has_key(aGroupName):
            rVal = self.groupsMap[aGroupName]
        return rVal
    # end _getGroup()

    def _getAttributeGroup(self, aAttrGroupName):
        # returns the attribute group element given name or None if not found.
        rVal = None
        if aAttrGroupName and self._isSupportedAttrGroup(aAttrGroupName) and self.attributeGroupsMap.has_key(aAttrGroupName):
            rVal = self.attributeGroupsMap[aAttrGroupName]
        return rVal
    # end _getAttributeGroup()

    def _initMaps(self):
        u"""Initialized lookup maps.""" #$NON-NLS-1$
        self.elementMap = {}
        eleList = self.getDocument().selectNodes(u"xs:element") #$NON-NLS-1$
        for ele in eleList:
            self.elementMap[ele.getAttribute(u"name")] = ele  #$NON-NLS-1$

        self.complexTypesMap = {}
        # Eg. Inline, Block, Flow, a.content, pre.content
        eleList = self.getDocument().selectNodes(u"xs:complexType") #$NON-NLS-1$
        for ele in eleList:
            self.complexTypesMap[ele.getAttribute(u"name")] = ele  #$NON-NLS-1$

        self.simpleTypesMap = {}
        # Eg ContentType,ContentTypes, URI, UriList
        eleList = self.getDocument().selectNodes(u"xs:simpleType") #$NON-NLS-1$
        for ele in eleList:
            self.simpleTypesMap[ele.getAttribute(u"name")] = ele  #$NON-NLS-1$

        self.groupsMap = {}
        # Eg. special.pre, special, fontstyle, phrase, heading, blocktext, block
        eleList = self.getDocument().selectNodes(u"xs:group") #$NON-NLS-1$
        for ele in eleList:
            self.groupsMap[ele.getAttribute(u"name")] = ele  #$NON-NLS-1$

        self.attributeGroupsMap = {}
        # Eg. coreattrs,i18n, attrs, events
        eleList = self.getDocument().selectNodes(u"xs:attributeGroup") #$NON-NLS-1$
        for ele in eleList:
            self.attributeGroupsMap[ele.getAttribute(u"name")] = ele  #$NON-NLS-1$
    # end _initMaps()
# end ZXhtmlSchema



#-------------------------------------------------------------------
# IZXhtmlValidator impl.
#-------------------------------------------------------------------
class ZXhtmlValidatorServiceImpl(IZXhtmlValidatorService):
    
    def __init__(self):
        self.applicationModel = None
        self.schemas = {}
        self.xhtmlXsdStrictPath = None
        self.xhtmlXsdTransPath = None
        self.xhtmlDtdStrictPath = None
        self.xhtmlDtdTransPath = None
    # end __init__()
    
    def start(self, applicationModel):
        self.applicationModel = applicationModel        
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.xhtmlXsdStrictPath = self.applicationModel.getSystemProfile().getSchema(u"xhtml/xhtml1-strict.xsd") #$NON-NLS-1$
        self.xhtmlXsdTransPath = self.applicationModel.getSystemProfile().getSchema(u"xhtml/xhtml1-transitional.xsd") #$NON-NLS-1$
        # dtd
        self.xhtmlDtdStrictPath = self.applicationModel.getSystemProfile().getSchema(u"xhtml/xhtml1-strict.dtd") #$NON-NLS-1$
        self.xhtmlDtdTransPath = self.applicationModel.getSystemProfile().getSchema(u"xhtml/xhtml1-transitional.dtd") #$NON-NLS-1$
        # create schemas
        self._createSchemas()                
        self.logger.debug(u"ZXhtmlValidatorServiceImpl started.") #$NON-NLS-1$
    # end start()
    
    def stop(self):
        pass
    # end stop()    
    
    def _createSchemas(self):
        self.schemas[IZXhtmlSchemaVersion.XHTML_1_STRICT] = ZXhtmlSchema(self.xhtmlXsdStrictPath)
        self.schemas[IZXhtmlSchemaVersion.XHTML_1_TRANSITIONAL] = ZXhtmlSchema(self.xhtmlXsdTransPath)
    # end _createSchemas
    
    def getSchema(self, version = IZXhtmlSchemaVersion.XHTML_1_TRANSITIONAL):
        if self.schemas.has_key(version):
            return self.schemas[version]
        else:
            self.logger.error(u"Schema version %s not found." % version) #$NON-NLS-1$
            raise
    # end getSchema()
    
    def getValidator(self, version):
        if not self.schemas.has_key(version):
            self.logger.error(u"Schema version %s not found." % version) #$NON-NLS-1$
            raise
        dtdFile = self._getDtdPath(version)
        return ZXhtmlDtDValidator(dtdFile)
    # end getValidator()
        
    def _getDtdPath(self, version):
        if version == IZXhtmlSchemaVersion.XHTML_1_STRICT:
            return self.xhtmlDtdStrictPath
        else:
            return self.xhtmlDtdTransPath
    # end _getDtdPath
    
    def tidyHtmlBody(self, htmlBody, izXhtmlValidationListener=None):
        u"""tidyHtmlBody(string, IZXhtmlValidationListener) -> (boolSuccess, tidyHtmlString, messageList)
        Runs Tidy on given xhtml body contents (i.e. children of <body> tag) as a string.
        This method returns the tuple (boolean, htmlResultString, list of ZXhtmlValidationMessage items).
        """ #$NON-NLS-1$
        
        if izXhtmlValidationListener:
            izXhtmlValidationListener.onXhtmlValidationStart()  
                  
        handler = ZXhtmlTidyCleanupHandler()
        (htmlResult, messageList, errorCount) = handler.runCleanupAndRunTidy(htmlBody, izXhtmlValidationListener)
        
        if izXhtmlValidationListener:
            izXhtmlValidationListener.onXhtmlValidationEnd( errorCount )
        if errorCount == 0:
            return (True, htmlResult, messageList)
        else:
            return (False, htmlBody, messageList)
            
    # end tidyHtmlBody()     
        
# end ZXhtmlValidatorImpl

#-----------------------------------------------------------
# Support class to clean up xhtml and run tidy.
#-----------------------------------------------------------
class ZXhtmlTidyCleanupHandler:
    
    def __init__(self):
        self.messageList = [] 
        self.zxhtmlValidationListener = None 
    # end __init__()
    
    def _clearMessages(self):
        self.messageList = []
    # end _clearMessages()
    
    def _addMessage(self, severity, line, col, message):
        m = ZXhtmlValidationMessage(severity, line, col, message)
        self.messageList.append(m)
        if self.zxhtmlValidationListener:
            self.zxhtmlValidationListener.onXhtmlValidationMessage(m)        
    # end _addMessage()
    
    def runCleanupAndRunTidy(self, htmlBodyString, izXhtmlValidationListener = None):
        # run tidy and return (htmlResultString, list of ZXhtmlValidationMessage, errorCount)
        self._clearMessages()
        self.zxhtmlValidationListener = izXhtmlValidationListener
        (ok, htmlBodyString) = self._cleanupMsOffice(htmlBodyString) #@UnusedVariable
        htmlBodyString = self._textToXhtml(htmlBodyString)
        htmlBodyString = self._runTidy(htmlBodyString)
        errCount = 0
        for msg in self.messageList:
            if msg.getSeverity() == ZXhtmlValidationMessage.ERROR or msg.getSeverity() == ZXhtmlValidationMessage.FATAL:
                errCount = errCount + 1 
        return (htmlBodyString, self.messageList, errCount)
    # end runCleanupAndRunTidy
    
    def _runTidy(self, xhtmlString):
        try:
            (tidyHtml, errorList) = runTidy(xhtmlString, SOURCE_OPTIONS)
            self._addTidyMessages(errorList)  
            if tidyHtml:
                xhtmlString = tidyHtml
            else:
                self._addMessage(ZXhtmlValidationMessage.FATAL,-1,-1,u"Tidy failed - Unknown reason.")  #$NON-NLS-1$
            
        except Exception, e:
            self._addMessage(ZXhtmlValidationMessage.FATAL,-1,-1,u"Tidy failed - %s"  % unicode(e) )  #$NON-NLS-1$
        return xhtmlString
    # end _runTidy
    
    def _addTidyMessages(self, tidyErrorList):
        for tidyError in tidyErrorList:
            # add ony error messages and ignore others.
            if tidyError.severity == ZTidyError.ERROR:
                self._addMessage(ZXhtmlValidationMessage.ERROR, tidyError.line, tidyError.col, tidyError.message)   
#            severity = ZXhtmlValidationMessage.INFO
#            msg = tidyError.message
#            if tidyError.severity == ZTidyError.WARN:
#                severity = ZXhtmlValidationMessage.WARNING
#            elif tidyError.severity == ZTidyError.ERROR:
#                severity = ZXhtmlValidationMessage.ERROR
#            elif tidyError.severity == ZTidyError.NONE:
#                msg = u"[NONE] " + msg #$NON-NLS-1$
#            elif tidyError.severity == ZTidyError.OTHER:
#                msg = u"[OTHER] " + msg #$NON-NLS-1$                
#            self._addMessage(severity, tidyError.line, tidyError.col, msg)    
    # end _addTidyMessages
    
    def _cleanupMsOffice(self, xhtmlString):
        bOk = True
        if xhtmlutil.hasMsOfficeMarkup(xhtmlString):            
            try:
                xhtmlString = xhtmlutil.cleanUpMsOfficeMarkup(xhtmlString)
                self._addMessage(ZXhtmlValidationMessage.INFO,-1, -1, u"Applied MS Office cleanup.")  #$NON-NLS-1$
            except:
                bOk = False
                self._addMessage(ZXhtmlValidationMessage.INFO,-1, -1, u"Failed cleaning up MS Office namespace markup.")  #$NON-NLS-1$
        return (bOk, xhtmlString)
    # end _cleanupMsOffice() 
    
    def _textToXhtml(self, xhtmlString):
        if not xhtmlutil.hasXhtmlMarkup(xhtmlString):
            self._addMessage(ZXhtmlValidationMessage.INFO, -1, -1, u"Converting plain text to xhtml markup.")  #$NON-NLS-1$
            # convert plain text to xhtml
            transformer = ZTextToXhtmlTransformer()
            xhtmlString = transformer.transform(xhtmlString)
        return xhtmlString
    #end _textToXhtml  
                     
# end ZXhtmlTidyCleanupHandler
# ------------------------------------------------------------
# XHTML validator using DTD
# ------------------------------------------------------------
class ZXhtmlDtDValidator(IZXhtmlValidator):

    XHTML_TEMPLATE=u"""<?xml version="1.0"?>
    <!DOCTYPE html SYSTEM "%s" >
    %s
    """  #$NON-NLS-1$

    XHTML_NO_BODY_TEMPLATE=u"""<?xml version="1.0"?>
    <!DOCTYPE html SYSTEM "%s" >
    <html>
    <head>
    <title>simple document</title>
    </head>
    <body>
    %s
    </body>
    </html>"""  #$NON-NLS-1$

    def __init__(self, dtdFilename):
        self.dtdFilename = dtdFilename
    # end__init__

    def getDtdFilename(self):
        u"""Returns xhtml DTD filename.""" #$NON-NLS-1$
        return self.dtdFilename
    # end getDtdFilename()

    def validateHtmlBody(self, htmlBody, izXhtmlValidationListener=None):
        dtdUri = getUriFromFilePath( self.getDtdFilename() )
        html = ZXhtmlDtDValidator.XHTML_NO_BODY_TEMPLATE % (dtdUri, htmlBody)
        return self._validate(html, 7, izXhtmlValidationListener)
    # end validateHtmlBody()

    def validateHtml(self, html, izXhtmlValidationListener=None):
        dtdUri = getUriFromFilePath( self.getDtdFilename() )
        html = ZXhtmlDtDValidator.XHTML_TEMPLATE % (dtdUri, html)
        return self._validate(html, 2, izXhtmlValidationListener)
    # end validateHtml()

    def _validate(self, html, offset = 0, izXhtmlValidationListener=None):
        #dtdDoc = xmldtd.load_dtd(self.getDtdFilename()) #@UnusedVariable
        val = xmlval.XMLValidator()
        handler = ZDtdParserHandlerApp(val, offset, izXhtmlValidationListener)
        val.set_application(handler)
        val.set_data_after_wf_error(0)
        val.set_error_handler(handler)
        if izXhtmlValidationListener:
            izXhtmlValidationListener.onXhtmlValidationStart()
        try:
            val.parser.parse_string(html)
        except Exception, e:
            if izXhtmlValidationListener:
                izXhtmlValidationListener.onXhtmlValidationException(e)
        messages = handler.getMessageList()
        if izXhtmlValidationListener:
            izXhtmlValidationListener.onXhtmlValidationEnd( len(messages) )
        return messages
    # end _validate()
# end ZXhtmlDtDValidator()

#-----------------------------------------------------
# HTML validating parser.
#-----------------------------------------------------
class ZDtdParserHandlerApp(xmlproc.Application):

    def __init__(self, val, offset=0, izXhtmlValidationListener=None):
       self._locator = val
       self.offset = offset
       self.izXhtmlValidationListener=izXhtmlValidationListener
       self.msgList = []
   # end __init__()

    def getMessageList(self):
        return self.msgList
    # end getMessageList()

    def handle_start_tag(self,name,attrs): #@UnusedVariable
        pass
    # end handle_start_tag

    def handle_end_tag(self,name): #@UnusedVariable
        pass
    # end handle_end_tag()

    def handle_data(self,data,start,end): #@UnusedVariable
        pass
    # end handle_data()

    def handle_comment(self,data): #@UnusedVariable
        pass
    # end handle_comment()

    def _handleMessage(self, severity, message):
        line = self._locator.get_line()- self.offset
        if line > 0:
            m = ZXhtmlValidationMessage(severity, line,self._locator.get_column(),message)
            self.msgList.append( m )
            if self.izXhtmlValidationListener:
                self.izXhtmlValidationListener.onXhtmlValidationMessage( m )
    # end _handleMessage()

    def warning(self, message):
        self._handleMessage(ZXhtmlValidationMessage.WARNING, message)
    # end warning()

    def error(self, message):
        self._handleMessage(ZXhtmlValidationMessage.ERROR, message)
    # end error()

    def fatal(self, message):
        self._handleMessage(ZXhtmlValidationMessage.FATAL, message)
    # end fatal()
# end ZDtdParserHandlerApp