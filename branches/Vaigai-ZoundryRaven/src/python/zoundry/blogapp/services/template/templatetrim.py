from zoundry.base.exceptions import ZException
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromFile
from zoundry.base.zdom.domvisitor import ZDomVisitor

# ------------------------------------------------------------------------------
# A visitor that visits the element and finds one called 'ravenBody'.
# ------------------------------------------------------------------------------
class ZTemplateBodyFindingVisitor(ZDomVisitor):

    def __init__(self):
        self.elements = []
    # end __init__()

    def visitElement(self, element):
        if element.localName.lower() == u"ravenbody": #$NON-NLS-1$
            self.elements.append(element)
    # end visitElement()

    def getBodyElements(self):
        return self.elements
    # end getBodyElements()

# end ZTemplateBodyFindingVisitor


# ------------------------------------------------------------------------------
# A visitor that visits the element and finds one called 'ravenTitle'.
# ------------------------------------------------------------------------------
class ZTemplateTitleFindingVisitor(ZDomVisitor):

    def __init__(self):
        self.elements = []
    # end __init__()

    def visitElement(self, element):
        if element.localName.lower() == u"raventitle": #$NON-NLS-1$
            self.elements.append(element)
    # end visitElement()

    def getTitleElements(self):
        return self.elements
    # end getTitleElements()

# end ZTemplateTitleFindingVisitor


# ------------------------------------------------------------------------------
# Class that takes a raw template and trims it down for use as a blog template.
# This amounts to removing everything in the xhtml document except the body
# and title.
# ------------------------------------------------------------------------------
class ZTemplateTrimmer:

    def __init__(self, template):
        self.template = template
    # end __init__()

    def trim(self):
        xhtmlDoc = loadXhtmlDocumentFromFile(self._getRootFile())
        xhtmlDom = xhtmlDoc.getDom()
        vizzy = ZTemplateBodyFindingVisitor()
        vizzy.visit(xhtmlDom)
        elem = vizzy.getResult()
        if elem is None:
            raise ZException(u"Failed to find Raven template marker content.") #$NON-NLS-1$

        self._doTrim(elem)
        self._save(xhtmlDom)
    # end trim()

    def _doTrim(self, elem):
        parent = elem.parentNode
        child = elem
        while not self._isBody(child):
            self._removeChildrenExcept(parent, child)
            newParent = parent.parentNode
            child = parent
            parent = newParent
    # end _doTrim()

    def _isBody(self, element):
        return element.nodeName.lower() == u"body" #$NON-NLS-1$
    # end _isBody()

    def _removeChildrenExcept(self, parent, childToKeep):
        for child in parent.getChildren():
            if child.node != childToKeep.node:
                parent.removeChild(child)
    # end _removeChildrenExcept()

    def _save(self, xhtmlDom):
        return xhtmlDom.save(self._getRootFile())
    # end _save()

    def _getRootFile(self):
        return self.template.getResolvedRootFile()
    # end _getRootFile()

# end ZTemplateTrimmer
