from zoundry.base.util.text.textio import loadUnicodeContent
from zoundry.base.util.text.texttransform import ZTextToXhtmlTransformer
from zoundry.base.xhtml import xhtmlutil
from zoundry.base.xhtml.xhtmldoc import XHTML_NSS_MAP
from zoundry.base.xhtml.xhtmldoc import ZXhtmlDocument
from zoundry.base.zdom import tidyutil
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zdom.dom import ZElement


# --------------------------------------------------------------------------------
# Interface for xhtml serializer
# --------------------------------------------------------------------------------
class IZXhtmlSerializer:

    def serialize(self, node):
        u"""Returns serialized (string) given xhtml node. """  #$NON-NLS-1$
    # end serialize()

# end IZXhtmlSerializer


# --------------------------------------------------------------------------------
# Interface for xhtml de-serializer
# --------------------------------------------------------------------------------
class IZXhtmlDeserializer:

    def getMessages(self):
        u"""Returns any error or warning message during de-serialization process."""  #$NON-NLS-1$
    # end getMessages()

    def deserialize(self):
        u"""Returns ZXhtmlDocument or None if failed."""  #$NON-NLS-1$
    # end deserialize()

# end IZXhtmlDeserializer


# --------------------------------------------------------------------------------
# Base class of the xhtml IZXhtmlSerializer.
# --------------------------------------------------------------------------------
class ZXhtmlSerializerBase(IZXhtmlSerializer):

    def __init__(self):
        self.formatters = []
        self.transformers = []
    # end __init__()

    def addFormatter(self, formatter):
        u"""Add a IZXhtmlFormatter to preprocess/filter the xhtml node prior serialization"""  #$NON-NLS-1$
        if formatter and formatter not in self.formatters:
            self.formatters.append(formatter)
    # end addFormatter()

    def addStringTransform(self, stringTransformer):
        u"""Add a IZTextTransformer further process/filter the serialized xhtml string."""  #$NON-NLS-1$
        if stringTransformer and not stringTransformer in self.transformers:
            self.transformers.append(stringTransformer)
    # end addStringTransform()

    def serialize(self, node):
        u"""Returns the serialized string representation of the given node
        The node is first run through the list of optional IZXhtmlFormatter filters, followed by
        serialization to the string domain. The serialized string is further filtered and processed
        by running it via the list of IZTextTransformer transforms.
        """  #$NON-NLS-1$
        # node = node.clone()
        self._processNode(node)
        xhtmlStr = self._internalSerialize(node)
        xhtmlStr = self._processString(xhtmlStr)
        return xhtmlStr
    # end serialize()

    def _internalSerialize(self, node):
        u"""Returns the serialized string without any processing."""  #$NON-NLS-1$
        # node.serialize or return (child::**).serialize()
        return node.serialize()
    # end _internalSerialize()

    def _processNode(self, node):
        u"""Applies the list of IZXhtmlFormatter against the node."""  #$NON-NLS-1$
        for formatter in self.formatters:
            formatter.format(node)
    # end _processNode()

    def _processString(self, data):
        u"""Applies the list of IZTextTransformer transforms against the data string."""  #$NON-NLS-1$
        for transformer in self.transformers:
                data = transformer.transform(data)
        return data
    # end _processString()

# end ZXhtmlSerializerBase


# --------------------------------------------------------------------------------
# Basic implemetantation of IZXhtmlSerializer.
# --------------------------------------------------------------------------------
class ZXhtmlSerializer(ZXhtmlSerializerBase):

    def __init__(self):
        ZXhtmlSerializerBase.__init__(self)
        #FIXME (PJ)  add text filters  strip n/l, strip/replace nbsp;
        #FIXME (PJ) also provide option to return only <body> child nodes.
    # end __init__()

# end ZXhtmlSerializer


# --------------------------------------------------------------------------------
# IZXhtmlSerializer for saving to files.
# --------------------------------------------------------------------------------
class ZXhtmlFileSerializer(ZXhtmlSerializer):

    def __init__(self):
        ZXhtmlSerializer.__init__(self)
        #FIXME (PJ) add formatter( new PathResolverFormatter(filepath:uri), # set base uri )
    # end __init__()

    def save(self, node, filename):
        u"""Saves given node to a file."""  #$NON-NLS-1$
        xhtmlString = self.serialize(node)
        f = open(filename, u"w") #$NON-NLS-1$
        try:
            f.write(xhtmlString)
        finally:
            f.close()
    # end save()

# end ZXhtmlFileSerializer


