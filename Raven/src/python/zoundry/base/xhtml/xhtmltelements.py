from zoundry.base.util.urlutil import getFilePathFromUri
from urllib import splitport
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.base.zdom.dom import ZElement
from zoundry.base.util.urlutil import unquote_plus
from zoundry.base.util.urlutil import quote_plus
import os
import urlparse

# ---------------------------------------------------------------------------------------
# Simple class that, given a string URL, parses the URL and makes available its component
# parts.
# ---------------------------------------------------------------------------------------
class ZUrl:

    def __init__(self, urlString):
        self.urlString = urlString
        (self.protocol, self.netloc, self.path, self.params, self.query, self.fragment) = urlparse.urlparse(self.urlString)
        (self.host, self.port) = splitport(self.netloc)

        if not self.port:
            self.port = None
        if not self.path:
            self.path = None
        if not self.params:
            self.params = None
        if not self.query:
            self.query = None
        if not self.fragment:
            self.fragment = None
    # end __init__()

    def createUrl(self, href):
        u"""createUrl(string) -> ZUrl""" #$NON-NLS-1$
        return ZUrl(urlparse.urljoin(self.urlString, href))
    # end createUrl()

    def getProtocol(self):
        return self.protocol
    # end getProtocol()

    def getHost(self):
        return self.host
    # end getHost()

    def getPort(self):
        return self.port
    # end getPort()

    def getPath(self):
        return self.path
    # end getPath()

    def getFile(self):
        return os.path.basename(self.getPath())
    # end getFile()

    def getParams(self):
        return self.params
    # end getParams()

    def getQuery(self):
        return self.query
    # end getQuery()

    def getFragment(self):
        return self.fragment
    # end getFragment()

    def toString(self):
        return self.urlString
    # end toString()

# end ZUrl

