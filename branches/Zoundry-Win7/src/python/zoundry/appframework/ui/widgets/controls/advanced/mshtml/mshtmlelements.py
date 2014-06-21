from zoundry.base.xhtml.xhtmltelements import ZXhtmlElement
from zoundry.base.xhtml.xhtmltelements import ZXhtmlImage
from zoundry.base.xhtml.xhtmltelements import ZXhtmlLink
from zoundry.base.zdom.domvisitor import ZDomTraverser
from pywintypes import IID #@UnresolvedImport
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.zdom.dom import ZAttr
from zoundry.base.zdom.dom import ZElement
from zoundry.base.zdom.dom import ZNode
from zoundry.base.zdom.domvisitor import ZDomVisitor
import win32com.client

#-----------------------------------------------------------------------------
# List of elem names
#-----------------------------------------------------------------------------
# xhtml block level elements
CSV_BLOCKS = u"address,blockquote,center,dir,div,dl,fieldset,form,h1,h2,h3,h4,h5,h6,hr" #$NON-NLS-1$
CSV_BLOCKS = CSV_BLOCKS + u"isindex,menu,noframes,noscript,ol,p,pre,table,ul" #$NON-NLS-1$
# child elements that can contain other block elements
CSV_CHILD_BLOCKS = u"dd,dt,frameset,li,tbody,td,tfoot,th,thead,tr" #$NON-NLS-1$
# inline and block elements
CSV_INLINE_BLOCKS = u"applet,button,del,iframe,ins,map,object,script" #$NON-NLS-1$
# elements that can have an hr element
CSV_HR_PARENTS = u"body,blockquote,div,li,dd,ins,del,th,td" #$NON-NLS-1$

BLOCK_LIST = [u"p", u"div" , u"del" , u"ins" , u"ul" , u"ol" , u"blockquote"] #$NON-NLS-6$ #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-7$
#XHTML_BLOCK_LEVEL_ELEMENTS = [u"p", u"div", u"blockquote", u"pre", u"hr", u"br", u"h1", u"h2", u"h3", u"h4", u"h5", u"h6"]
XHTML_BLOCK_LEVEL_ELEMENTS = CSV_BLOCKS.split(u",") #$NON-NLS-1$
XHTML_CHILD_BLOCK_LEVEL_ELEMENTS = CSV_CHILD_BLOCKS.split(u",") #$NON-NLS-1$
XHTML_INLINE_BLOCK_LEVEL_ELEMENTS = CSV_INLINE_BLOCKS.split(u",") #$NON-NLS-1$
XHTML_HR_PARENT_ELEMENTS = CSV_HR_PARENTS.split(u",") #$NON-NLS-1$


#----------------------------------------
# ZNode and ZElement wrappers around the corresponding MSHTML elements
#----------------------------------------

def isMshtmlSimpleType(node):
    return \
        isinstance(node, str) or \
        isinstance(node, unicode) or \
        isinstance(node, float) or \
        isinstance(node, int) or \
        isinstance(node, bool)
# end isSimpleType()

def zMshtmlNodeFactory(node, dom):
    if node:
        if isMshtmlSimpleType(node):
            rval = dom.createElement(u"result") #$NON-NLS-1$
            rval.setText(unicode(node))
            return rval
        elif node.nodeType == 1:
            return ZMshtmlElement(node)
        elif node.nodeType == 2:
            return ZMshtmlAttr(node)
        else:
            return ZMshtmlNode(node)
    return None
# end zNodeFactory()

def applyZMshtmlNodeFactoryToList(nodeList, dom):
    zNodeList = []
    for n in nodeList:
        zNodeList.append(zMshtmlNodeFactory(n, dom))
    return zNodeList
#end applyZNodeFactoryToList()

# --------------------------------------------------------------------------------
# Returns the IDispatch object given MSHTML element interface.
# --------------------------------------------------------------------------------
def getDispElement(ihtmlElement):
    try:
        dispEle = win32com.client.Dispatch(ihtmlElement, IID(u'{3050F1FF-98B5-11CF-BB82-00AA00BDCE0B}')) #$NON-NLS-1$        
        return dispEle
    except:
        # FIXME (PJ) log error 
        return None
# --------------------------------------------------------------------------------
# Returns the ZMshtmlElement object given MSHTML element interface (from MSHTMLDocument)
# --------------------------------------------------------------------------------
def createMshtmlElementFromIHTMLElement(ihtmlElement):
    dispElem = getDispElement(ihtmlElement)
    elem = ZMshtmlElement(dispElem)
    return elem

# --------------------------------------------------------------------------------
# Creates and returns an instance of IZXhtmlElement MSHTML element interface (from MSHTMLDocument)
# Returns IZXhtmlLink for a link
# Returns IZXhtmlImage for an image
# Returns IZXhtmlElement for all other cases.
# --------------------------------------------------------------------------------
def createIZXhtmlElementFromIHTMLElement(ihtmlElement):
    izXhtmlElement = None
    if ihtmlElement:
        elem = createMshtmlElementFromIHTMLElement(ihtmlElement)
        if ihtmlElement.tagName == u"A": #$NON-NLS-1$
            izXhtmlElement = ZXhtmlLink(elem, 0)
        elif ihtmlElement.tagName == u"IMG": #$NON-NLS-1$
            izXhtmlElement = ZXhtmlImage(elem, 0)
        else:
            izXhtmlElement = ZXhtmlElement(elem)        
    return izXhtmlElement
