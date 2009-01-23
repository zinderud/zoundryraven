from Ft.Xml import InputSource
from Ft.Xml.Domlette import NonvalidatingReaderBase
from Ft.Xml.Domlette import PrettyPrint
from Ft.Xml.Domlette import Print
from Ft.Xml.XPath import Evaluate
from Ft.Xml.XPath.Context import Context
from Ft.Xml.Xslt import Processor
from Ft.Xml.Xvif import RelaxNgValidator
from tidyutil import XHTML_OPTIONS
from tidyutil import tidyHtml
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.unicodeutil import convertToUnicode
import StringIO

# FIXME rename zdom package to dom

RELAX_NG_VALIDATION = 1
W3C_VALIDATION = 2
DTD_VALIDATION = 3

BOGUS_ZOUNDRY_URI = u"urn:com.zoundry.bogus/2006/02" #$NON-NLS-1$

def isSimpleType(node):
    return \
        isinstance(node, str) or \
        isinstance(node, unicode) or \
        isinstance(node, float) or \
        isinstance(node, int) or \
        isinstance(node, bool)
# end isSimpleType()

def zNodeFactory(node, dom):
    if node:
        if isSimpleType(node):
            rval = dom.createElement(u"result") #$NON-NLS-1$
            rval.setText(unicode(node))
            return rval
        elif node.nodeType == 1:
            return ZElement(node, dom)
        elif node.nodeType == 2:
            return ZAttr(node, dom)
        else:
            return ZNode(node, dom)
    return None
# end zNodeFactory()

def applyZNodeFactoryToList(nodeList, dom):
    zNodeList = []
    for n in nodeList:
        zNodeList.append(zNodeFactory(n, dom))
    return zNodeList
#end applyZNodeFactoryToList()


