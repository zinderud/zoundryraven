from zoundry.base.zdom.dom import ZElement

# ----------------------------------------------------------------------------------------
# Interface that must be implemented by a DOM Visitor.  The DOM traverser will call these
# methods during the traversal of the DOM.
# ----------------------------------------------------------------------------------------
class IZDomVisitor:
    
    def visitDocument(self, document):
        u"Called when the root Document is visited." #$NON-NLS-1$
    # end visitDocument()
    
    def visitElement(self, element):
        u"Called when an element is visited." #$NON-NLS-1$
    # end visitElement()
    
    def visitAttribute(self, attribute):
        u"Called when an attribute is visited." #$NON-NLS-1$
    # end visitAttribute()
    
    def visitOtherNode(self, node):
        u"Called when some other node is visited." #$NON-NLS-1$
    # end visitOtherNode()

# end IZDomVisitor


# ----------------------------------------------------------------------------------------
# A class that knows how to traverse a DOM, calling a DOM Visitor whenever it traverses
# a new node in the DOM.
# ----------------------------------------------------------------------------------------
class ZDomTraverser:

    def __init__(self, dom, visitor):
        self.dom = dom
        self.visitor = visitor
    # end __init__()

    def traverse(self):
        if isinstance(self.dom, ZElement):
            self.traverseElement(self.dom)
        else:
            self.traverseDocument(self.dom)
    # end traverse()

    def traverseDocument(self, document):
        if self.visitor.visitDocument(document) is False:
            return
        
        if document.documentElement:
            self.traverseElement(document.documentElement)
    # end traverseDocument()

    def traverseElement(self, element):
        if self.visitor.visitElement(element) is False:
            return
        if self._traverseElementAttributes(element) is False:
            return
        for child in element.getChildren():
            if isinstance(child, ZElement):
                if self.traverseElement(child) is False:
                    return
            else:
                if self.traverseOtherNode(child) is False:
                    return
    # end traverseElement()
    
    def _traverseElementAttributes(self, element):
        # Subclasses can override to skip traversing of element attributes. 
        # E.g. MSHTML IHtmlDocument traverser overrides to skip attributes for speed reasons.
        for attr in element.getAttributes():
            if self.traverseAttribute(attr) is False:
                return False
        return True
    # end _traverseElementAttributes()
        
    def traverseAttribute(self, attribute):
        self.visitor.visitAttribute(attribute)
    # end traverseAttribute()

    def traverseOtherNode(self, otherNode):
        self.visitor.visitOtherNode(otherNode)
    # end traverseOtherNode()

# end ZDomTraverser


# ----------------------------------------------------------------------------------------
# A base class for any DOM visitor that wants to leverage the standard DOM traverser.  
# This base class creates a DOM traverser and uses it to traverse the DOM, calling back
# the methods on IZDomVisitor while it traverses.
# ----------------------------------------------------------------------------------------
class ZDomVisitor(IZDomVisitor):
    
    def __init__(self):
        pass
    # end __init__()

    def visit(self, dom):
        self.traverser = self._createTraverser(dom, self)
        self.traverser.traverse()
    # end visit()
    
    def _createTraverser(self, dom, visitor):
        return ZDomTraverser(dom, visitor)
    # end _createTraverser()

# end ZDomVisitor
