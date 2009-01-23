from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlUrlIDNAEncodingAnalyser
from zoundry.base.zdom.dom import ZDom
from zoundry.base.exceptions import ZNotYetImplementedException
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlAnalysisVisitor
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlBodyFindingAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlFilePathAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlImageFindingAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlLinkFindingAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlScriptFindingAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlStylesheetFindingAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlSummaryAnalyser
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlTagwordFindingAnalyser
import re

XHTML_NAMESPACE = u"http://www.w3.org/1999/xhtml" #$NON-NLS-1$
XHTML_PREFIX = u"xhtml" #$NON-NLS-1$

XHTML_NSS_MAP = {
    XHTML_PREFIX :XHTML_NAMESPACE,
    u"v"     : u"urn:schemas-microsoft-com:vml", #$NON-NLS-1$ #$NON-NLS-2$
    u"o"     : u"urn:schemas-microsoft-com:office:office", #$NON-NLS-1$ #$NON-NLS-2$
    u"w"     : u"urn:schemas-microsoft-com:office:word",#$NON-NLS-1$ #$NON-NLS-2$
    u"st1"   : u"urn:schemas-microsoft-com:office:smarttags" #$NON-NLS-1$ #$NON-NLS-2$
}

REPEATING_SLASHES_PATTERN = r'(\n\W*//\W*\n)' #$NON-NLS-1$
REPEATING_SLASHES_RE = re.compile(REPEATING_SLASHES_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL)

# ---------------------------------------------------------------------------------------
# Interface for formatting XHtml.
# ---------------------------------------------------------------------------------------
class IZXhtmlFormatter:

    # impls: add PoweredBY, add Tags, ResolvePaths
    def format(self, node):
        u"Called to format the node." #$NON-NLS-1$
    # end format()

# end IZXhtmlFormatter