# --------------------------------------------------------------------------------
# Wrapper around the Python XML Node object to provide integrated
# XPath support as well as various convenience methods.
#
# To access the actual XML Node, use the 'node' member variable (attribute).
# --------------------------------------------------------------------------------
class ZNode:
    u"""Wrapper around the Python XML Node object to provide integrated
        XPath support as well as various convenience methods.

        To access the actual XML Node, use the 'node' member variable (property).""" #$NON-NLS-1$

    # Constructor
    def __init__(self, node, dom):
        self.node = node
        self.ownerDom = dom
    # end __init__()

    # Returns a list of ZNode or ZElement wrappers for each
    #   Python XML node that matches the expression
    # If the expression does not match, returns an empty list
    def selectNodes(self, expression, nssMap = None):
        ctx = None
        if nssMap:
            ctx = Context(self.node, processorNss = nssMap)
        if not ctx:
            ctx = self.ownerDom.context
        result = Evaluate(expression, self.node, ctx)
        if result:
            return applyZNodeFactoryToList(result, self.ownerDom)
        else:
            return []
    # end selectNodes()

    # If the expression matches, returns a ZNode or ZElement
    #   wrapper around the *first* Python XML node in the list
    # If the expression does not match, returns None
    def selectSingleNode(self, expression, nssMap = None):
        ctx = None
        if nssMap:
            ctx = Context(self.node, processorNss = nssMap)
        if not ctx:
            ctx = self.ownerDom.context
        result = Evaluate(expression, self.node, ctx)
        if result and len(result) > 0:
            return zNodeFactory(result[0], self.ownerDom)
    # end selectSingleNodes()

    # Returns the text for the node pointed to by the xpath expression.  If the
    # node is not found, returns the given dflt or None if not supplied.
    def selectSingleNodeText(self, expression, dflt = None, nssMap = None):
        elem = self.selectSingleNode(expression, nssMap)
        if not elem:
            return dflt
        return elem.getText()
    # end selectSingleNodeText()

    # Returns the raw result from executing the given xpath expression.
    def selectRaw(self, expression, dflt = None, nssMap = None):
        ctx = None
        if nssMap:
            ctx = Context(self.node, processorNss = nssMap)
        if not ctx:
            ctx = self.ownerDom.context
        result = Evaluate(expression, self.node, ctx)
        if result:
            return result
        else:
            return dflt
    # end selectRaw()

    # Wrapper around XML Node's removeChild() method
    # The removed child is returned
    # Warning: this method can raise a ValueError
    def removeChild(self, child):
        self.node.removeChild(child.node)
        return child
    # end removeChild()
    
    def removeAllChildren(self):
        for child in self.getChildren():
            self.removeChild(child)
    # end removeAllChildren()

    # Wrapper around XML Node's appendChild() method
    # The appended child is returned
    # Warning: this method can raise a ValueError
    def appendChild(self, child):
        self.node.appendChild(child.node)
        return child
    # end appendChild()

    # Wrapper around XML Node's cloneNode() method
    # The clone is returned
    # Warning: this method can raise a ValueError
    def cloneNode(self, deep):
        return zNodeFactory(self.node.cloneNode(deep), self.ownerDom)
    # end cloneNode()

    # 2004/04/28/PJ :replaceChild
    def replaceChild(self, newChild, oldChild):
        return self.node.replaceChild(newChild.node, oldChild.node)
    # end replaceChild()

    def insertBefore(self, newChild, refChild):
        return self.node.insertBefore(newChild.node, refChild.node)
    # end insertBefore()

    def normalize(self):
        return self.node.normalize()
    # end normalize()

    def getChildren(self):
        try:
            children = self.node.childNodes
            return applyZNodeFactoryToList(children, self.ownerDom)
        except Exception, e:
            raise ZException(u"Error getting Node children.", e) #$NON-NLS-1$
    # end getChildren()

    # dynamic attributes ...
    def __getattr__(self, name):
        if name == u"parentNode": #$NON-NLS-1$
            return zNodeFactory(self.node.parentNode, self.ownerDom)
        elif name == u"nodeType": #$NON-NLS-1$
            return self.node.nodeType
        elif name == u"nodeValue": #$NON-NLS-1$
            return self.node.nodeValue

        # 2004/04/28/PJ: added attr for 'localName'.
        elif name == u"localName": #$NON-NLS-1$
            return self.node.localName
        elif name == u"nodeName": #$NON-NLS-1$
            return self.node.nodeName
        elif name == u"ownerDocument": #$NON-NLS-1$
            return self.ownerDom
        elif name == u"childNodes": #$NON-NLS-1$
            return applyZNodeFactoryToList(self.node.childNodes, self.ownerDom)
        else:
            raise AttributeError, name
    # end __getattr__

    # Saves the DOM to the given file-like object.
    def _saveToFile(self, file, pretty=False, asHtml=False):
        if pretty:
            PrettyPrint(self.node, file, asHtml=asHtml)
        else:
            Print(self.node, file, asHtml=asHtml)
    # end _saveToFile()

    # Saves the node to a file.
    def save(self, fileName, append=False, pretty=False, asHtml=False):
        try:
            mode = u"w" #$NON-NLS-1$
            if append:
                mode = u"a" #$NON-NLS-1$
            ofile = open(fileName, mode)
            self._saveToFile(ofile, pretty, asHtml)
            ofile.close()
        except Exception, e:
            raise ZException(u"Error saving node to file '%s'." % fileName, e) #$NON-NLS-1$
    # end save()

    # Serializes the node to an XML string.
    def serialize(self, pretty=False, asHtml=False):
        u"""Serializes the node to a string.""" #$NON-NLS-1$
        stream = StringIO.StringIO()
        self._saveToFile(stream, pretty, asHtml)
        rval = convertToUnicode(stream.getvalue())
        stream.close()
        return rval
    # end serialize()

    # Validates this node against the given Relax NG schema.
    def validate(self, schemaXML, type = RELAX_NG_VALIDATION):
        if type == RELAX_NG_VALIDATION:
            schemaIsrc = InputSource.DefaultFactory.fromString(str(schemaXML), BOGUS_ZOUNDRY_URI)
            validator = RelaxNgValidator(schemaIsrc)
            result = validator.validateNode(self.node)
            if not result.nullable():
                raise ZException(result.msg)
        elif type == W3C_VALIDATION:
            raise ZException(u"W3C validation not currently supported.") #$NON-NLS-1$
        elif type == DTD_VALIDATION:
            raise ZException(u"DTD validation not currently supported.") #$NON-NLS-1$
    # end validateRelaxNG()

#end class ZNode