# --------------------------------------------------------------------------------
# Wrapper around the MSHTML XML Node object.
# --------------------------------------------------------------------------------
class ZMshtmlNode(ZNode):
    u"""Wrapper around the MSHTML IHTMLDOMNode dispatch object.
""" #$NON-NLS-1$

    # Constructor
    def __init__(self, node):  
        # Node is MSHTML IHTMLDOMNode 
        self.node = node
        self.ownerDom = node.ownerDocument
    # end __init__()
    
        
    def _setAttribute(self, name, value):
        if self.node.nodeType == 1 and name and value is not None:
            value = convertToUnicode(value)
            if name == u"style": #$NON-NLS-1$
                self.node.style.cssText = value
            else:
                attrs = self.node.attributes
                # remove old attr
                attrs.removeNamedItem(name)
                # create new attr
                namedItem = self.ownerDom.createAttribute(name)
                namedItem.value = value
                attrs.setNamedItem(namedItem);
                
    def _getAttribute(self, name):
        rval = None
        if self.node.nodeType == 1 and name:
            if name == u"style": #$NON-NLS-1$
                rval = self.node.style.cssText
            else:            
                attrs = self.node.attributes
                namedItem = attrs.getNamedItem(name)
                if namedItem:
                    rval = convertToUnicode(namedItem.value)
        return rval
    
    def _removeAttribute(self, name):
        if self.node.nodeType == 1 and name:
            attrs = self.node.attributes
            attrs.removeNamedItem(name)

    def selectNodes(self, expression, nssMap = None):
        raise ZException(u"selectNodes() not currently supported.") #$NON-NLS-1$        
    # end selectNodes()

    def selectSingleNode(self, expression, nssMap = None):
        raise ZException(u"selectSingleNode() not currently supported.") #$NON-NLS-1$
    # end selectSingleNodes()

    def selectSingleNodeText(self, expression, dflt = None, nssMap = None):
        raise ZException(u"selectSingleNodeText() not currently supported.") #$NON-NLS-1$
    # end selectSingleNodeText()

    def removeChild(self, child):
        raise ZException(u"removeChild() not currently supported.") #$NON-NLS-1$
    # end removeChild()

    def appendChild(self, child):
        raise ZException(u"appendChild() not currently supported.") #$NON-NLS-1$
    # end appendChild()

    def cloneNode(self, deep):
        clone = self.node.cloneNode(deep)
        return zMshtmlNodeFactory(clone, self.ownerDom)
    # end cloneNode()

    def replaceChild(self, newChild, oldChild):
        raise ZException(u"replaceChild() not currently supported.") #$NON-NLS-1$
    # end replaceChild()

    def insertBefore(self, newChild, refChild):
        raise ZException(u"insertBefore() not currently supported.") #$NON-NLS-1$
    # end insertBefore()

    def normalize(self):
        self.node.normalize()
    # end normalize()

    def getChildren(self):
        if self.node.hasChildNodes():
            return applyZMshtmlNodeFactoryToList(self.node.childNodes, self.ownerDom)
        else:
            return []
    # end getChildren()

    # dynamic attributes ...
    def __getattr__(self, name):
        # type 1 = element
        # type 3 = text node
        # type 8 = commnet
        # type ? = document
        
        # name == documentElement ?
        if name == u"parentNode": #$NON-NLS-1$
            if self.node.parentNode:
                parentDispEle = getDispElement(self.node.parentNode)
                return zMshtmlNodeFactory(parentDispEle, parentDispEle.ownerDocument)
            else:
                return None
        elif name == u"nodeType": #$NON-NLS-1$
            return self.node.nodeType
        elif name == u"nodeValue": #$NON-NLS-1$
            return self.node.nodeValue
        elif name == u"localName": #$NON-NLS-1$
            return self.node.nodeName.lower()
        elif name == u"nodeName": #$NON-NLS-1$
            return self.node.nodeName.lower()
        elif name == u"ownerDocument": #$NON-NLS-1$
            return self.ownerDom
        elif name == u"childNodes": #$NON-NLS-1$
            return self.getChildren()
        elif name == u"documentElement": #$NON-NLS-1$
            return zMshtmlNodeFactory(getDispElement(self.node.documentElement), self.ownerDom)        
        else:
            raise AttributeError, name
    # end __getattr__

    # Saves the DOM to the given file-like object.
    def _saveToFile(self, file, pretty=False, asHtml=False):
        raise ZException(u"_saveToFile() not currently supported.") #$NON-NLS-1$
    # end _saveToFile()

    # Saves the node to a file.
    def save(self, fileName, append=False, pretty=False, asHtml=False):
        raise ZException(u"save() not currently supported.") #$NON-NLS-1$
    # end save()

    # Serializes the node to an XML string.
    def serialize(self, pretty=False, asHtml=False): #@UnusedVariable
        return self.node.outerHTML
    # end serialize()

    # Validates this node against the given Relax NG schema.
    def validate(self, schemaXML, type = 0):
        raise ZException(u"Validation not currently supported.") #$NON-NLS-1$
    # end validateRelaxNG()

