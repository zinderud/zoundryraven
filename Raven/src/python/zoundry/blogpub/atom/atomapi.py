from zoundry.base.net.authhandlers import ZXWsseUsernameAuthHandler
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.dateutil import getIso8601Date
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.zdatetime import getCurrentUtcDateTime
from zoundry.base.zdom.dom import ZDom
from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.blogpub.blogserverapi import IZBlogServerFactory
from zoundry.blogpub.blogserverapi import ZBlogServer
from zoundry.blogpub.blogserverapi import ZBlogServerException
from zoundry.blogpub.blogserverapi import ZServerBlogCategory
from zoundry.blogpub.blogserverapi import ZServerBlogEntry
from zoundry.blogpub.blogserverapi import ZServerBlogInfo
from zoundry.blogpub.namespaces import ATOM_10_FEED_NAMESPACE
from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
import base64
import time



ATOM_10_EMPTY_FEED_XML = u"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' />"""  #$NON-NLS-1$


def getAtomGeneratorVersion():
    return u"0.1" #$NON-NLS-1$

def getAtomGeneratorName():
    return u"Zoundry Raven" #$NON-NLS-1$

#================================================
# Atom Server public interfaces (meant to hide 1.0 and 0.3 impls)
#================================================

#---------------------------------------------
# Generic atom exception
#---------------------------------------------
class ZAtomException(ZBlogServerException):

    def __init__(self, message = u"", rootCause = None, stage = u"",  code = 0):  #$NON-NLS-1$  #$NON-NLS-2$
        ZBlogServerException.__init__(self, rootCause, stage, message, code)
    # end __init__()

