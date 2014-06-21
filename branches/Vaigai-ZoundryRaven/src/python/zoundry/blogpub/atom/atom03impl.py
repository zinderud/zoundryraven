from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
from zoundry.base.net.http import HTTP_DELETE
from zoundry.base.net.http import HTTP_PUT
from zoundry.base.net.http import HTTP_POST
from zoundry.blogpub.atom.atomapi import getAtomGeneratorVersion
from zoundry.blogpub.atom.atomapi import getAtomGeneratorName
from zoundry.blogpub.atom.atomapi import ZAtomException
from zoundry.blogpub.atom.atomapi import ZAtomBlog
from zoundry.blogpub.atom.atomapi import ZAtomCategory
from zoundry.blogpub.atom.atomapi import ZAtomBlogEntry
from zoundry.blogpub.atom.atomapi import ZAtomEntryDocument

from zoundry.blogpub.atom.atomapi import ZAtomRequest
from zoundry.blogpub.atom.atomapi import ZAtomServer

from zoundry.blogpub.namespaces import ATOM_03_FEED_NAMESPACE
from zoundry.blogpub.namespaces import XHTML_NAMESPACE
from zoundry.blogpub.namespaces import DUBLIN_CORE_ELE_NAMESPACE
from zoundry.blogpub.namespaces import BLOGGER_ATOM03_EXT_NAMESPACE
from zoundry.blogpub.namespaces import SA_ATOM_CATEGORIES_NAMESPACE


#================================================
# Atom 0.3 Impl.
#================================================
ATOM_NEW_BLOG_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<entry xmlns="http://purl.org/atom/ns#">
   <generator url="http://www.zoundry.com" version="%s">%s</generator>
   <title mode="escaped" type="text/html" />
   <issued />
   <content mode="escaped" type="text/html" />
</entry>
""" % (getAtomGeneratorVersion(), getAtomGeneratorName() )#$NON-NLS-1$

ATOM_EDIT_BLOG_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<entry xmlns="http://purl.org/atom/ns#">
   <generator url="http://www.zoundry.com" version="%s">%s</generator>
   <issued />
   <link />
   <title type="text/html" mode="escaped" />
   <content type="text/html" mode="escaped" />
</entry>
""" % (getAtomGeneratorVersion(), getAtomGeneratorName()) #$NON-NLS-1$


ATOM_NSS_MAP = {
    u"atom"   : ATOM_03_FEED_NAMESPACE,  #$NON-NLS-1$
    u"pab"    : BLOGGER_ATOM03_EXT_NAMESPACE, #$NON-NLS-1$
    u"xhtml"  : XHTML_NAMESPACE,  #$NON-NLS-1$
    u"tp"     : SA_ATOM_CATEGORIES_NAMESPACE,  #$NON-NLS-1$
    u"dc"     : DUBLIN_CORE_ELE_NAMESPACE  #$NON-NLS-1$
}

# FIXME (PJ) handle typepad atom convertLineBrak -> <convertLineBreaks xmlns="http://sixapart.com/atom/post#">true</convertLineBreaks>

