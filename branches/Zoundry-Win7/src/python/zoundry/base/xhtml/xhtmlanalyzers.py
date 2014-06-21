from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.net.http import getHostAndPath
from zoundry.base.util.text.texttransform import ZNormalizeTextTransformer
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.urlutil import decodeUri
from zoundry.base.util.urlutil import encodeIDNA
from zoundry.base.util.urlutil import encodeUri
from zoundry.base.util.urlutil import getUriFromFilePath
from zoundry.base.util.urlutil import unquote_plus
from zoundry.base.xhtml.xhtmltelements import ZXhtmlImage
from zoundry.base.xhtml.xhtmltelements import ZXhtmlLink
from zoundry.base.xhtml.xhtmltelements import ZXhtmlScript
from zoundry.base.xhtml.xhtmltelements import ZXhtmlStylesheet
from zoundry.base.zdom.domvisitor import ZDomVisitor

# ---------------------------------------------------------------------------------------
# Interface for analysing XHtml.
# ---------------------------------------------------------------------------------------
class IZXhtmlAnalyser:

    def analyseElement(self, elementNode):
        u"Called to analyse a given element." #$NON-NLS-1$
    # end analyseElement()

    def analyseText(self, textNode):
        u"Called to analyse a text node." #$NON-NLS-1$
    # end analyseText()

    def analyseComment(self, commentNode):
        u"Called to analyse a comment node." #$NON-NLS-1$
    # end analyseComment()

# end IZXhtmlAnalyser


# ------------------------------------------------------------------------------------
# This visitor is used by the XHtmlDocument in order to execute a IZXhtmlAnalyser
# against all of the nodes in an XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlAnalysisVisitor(ZDomVisitor):

    def __init__(self, analyser):
        self.analyser = analyser
    # end __init__()

    def visitElement(self, element):
        return self.analyser.analyseElement(element)
    # end visitElement()

    def visitOtherNode(self, node):
        if node.nodeType == 3:
            return self.analyser.analyseText(node)
        elif node.nodeType == 8:
            return self.analyser.analyseComment(node)

# end ZXhtmlAnalysisVisitor


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the links in the XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlBodyFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.body = None
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"body": #$NON-NLS-1$
            self.body = node
            return False
    # end analyse()

    def getBody(self):
        return self.body
    # end getBody()

# end ZXhtmlBodyFindingAnalyser

# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract short text summary of XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlSummaryAnalyser(IZXhtmlAnalyser):

    def __init__(self, maxLength = 100):
        self.summary = u""  #$NON-NLS-1$
        self.maxLength = maxLength
        self.inBody = False
        self.length = 0
        self.normalizer = ZNormalizeTextTransformer(True)
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"body": #$NON-NLS-1$
            self.inBody = True
    # end analyseElement()

    def analyseText(self, node):
        if not self.inBody or len(self.summary) > self.maxLength:
            return
        text = convertToUnicode(node.nodeValue)
        if text:
            # use transformer to remove newlines and repeating white spaces.
            self.summary = self.normalizer.transform( self.summary + text)
    # end analyseText

    def getSummary(self):
        return self._ellipsis(self.summary, self.maxLength)
    # end getSummary()

    def _ellipsis(self, s, max):
        if not s:
            return u"" #$NON-NLS-1$
        s = s.strip()
        l = len(s)
        if l < max:
            return s
        end = max - 1
        s = s[0: end]
        s = s + u"..." #$NON-NLS-1$
        return s.strip()

# end ZXhtmlSummaryAnalyser


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the links in the XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlLinkFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.links = []
        self.linkMap = {}
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            # Update the hit count for the link href
            hitCount = 0
            href = node.getAttribute(u"href") #$NON-NLS-1$
            if href in self.linkMap:
                hitCount = self.linkMap[href] + 1
            self.linkMap[href] = hitCount

            self.links.append(ZXhtmlLink(node, hitCount))
    # end analyse()

    def getLinks(self):
        return self.links
    # end getLinks()

# end ZXhtmlLinkFindingAnalyser


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the images in the XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlImageFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.images = []
        self.imageMap = {}
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"img": #$NON-NLS-1$
            # Update the hit count for the image src
            hitCount = 0
            src = node.getAttribute(u"src") #$NON-NLS-1$
            if src in self.imageMap:
                hitCount = self.imageMap[src] + 1
            self.imageMap[src] = hitCount
            self.images.append(ZXhtmlImage(node, hitCount))
    # end analyse()

    def getImages(self):
        return self.images
    # end getImages()

# end ZXhtmlImageFindingAnalyser


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the tags in the XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlTagwordFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.tagwords = []
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            href = node.getAttribute(u"href") #$NON-NLS-1$
            rel = node.getAttribute(u"rel").lower() #$NON-NLS-1$
            if rel.find(u"tag") == -1:#$NON-NLS-1$
                return
            (host, path) = getHostAndPath(href) #@UnusedVariable
            if not path:
                return
            pathparts = path.split(u"/") #$NON-NLS-1$
            tag = pathparts[-1].strip()
            if not tag:
                return
            try:
                self.tagwords.append(unquote_plus(tag))
            except:
                # ignore any conversion errors (for now)
                pass
    # end analyse()

    def getTagWords(self):
        return self.tagwords
    # end getTagWords()