# ---------------------------------------------------------------------------------------
# Interface to for a wrapper for any XHTML element.
# ---------------------------------------------------------------------------------------
class IZXhtmlElement:

    def getNode(self):
        u"""getNode() -> object
        Returns the underlying node. E.g. ZNode.
        """ #$NON-NLS-1$

    def getNodeName(self):
        u"""getNodeName() -> string
        Returns the element node local name.
        """ #$NON-NLS-1$
        pass

    def getParent(self):
        u"""getParent() -> IZXhtmlElement
        Returns parent element if available else returns None.
        """ #$NON-NLS-1$
        pass

    def getChildren(self):
        u"""getChildren() -> List
        Returns list of child IZXhtmlElement elements.
        """ #$NON-NLS-1$
        pass

    def isLinked(self):
        u"""isLinked() -> boolean
        Returns true if this element is linked via <a>.
        """ #$NON-NLS-1$
    # end isLinked()

    def getLink(self):
        u"""getLink() -> IZXhtmlLink
        Returns the enclosing IZXhtmlLink if this element is linked.
        """ #$NON-NLS-1$
    # end getLink

    def getId(self):
        u"""getId() -> string
        Returns the xhtml core ID attribute.
        """ #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"""setId(string) -> void
        sets the xhtml element id.
        """ #$NON-NLS-1$
    # end setId()

    def getTitle(self):
        u"""getTitle() -> string
        Returns xhtml element core title attribute.
        """ #$NON-NLS-1$
    # end getTitle()

    def setTitle(self, title):
        u"""setTitle(string) -> void
        Sets the element title attribute
        """ #$NON-NLS-1$
    # end setTitle()

    def getClass(self):
        u"""getClass() -> string
        Returns CSS classname attribute value.
        """ #$NON-NLS-1$
    # end getClass()

    def setClass(self, classValue):
        u"""setClass(string) -> void
        Sets the CSS classname attribute.
        """ #$NON-NLS-1$
    # end setClass()

    def getStyle(self):
        u"""getStyle() -> string
        Returns CSS style attribute value
        """ #$NON-NLS-1$
    # end getStyle()

    def setStyle(self, style):
        u"""setStyle(string) -> void
        Sets the CSS style attribute value.
        """ #$NON-NLS-1$
    # end setStyle()

    def getAttribute(self, name): #@UnusedVariable
        u"""getAttribute(string) -> string
        Returns the name attribute value of None if it does not exist.
        """ #$NON-NLS-1$
    # end getAttribute()

    def setAttribute(self, name, value):
        u"""setAttribute(string, string) -> void
        Sets the name attribute value.
        """ #$NON-NLS-1$
    # end setAttribute()

    def removeAttribute(self, name):
        u"""removeAttribute(name) -> void
        Removes the named attribute.
        """ #$NON-NLS-1$

# ---------------------------------------------------------------------------------------
# Interface to for a wrapper for XHTML <a/> element.
# ---------------------------------------------------------------------------------------
class IZXhtmlLink(IZXhtmlElement):

    def getHref(self):
        u"""getHref() -> string
        Return the href attribute value
        """ #$NON-NLS-1$
    # end getHref()

    def setHref(self, href):
        u"""setHref(string) -> void
        Sets the link href
        """ #$NON-NLS-1$
    # end setHref()

    def isEnclosure(self):
        u"""isEnclosure() -> bool
        Returns true if the points to a local audio or video file.
        """ #$NON-NLS-1$
    # end isEncloser()

    def getResourceName(self):
        u"""getResourceName() -> string
        Returns the resource (e.g. file) name if href is a local file and it is available or None otherwise.
        """ #$NON-NLS-1$
    # end getResourceName()


    def getRel(self):
        u"""getRel() -> string
        Returns the rel attribute
        """ #$NON-NLS-1$
    # end getRel()

    def setRel(self, relStr):
        u"""setRel(string) -> void
        Sets the rel attribute value.
        """  #$NON-NLS-1$
    # end setRel()


    def hasRel(self, rel):
        u"""hasRel(string) -> bool
        Returns true if the given rel value exists.
        """  #$NON-NLS-1$
    # end hasRel

    def addRel(self, rel): #@UnusedVariable
        u"""addRel(string) -> void
        Adds a single rel value.
        """  #$NON-NLS-1$
    # end addRel()

    def clearRel(self):
        u"""clearRel() -> void
        Clears the rel attribute value.
        """  #$NON-NLS-1$
    # end clearRel()

    def getTarget(self):
        u"""getTarget() -> string
        Returns the target attribute
        """ #$NON-NLS-1$
    # end getTarget()

    def setTarget(self, target):
        u"""setTarget(string) -> void
        Sets the target attribute value.
        """  #$NON-NLS-1$
    # end setTarget()

# ---------------------------------------------------------------------------------------
# Interface to for a wrapper for XHTML <img/> element.
# ---------------------------------------------------------------------------------------
class IZXhtmlImage(IZXhtmlElement):

    def getSrc(self):
        u"""getSrc() -> string
        Return the image src attribute value
        """ #$NON-NLS-1$
    # end getSrc()

    def setSrc(self, src):
        u"""setSrc(string) -> void
        Sets the image src value.
        """ #$NON-NLS-1$
    # end setSrc
# ---------------------------------------------------------------------------------------
# Wrapper for any XHtml element.  This base class has convenience methods for the common
# attributes that any Xhtml element might have.
# ---------------------------------------------------------------------------------------
class ZXhtmlElement(IZXhtmlElement):

    def __init__(self, element):
        self.element = element
    # end __init__()

    def _createWrapper(self, zdomElement):
        if zdomElement.localName == u"a": #$NON-NLS-1$
            return ZXhtmlLink(zdomElement,-1)
        elif zdomElement.localName == u"img": #$NON-NLS-1$
            return ZXhtmlImage(zdomElement, -1)
        else:
            return ZXhtmlElement(zdomElement)
    # end _createWrapper()

    def getNode(self):
        return self.element

    def getNodeName(self):
        return self.element.localName.lower()
    # end getNodeName

    def getParent(self):
        parent = self.element.parentNode
        if parent:
            return self._createWrapper(parent)
        else:
            return None
    # end getParent()

    def getChildren(self):
        rval = []
        for ele in self.element.getChildren():
            if isinstance(ele, ZElement):
                rval.append( self._createWrapper(ele) )
        return rval
    # end getChildren()

    def isLinked(self):
        linkEle = self._findParentLink()
        return linkEle is not None
    # end isLinked()

    def getLink(self):
        linkEle = self._findParentLink()
        if linkEle:
            return ZXhtmlLink(linkEle, -1)
        else:
            return None
    # end getLink

    def _findParentLink(self):
        ele = self.element
        while ele is not None and ele.localName != u"a": #$NON-NLS-1$
            ele = ele.parentNode
        if ele is not None and ele.localName == u"a": #$NON-NLS-1$
            return ele
        else:
            return None
    # end _findParentLink()

    def getId(self):
        return self.element.getAttribute(u"id") #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        self.element.setAttribute(u"id", id) #$NON-NLS-1$
    # end setId()

    def getTitle(self):
        return self.element.getAttribute(u"title") #$NON-NLS-1$
    # end getTitle()

    def setTitle(self, title):
        self.element.setAttribute(u"title", title) #$NON-NLS-1$
    # end setTitle()

    def getClass(self):
        return self.element.getAttribute(u"class") #$NON-NLS-1$
    # end getClass()

    def setClass(self, classValue):
        self.element.setAttribute(u"class", classValue) #$NON-NLS-1$
    # end setClass()

    def getStyle(self):
        return self.element.getAttribute(u"style") #$NON-NLS-1$
    # end getStyle()

    def setStyle(self, style):
        self.element.setAttribute(u"style", style) #$NON-NLS-1$
    # end setStyle()

    def getAttribute(self, name): #@UnusedVariable
        return self.element.getAttribute(name)
    # end getAttribute()

    def setAttribute(self, name, value):
        if name and value is not None:
            self.element.setAttribute(name, value) #$NON-NLS-1$
    # end setAttribute()

    def removeAttribute(self, name):
        self.element.removeAttribute(name)
    # end removeAttribute()
# end ZXhtmlElement


# ---------------------------------------------------------------------------------------
# A base class for any Xhtml element that might effectively be considered a Uri.  The
# obvious examples of this are links (<a href="[URI]">) and images (<img src="[URI]">).
# This class provides a convenience method for getting the parsed-out URI as a ZUrl
# instance.
# ---------------------------------------------------------------------------------------
class ZXhtmlUri(ZXhtmlElement):

    def __init__(self, element):
        ZXhtmlElement.__init__(self, element)
    # end __init__()

    def getUrl(self):
        urlString = self._getUrl()
        return ZUrl(urlString)
    # end getUrl()

    def setUrl(self, urlString):
        self._setUri(urlString)
    # end setUrl()

    # Abstract method - should be overridden
    def _getUrl(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getUrl") #$NON-NLS-1$
    # end _getUrl

    # Abstract method - should be overridden
    def _setUrl(self, urlString): #@UnusedVariable
        raise ZAbstractMethodCalledException(self.__class__, u"_setUrl") #$NON-NLS-1$
    # end _setUrl()

# end ZXhtmlUri


# ---------------------------------------------------------------------------------------
# A XHtml link:  <a href='...'>test</a>
# ---------------------------------------------------------------------------------------
class ZXhtmlLink(ZXhtmlUri, IZXhtmlLink):

    def __init__(self, element, hitCount):
        self.hitCount = hitCount
        ZXhtmlUri.__init__(self, element)
    # end __init__()

    def getHitCount(self):
        return self.hitCount
    # end getHitCount()

    def getHref(self):
        return unquote_plus(self.element.getAttribute(u"href")) #$NON-NLS-1$
    # end getHref()

    def setHref(self, href):
        href = quote_plus(href)
        self.element.setAttribute(u"href", href) #$NON-NLS-1$
    # end setHref()

    def getType(self):
        return self.element.getAttribute(u"type") #$NON-NLS-1$
    # end getType()

    def setType(self, type):
        self.element.setAttribute(u"type", type) #$NON-NLS-1$
    # end setType()

    def getRel(self):
        return self.element.getAttribute(u"rel").strip() #$NON-NLS-1$
    # end getRel()

    def setRel(self, relStr):
        if relStr is not None:
            self.element.setAttribute(u"rel", relStr.strip()) #$NON-NLS-1$
    # end setRel()

    def getRelList(self):
        return self.getRel().lower().split(u" ") #$NON-NLS-1$
    # end getRelList()

    def hasRel(self, rel):
        rellist = self.getRelList()
        return rel and rel.lower() in rellist
    # end hasRel

    def addRel(self, rel): #@UnusedVariable
        rellist = self.getRelList()
        if rel and rel not in rellist:
            rellist.append( rel.strip() )
            self.setRel( u" ".join(rellist).lower() ) #$NON-NLS-1$
    # end addRel()

    def clearRel(self):
        self.setRel(u""); #$NON-NLS-1$
    # end clearRel()

    def getTarget(self):
        return self.element.getAttribute(u"target") #$NON-NLS-1$
    # end getTarget()

    def setTarget(self, target):
        self.element.setAttribute(u"target", target) #$NON-NLS-1$
    # end setTarget()

    def isEnclosure(self):
        # get file path  (href)
        filePath = getFilePathFromUri( self.getHref() )
        # filepath is None if path does not exist ot if the protocol is not file://
        rval = False
        if filePath:
            # filepath points to a local file
            (base, ext) = os.path.splitext(filePath) #@UnusedVariable
            # FIXME (PJ) use mime registry to determine types.
            EXTS = u".mp3 .wma .mov .mp4 .wav .mpg .mpeg .zip .exe .pdf .doc .xls .ppt" #$NON-NLS-1$
            rval = ext and EXTS.find(ext.strip()) != -1
        return rval
    # end isEncloser()

    def getResourceName(self):
        u"""getResourceName() -> string
        Returns the resource (e.g. file) name if href is a local file and it is available or None otherwise.
        """ #$NON-NLS-1$
        rval = None
        filePath = getFilePathFromUri( self.getHref() )
        if filePath:
            # local file exists
            rval = filePath.replace(u'\\',u'/').split(u'/')[-1] #$NON-NLS-1$  #$NON-NLS-2$  #$NON-NLS-3$
        return rval
    # end getResourceName()

    def getSize(self):
        fileSize = -1
        filePath = getFilePathFromUri( self.getHref() )
        if filePath:
            # local file exists
            try:
                fileSize = os.path.getsize(filePath)
            except:
                pass
        return fileSize
    # end getSize()

    def getText(self):
        return self.element.getText()
    # end getText()

    def _getUrl(self):
        return self.getHref()
    # end _getUrl

    def _setUrl(self, urlString): #@UnusedVariable
        self.setHref(urlString)
    # end _setUrl()

# end ZXhtmlLink


# ------------------------------------------------------------------------------
# A XHtml image:  <img src='' alt=''></img>
# ------------------------------------------------------------------------------
class ZXhtmlImage(ZXhtmlUri, IZXhtmlImage):

    def __init__(self, element, hitCount):
        self.hitCount = hitCount
        ZXhtmlUri.__init__(self, element)
    # end __init__()

    def getHitCount(self):
        return self.hitCount
    # end getHitCount()

    def getSrc(self):
        return unquote_plus(self.element.getAttribute(u"src")) #$NON-NLS-1$
    # end getSrc()

    def setSrc(self, src):
        self.element.setAttribute(u"src", quote_plus(src)) #$NON-NLS-1$
    # end setSrc()

    def _getUrl(self):
        return self.getSrc()
    # end _getUrl

    def _setUrl(self, urlString):
        self.setSrc(urlString)
    # end _setUrl()

# end ZXHtmlImage


# ------------------------------------------------------------------------------
# A Xhtml stylesheet: <link rel="stylesheet" type="text/css" href="/css/yourcss.css">
# ------------------------------------------------------------------------------
class ZXhtmlStylesheet(ZXhtmlUri):

    def __init__(self, element):
        ZXhtmlUri.__init__(self, element)
    # end __init__()

    def getHref(self):
        return self.element.getAttribute(u"href") #$NON-NLS-1$
    # end getHref()

    def setHref(self, href):
        self.element.setAttribute(u"href", href) #$NON-NLS-1$
    # end setHref()

    def getRel(self):
        return self.element.getAttribute(u"rel") #$NON-NLS-1$
    # end getRel()

    def setRel(self, rel):
        self.element.setAttribute(u"rel", rel) #$NON-NLS-1$
    # end setRel()

    def _getUrl(self):
        return self.getHref()
    # end _getUrl

    def _setUrl(self, urlString): #@UnusedVariable
        self.setHref(urlString)
    # end _setUrl()

# end ZXhtmlStylesheet


# ------------------------------------------------------------------------------
# A Xhtml script:  <script type="text/javascript" src="whatever.js">
# ------------------------------------------------------------------------------
class ZXhtmlScript(ZXhtmlUri):

    def __init__(self, element):
        ZXhtmlUri.__init__(self, element)
    # end __init__()

    def getType(self):
        return self.element.getAttribute(u"type") #$NON-NLS-1$
    # end getType()

    def setType(self, type):
        self.element.setAttribute(u"type", type) #$NON-NLS-1$
    # end setType()

    def getLanguage(self):
        return self.element.getAttribute(u"language") #$NON-NLS-1$
    # end getLanguage()

    def setLanguage(self, language):
        self.element.setAttribute(u"language", language) #$NON-NLS-1$
    # end setLanguage()

    def getSrc(self):
        return self.element.getAttribute(u"src") #$NON-NLS-1$
    # end getSrc()

    def setSrc(self, src):
        self.element.setAttribute(u"src", src) #$NON-NLS-1$
    # end setSrc()

    def _getUrl(self):
        return self.getSrc()
    # end _getUrl

    def _setUrl(self, urlString): #@UnusedVariable
        self.setSrc(urlString)
    # end _setUrl()

# end ZXhtmlScript