#end class ZMshtmlNode

# --------------------------------------------------------------------------------
# Zoundry wrapper class for an XML Attribute.
# --------------------------------------------------------------------------------
class ZMshtmlAttr(ZMshtmlNode, ZAttr):
    # Constructor
    def __init__(self, attr):
        ZMshtmlNode.__init__(self, attr)
        self.attr = attr
    # end __init__()

    def getText(self, default = u""): #$NON-NLS-1$
        try:
            return convertToUnicode(self.attr.nodeValue)
        except:
            return default        
    # end getText()

    def setText(self, value):
        value = convertToUnicode(value)
        try:
            self.attr.nodeValue = value
        except Exception, e:
            raise ZException(u"Error setting the text of an attribute.", e) #$NON-NLS-1$
    # end setText()

#end class ZAttr


# --------------------------------------------------------------------------------
# Wrapper class for an MSHTML Element.
# --------------------------------------------------------------------------------
class ZMshtmlElement(ZMshtmlNode, ZElement):
    u"""
    Wrapper around MSHTML Element object.""" #$NON-NLS-1$

    # Constructor
    def __init__(self, element):
        ZMshtmlNode.__init__(self, element)
        self.element = element
    # end __init__()

    def getNamespaceUri(self):
        # FIXME (PJ) get NS from MSHTML
        return self.element.namespaceURI
    # end getNamespaceUri()

    def getAttribute(self, attribute, default = u""): #$NON-NLS-1$ @UnusedVariable
        if attribute == u"class": #$NON-NLS-1$
            attribute = u"className" #$NON-NLS-1$
        return self._getAttribute(attribute)
    #end getAttribute()

    # Returns a list of all ZAttr children of the Element.
    def getAttributes(self):
        return applyZMshtmlNodeFactoryToList(self.node.attributes, self.ownerDom)
    # end getAttributes()

    def setAttribute(self, attribute, value):
        if attribute == u"class": #$NON-NLS-1$
            attribute = u"className" #$NON-NLS-1$        
        self._setAttribute(attribute, value)
    #end setAttribute()

    def removeAttribute(self, attribute):
        if attribute == u"class": #$NON-NLS-1$
            attribute = u"className" #$NON-NLS-1$        
        self._removeAttribute(attribute)
    # end removeAttribute()

    def getText(self, default = u""): #$NON-NLS-1$ @UnusedVariable
        return self.element.innerText
    #end getText()

    def setText(self, value):
        if value is not None:
            self.element.innerText = value
    #end setText()

    def appendText(self, value):
        if value is not None:
            self.element.innerText = self.element.innerText + value
    # end appendText()

#end class ZMshtmlElement

# --------------------------------------------------------------------------------
# DOM traverser which skips traversing attributes for optimization.
# --------------------------------------------------------------------------------
class ZMshtmlDomTraverser(ZDomTraverser):

    def __init__(self, dom, visitor):
        ZDomTraverser.__init__(self, dom, visitor)

    def _traverseElementAttributes(self, element): #@UnusedVariable
        # override to skip iterating over attributes.
        return True
    # end _traverseElementAttributes()
# end ZMshtmlDomTraverser

# --------------------------------------------------------------------------------
#Base clas for the mshtml dom visitor
# --------------------------------------------------------------------------------
class ZMshtmlDomVisitor(ZDomVisitor):
    
    def _createTraverser(self, dom, visitor):
        # override to create mshtml traverser
        return ZMshtmlDomTraverser(dom, visitor)
    # end _createTraverser()
        
    def visit(self, ihtmlDocument):
        dispDocument = getDispElement(ihtmlDocument)
        ZDomVisitor.visit(self, zMshtmlNodeFactory(dispDocument, None))
    
    def visitDocument(self, document):  #@UnusedVariable
        return True
    # end visitDocument()
    
    def visitElement(self, element):  #@UnusedVariable
        return True
    # end visitElement()
    
    def visitAttribute(self, attribute):  #@UnusedVariable
        return False
    # end visitAttribute()
    
    def visitOtherNode(self, node): #@UnusedVariable
        if node.nodeType == 3:
            return self.visitTextNode(node)
        elif node.nodeType == 8:
            return self.visitCommentNode(node)
        else:
            return True
    # end visitOtherNode()
    
    def visitTextNode(self, node): #@UnusedVariable
        return True
    # end visitTextNode()

    def visitCommentNode(self, node): #@UnusedVariable
        return True
    # end visitCommentNode()
# end ZMshtmlDomVisitor     