# --------------------------------------------------------------------------------
# Basic implemetantation of IZXhtmlDeserializer.
# --------------------------------------------------------------------------------
class ZXhtmlDeserializer(IZXhtmlDeserializer):

    def __init__(self, inputResource = None):
        u"""Initializes with the given xhtml content source in the inputResource."""  #$NON-NLS-1$
        self.inputResource = inputResource
        self.deserialized = False
        self.messages = []
        self.document = None
    # end __init__()

    def getMessages(self):
        u"""Returns list of any error or warning messages."""  #$NON-NLS-1$
        self._deserialize()
        return self.messages
    # end getMessages()

    def deserialize(self):
        u"""Returns deserialized ZXhtmlDocument or None if error."""  #$NON-NLS-1$
        self._deserialize()
        return ZXhtmlDocument(self.document)
    # end deserialize()

    def _getXhtmlStringContent(self, inputResource):
        u"""Converts the give inputResource (string, filename or url) into xhtml string content."""  #$NON-NLS-1$
        # default case - inputResource param is xhtml string content. Return as is.
        return inputResource
    # end _getXhtmlStringContent()

    def _deserialize(self):
        u"""Deserializes the inputResource and creates the zDom document.""" #$NON-NLS-1$
        if self.deserialized:
            return
        try:
            # get string given input resource
            xhtmlString = self._getXhtmlStringContent(self.inputResource)
            # load document from string.
            self._deserializeString(xhtmlString)
        finally:
            self.deserialized = True
    # end _deserialize()

    def _deserializeString(self, xhtmlString):
        u"""Deserializes the xhtmlString and creates zDom. Once the dom is loaded, _processDocument is then called."""  #$NON-NLS-1$
        if not xhtmlString:
            self.messages.append(u"xhtml string content not available.")#$NON-NLS-1$
            xhtmlString = u"<xhtml><body> </body></xhtml>" #$NON-NLS-1$

        xhtmlString = self._prepareForLoading(xhtmlString)
        if xhtmlString:
            xhtmlString = self._tidyHtml(xhtmlString)
            doc = self._loadDocument(xhtmlString)
            if doc is None:
                self.messages.append(u"running html tidy (pass 2).")#$NON-NLS-1$
                xhtmlString = self._tidyHtml(xhtmlString)
                doc = self._loadDocument(xhtmlString)
            if doc:
                self.document = self._processDocument(doc)
            else:
                self.messages.append(u"Failed to load document from xhtml string content.")#$NON-NLS-1$
        else:
            self.messages.append(u"xhtml string content preparation failed.")#$NON-NLS-1$
    # end _deserializeString()

    def _prepareForLoading(self, xhtmlString):
        u"""Prepares the raw xhtml string for loading into zDom."""  #$NON-NLS-1$
        xhtmlString = xhtmlString.lstrip()
        if xhtmlString.startswith(u"<!DOCTYPE"): #$NON-NLS-1$
            xhtmlString = xhtmlString[xhtmlString.find(u">") + 1:] #$NON-NLS-1$

        xhtmlString = xhtmlString.replace(u'&nbsp;', u' ') #$NON-NLS-1$ #$NON-NLS-2$
        (bOk, xhtmlString) = self._cleanupMsOffice(xhtmlString) #@UnusedVariable

        # if the string content does not have a <body/> then convert to xhtml and wrap it
        # with <html><body/></html>
        if not xhtmlutil.hasBody(xhtmlString):
            if not xhtmlutil.hasXhtmlMarkup(xhtmlString):
                self.messages.append(u"Converting plain text to xhtml markup.")  #$NON-NLS-1$
                # convert plain text to xhtml
                transformer = ZTextToXhtmlTransformer()
                xhtmlString = transformer.transform(xhtmlString)
            xhtmlString = xhtmlutil.wrapHtmlBody(xhtmlString)
            self.messages.append(u"Adding <html><body></body></html> wrapper.")  #$NON-NLS-1$
        return xhtmlString
    # end _prepareForLoading()

    def _cleanupMsOffice(self, xhtmlString):
        bOk = True
        if xhtmlutil.hasMsOfficeMarkup(xhtmlString):
            self.messages.append(u"Attempting to cleanup MS Office namespace markup.")  #$NON-NLS-1$
            try:
                xhtmlString = xhtmlutil.cleanUpMsOfficeMarkup(xhtmlString)
            except:
                bOk = False
                self.messages.append(u"Failed cleaning up MS Office namespace markup.")  #$NON-NLS-1$
        return (bOk, xhtmlString)
    # end _cleanupMsOffice()

    def _tidyHtml(self, xhtmlString):
        xhtmlString = tidyutil.tidyHtml(xhtmlString, tidyutil.EDITING_OPTIONS)
        xhtmlString = xhtmlString.replace(u"""<?xml version="1.0" encoding="utf-8"?>""", u"") #$NON-NLS-1$ #$NON-NLS-2$
        return xhtmlString.lstrip()
    # end _tidyHtml()

    def _loadDocument(self, xhtmlString):
        u"""Attempts to load zDom."""  #$NON-NLS-1$        
        dom = self._createDocument(xhtmlString, True)
        return dom
        #clean up msword, wrap html, tidy, text2html etc.
        #strip/replace nbsp;
    # end _loadDocument()

    def _createDocument(self, xhtmlString, throwOnError = False):
        u"""Creates and loads the given string into the zDom."""  #$NON-NLS-1$
        xhtmlString = xhtmlString.lstrip()
        if xhtmlString.startswith(u"<!DOCTYPE"): #$NON-NLS-1$
            xhtmlString = xhtmlString[xhtmlString.find(u">") + 1:] #$NON-NLS-1$
        try:
            dom = ZDom()
            dom.setNamespaceMap(XHTML_NSS_MAP)
            dom.loadXML(xhtmlString)
            return dom
        except:
            if throwOnError:
                raise
            return None
    # end _createDocument()

    def _processDocument(self, document):
        u"""Entry point to further process/filter loaded document."""  #$NON-NLS-1$
        return document
    # end _processDocument()