# --------------------------------------------------------------------------------
# Zoundry wrapper class for an XML Attribute.
# --------------------------------------------------------------------------------
class ZAttr(ZNode):
    u"""
    Wrapper around the Python XML Attr object to provide integrated
    XPath support as well as various convenience methods.

    To access the actual XML Attr node, use the 'attr' member variable (property)
    """ #$NON-NLS-1$

    # Constructor
    def __init__(self, attr, dom):
        ZNode.__init__(self, attr, dom)
        self.attr = attr
    # end __init__()

    # Returns the attribute's text or the default.
    # Will NOT throw
    def getText(self, default = u""): #$NON-NLS-1$
        try:
            return convertToUnicode(self.attr.nodeValue)
        except:
            return default
    # end getText()

    # Sets the value of the attribute.
    # Will NOT throw
    def setText(self, value):
        value = convertToUnicode(value)
        try:
            self.attr.nodeValue = value
        except Exception, e:
            raise ZException(u"Error setting the text of an attribute.", e) #$NON-NLS-1$
    # end setText()

#end class ZAttr


# --------------------------------------------------------------------------------
# Zoundry wrapper class for an XML Element.
# --------------------------------------------------------------------------------
class ZElement(ZNode):
    u"""
    Wrapper around the Python XML Element object to provide integrated
    XPath support as well as various convenience methods.

    To access the actual XML Element, use the 'element' member variable (property)
    """ #$NON-NLS-1$

    # Constructor
    def __init__(self, element, dom):
        ZNode.__init__(self, element, dom)
        self.element = element
    # end __init__()

    def getNamespaceUri(self):
        return self.element.namespaceURI
    # end getNamespaceUri()

    # Convenience method to retrieve the attribute value for attributes
    # without namespaces.
    # Returns attribute value or the default value. Will NOT throw.
    def getAttribute(self, attribute, default = u""): #$NON-NLS-1$
        try:
            value = self.node.getAttributeNS(None, attribute)
            if not value or len(value) == 0:
                value = default
        except Exception, e:
            raise ZException(u"Error getting an attribute ('%s')." % attribute, e) #$NON-NLS-1$
        return convertToUnicode(value)
    #end getAttribute()

    # Returns a list of all ZAttr children of the Element.
    def getAttributes(self):
        try:
            return applyZNodeFactoryToList(self.node.attributes.values(), self.ownerDom)
        except Exception, e:
            raise ZException(u"Error getting attributes.", e) #$NON-NLS-1$
    # end getAttributes()

    # Convenience method to set the attribute value for attributes
    # without namespaces.
    def setAttribute(self, attribute, value):
        if (value):
            value = convertToUnicode(value)
            try:
                self.node.setAttributeNS(None, attribute, value)
            except Exception, e:
                raise ZException(u"Error setting an attribute.", e) #$NON-NLS-1$
    #end setAttribute()

    def removeAttribute(self, attribute):
        if attribute:
            try:
                self.node.removeAttributeNS(None, attribute)
            except Exception, e:
                raise ZException(u"Error removing an attribute.", e) #$NON-NLS-1$
    # end removeAttribute()

    # Returns the element's text (concatenates all text nodes) or the default
    # Will NOT throw
    def getText(self, default = u""): #$NON-NLS-1$
        try:
            text = u"" #$NON-NLS-1$
            jnodes = self.selectNodes(u"text()") #$NON-NLS-1$
            for jn in jnodes:
                text = text + jn.node.nodeValue
            return convertToUnicode(text)
        except:
            return default
    #end getText()

    def setText(self, value):
        try:
            if not value:
                value = u"" #$NON-NLS-1$
            value = convertToUnicode(value)

            newTextNode = self.element.ownerDocument.createTextNode(value)
            childNodes = self.element.childNodes
            for childNode in childNodes:
                self.element.removeChild(childNode)
            self.element.appendChild(newTextNode)
        except Exception, e:
            raise ZException(u"Error setting the text of an Element.", e) #$NON-NLS-1$
    #end setText()
    
    def addTextNode(self, value):
        try:
            if not value:
                value = u"" #$NON-NLS-1$
            value = convertToUnicode(value)

            newTextNode = self.element.ownerDocument.createTextNode(value)
            self.element.appendChild(newTextNode)
        except Exception, e:
            raise ZException(u"Error adding text node to an Element.", e) #$NON-NLS-1$
    # end addTextNode()

    def appendText(self, value):
        try:
            if not value:
                value = u"" #$NON-NLS-1$
            value = convertToUnicode(value)
            newTextNode = self.element.ownerDocument.createTextNode(value)
            self.element.appendChild(newTextNode)
        except Exception, e:
            raise ZException(u"Error appending text to an Element.", e) #$NON-NLS-1$
    # end appendText()

#end class ZElement