#---------------------------------------------
# List of well known rel types used in Atom API
#---------------------------------------------
class ZAtomRelTypes:
    # list of well known rel values.
    ATOM_FEED_LINK_REL_LIST       = [u"service.feed", u"http://schemas.google.com/g/2005#feed", u"service.subscribe"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    ATOM_POST_LINK_REL_LIST       = [u"service.post", u"http://schemas.google.com/g/2005#post"]  #$NON-NLS-1$ #$NON-NLS-2$
    ATOM_EDIT_LINK_REL_LIST       = [u"service.edit", u"edit"]  #$NON-NLS-1$ #$NON-NLS-2$
    ATOM_UPLOAD_LINK_REL_LIST     = [u"service.upload"]  #$NON-NLS-1$
    ATOM_CATEGORIES_LINK_REL_LIST = [u"service.categories"]  #$NON-NLS-1$
    ATOM_FEED_NEXT_REL_LIST       = [u"next"]  #$NON-NLS-1$

    def __init__(self, atomPrefix = u"atom:", atom03Prefix = u"atom03:", atomApiPrefix = u"app:"): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.atomPrefix = atomPrefix
        self.atom03Prefix = atom03Prefix
        self.atomApiPrefix = atomApiPrefix

    def _getRelList(self, rel):
        # rel field may have multiple values, separated by a space.
        rel = rel.lower().strip()
        relList = rel.split(u" ") #$NON-NLS-1$
        return relList

    def _isInRelList(self, rel, relRefList):
        # relRefList is a known list eg [service.post]
        # rel is the list we search against.
        # rel field may have multiple values, separated by a space and may be mixed case.
        rel = rel.lower().strip()
        for relRef in relRefList:
            if rel.find(relRef) != -1:
                return True
        return False

    def isFeedLink(self, rel, type = None):
        u"""Returns true if the given link is a service.feed link""" #$NON-NLS-1$
        return self._isInRelList(rel, ZAtomRelTypes.ATOM_FEED_LINK_REL_LIST)

    def isPostLink(self, rel, type = None):
        u"""Returns true if the given link is a service.post link""" #$NON-NLS-1$
        return self._isInRelList(rel, ZAtomRelTypes.ATOM_POST_LINK_REL_LIST)

    def isEditLink(self, rel, type = None):
        u"""Returns true if the given link is a service.edit link""" #$NON-NLS-1$
        return self._isInRelList(rel, ZAtomRelTypes.ATOM_EDIT_LINK_REL_LIST)

    def isUploadLink(self, rel, type = None):
        u"""Returns true if the given link is a service.upload link""" #$NON-NLS-1$
        return self._isInRelList(rel, ZAtomRelTypes.ATOM_UPLOAD_LINK_REL_LIST)

    def isCategoriesLink(self, rel, type = None):
        u"""Returns true if the given link is a service.categories link""" #$NON-NLS-1$
        return self._isInRelList(rel, ZAtomRelTypes.ATOM_CATEGORIES_LINK_REL_LIST)

    def isAlternateLink(self, rel, type = None):
        u"""Returns true if the given link is a service.categories link""" #$NON-NLS-1$
        return u"alternate" == rel.strip().lower() #$NON-NLS-1$

#---------------------------------------------------
# Atom 1.0 category
#---------------------------------------------------
class ZAtomCategory(ZServerBlogCategory):

    def __init__(self, term, label = None, scheme = None):
        self.term = term
        self.label = label
        self.scheme = scheme
        name = getNoneString(label)
        if not name:
            name = getSafeString(term)
        ZServerBlogCategory.__init__(self, term, name)

    def getTerm(self):
        return self.term

    def getLabel(self):
        return self.label

    def getScheme(self):
        return self.scheme

#---------------------------------------------------
# Atom Blog
#---------------------------------------------------
class ZAtomBlog (ZServerBlogInfo):

    CONTENT_TYPE    = u"content-type"  #$NON-NLS-1$
    TITLE           = u"feed-title"  #$NON-NLS-1$
    ID              = u"id"   #$NON-NLS-1$
    ALT_LINK        = u"alt-link"  #$NON-NLS-1$
    POST_LINK       = u"post-link" #$NON-NLS-1$
    FEED_LINK       = u"feed-link" #$NON-NLS-1$
    UPLOAD_LINK     = u"upload-link" #$NON-NLS-1$
    CATEGORIES_LINK = u"categories-link" #$NON-NLS-1$
    AUTHOR          = u"author" #$NON-NLS-1$

    def __init__(self):
        id = None
        name = None
        url = None
        ZServerBlogInfo.__init__(self, id, name, url)
    # end __init__()

    def getType(self):
        return self.getAttribute(ZAtomBlog.CONTENT_TYPE, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

    def getAlternateLink(self):
        return self.getAttribute(ZAtomBlog.ALT_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

    def getPostLink(self):
        return self.getAttribute(ZAtomBlog.POST_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

    def getFeedLink(self):
        return self.getAttribute(ZAtomBlog.FEED_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

    def getUploadLink(self):
        return self.getAttribute(ZAtomBlog.UPLOAD_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

    def getCategoriesLink(self):
        return self.getAttribute(ZAtomBlog.CATEGORIES_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)

#---------------------------------------------------
# Base class for atom entry node/document
#---------------------------------------------------

class ZAtomDocument:

    def __init__(self, node = None):
        self.node = node

    def getNode(self):
        if not self.node:
            self.node = self._createNode()
        return self.node

    def getDom(self):
        node = self.getNode()
        if isinstance(node, ZDom):
            return node
        else:
            return node.ownerDocument

    def _createNode(self):
        dom = ZDom()
        self._initNode(dom)
        return dom

    def _initNode(self, node): #@UnusedVariable
        pass
# end ZAtomDocument

#================================================
# Atom Feed Entry
#================================================
class ZAtomFeedEntry(ZAtomDocument):
    # Constructs an Atom feed entry object from an Atom XML entry node.
    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZAtomDocument.__init__(self, entryNode)
        self.prefix = prefix
    # end __init__
    
    def getId(self):
        u"Gets the feed entry ID." #$NON-NLS-1$
        return self._getId()
    # end getId()

    def getEditLink(self):
        u"Gets the service.edit link for the entry." #$NON-NLS-1$
        return self._getEditLink()
    # end getEditLink()

    def getAlternateLink(self):
        u"Gets a link to the alternate representation of the entry." #$NON-NLS-1$
        return self._getAlternateLink()
    # end getAlternateLink

    def getPublishedDate(self):
        u"Gets the date the entry was published." #$NON-NLS-1$
        datetimeStr = self._getPublishedDate()
        return self._parseISO8601Date(datetimeStr)
    # end getPublishedDate()

    def getUpdatedDate(self):
        u"Gets the date the entry was updated." #$NON-NLS-1$
        datetimeStr = self._getUpdatedDate()
        return self._parseISO8601Date(datetimeStr)
    # end getUpdateDate()
    
    def getAuthor(self):
        u"Gets the entry author." #$NON-NLS-1$
        return self._getAuthor()
    # end getAuthor()

    def getTitle(self):
        u"Gets the entry title." #$NON-NLS-1$
        titleNode = self._getTitleNode()
        if titleNode:
            return self._getContentAsText(titleNode)
        else:
            return u"" #$NON-NLS-1$
    # end getTitle()

    def getContent(self):
        contentNode = self._getContentNode()
        if contentNode:
            return self._getContentAsText(contentNode)
        else:
            return u"" #$NON-NLS-1$
    # getGetContent()

    def getCategories(self):
        # returns list of AtomCategory objects.
        return self._getCategories()
    # end getCategories()

    def _getContentAsText(self, contentNode):
        # Atom 1.0
        type = contentNode.getAttribute(u"type", u"") #$NON-NLS-2$ #$NON-NLS-1$
        # Atom 0.3
        mode = contentNode.getAttribute(u"mode", u"") #$NON-NLS-2$ #$NON-NLS-1$
        type = type.lower().strip()
        mode =  mode.lower().strip()
        rVal = u"" #$NON-NLS-1$
        if mode == u"xml" or type == u"xml" or type == u"xhtml" or type == u"application/xhtml+xml": #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
            rVal = self._getXMLContent(contentNode)
        elif mode == u"escaped" or type == u"html" or type == u"text" or type.startswith(u"text/"): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
            rVal = self._getEscapedContent(contentNode)
        elif mode == u"base64" : #$NON-NLS-1$
            rVal = self._getBase64Content(contentNode)
        elif mode == u""  and type == u"": #$NON-NLS-1$ #$NON-NLS-2$
            # 1.0 spec: if type not given, assume text
            rVal = self._getEscapedContent(contentNode)
        else:
            rVal = self._getLiteralContent(contentNode)
        return rVal
    # end _getContentAsText()

    def _getEscapedContent(self, contentNode):
        u"Gets escaped content from the content node." #$NON-NLS-1$
        return contentNode.getText()
    # end _getEscapedContent()

    # Gets content formatted as application/xhtml+xml.
    def _getLiteralContent(self, contentNode):
        u"Gets content formatted as application/xhtml+xml." #$NON-NLS-1$
        rval = u"" #$NON-NLS-1$
        nodes = contentNode.selectNodes(u"child::*") #$NON-NLS-1$
        if len(nodes) == 0:
            return self._getEscapedContent(contentNode)
        for node in nodes:
            rval = rval + node.serialize() #+ u"\n" #$NON-NLS-1$
        return rval
    # end _getLiteralContent()

    # Gets content formatted as XML (TypePad).
    def _getXMLContent(self, contentNode):
        u"Gets content formatted as XML (TypePad)." #$NON-NLS-1$
        rval = u"" #$NON-NLS-1$
        nodes = contentNode.selectNodes(u"child::*") #$NON-NLS-1$
        if len(nodes) == 0:
            return self._getEscapedContent(contentNode)
        for node in nodes:
            rval = rval + node.serialize()
        return rval
    # end _getXMLContent()

    # Gets content formatted as base64.
    def _getBase64Content(self, node):
        u"Gets content formatted as base64." #$NON-NLS-1$
        try:
            b64Txt = node.getText()
            return base64.decodestring(b64Txt).decode(u"utf-8") #$NON-NLS-1$
        except:
            self.exception()
            return u"<div>Error getting base64 encoded content (Atom API error).</div>" #$NON-NLS-1$
    # end _getBase64Content()

    # Parses a date string formatted in extended ISO8601 date-time format (aka xsd:dateTime format).
    def _parseISO8601Date(self, dateStr, dflt = None):
        u"Parses a date string formatted in extended ISO8601 date-time format (aka xsd:dateTime format)." #$NON-NLS-1$
        if dateStr:
            dateStr = dateStr.strip(u"\r\n")  #$NON-NLS-1$
            dateStr = dateStr.strip(u"\r")  #$NON-NLS-1$
            dateStr = dateStr.strip(u"\n")  #$NON-NLS-1$
        schemaDt = getIso8601Date(dateStr)
        rval = None
        if schemaDt:
            rval = schemaDt.getDateTime()
        if not schemaDt and dflt:
            rval = dflt
        elif not schemaDt:
            rval = getCurrentUtcDateTime()
        return rval
    # end _parseISO8601Date()

    def _getId(self):
        idElem = self.getNode().selectSingleNode(u"%sid" % self.prefix) #$NON-NLS-1$
        if idElem:
            return idElem.getText()
        else:
            return None

    def _getEditLink(self):
        # atom 1.0
        linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'edit']" % self.prefix) #$NON-NLS-1$
        if not linkElem:
            # for servers with atom 0.3 and some or partial 1.0 impls.
            linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'service.edit']" % self.prefix) #$NON-NLS-1$
        if not linkElem:
            # atom 1.0 backup
            linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'self' and @type = 'application/atom+xml']" % self.prefix) #$NON-NLS-1$

        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end _getEditLink

    def _getAlternateLink(self):
        altLinkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'alternate']" % self.prefix) #$NON-NLS-1$
        if altLinkElem:
            return altLinkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end _getAlternateLink

    def _getPublishedDate(self):
        dtStr = self.getNode().selectSingleNodeText(u"%spublished" % self.prefix, None) #$NON-NLS-1$
        if not dtStr:
            dtStr = self.getNode().selectSingleNodeText(u"%supdated" % self.prefix, None) #$NON-NLS-1$
        return dtStr
    # end _getPublishedDate()

    def _getUpdatedDate(self):
        dtStr = self.getNode().selectSingleNodeText(u"%supdated" % self.prefix, None) #$NON-NLS-1$
        if not dtStr:
            dtStr = self.getNode().selectSingleNodeText(u"%spublished" % self.prefix, None) #$NON-NLS-1$
        return dtStr
    # end _getUpdatedDate()
    
    def _getAuthor(self):
        authNameElem = self.getNode().selectSingleNode(u"%sauthor/%sname" % (self.prefix, self.prefix)) #$NON-NLS-1$
        if authNameElem:
            return authNameElem.getText()
        else:
            return None
    # end _getAuthor

    def _getTitleNode(self):
        return self.getNode().selectSingleNode(u"%stitle" % self.prefix) #$NON-NLS-1$

    def _getContentNode(self):
        contentNode = self.getNode().selectSingleNode(u"%scontent" % self.prefix) #$NON-NLS-1$
        if not contentNode:
            contentNode = self.getNode().selectSingleNode(u"%ssummary" % self.prefix) #$NON-NLS-1$
        return contentNode
    # end _getContentNode()

    def _getCategories(self):
        rVal = []
        categories = self.getNode().selectNodes(u"atom:category") #$NON-NLS-1$
        if categories and len(categories) > 0:
            for catNode in categories:
                term = catNode.getAttribute(u"term") #$NON-NLS-1$
                label = catNode.getAttribute(u"label") #$NON-NLS-1$
                scheme = catNode.getAttribute(u"scheme") #$NON-NLS-1$
                if term and term != u"": #$NON-NLS-1$
                    rVal.append( ZAtomCategory(term, label, scheme) )
        return rVal
    # end _getCategories
        
# end ZAtomFeedEntry

#================================================
# Atom Blog Entry
#================================================
class ZAtomBlogEntry(ZAtomFeedEntry, ZServerBlogEntry):

    EDIT_LINK        = u"edit-link"  #$NON-NLS-1$

    # Constructs an Atom blog entry object from an Atom XML entry node.
    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZAtomFeedEntry.__init__(self, entryNode, prefix)
        self.supportsDraftMode = False
        ZServerBlogEntry.__init__(self, self.getId() )
        self.setAttribute(ZAtomBlog.ID, self.getId(), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        self.setAttribute(ZAtomBlog.ALT_LINK, self.getAlternateLink(), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        self.setAttribute(ZAtomBlogEntry.EDIT_LINK, self.getEditLink(), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        self.setAttribute(ZAtomBlog.AUTHOR, self.getAuthor(), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
    # end __init__()

    def isDraft(self):
        u"Returns True if this entry is in 'draft mode'." #$NON-NLS-1$
        return self._isDraft()

    def getUrl(self):
        return self.getAlternateLink()

    def getRawContent(self):
        return self.getContent()

    def getUtcDateTime(self):
        return self.getPublishedDate()

    def _isDraft(self):
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return False

#--------------------------------------------
#  entry that is used for PUT/POST/DELETE delegate.
#--------------------------------------------
class ZAtomEntryDocument(ZAtomDocument):

    def __init__(self):
        ZAtomDocument.__init__(self, None)
        # set default time to now
        self.setDate(None)
        self.atomCategoryScheme = None
    # end __init__()

    def setCategoryScheme(self, scheme):
        self.atomCategoryScheme = scheme
    # end setCategoryScheme()

    def getCategoryScheme(self):
        return self.atomCategoryScheme
    # end getCategoryScheme()

    def setEditLink(self, editLink):
        self._setEditLink(editLink)
    # end setEditLink()

    def getEditLink(self):
        return self._getEditLink()
    # end getEditLink()

    def setId(self, entryId):
        self._setId(entryId)
    # end setId()

    def setTitle(self, title):
        self._setTitle(title)
    # end setTitle()

    def setContent(self, content):
        self._setContent(content)
    # end setContent()

    def setCategories(self, atomCategoryList):
        if atomCategoryList and len(atomCategoryList) > 0:
            self._setCategories(atomCategoryList)
    # end setCategories()

    def setDate(self, dateTime = None):
        if not dateTime:
            dateTime = getCurrentUtcDateTime()
        schemaDt = ZSchemaDateTime(dateTime)
        dateTimeStr = str(schemaDt)
        self._setDateStr(dateTimeStr)
    # end setDate()

    # FIXME (PJ) move this down to the BlogEntry ?
    def setDraft(self, bDraft):
        self._setDraft(bDraft)
    # end setDraft()

    def setAuthor(self, author):
        self._setAuthor(author)
    # end setAuthor()

    def _setId(self, entryId):
        idElem = self.getDom().selectSingleNode(u"/atom:entry/atom:id") #$NON-NLS-1$
        if idElem:
            idElem.setText(entryId)
    # end _setId()

    def _setTitle(self, title):
        titleElem = self.getDom().selectSingleNode(u"/atom:entry/atom:title") #$NON-NLS-1$
        if titleElem:
            titleElem.setText(title)
    # _setTitle()

    def _setContent(self, content):
        contentElem = self.getDom().selectSingleNode(u"/atom:entry/atom:content") #$NON-NLS-1$
        if contentElem:
            try:
                contentElem.setText(content)
            except:
                self.exception()
    # end _setContent()

    def _setCategories(self, atomCategoryList):
        # set Atom 1.0 categories
        self._setAtomCategories(atomCategoryList, ATOM_10_FEED_NAMESPACE)
    #end _setCategories()

    def _setAtomCategories(self, atomCategoryList, namespace):
        # Atom 1.0
        for cat in atomCategoryList: #$NON-NLS-1$
            catElem = self.getDom().createElement(u"category", namespace) #$NON-NLS-2$ #$NON-NLS-1$
            catElem.setAttribute(u"term", cat.getTerm()) #$NON-NLS-1$
            # FIXME (PJ) GData does not like 'label' attribute.  Always set label. Override  Blogger Atom api impl. so that label is not written.
#            if cat.getLabel():
#                catElem.setAttribute(u"label", cat.getLabel()) #$NON-NLS-1$
            if cat.getScheme():
                catElem.setAttribute(u"scheme", cat.getScheme()) #$NON-NLS-1$
            elif self.getCategoryScheme():
                catElem.setAttribute(u"scheme", self.getCategoryScheme()) #$NON-NLS-1$
            self.getDom().selectSingleNode(u"/atom:entry").appendChild(catElem) #$NON-NLS-1$
    # end _setAtomCategories()

    def _setEditLink(self, editLink):
        linkElem = self.getDom().selectSingleNode(u'/atom:entry/atom:link[@rel="edit"]') #$NON-NLS-1$
        if linkElem:
            linkElem.setAttribute(u"href", editLink) #$NON-NLS-1$
    # _setEditLink()

    def _getEditLink(self):
        linkElem = self.getDom().selectSingleNode(u'/atom:entry/atom:link[@rel="edit"]') #$NON-NLS-1$
        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end _getEditLink()

    def _setDateStr(self, dateTimeStr):
        # For new entry, set the published time.
        self._setPublishedDateStr(dateTimeStr)
        self._setUpdatedDateStr(dateTimeStr)
    # end _setDateStr()
    
    def _setPublishedDateStr(self, dateTimeStr):
        elem = self.getDom().selectSingleNode(u"/atom:entry/atom:published") #$NON-NLS-1$
        if not elem:
            elem = self.getDom().createElement(u"published", ATOM_10_FEED_NAMESPACE) #$NON-NLS-1$
            self.getDom().selectSingleNode(u"/atom:entry").appendChild(elem) #$NON-NLS-1$
        if elem:
            elem.setText(dateTimeStr)
    # end _setPublishedDateStr()

    def _setUpdatedDateStr(self, dateTimeStr):
        elem = self.getDom().selectSingleNode(u"/atom:entry/atom:updated") #$NON-NLS-1$
        if not elem:
            elem = self.getDom().createElement(u"updated", ATOM_10_FEED_NAMESPACE) #$NON-NLS-1$
            self.getDom().selectSingleNode(u"/atom:entry").appendChild(elem) #$NON-NLS-1$
        if elem:
            elem.setText(dateTimeStr)
    # end _setUpdatedDateStr()

    def _setAuthor(self, author):
        elem = self.getDom().selectSingleNode(u"/atom:entry/atom:author/atom:name") #$NON-NLS-1$
        if elem:
            elem.setText(author)
    # end  _setAuthor
       
    def _setDraft(self, bDraft): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
    # end _setDraft
# end ZAtomEntryDocument

#--------------------------------------------
# interface for atom new/create entry
#--------------------------------------------
class ZAtomNewEntry:

    def __init__(self, atomdoc):
        self.atomdoc = atomdoc
    # end __init__()

    def getEntryDocument(self):
        return self.atomdoc
    # end getEntryDocument()

    def setTitle(self, title):
        self.atomdoc.setTitle(title)
    # end setTitle()

    def setContent(self, content):
        self.atomdoc.setContent(content)
    # end setContent()

    def setCategories(self, catList):
        self.atomdoc.setCategories(catList)
    # end setCategories()

    def setDate(self, dateTime = None):
        self.atomdoc.setDate(dateTime)
    # end setDate()

    def setDraft(self, bDraft):
        self.atomdoc.setDraft(bDraft)
    # end setDraft()

    def setAuthor(self, author):
        self.atomdoc.setAuthor(author)
    # end setAuthor()
# end ZAtomNewEntry()


#--------------------------------------------
# atom edit/update entry
#--------------------------------------------
class ZAtomEditEntry(ZAtomNewEntry):

    def __init__(self, atomdoc):
        ZAtomNewEntry.__init__(self, atomdoc)
    # end __init__

    def setEditLink(self, editLink):
        self.atomdoc.setEditLink(editLink)
    # end setEditLink()
    
    def getEditLink(self):
        return self.atomdoc.getEditLink()
    # end getEditLink()

    def setId(self, entryId):
        self.atomdoc.setId(entryId)
    # end setId()

#--------------------------------------------
# interface for atom new/create entry
#--------------------------------------------
class ZAtomNewBlogEntry(ZAtomNewEntry):

    def __init__(self, atomdoc):
        ZAtomNewEntry.__init__(self, atomdoc)
    # end __init__()

# end ZAtomNewBlogEntry()

#--------------------------------------------
# atom edit/update entry
#--------------------------------------------
class ZAtomEditBlogEntry(ZAtomNewBlogEntry, ZAtomEditEntry):

    def __init__(self, atomdoc):
        ZAtomNewBlogEntry.__init__(self, atomdoc)
        ZAtomEditEntry.__init__(self, atomdoc)
    # end ZAtomEditBlogEntry
# end ZAtomEditBlogEntry


#--------------------------------------------
# atom delete entry
#--------------------------------------------
class ZAtomDeleteBlogEntry(ZAtomEditBlogEntry):

    def __init__(self, atomdoc):
        ZAtomEditBlogEntry.__init__(self, atomdoc)
    # end __init__()
# end ZAtomDeleteBlogEntry

#-------------------------------------------------------------
# Class Definition for an Atom API Request.  This is a base
# class which should be extended to implement specific Atom
# requests, such as posting a new entry, modifying an entry,
# getting a list of entries, etc etc.
#-------------------------------------------------------------
class ZAtomRequest(ZSimpleXmlHTTPRequest):

    def __init__(self, url, username, password, debug = False):
        atomHeaders = {}
        atomHeaders[u"Accept"] = u"application/atom+xml; text/html; text/xml; text/plain" #$NON-NLS-2$ #$NON-NLS-1$
        atomHeaders[u"Content-Type"] = u"application/atom+xml" #$NON-NLS-2$ #$NON-NLS-1$
        ZSimpleXmlHTTPRequest.__init__(self, url, atomHeaders)
        self.setAuthorization(username, password)
        self.errorData = None
        self.dom = None
        self.debug = debug
        self.logger = None
    # end __init__()

    def setLogger(self, logger):
        self.logger = logger

    def getLogger(self):
        return self.logger

    def setDebug(self, bdebug):
        self.debug = bdebug

    def _isDebug(self):
        return self.debug

    def getRequestType(self):
        # descriptive name or  type of request - normally overloaded by subclasses.
        return self.__class__.__name__

    def _debug(self, message):
        if self.getLogger():
            self.getLogger().debug(message)

    def _error(self, message):
        if self.getLogger():
            self.getLogger().error(message)

    def _warning(self, message):
        if self.getLogger():
            self.getLogger().warning(message)

    def _logData(self, prefix, data, ext): #@UnusedVariable
        if self.getLogger() and data:
            fname = u"atom_" + prefix + u"_" + time.strftime(str(u"%Y-%m-%dT%H.%M.%SZ"), time.gmtime()) + u"." + ext #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
            data = convertToUnicode(data)
            self.getLogger().logData(fname, data)
        else:
            self._error(u"No data found for _logData.") #$NON-NLS-1$
    # end _logData()

    # Logs the post data of the current request to a file.
    def _logPostData(self, data):
        if self._isDebug():
            self._logData(u"req", data, u"xml") #$NON-NLS-2$ #$NON-NLS-1$
    # end _logPostData()

    # Logs the response data to a file.
    def _logRespData(self, data):
        if self._isDebug():
            self._logData(u"resp", data, u"xml") #$NON-NLS-2$ #$NON-NLS-1$
    # end _logRespData()

    # Logs an error response.
    def _logErrorResponse(self, data):
        if self._isDebug():
            self._logData(u"resp_error", data, u"log") #$NON-NLS-2$ #$NON-NLS-1$
    # end _logErrorResponse()

    def _processPostData(self, postData):
        data = postData
        if data and isinstance(data, ZAtomDocument):
            data = postData.getDom() # entry zdom
        data = ZSimpleXmlHTTPRequest._processPostData(self, data)
        self._logPostData(data)
        return data
    # end _processPostData()

    def _processResponseData(self, resp, txt):
        dom = None
        if txt and len( txt.strip() ) > 0:
            self._logRespData(txt)
            dom = ZSimpleXmlHTTPRequest._processResponseData(self, resp, txt)
            self._setDomNSS(dom)

        elif resp.status >= 200 and resp.status <= 299:
            txt = u"Empty response data. Http code %d for URI %s" % (resp.status, self.url)  #$NON-NLS-1$
            self._debug(txt )
            # create place holder dom
            dom = self._createEmptyFeed()
        else:
            txt = u"Empty response data. Http code %d for URI %s" % (resp.status, self.url)  #$NON-NLS-1$
            self._error(txt)

        self.dom = dom
        return dom
    # end _processResponseData()

    def _createEmptyFeed(self):
        # create place holder dom
        dom = ZDom()
        dom.loadXML(ATOM_10_EMPTY_FEED_XML)
        self._setDomNSS(dom)
        return dom

    def _setDomNSS(self, dom): #@UnusedVariable
        pass

    def _getAuthSchemeFromResponse(self, httpResponse):
        # return wsse for tp
        scheme = ZSimpleXmlHTTPRequest._getAuthSchemeFromResponse(self, httpResponse)
        if not scheme:
            # use xwsse as default. (Typepad does not return auth scheme - bug)
            scheme = ZXWsseUsernameAuthHandler.SCHEME
        return scheme

    def _responseIsAuthenticate(self, resp):
        # Note, sometimes, Typepad returns 500 or 409 instead of 401.
        rval = resp.status == 401 or  resp.status == 409 or resp.status >= 500
        return rval

    def _processError(self, resp):
        self._atomProcessError(resp)
    # end _processError()

    def _responseIsGood(self, resp):
        if resp:
            self._debug(u"atom request http response is %d" % resp.status)#$NON-NLS-1$
        else:
            self._debug(u"atom request http response is None")#$NON-NLS-1$
            return False
        return self._atomResponseIsGood(resp)

    def _atomResponseIsGood(self, resp):
        return resp.status >= 200 and resp.status <= 299

    def _atomProcessError(self, resp):
        self.errorData = ZSimpleXmlHTTPRequest._processError(self, resp)
        self._logErrorResponse(self.errorData)
    # end _processError()

    def getErrorMessage(self):
        return self.errorData
    # end getErrorMessage()

    def getDom(self):
        return self.dom

# end AtomRequest

#================================
# V.1.0 request base
# Sublcasses must implement:
# _setDomNSS(map)
#================================

class ZAtom10RequestBase(ZAtomRequest):

    def __init__(self, url, username, password):
        ZAtomRequest.__init__(self, url, username, password)
    # end __init__()

    def _hasMore(self):
        nextHref = self._getNextHref()
        lastHref = self._getLastHref()
        selfHref = self._getSelfHref()
        rVal = False
        if nextHref and selfHref and lastHref and selfHref != lastHref:
            rVal = True
        elif nextHref and selfHref and selfHref != nextHref:
            rVal = True
        return rVal
    # end _hasMore()

    def _getNextHref(self):
        return self._getLinkHref(u"next")  #$NON-NLS-1$
    # end _getNextHref()

    def _getSelfHref(self):
        return self._getLinkHref(u"self")  #$NON-NLS-1$
    # end _getSelfHref()

    def _getLastHref(self):
        return self._getLinkHref(u"last")  #$NON-NLS-1$
    # end _getLastHref()

    def _getLinkHref(self, rel):
        if self.getDom():
            linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = '%s']" % rel) #$NON-NLS-1$
            if linkElem:
                return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end _getLinkHref()
# end ZAtom10RequestBase      

#================================
# Base class for atom 1.0 feed request
# Sublcasses must implement:
# _setDomNSS(map)
# _getEntryList()
#================================
class ZAtom10FeedRequestBase(ZAtom10RequestBase):

    def __init__(self, url, username, password):
        ZAtom10RequestBase.__init__(self, url, username, password)
    # end __init__()

    def getPostLink(self):
        u"Returns the link used to post new entries to, or None." #$NON-NLS-1$
        linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'service.post']") #$NON-NLS-1$
        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end getPostLink()

    def getFeedLink(self):
        u"Returns the link used to retrieve the feed, or None." #$NON-NLS-1$
        linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'service.feed']") #$NON-NLS-1$
        if not linkElem:
            # try SixApart Vox format
            linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'service.subscribe']") #$NON-NLS-1$
        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end getFeedLink()

    def getTitle(self):
        u"Returns the title of the feed, or None." #$NON-NLS-1$
        titleElem = self.getDom().selectSingleNode(u"/atom:feed/atom:title") #$NON-NLS-1$
        if titleElem:
            return titleElem.getText()
        else:
            return u"" #$NON-NLS-1$
    # end getTitle()

    def getSubTitle(self):
        u"Returns the feed tagline, or None." #$NON-NLS-1$
        taglineElem = self.getDom().selectSingleNode(u"/atom:feed/atom:subtitle") #$NON-NLS-1$
        if taglineElem:
            return taglineElem.getText()
        else:
            return u"" #$NON-NLS-1$
    # end getSubTitle()
    
    def getAlternateLink(self):
        u"Returns a link to the alternate representation of the entry, or None." #$NON-NLS-1$
        altLinkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'alternate']") #$NON-NLS-1$
        if altLinkElem:
            return altLinkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None
    # end getAlternateLink()

    def getId(self):
        u"Returns the ID of this entry, or None." #$NON-NLS-1$
        idElem = self.getDom().selectSingleNode(u"/atom:feed/atom:id") #$NON-NLS-1$
        if idElem:
            return idElem.getText()
        else:
            return None
    # end getId()

    # Returns the generator information (who generated the feed).
    def getGenerator(self):
        u"Returns the feed generator information XML node, or None." #$NON-NLS-1$
        return self.getDom().selectSingleNode(u"/atom:feed/atom:generator") #$NON-NLS-1$
    # end getGenerator()

    # Gets a list of entries found in this feed.
    def getEntries(self):
        u"Gets a list of entries found in this feed or empty list None." #$NON-NLS-1$
        if self.getDom():
            return self._getEntryList()
        else:
            return []
    # end getEntries()

    def _getEntryList(self):
        # Map the entry constructor onto the list of entry XML nodes.
        return map(ZAtomFeedEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end _getEntryList()
# end ZAtom10FeedRequestBase

#===================================================
# Atom Server base
#===================================================
class ZAtomServerBase(ZBlogServer):

    def __init__(self, apiUrl, username, password, authScheme = None, version = None, name =  u"ZAtomServer"): #$NON-NLS-1$
        ZBlogServer.__init__(self, apiUrl, username, password, version, name)
        self.authScheme = authScheme # not used anymore.
    # end __init__()

    def getAuthScheme(self):
        return self.authScheme
    # end getAuthScheme()

    def _initAtomRequest(self, atomRequest):
        atomRequest.setLogger( self.getLogger() )
        atomRequest.setDebug( self.isDebug() )
        atomRequest.setAuthenticationScheme(self.getAuthScheme())
    # end _initAtomRequest()

    def _sendAtomRequest(self, atomRequest):
        self._initAtomRequest(atomRequest)
        if not atomRequest.send():
            self._error(atomRequest.getRequestType() + u" request failed.") #$NON-NLS-1$
            raise ZAtomException(atomRequest.getErrorMessage())
    # end _sendAtomRequest()

    def _sendAtomEntry(self, atomRequest, atomEntry):
        self._sendAtomDocument(atomRequest, atomEntry.getEntryDocument() )
    # end _sendAtomEntry()
    
    def _sendAtomDocument(self, atomRequest, atomDocument):
        self._initAtomRequest(atomRequest)
        if not atomRequest.send(atomDocument):
            self._error(atomRequest.getRequestType() + u" request failed.") #$NON-NLS-1$
            raise ZAtomException(atomRequest.getErrorMessage())
    # end _sendAtomDocument()     
# end ZAtomServerBase  

#================================================
# Atom Blog Server base class.
#================================================
class ZAtomServer(ZAtomServerBase):

    def __init__(self, apiUrl, username, password, authScheme = None, version = None, name =  u"ZAtomServer"): #$NON-NLS-1$
        ZAtomServerBase.__init__(self, apiUrl, username, password, authScheme, version, name)
    # end __init__()

    def _initNewEntryDocument(self, atomDoc): #@UnusedVariable
        u"""Allows subclasses to initialize the atom new entry dom.""" #$NON-NLS-1$
        pass
    # end _initNewEntryDocument()

    def _initEditEntryDocument(self, atomDoc): #@UnusedVariable
        u"""Allows subclasses to initialize the atom edit entry dom.""" #$NON-NLS-1$
        pass
    # end _initEditEntryDocument()

    def _initDeleteEntryDocument(self, atomDoc): #@UnusedVariable
        u"""Allows subclasses to initialize the atom delete entry dom.""" #$NON-NLS-1$
        pass
    # end _initDeleteEntryDocument()

    def createNewBlogEntry(self):
        u"""Creates and returns a AtomNewBlogEntry wrapper object.""" #$NON-NLS-1$
        atomdoc = self._createNewEntryDocument()
        self._initNewEntryDocument(atomdoc)
        return ZAtomNewBlogEntry(atomdoc)
    # end createNewBlogEntry()

    def createEditBlogEntry(self):
        u"""Creates and returns a AtomEditBlogEntry wrapper object.""" #$NON-NLS-1$
        atomdoc = self._createEditEntryDocument()
        self._initEditEntryDocument(atomdoc)
        return ZAtomEditBlogEntry(atomdoc)
    # end createEditBlogEntry()

    def createDeleteBlogEntry(self):
        u"""Creates and returns a AtomDeleteBlogEntry wrapper object.""" #$NON-NLS-1$
        atomdoc = self._createDeleteEntryDocument()
        self._initDeleteEntryDocument(atomdoc)
        return ZAtomDeleteBlogEntry(atomdoc)
    # end createDeleteBlogEntry()

    def listBlogs(self):
        u"""Returns list of AtomBlog objects.""" #$NON-NLS-1$
        atomRequest = self._createListBlogsRequest()
        self._sendAtomRequest(atomRequest)
        blogList = atomRequest.getBlogList()
        del atomRequest
        self._debug(u"Atom List Blogs - returned a list of %d blogs." % len(blogList)) #$NON-NLS-1$
        return blogList

    def getAtomEntry(self, editLink):
        u"""Returns a AtomBlogEntry object for the entry edit link.""" #$NON-NLS-1$
        atomRequest = self._createGetEntryRequest(editLink)
        self._sendAtomRequest(atomRequest)
        rval = atomRequest.getEntry()
        del atomRequest
        return rval
    # end getAtomEntry()

    def listAtomEntries(self, feedLink, maxEntries=-1): #@UnusedVariable
        u"""Returns list of AtomBlogEntry objects for the given feed link.""" #$NON-NLS-1$
        atomRequest = self._createListEntriesRequest(feedLink)
        self._sendAtomRequest(atomRequest)
        rval = atomRequest.getEntries()
        del atomRequest
        return rval
    # end listAtomEntries()

    def listCategories(self, categoriesLink):
        u"""Returns list of AtomCategory objects.""" #$NON-NLS-1$
        atomRequest = self._createListCategoriesRequest(categoriesLink)
        self._sendAtomRequest(atomRequest)
        catList = atomRequest.getCategoryList()
        del atomRequest
        return catList
    # end listCategories()

    def createAtomEntry(self, postLink, atomNewEntry):
        u"""Creates (posts) a new entry to the server and returns a AtomBlogEntry as the response.""" #$NON-NLS-1$
        atomRequest = self._createNewEntryRequest(postLink, atomNewEntry)
        self._sendAtomEntry(atomRequest, atomNewEntry)
        atomEntry = atomRequest.getEntry()
        del atomRequest
        return atomEntry
    # end createAtomEntry()

    def updateAtomEntry(self, editLink, atomEditEntry):
        u"""Updates an entry on the server and returns a AtomBlogEntry as the response.""" #$NON-NLS-1$
        atomRequest = self._createUpdateEntryRequest(editLink, atomEditEntry)
        self._sendAtomEntry(atomRequest, atomEditEntry)
        #
        # Note:
        # Typepad 0.3 version's response does not include the edit link.
        #
        atomEntry = atomRequest.getEntry()
        del atomRequest
        return atomEntry
    # end updateAtomEntry()

    def deleteAtomEntry(self, deleteLink, atomDeleteEntry):
        u"""Deletes the given entry from the server and returns true, else throws error on fault.""" #$NON-NLS-1$
        atomRequest = self._createDeleteEntryRequest(deleteLink, atomDeleteEntry)
        self._sendAtomRequest(atomRequest)
        return True
    # end deleteAtomEntry()

    def newPost(self, postLink, zserverBlogEntry):
        u"""Convenience method to create (blog post) a new entry to the server using the ZServerBlogEntry class.
        This method returns a AtomBlogEntry as the response.""" #$NON-NLS-1$
        atomEntry = self.createNewBlogEntry()
        self._populateAtomEntry(atomEntry, zserverBlogEntry)
        # publish entry
        atomRespEntry = self.createAtomEntry(postLink, atomEntry)
        return atomRespEntry
    # end newPost()

    def updatePost(self, editLink, entryId, zserverBlogEntry):
        u"""Convenience method to update a (post) entry to the server using the ZServerBlogEntry class.
        This method returns a AtomBlogEntry as the response.""" #$NON-NLS-1$
        atomEntry = self.createEditBlogEntry()
        atomEntry.setId(entryId)
        atomEntry.setEditLink(editLink)
        self._populateAtomEntry(atomEntry, zserverBlogEntry)
        # update entry
        atomRespEntry = self.updateAtomEntry(editLink, atomEntry)
        return atomRespEntry
    # end updatePost()

    def deletePost(self, editLink, entryId):
        u"""Convenience method to delete an entry given edit link and entry id..
        This method returns True if the entry was deleted.""" #$NON-NLS-1$

        deleteAtomEntry = self.createDeleteBlogEntry()
        deleteAtomEntry.setId(entryId)
        return self.deleteAtomEntry(editLink, deleteAtomEntry)
    # end deletePost()

    def _populateAtomEntry(self, atomEntry, zserverBlogEntry):
        title = getSafeString( zserverBlogEntry.getTitle() )
        content = getSafeString( self._formatContentForPublishing( zserverBlogEntry ) )
        utcDateTime = zserverBlogEntry.getUtcDateTime()
        draft = zserverBlogEntry.isDraft()
        author = getNoneString( zserverBlogEntry.getAuthor() )
        if not author:
            author = self.getUsername()

        atomEntry.setTitle(title)
        atomEntry.setDate(utcDateTime)
        atomEntry.setContent(content)
        atomEntry.setDraft(draft)
        atomEntry.setAuthor(author)

        atomCatList = []
        # list of categories already added
        catNames = []
        for cat in zserverBlogEntry.getCategories():
            # map Zoundry cat id to atom category 'term' attribute.
            atomCat = ZAtomCategory(cat.getId(), cat.getName() )
            atomCatList.append( atomCat )
            name = cat.getName().lower()
            if name not in catNames:
                catNames.append(name)
        # Special case for Blogger. Blend zcategories + ztags into atom catories
        # FIXME (PJ) externalize this to a capability or param
        if zserverBlogEntry.getTagwords() and self.getApiUrl().startswith(u"http://www.blogger.com/feeds/default/blogs"): #$NON-NLS-1$
            for tagword in zserverBlogEntry.getTagwords():
                if tagword.lower() not in catNames:
                    catid = tagword
                    atomCat = ZAtomCategory(catid, tagword )
                    atomCatList.append( atomCat )

        atomEntry.setCategories(atomCatList)
    # end _populateAtomEntry()

    # -------------------------------------------
    # Abstract methods to be implemented by subclasses
    # -------------------------------------------
    def _createNewEntryDocument(self):
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createNewEntryDocument()

    def _createEditEntryDocument(self):
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createEditEntryDocument()

    def _createDeleteEntryDocument(self):
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createDeleteEntryDocument()

    def _createListBlogsRequest(self):
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createListBlogsRequest()

    def _createGetEntryRequest(self, editLink): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createGetEntryRequest()

    def _createListEntriesRequest(self, feedLink): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createListEntriesRequest()

    def _createListCategoriesRequest(self, categoriesLink): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createListCategoriesRequest()

    def _createNewEntryRequest(self, postLink, atomNewEntry): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createNewEntryRequest()

    def _createUpdateEntryRequest(self, editLink, atomEditEntry): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    #end _createNewEntryRequest()

    def _createDeleteEntryRequest(self, deleteLink, atomDeleteEntry): #@UnusedVariable
        self.warning(u"Method called on abstract base class.") #$NON-NLS-1$
        return None
    # end _createDeleteEntryRequest()
# end ZAtomServer    

class ZAtomServerFactory(IZBlogServerFactory):

    def createServer(self, properties): #@UnusedVariable
        u"""createServer(dict) ->  ZAtomServer
        Creates and returns an atom server proxy."""#$NON-NLS-1$
        className = properties[IZBlogApiParamConstants.SERVER_CLASSNAME]
        url = properties[IZBlogApiParamConstants.API_ENDPOINT_URL]
        username = properties[IZBlogApiParamConstants.API_USERNAME]
        password = properties[IZBlogApiParamConstants.API_PASSWORD]
        version = None #@UnusedVariable
        if properties.has_key(IZBlogApiParamConstants.API_CLIENT_VERSION):
            version = properties[IZBlogApiParamConstants.API_CLIENT_VERSION] #@UnusedVariable
        authScheme = None
        if properties.has_key(IZBlogApiParamConstants.API_AUTH_SCHEME):
            authScheme = properties[IZBlogApiParamConstants.API_AUTH_SCHEME]

        # Load class
        atomServerClass = ZClassLoader().loadClass(className)
        # Create new instance, with url = base data dir.
        server = atomServerClass(url, username, password, authScheme)

        return server
    #end createServer
#end ZAtomServerFactory