# end ZXhtmlDeserializer


# --------------------------------------------------------------------------------
# IZXhtmlDeserializer implementation for deserializing from files.
# --------------------------------------------------------------------------------
class ZXhtmlFileDeserializer(ZXhtmlDeserializer):

    def __init__(self, resourceUri):
        u"""Initializes with the given resourceUri which should be a valid filename."""  #$NON-NLS-1$
        self.resourceUri = resourceUri
        ZXhtmlDeserializer.__init__(self, resourceUri)
    # end __init__()

    def getResourceUri(self):
        u"""Returns the resource uri (filename or URL)"""  #$NON-NLS-1$
        return self.resourceUri
    # end getResourceUri()

    def _getXhtmlStringContent(self, inputResource):
        u"""Loads and returns the string content from the given inputResource filename"""  #$NON-NLS-1$
        # resourceUri is filename = load xhtml from file.
        xhtmlString = loadUnicodeContent(inputResource)
        return xhtmlString
    # end _getXhtmlStringContent()

    def _processDocument(self, document):
        # FIXME (PJ) fixImageFilepaths(getDocument()) - handle image and link relative path - convert to abs path , set base uri
        return document
    # end _processDocument()

# end ZXhtmlFileDeserializer


# --------------------------------------------------------------------------------
# IZXhtmlDeserializer implemetation for deserializing from URLs
# --------------------------------------------------------------------------------
class ZXhtmlUriDeserializer(ZXhtmlFileDeserializer):

    def __init__(self, resourceUri):
        u"""Initializes with the given resourceUri which should be a valid filename."""  #$NON-NLS-1$
        self.resourceUri = resourceUri
        ZXhtmlFileDeserializer.__init__(self, resourceUri)
    # end __init__()

    def _getXhtmlStringContent(self, inputResource):
        # FIXME (PJ) resourceUri is url = load xhtml from url.
        return inputResource
    # end _getXhtmlStringContent()

# end ZXhtmlUriDeserializer


# --------------------------------------------------------------------------------
# IZXhtmlDeserializer implemetation for deserializing from a DOM Node
# --------------------------------------------------------------------------------
class ZXhtmlDOMDeserializer(ZXhtmlDeserializer):
    
    def __init__(self, node):
        self.node = node
        
        ZXhtmlDeserializer.__init__(self, None)
    # end __init__()

    # Overrides to attempt to create an xhtml document from the Node.
    # If the Node is not an x:html element, then this will serialize
    # the node and revert to the basic String-based deserializer
    def deserialize(self):
        if isinstance(self.node, ZElement) and self.node.localName == u"html": #$NON-NLS-1$
            return ZXhtmlDocument(self.node)
        elif self.node is None:
            self.inputResource = u"" #$NON-NLS-1$
        else:
            self.inputResource = self.node.serialize()

        return ZXhtmlDeserializer.deserialize(self)
    # end deserialize()
    
# end ZXhtmlDOMDeserializer

def loadXhtmlDocumentFromFile(filename):
    u"""loadXhtmlDocumentFromFile(file) -> ZXhtmlDocument""" #$NON-NLS-1$
    deserializer = ZXhtmlFileDeserializer(filename)
    return deserializer.deserialize()
# end loadXhtmlDocumentFromFile()

def loadXhtmlDocumentFromString(htmlString):
    u"""loadXhtmlDocumentFromString(string) -> ZXhtmlDocument""" #$NON-NLS-1$
    deserializer = ZXhtmlDeserializer(htmlString)
    return deserializer.deserialize()
# end loadXhtmlDocumentFromString()

def loadXhtmlDocumentFromDOM(domNode):
    u"""loadXhtmlDocumentFromDOM(zdom) -> ZXhtmlDocument""" #$NON-NLS-1$
    deserializer = ZXhtmlDOMDeserializer(domNode)
    return deserializer.deserialize()
# end loadXhtmlDocumentFromDOM()