# --------------------------------------------------------------------------------
# This class is the main Zoundry API Document Object Model class.  The DOM object
# is an in-memory representation of an XML document.
# --------------------------------------------------------------------------------
class ZDom:
    u"""
    Wrapper around the 4Suite Domlette object to provide integrated
    XPath support as well as various convenience methods.

    To access the actual DOM, use the 'dom' member variable (property)
    """ #$NON-NLS-1$

    # Constructor
    def __init__(self, xmlString = None):
        self.dom = None
        self.context = None
        
        if xmlString is not None:
            self.loadXML(xmlString)
    # end __init__()

    # This method could throw a ZException exception if the file cannot
    # be parsed (or found).  The file needs to be in utf-8 format I believe.
    def load(self, fileName, baseUri = BOGUS_ZOUNDRY_URI):
        try:
            f = open(fileName, u"r") #$NON-NLS-1$
            try:
                self.loadFromStream(f, baseUri)
            finally:
                f.close()
        except Exception, e:
            raise ZException(u"Error loading XML file '%s' [%s]." % (fileName, unicode(e)), e) #$NON-NLS-1$
    # end load()

    # This method could throw a ZException exception if the XML is not well-formed.
    def loadXML(self, xml, baseUri = BOGUS_ZOUNDRY_URI):
        if isinstance(xml, unicode):
            xml = xml.encode(u"utf8") #$NON-NLS-1$
        try:
            # using a thread safe reader instead of the "global" reader
            reader = NonvalidatingReaderBase()
            self.dom = reader.parseString(xml, baseUri)
            del reader  # helps with garbage collection
        except Exception, e:
            raise ZException(u"Error loading XML [%s]." % unicode(e), e) #$NON-NLS-1$
    # end loadXML()


    # Loads an HTML document.  It is first tried without modification.  If that fails, then
    # Html Tidy is called to convert the HTML to XHTML.
    def loadHTML(self, html, baseUri = None):
        # FIXME: PJ - remove this loadHTML method. ZDom should load only valid xml files. For xhtml files, use xhtml deserializer.
        # Try it as XHTML first.
        try:
            self.loadXML(html, baseUri)
            return
        except:
            pass

        # Strip away the HTML <!DOCTYPE ...> preamble if it's there.
        if html.startswith(u"<!DOCTYPE"): #$NON-NLS-1$
            html = html[html.find(u">") + 1:] #$NON-NLS-1$

        # Convert to UTF8 if we're dealing with a unicode string.
        if isinstance(html, unicode):
            html = html.encode(u"utf8") #$NON-NLS-1$
        try:
            # Use Tidy to convert HTML to XML
            output = tidyHtml(html, XHTML_OPTIONS)
            self.loadXML(output)
        except Exception, e:
            raise ZException(u"Error loading HTML.", e) #$NON-NLS-1$
    # end loadHTML()

    # This method could throw a ZException exception if the XML is not well-formed.
    def loadFromStream(self, stream, baseUri = BOGUS_ZOUNDRY_URI):
        u"""Loads XML content from a (previously opened) stream.""" #$NON-NLS-1$
        try:
            reader = NonvalidatingReaderBase()
            self.dom = reader.parseStream(stream, baseUri)
            del reader  # helps with garbage collection
        except Exception, e:
            raise ZException(u"Error loading XML from stream.", e) #$NON-NLS-1$
    # end loadFromStream()

    # Saves the DOM to a file-like object.
    def _saveToFile(self, file, pretty=False):
        try:
            if pretty:
                PrettyPrint(self.dom, file)
            else:
                Print(self.dom, file)
            return True
        except Exception, e:
            raise ZException(u"Error saving XML to file.", e) #$NON-NLS-1$
    # end _saveToFile()

    # Saves the DOM to a file (the filename is given as the first param).
    def save(self, fileName, pretty=False):
        try:
            ofile = open(fileName, u"w") #$NON-NLS-1$
            try:
                self._saveToFile(ofile, pretty)
            finally:
                ofile.close()
        except Exception, e:
            raise ZException(u"Error saving XML to file '%s'." % fileName, e) #$NON-NLS-1$
    # end save()

    # This method serializes the DOM to a string which it returns.
    def serialize(self, pretty=False):
        u"""Serializes the DOM to a string.""" #$NON-NLS-1$
        stream = StringIO.StringIO()
        self._saveToFile(stream, pretty)
        return convertToUnicode(stream.getvalue())
    # end serialize()

    # Validates this dom against the given Relax NG schema.
    def validate(self, schemaXML, type = RELAX_NG_VALIDATION):
        if type == RELAX_NG_VALIDATION:
            try:
                schemaIsrc = InputSource.DefaultFactory.fromString(str(schemaXML), BOGUS_ZOUNDRY_URI)
                validator = RelaxNgValidator(schemaIsrc)
                result = validator.validateNode(self.dom)
                # TODO (EPW):  handle case where rng validation fails if there is a xml comment before the root element.
                if not result.nullable():
                    raise ZException(result.msg)
            except ZException, ze:
                raise ze
            except Exception, e:
                raise ZException(rootCause = e)
            except:
                raise ZException(u"RNG validation failed.") #$NON-NLS-1$
        elif type == W3C_VALIDATION:
            raise ZException(u"W3C validation currently not supported.") #$NON-NLS-1$
        elif type == DTD_VALIDATION:
            raise ZException(u"DTD validation currently not supported.") #$NON-NLS-1$
    # end validateRelaxNG()

    def transform(self, transformFilename):
        processor = Processor.Processor()
        transform = InputSource.DefaultFactory.fromStream(open(transformFilename, u"r"), BOGUS_ZOUNDRY_URI) #$NON-NLS-1$
        processor.appendStylesheet(transform)
        return processor.runNode(self.dom, None)
    # end transform()

    def transformToXML(self, transformFilename):
        processor = Processor.Processor()
        transform = InputSource.DefaultFactory.fromStream(open(transformFilename, u"r"), BOGUS_ZOUNDRY_URI) #$NON-NLS-1$
        processor.appendStylesheet(transform)
        str = processor.runNode(self.dom, None)
        rdom = ZDom()
        rdom.loadXML(str)
        return rdom
    # end transformToXML()

    # Returns a list of ZNode or ZElement wrappers for each
    #   Python XML node that matches the expression
    # If the expression does not match, returns an empty list
    def selectNodes(self, expression, nssMap = None):
        ctx = None
        if nssMap:
            ctx = Context(self.dom, processorNss = nssMap)
        if not ctx:
            ctx = self.context
        result = Evaluate(expression, self.dom.documentElement, ctx)
        if result:
            return applyZNodeFactoryToList(result, self)
        else:
            return []
    # end selectNodes()

    # If the expression matches, returns a ZNode or ZElement
    #   wrapper around the *first* Python XML node in the list
    # If the expression does not match, returns None
    def selectSingleNode(self, expression, nssMap = None):
        ctx = None
        if nssMap:
            ctx = Context(self.dom, processorNss = nssMap)
        if not ctx:
            ctx = self.context
        result = Evaluate(expression, self.dom.documentElement, ctx)
        if result:
            if isinstance(result, list):
                return zNodeFactory(result[0], self)
            else:
                return zNodeFactory(result, self)
        #end if
    # end selectSingleNode()

    # Returns the text for the node pointed to by the xpath expression.  If the
    # node is not found, returns the given dflt or None if not supplied.
    def selectSingleNodeText(self, expression, dflt = None, nssMap = None):
        elem = self.selectSingleNode(expression, nssMap)
        if not elem:
            return dflt
        return elem.getText()
    # end selectSingleNodeText()

    # Wrapper method for XML DOM createElement() method
    def createElement(self, tag, namespace = None):
        return ZElement(self.dom.createElementNS(namespace, tag), self)
    # end createElement()

    # Wrapper method for XML DOM createComment() method
    def createComment(self, comment):
        return ZNode(self.dom.createComment(comment) , self)
    # end createComment()

    # Wrapper around XMLDOM's importNode() method
    # The imported ZNode is returned
    # Warning: this method can raise a ValueError
    def importNode(self, node, deep):
        newNode = self.dom.importNode(node.node, deep)
        return zNodeFactory(newNode, self.dom)
    # end importNode()

    # Creates a context for the DOM with a given map from namespace prefix to namespace uri.
    def setNamespaceMap(self, namespaceMap):
        self.context = Context(self.dom, processorNss = namespaceMap)
        return self.context
    # end setNamespaceMap()

    # dynamic attributes ...
    def __getattr__(self, name):
        if name == u"documentElement": #$NON-NLS-1$
            if self.dom.documentElement is None:
                return None
            else:
                return ZElement(self.dom.documentElement, self)
        else:
            raise AttributeError, name
    #end __getattr__

#end class ZDom