# end ZXhtmlTagwordFindingAnalyser


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the stylesheets in the XHtml
# document.
# ------------------------------------------------------------------------------------
class ZXhtmlStylesheetFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.stylesheets = []
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"link": #$NON-NLS-1$
            if node.getAttribute(u"type") == u"text/css": #$NON-NLS-1$ #$NON-NLS-2$
                self.stylesheets.append(ZXhtmlStylesheet(node))
    # end analyse()

    def getStylesheets(self):
        return self.stylesheets
    # end getStylesheets()

# end ZXhtmlStylesheetFindingAnalyser


# ------------------------------------------------------------------------------------
# An XHtml document analyser that will extract all of the scripts in the XHtml document.
# ------------------------------------------------------------------------------------
class ZXhtmlScriptFindingAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.scripts = []
    # end __init__()

    def analyseElement(self, node):
        if node.localName.lower() == u"script": #$NON-NLS-1$
            self.scripts.append(ZXhtmlScript(node))
    # end analyse()

    def getScripts(self):
        return self.scripts
    # end getScripts()

# end ZXhtmlScriptFindingAnalyser


# ------------------------------------------------------------------------------------
# Visitor that checks each <img> src attribute or <a> href attribute
# to see if it is pointing to a local file resource and if so, properly
# escape the content and append the file:// protocol.
# ------------------------------------------------------------------------------------
class ZXhtmlFilePathAnalyser(IZXhtmlAnalyser):

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"href")  #$NON-NLS-1$
        elif node.localName.lower() == u"img": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"src")  #$NON-NLS-1$
    # end analyseElement()

    def _checkFilePathAttribute(self, node, attrName):
        fpath = node.getAttribute(attrName)
        uri = getUriFromFilePath(fpath)
        if uri:
            uri = encodeIDNA(uri)
            node.setAttribute(attrName, uri )
    # end _checkFilePathAttribute()

# end ZXhtmlFilePathAnalyser

# ------------------------------------------------------------------------------------
# Visitor that checks each <img> src attribute or <a> href attribute
# and correctly sets the url encoding with utf8 and idna.
# ------------------------------------------------------------------------------------
class ZXhtmlUrlIDNAEncodingAnalyser(IZXhtmlAnalyser):

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"href")  #$NON-NLS-1$
        elif node.localName.lower() == u"img": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"src")  #$NON-NLS-1$
    # end analyseElement()

    def _checkFilePathAttribute(self, node, attrName):
        fpath = node.getAttribute(attrName)
        uri = getUriFromFilePath(fpath)
        # Hack alert: we don't want to modify any URIs that contain the 
        # special template directory token.
        if uri and not u"__RAVEN_TEMPLATE_DIR__" in uri: #$NON-NLS-1$
            # decode url if it is in unicode 'quoted' (e.g. %20 etc).
            uri = decodeUri(uri)
            # if needed, convert hostname to IDNA.
            uri = encodeIDNA(uri)
            # re-encode to Raven conention i.e. internally, store content as IDNA (hostname) with Unicode paths
            uri = encodeUri(uri)
            node.setAttribute(attrName, uri )
    # end _checkFilePathAttribute()
# end ZXhtmlUrlIDNAEncodingAnalyser

# ------------------------------------------------------------------------------------
# Visitor that checks each <img> src attribute or <a> href attribute
# and IDNDA decodes URL. This is useful when the code for xhtml editor needs to
# be displayed
# ------------------------------------------------------------------------------------
class ZXhtmlUrlIDNADecodingAnalyser(IZXhtmlAnalyser):

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"href")  #$NON-NLS-1$
        elif node.localName.lower() == u"img": #$NON-NLS-1$
            self._checkFilePathAttribute(node, u"src")  #$NON-NLS-1$
    # end analyseElement()

    def _checkFilePathAttribute(self, node, attrName):
        fpath = node.getAttribute(attrName)
        uri = decodeUri(fpath)
#        print u"decodeUri: %s" % fpath.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#        print u"         : %s" % uri.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        if uri:
            node.setAttribute(attrName, uri )
    # end _checkFilePathAttribute()
# end ZXhtmlUrlIDNADecodingAnalyser

# ------------------------------------------------------------------------------------
# Visitor remove xml and xmln attributes.
# ------------------------------------------------------------------------------------
class ZXhtmlRemovePrefixVisitor(ZDomVisitor):

    def __init__(self, prefixes = u"xml,xmlns"): #$NON-NLS-1$
        prefixes = getSafeString(prefixes)
        self.prefixList = prefixes.split(u",") #$NON-NLS-1$
    # end __init__()

    def visitElement(self, element):
        attrs = element.getAttributes()
        for attr in attrs:
            idx = attr.nodeName.find(u":") #$NON-NLS-1$
            if idx != -1 and attr.nodeName[0:idx] in self.prefixList:
                element.node.removeAttributeNode(attr.node)
    # end visitElement()
# end ZXhtmlRemovePrefixVisitor
