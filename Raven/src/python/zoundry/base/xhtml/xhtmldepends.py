from zoundry.base.resdepends import IZResourceDependencyFinder
from zoundry.base.resdepends import IZResourceDependencyTypes
from zoundry.base.resdepends import ZResourceDependency
from zoundry.base.xhtml.xhtmlanalyzers import IZXhtmlAnalyser
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.css.cssdepends import ZCSSDependencyFinder

# ------------------------------------------------------------------------------
# Finds dependencies in the xhtml content.  This class looks for images,
# imported javascript, and imported CSS.
# ------------------------------------------------------------------------------
class ZXhtmlDependencyFinder(IZResourceDependencyFinder, IZXhtmlAnalyser):

    def __init__(self, xhtml):
        self.xhtml = xhtml
        self.dependencies = []
        self.baseHref = None
    # end __init__()
    
    def getBaseHref(self):
        return self.baseHref
    # end getBaseHref()

    def findDependencies(self):
        u"""findDependencies() -> ZResourceDependency[]""" #$NON-NLS-1$
        xhtmlDoc = loadXhtmlDocumentFromString(self.xhtml)
        self.baseHref = xhtmlDoc.getBaseHref()
        # Find images
        for image in xhtmlDoc.getImages():
            if image.getSrc():
                self.dependencies.append(ZResourceDependency(IZResourceDependencyTypes.IMAGE, image.getSrc()))
        # Find CSS stylesheets
        for stylesheet in xhtmlDoc.getStylesheets():
            if stylesheet.getHref():
                self.dependencies.append(ZResourceDependency(IZResourceDependencyTypes.CSS, stylesheet.getHref()))
        # Find scripts
        for script in xhtmlDoc.getScripts():
            if script.getSrc():
                self.dependencies.append(ZResourceDependency(IZResourceDependencyTypes.SCRIPT, script.getSrc()))

        # Now find some stuff that the regular analysers miss (in-line CSS)
        xhtmlDoc.analyse(self)
        return self.dependencies
    # end findDependencies()

    def analyseElement(self, elementNode):
        if elementNode.localName.lower() == u"style": #$NON-NLS-1$
            css = elementNode.getText()
            cssFinder = ZCSSDependencyFinder(css)
            for dep in cssFinder.findDependencies():
                self.dependencies.append(dep)
    # end analyseElement()

# end ZXhtmlDependencyFinder