# ---------------------------------------------------------------------------------------
# An XHtml document.  This class wraps a ZDom and provides convenient access to various
# parts of the XHtml document.
# ---------------------------------------------------------------------------------------
class ZXhtmlDocument:

    def __init__(self, dom):
        self.docTypeString = None
        self.dom = dom
        self.mRootAbsPath = None
        self._runInitAnalysers()
    # end __init__()

    def clone(self):
        u"""clone() -> ZXhtmlDocument()
        Returns copy based on cloning the underlying ZDom instance for this document.""" #$NON-NLS-1$
        newDom = ZDom()
        newDom.loadXML(self.dom.serialize())
        newDom.setNamespaceMap(XHTML_NSS_MAP)
        xhtmlDoc = ZXhtmlDocument(newDom)
        xhtmlDoc.docTypeString = self.docTypeString
        xhtmlDoc.mRootAbsPath = self.mRootAbsPath
        return xhtmlDoc
    # end clone()

    def getDocTypeString(self):
        return self.docTypeString
    # end getDocTypeString()

    def setDocTypeString(self, docTypeString):
        self.docTypeString = docTypeString
    # end setDocTypeString()
    
    def hasDocTypeString(self):
        return self.docTypeString is not None
    # end hasDocTypeString()

    def getDom(self):
        u"Returns the underlying ZDom instance for this document." #$NON-NLS-1$
        return self.dom
    # end getDom()

    def getTitle(self):
        u"Returns the document's <title>, if any." #$NON-NLS-1$
        return None
    # end getTitle()

    def getSummary(self, length = 255): #@UnusedVariable
        u"Generates a summary for this document and returns it." #$NON-NLS-1$
        analyser = ZXhtmlSummaryAnalyser(length)
        self.analyse(analyser)
        return analyser.getSummary()
    # end getSummary()

    def getBody(self):
        u"Returns the <body> of the document." #$NON-NLS-1$
        analyser = ZXhtmlBodyFindingAnalyser()
        self.analyse(analyser)
        return analyser.getBody()
    # end getBody()

    def serialize(self, serializer = None, pretty = False): #@UnusedVariable
        u"Serializes the document and returns the resulting string." #$NON-NLS-1$
        if not serializer:
            return self.dom.serialize(pretty)
        else:
            raise ZNotYetImplementedException(self.__class__.__name__, u"serialize") #$NON-NLS-1$
    # end serialize()

    def getLinks(self):
        u"Returns a list of ZXhtmlLink objects representing all of the links in the document." #$NON-NLS-1$
        analyser = ZXhtmlLinkFindingAnalyser()
        self.analyse(analyser)
        return analyser.getLinks()
    # end getLinks()

    def getImages(self):
        u"Returns a list of ZXhtmlImage objects representing all of the images in the document." #$NON-NLS-1$
        analyser = ZXhtmlImageFindingAnalyser()
        self.analyse(analyser)
        return analyser.getImages()
    # end getImages()

    def getTagwords(self):
        u"""getTagwords() -> string[]
        Return a list of tag word strings.""" #$NON-NLS-1$
        analyser = ZXhtmlTagwordFindingAnalyser()
        self.analyse(analyser)
        return analyser.getTagWords()
    # end getTagwords()

    def getStylesheets(self):
        u"""getStylesheets() -> ZXhtmlStylesheet[]""" #$NON-NLS-1$
        analyser = ZXhtmlStylesheetFindingAnalyser()
        self.analyse(analyser)
        return analyser.getStylesheets()
    # end getStylesheets()

    def getScripts(self):
        u"""getScripts() -> ZXhtmlScript[]""" #$NON-NLS-1$
        analyser = ZXhtmlScriptFindingAnalyser()
        self.analyse(analyser)
        return analyser.getScripts()
    # end getScripts()
    
    def getBaseHref(self):
        u"""getBaseHref() -> string
        Returns the xhtml document's base href.""" #$NON-NLS-1$
        nsMap = { u"xhtml" :  XHTML_NAMESPACE } #$NON-NLS-1$
        baseElem = self.getDom().selectSingleNode(u"/xhtml:html/xhtml:head/xhtml:base", nsMap) #$NON-NLS-1$
        if baseElem is not None:
            return baseElem.getAttribute(u"href") #$NON-NLS-1$
        return None
    # end getBaseHref()

    def checkFilePaths(self):
        analyser = ZXhtmlFilePathAnalyser()
        self.analyse(analyser)
    # end checkFilePaths()

    def analyse(self, analyser):
        visitor = ZXhtmlAnalysisVisitor(analyser)
        visitor.visit(self.dom)
    # end analyse()
    
    def _runInitAnalysers(self):
        self._runUrlIDNAEncodingAnalyser()
        self._runRemoveScriptSlashesAnalyser()
    # end _runInitAnalysers
    
    def _runUrlIDNAEncodingAnalyser(self):
        # Fixes any unicode/idna encoding issues in img and <a> elements.
        try:
            analyser = ZXhtmlUrlIDNAEncodingAnalyser()
            self.analyse(analyser)
        except:
            pass
    # end _runUrlIDNAEncodingAnalyser()
    
    def _runRemoveScriptSlashesAnalyser(self):
        # ----------------------------------------------------------
        # Removes extra comment slashes (//) from <scrip> tags.
        # Eg:
        #  <script>
        #   //
        #   //
        #   var i = i +1
        #   //
        #   //
        #  </script>
        # This is a work around for TidyHtml which keeps inserting slashes at the start and end of 
        # the script tag resulting in a lot of repeating slashes.
        # -----------------------------------------------------------
        analyser = ZXhtmlScriptFindingAnalyser()
        self.analyse(analyser)
        for scriptOb in analyser.getScripts():
            text = getNoneString(scriptOb.element.getText())
            if text:
                text = getSafeString(REPEATING_SLASHES_RE.sub(u"\n", text)) #$NON-NLS-1$
                scriptOb.element.setText(text)
    # end _runRemoveScriptSlashesAnalyser

# end ZXhtmlDocument