#================================================
# Atom 0.3 Blog
#================================================
class Atom03Blog(ZAtomBlog):

    def __init__(self, nodeSet = None):
        ZAtomBlog.__init__(self)
        self._extractBlogInfo(nodeSet)
    # end __init__()

    def _extractBlogInfo(self, nodeSet):
        #
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.post" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.feed" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.upload" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=upload" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.categories" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=categories" title="joey" />
        # note: alt link:
        #  <link xmlns="http://purl.org/atom/ns#" type="text/html" rel="alternate" href="http://pidge.blogs.com/joey/" title="joey" />
        id = None
        name = None
        type = u"text/html"  #$NON-NLS-1$
        for node in nodeSet:
            name = node.getAttribute(u"title") #$NON-NLS-1$
            rel = node.getAttribute(u"rel") #$NON-NLS-1$
            if rel == u"service.post": #$NON-NLS-1$
                id = node.getAttribute(u"href") #$NON-NLS-1$
                type = node.getAttribute(u"type") #$NON-NLS-1$
                self.setAttribute(ZAtomBlog.POST_LINK, id, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
            elif rel == u"service.feed": #$NON-NLS-1$
                self.setAttribute(ZAtomBlog.FEED_LINK, node.getAttribute(u"href"), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE )#$NON-NLS-1$
            elif rel == u"service.upload": #$NON-NLS-1$
                self.setAttribute(ZAtomBlog.UPLOAD_LINK, node.getAttribute(u"href"), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE ) #$NON-NLS-1$
            elif rel == u"service.categories": #$NON-NLS-1$
                self.setAttribute(ZAtomBlog.CATEGORIES_LINK, node.getAttribute(u"href"), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)  #$NON-NLS-1$
            elif rel == u"alternate": #$NON-NLS-1$
                self.setAttribute(ZAtomBlog.ALT_LINK, node.getAttribute(u"href"), IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)  #$NON-NLS-1$
        # end for
        self.setAttribute(ZAtomBlog.CONTENT_TYPE, type, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        url = self.getAttribute(ZAtomBlog.ALT_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        if not url:
            url = self.getAttribute(ZAtomBlog.FEED_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        self._setId(id)
        self._setName(name)
        self._setUrl(url)


#================================================
# Atom 0.3 Blog/Feed Entry
#================================================
class ZAtom03BlogEntry(ZAtomBlogEntry):
    # Constructs an Atom blog entry object from an Atom XML entry node.
    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZAtomBlogEntry.__init__(self, entryNode, prefix)
    # end __init__()

    def _getPublishedDate(self):
        dtStr = self.getNode().selectSingleNodeText(u"%sissued" % self.prefix, None) #$NON-NLS-1$
        if not dtStr:
            dtStr = self.getNode().selectSingleNodeText(u"%screated" % self.prefix, None) #$NON-NLS-1$
        return dtStr

    def _getUpdatedDate(self):
        dtStr = self.getNode().selectSingleNodeText(u"%smodified" % self.prefix, None) #$NON-NLS-1$
        if not dtStr:
            dtStr = self.getNode().selectSingleNodeText(u"%sissued" % self.prefix, None) #$NON-NLS-1$
        return dtStr

    def _getCategories(self):
        u"Gets the value of the categories - supported by TypePad only right now." #$NON-NLS-1$
        categories = self.getNode().selectNodes(u"dc:subject") #$NON-NLS-1$
        if categories and len(categories) > 0:
            rVal = []
            for cat in categories:
                term = cat.getText()
                rVal.append( ZAtomCategory(term, None , None) )
            return rVal
        else:
            # revert to atom <category> element. Note that Typepad now uses this element instead of dc:subject, but still in the 0.3 namespace.
            return ZAtomBlogEntry._getCategories(self)

    def _isDraft(self):
        # Blogger 0.3 only.
        draftElem = self.getNode().selectSingleNode(u"pab:draft") #$NON-NLS-1$
        if draftElem:
            return draftElem.getText() == u"true" or draftElem.getText() == u"True" #$NON-NLS-2$ #$NON-NLS-1$
        return False

    # Gets content formatted as XML (TypePad).
    def _getXMLContent(self, contentNode):
        u"Gets content formatted as XML (TypePad)." #$NON-NLS-1$
        rval = ZAtomBlogEntry._getXMLContent(self,contentNode)
        rval = rval.replace(u"<default:", u"<") #$NON-NLS-2$ #$NON-NLS-1$
        rval = rval.replace(u"</default:", u"</") #$NON-NLS-2$ #$NON-NLS-1$
        return rval
    # end _getXMLContent()


#--------------------------------------------
# new entry
#--------------------------------------------
class ZAtom03EntryDocument(ZAtomEntryDocument):

    def __init__(self):
        ZAtomEntryDocument.__init__(self)

    def _initNode(self, dom):
        dom.loadXML(ATOM_NEW_BLOG_ENTRY_TEMPLATE)
        dom.setNamespaceMap(ATOM_NSS_MAP)

    def _setEditLink(self, editLink):
        linkElem = self.getDom().selectSingleNode(u"/atom:entry/atom:link") #$NON-NLS-1$
        if linkElem:
            linkElem.setText(editLink)

    def _getEditLink(self):
        linkElem = self.getDom().selectSingleNode(u"/atom:entry/atom:link") #$NON-NLS-1$
        if linkElem:
            return linkElem.getText()
        else:
            return None

    def _setCategories(self, atomCategoryList):
        # Set Atom categories using 0.3 namespace since now Typepad uses it - not sure if this is permanent.
        self._setAtomCategories(atomCategoryList, ATOM_03_FEED_NAMESPACE)
        # Typepad 0.3 - the original way Typepad used to set categories.
#        for cat in atomCategoryList:
#            catElem = self.getDom().createElement(u"subject", DUBLIN_CORE_ELE_NAMESPACE)  #$NON-NLS-1$
#            catElem.setText(cat.getTerm())
#            self.getDom().selectSingleNode(u"/atom:entry").appendChild(catElem) #$NON-NLS-1$

    def _setDraft(self, bDraft):
        # blogger only
        draftVal = u"false" #$NON-NLS-1$
        if bDraft:
            draftVal = u"true" #$NON-NLS-1$

        entryElem = self.getDom().selectSingleNode(u"/atom:entry") #$NON-NLS-1$
        draftElem = self.getDom().selectSingleNode(u"/atom:entry/pab:draft") #$NON-NLS-1$
        # If we didn't find the draft element, make a new one
        if not draftElem:
            draftElem = self.getDom().createElement(u"draft", BLOGGER_ATOM03_EXT_NAMESPACE) #$NON-NLS-1$
            entryElem.appendChild(draftElem)
        draftElem.setText(draftVal)

    def _setDateStr(self, dateTimeStr):
        issuedElem = self.getDom().selectSingleNode(u"/atom:entry/atom:issued") #$NON-NLS-1$
        if issuedElem:
            issuedElem.setText(dateTimeStr)

    def _setAuthor(self, author): #@UnusedVariable
        pass


#--------------------------------------------
# edit entry
#--------------------------------------------
class ZAtom03EditDocument(ZAtom03EntryDocument):

    def __init__(self):
        ZAtom03EntryDocument.__init__(self)

    def _initNode(self, dom):
        dom.loadXML(ATOM_EDIT_BLOG_ENTRY_TEMPLATE)
        dom.setNamespaceMap(ATOM_NSS_MAP)


#================================
# V.0.3 request
#================================

class ZAtom03Request(ZAtomRequest):

    def __init__(self, url, username, password):
        ZAtomRequest.__init__(self, url, username, password)

    def _setDomNSS(self, dom):
        dom.setNamespaceMap(ATOM_NSS_MAP)

#================================
# V.0.3 category request
#================================
class ZAtom03CategoryListRequest(ZAtom03Request):
    def __init__(self, url, username, password):
        ZAtom03Request.__init__(self, url, username, password)
    # end __init__()

    def getCategoryList(self):
        rval = []
        for node in self.getDom().selectNodes(u"/tp:categories/dc:subject"): #$NON-NLS-1$
            rval.append(ZAtomCategory( node.getText()) )
        return rval

#================================
# V.0.3 blog list request
#================================
class ZAtom03BlogListRequest(ZAtom03Request):
    def __init__(self, url, username, password):
        ZAtom03Request.__init__(self, url, username, password)
    # end __init__()

    # Gets the list of returned blogs.
    def getBlogList(self):
        u"Gets the list of returned blogs." #$NON-NLS-1$
        # For each blog (based on link title), expect the following:
        # (only service.post and service.feed is required; Typepad also supports service.upload and service.categories)
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.post" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.feed" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.upload" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=upload" title="joey" />
        #  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.categories" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=categories" title="joey" />

        # Sort out links into bins based on title (blog name) attribute.
        linkSets = {}
        for node in self.getDom().selectNodes(u"/atom:feed/atom:link"): #$NON-NLS-1$
            title = node.getAttribute(u"title") #$NON-NLS-1$
            linkSet = []
            if linkSets.has_key(title):
                linkSet = linkSets[title]
            else:
                linkSets[title] = linkSet
            linkSet.append(node)
        return map(Atom03Blog, linkSets.values())
    # end getBlogList()

#================================
# V.0.3 blog feed request
#================================
class ZAtom03FeedRequest(ZAtom03Request):
    def __init__(self, url, username, password):
        ZAtom03Request.__init__(self, url, username, password)
    # end __init__()

    # Returns the link used to post new blog entries to.
    def getPostLink(self):
        u"Returns the link used to post new blog entries to, or None." #$NON-NLS-1$
        linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'service.post']") #$NON-NLS-1$
        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None

    # end getPostLink()

    # Returns the link used to retrieve the blog feed.
    def getFeedLink(self):
        u"Returns the link used to retrieve the blog feed, or None." #$NON-NLS-1$
        linkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'service.feed']") #$NON-NLS-1$
        if linkElem:
            return linkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None

    # end getFeedLink()

    # Returns the title of the blog.
    def getTitle(self):
        u"Returns the title of the blog, or None." #$NON-NLS-1$
        titleElem = self.getDom().selectSingleNode(u"/atom:feed/atom:title") #$NON-NLS-1$
        if titleElem:
            return titleElem.getText()
        else:
            return u"" #$NON-NLS-1$
    # end getTitle()

    # Returns the blog tagline.
    def getSubTitle(self):
        u"Returns the blog tagline, or None." #$NON-NLS-1$
        taglineElem = self.getDom().selectSingleNode(u"/atom:feed/atom:tagline") #$NON-NLS-1$
        if taglineElem:
            return taglineElem.getText()
        else:
            return u"" #$NON-NLS-1$

    # end getTagline()

    # Returns a link that points to the 'alternate' representation of this blog (typically the
    # human readable html representation).
    def getAlternateLink(self):
        u"Returns a link to the alternate representation of the blog, or None." #$NON-NLS-1$
        altLinkElem = self.getDom().selectSingleNode(u"/atom:feed/atom:link[@rel = 'alternate']") #$NON-NLS-1$
        if altLinkElem:
            return altLinkElem.getAttribute(u"href") #$NON-NLS-1$
        else:
            return None

    # end getAlternateLink()

    # Returns the ID of this blog.
    def getId(self):
        u"Returns the ID of this blog, or None." #$NON-NLS-1$
        idElem = self.getDom().selectSingleNode(u"/atom:feed/atom:id") #$NON-NLS-1$
        if idElem:
            return idElem.getText()
        else:
            return None

    # end getId()

    # Returns the generator information (who generated the feed).
    def getGenerator(self):
        u"Returns the blog's generator information XML node, or None." #$NON-NLS-1$
        return self.getDom().selectSingleNode(u"/atom:feed/atom:generator") #$NON-NLS-1$
    # end getGenerator()

    # Gets a list of blog entries found in this feed.
    def getEntries(self):
        u"Gets a list of blog entries found in this feed." #$NON-NLS-1$
        # Map the blog entry constructor onto the list of entry XML nodes.
        return map(ZAtom03BlogEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end getBlogEntries()

#-------------------------------------------------------------
# Class Definition for an Atom API GET Entry Request.
#
# This class is not strictly necessary, as a GET request to
# an Atom Entry's service.edit link will simply return an
# Atom Feed with only one entry.  However, the class is used
# to make the coding of the application clearer.
#-------------------------------------------------------------
class ZAtom03BlogEntryRequest(ZAtom03FeedRequest):

    def __init__(self, url, username, password):
        ZAtom03FeedRequest.__init__(self, url, username, password)
    # end __init__()

    # Gets the blog entry as a wrapper object.
    def getEntry(self):
        u"Get a blog entry object." #$NON-NLS-1$
        node = self.getDom().selectSingleNode(u"/atom:entry") #$NON-NLS-1$
        prefix = u"atom:" #$NON-NLS-1$
        if not node:
            self._error(u"//atom:entry in atom NS not found. Trying /entry without namespace. The URI is %s " % self.url)  #$NON-NLS-1$
            node = self.getDom().selectSingleNode(u"//entry") #$NON-NLS-1$
            prefix = u"" #$NON-NLS-1$
        if not node:
            # FIXME (PJ) extern this
            ex = ZAtomException(u"atom.invalid_atom_response_error") #$NON-NLS-1$
            raise ex
        return ZAtom03BlogEntry(node, prefix)
    # end getEntry()

# end AtomBlogEntryRequest


#-------------------------------------------------------------
# Class Definition for an Atom API POST Create Entry Request.
#
# This class creates a new Blog Entry on the server.
#-------------------------------------------------------------
class ZAtom03CreateEntryRequest(ZAtom03Request):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom03Request.__init__(self, url, username, password)
        # This is not a GET (which is the default) so override.
        self._setMethod(HTTP_POST)
    # end __init__()

    # Gets the blog entry as a wrapper object.
    def getEntry(self):
        u"Gets the blog entry object (the response of a POST)." #$NON-NLS-1$
        node = self.getDom().selectSingleNode(u"/atom:entry") #$NON-NLS-1$
        prefix = u"atom:" #$NON-NLS-1$
        if not node:
            node = self.getDom().selectSingleNode(u"/entry") #$NON-NLS-1$
            prefix = u"" #$NON-NLS-1$
        if not node:
            # FIXME (PJ) extern this
            ex = ZAtomException(u"atom.invalid_atom_response_error") #$NON-NLS-1$
            raise ex

        return ZAtom03BlogEntry(node, prefix)
    # end getEntry()

# end AtomCreateEntryRequest


#-------------------------------------------------------------
# Class Definition for an Atom API Edit Blog Entry Request.
#
# This class edits/updates an existing blog entry on the server.
#-------------------------------------------------------------
class Atom03EditEntryRequest(ZAtom03CreateEntryRequest):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom03CreateEntryRequest.__init__(self, url, username, password)
        # This is not a GET (which is the default) so override.
        self._setMethod(HTTP_PUT)
    # end __init__()

    def _atomResponseIsGood(self, resp):
        self._debug(u"STATUS: %d" % resp.status) #$NON-NLS-1$
        return resp.status >= 200 and resp.status <= 301
    # end _responseIsGood()

# end AtomCreateEntryRequest

#-------------------------------------------------------------
# Class Definition for an Atom API Delete Blog Entry Request.
#
# This class deletes an existing blog entry on the server.
#-------------------------------------------------------------
class Atom03DeleteEntryRequest(ZAtom03Request):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom03Request.__init__(self, url, username, password)
        # This is not a GET (which is the default) so override.
        self._setMethod(HTTP_DELETE)
        # Note: do not expect http response data for a delte - just the header only
    # end __init__()

    def _atomResponseIsGood(self, resp):
        return resp.status == 410 or ZAtomRequest._atomResponseIsGood(self, resp)
    # end _responseIsGood()

    # Delete requests probably return no data - so override the _processResponseData() method.
    def _processResponseData(self, resp, txt):  #@UnusedVariable
        return ZAtom03Request._createEmptyFeed(self)
    # end _processResponseData()

# end AtomDeleteEntryRequest

#================================================
# Atom Server base class.
#================================================

class ZAtom03Server(ZAtomServer):

    def __init__(self, username, password, apiUrl, authType):
        ZAtomServer.__init__(self, username, password, apiUrl, authType)

    def _createNewEntryDocument(self):
        return ZAtom03EntryDocument()

    def _createEditEntryDocument(self):
        return ZAtom03EditDocument()

    def _createDeleteEntryDocument(self):
        return ZAtom03EditDocument()

    def _createListBlogsRequest(self):
        atomRequest = ZAtom03BlogListRequest( self.getApiUrl(), self.getUsername(), self.getPassword() )
        return atomRequest

    def _createGetEntryRequest(self, editLink):
        atomRequest = ZAtom03BlogEntryRequest(editLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createListEntriesRequest(self, feedLink):
        atomRequest = ZAtom03FeedRequest(feedLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createListCategoriesRequest(self, categoriesLink):
        atomRequest = ZAtom03CategoryListRequest(categoriesLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createNewEntryRequest(self, postLink, atomNewEntry): #@UnusedVariable
        atomRequest = ZAtom03CreateEntryRequest(postLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createUpdateEntryRequest(self, editLink, atomEditEntry):    #@UnusedVariable
        atomRequest = Atom03EditEntryRequest(editLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createDeleteEntryRequest(self, deleteLink, atomDeleteEntry):  #@UnusedVariable
        atomRequest = Atom03DeleteEntryRequest(deleteLink, self.getUsername(), self.getPassword())
        return atomRequest
