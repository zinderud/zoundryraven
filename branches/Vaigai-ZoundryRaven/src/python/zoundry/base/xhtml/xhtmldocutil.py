from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.zdom.dom import ZDom
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.xhtml.xhtmldoc import XHTML_NAMESPACE

def getAnchorNode(aNode):
    u"""Returns the anchor node hyperlinking the given aNode.
    Returns None if the node is not hyperlinked.
    """ #$NON-NLS-1$
    n = aNode
    while n:
        # FIXME (PJ) use qualified name (xhtml:a)
        if n.localName == u'a': #$NON-NLS-1$
            return n
        n = n.parentNode
    return None

def isHyperlinked(aNode):
    u"""Returns true if the given aNode is hyperlinked. """ #$NON-NLS-1$
    return getAnchorNode(aNode) is not None

def hyperlinkNode(aNode, href, attrs = {}):
    u"""Creates a hyperlink around the given node and returns the created anchor node.
    If the node is already hyperlinked, then this method does not do anything and returns None.
    Additional <a> attributes such as id, class, border etc. can be set via attrs map.
     """ #$NON-NLS-1$

    if not aNode or isHyperlinked(aNode):
        return None
    ownerDom = aNode.ownerDocument
    linkNode = ownerDom.createElement(u"a", XHTML_NAMESPACE) #$NON-NLS-1$
    for (key, value) in attrs.iteritems():
        if value:
            linkNode.setAttribute(key, value)
    linkNode.setAttribute(u"href", href) #$NON-NLS-1$
    tempNode = aNode
    aNode.parentNode.replaceChild(linkNode, aNode)
    linkNode.appendChild(tempNode)
    return linkNode

ELEMENT_TEMPLATE = u"""<zoundry-root></zoundry-root>""" #$NON-NLS-1$

def createHtmlElement(parentElement, elementName, attrMap = {}, elementText = None):
    u"""createHtmlElement(Node, string, map, string) -> Node
    Creates a element given element name, attribute map and optional element node text.
    If the parentElement node is None, then element is under new document (zdom).
     """ #$NON-NLS-1$
    element = None
    elementName = getNoneString(elementName)
    elementText = getNoneString(elementText)
    if not elementName:
        return None
    dom = None
    if parentElement:
        dom = parentElement.ownerDocument
    else:
        dom = ZDom()
        dom.loadXML(ELEMENT_TEMPLATE)
        parentElement = dom.documentElement
    try:
        element = dom.createElement(elementName)
        parentElement.appendChild(element)
        for (n,v) in attrMap.iteritems():
            if n and v:                
                element.setAttribute(n,v)
        if elementText:
            element.setText(elementText)
    except:
        pass    
    return element
# end createHtmlElement()

def appendHtmlFragment(parentNode, htmlFragString):
    u"""appendHtmlFragment(Node, string) -> Node
    Deserializes the htmlFragString into an Node and appends
    it to the parent Node
     """ #$NON-NLS-1$        
    try:
        xhtmlFragDoc = loadXhtmlDocumentFromString(htmlFragString)
        fragNode = parentNode.ownerDocument.importNode(xhtmlFragDoc.getBody(), True)
        parentNode.appendChild(fragNode)
        return parentNode
    except:
        return None
# end appendHtmlFragment()

# ------------------------------------------------------------------------------
# Removes script references from the xhtml document.
# ------------------------------------------------------------------------------
def removeJavaScript(xhtmlDoc):
    xhtmlDoc.getBody().removeAttribute(u"onLoad") #$NON-NLS-1$
    xhtmlDoc.getBody().removeAttribute(u"onload") #$NON-NLS-1$
    scripts = xhtmlDoc.getScripts()
    for scriptOb in scripts:
        try:
            scriptOb.element.parentNode.removeChild(scriptOb.element)
        except:
            pass
# end removeJavaScript     

