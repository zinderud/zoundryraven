from zoundry.blogpub.atom.atomapi import ZAtom10FeedRequestBase
from zoundry.blogpub.atom.atomapi import ZAtom10RequestBase
from zoundry.blogpub.namespaces import YAHOO_MEDIA
from zoundry.blogpub.namespaces import GOOGLE_PHOTO
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
from zoundry.base.net.googledata import ZGoogleLoginAuthHandler
from zoundry.base.net.authhandlers import ZAuthenticationManager
from zoundry.blogpub.atom.atom03impl import ZAtom03BlogEntry
from zoundry.blogpub.atom.atomapi import ZAtomRelTypes
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
from zoundry.blogpub.atom.atomapi import ZAtomServer

from zoundry.blogpub.namespaces import ATOM_03_FEED_NAMESPACE
from zoundry.blogpub.namespaces import ATOM_10_FEED_NAMESPACE
from zoundry.blogpub.namespaces import ATOM_10_API_NAMESPACE
from zoundry.blogpub.namespaces import ATOM_10_API_CONTROL_NAMESPACE
from zoundry.blogpub.namespaces import XHTML_NAMESPACE
from zoundry.blogpub.namespaces import DUBLIN_CORE_ELE_NAMESPACE
from zoundry.blogpub.namespaces import SA_ATOM_CATEGORIES_NAMESPACE


#================================================
# Atom 1.0 Impl.
#================================================

ATOM_NEW_BLOG_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="%s">
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
    <author>
        <name/>
    </author>
    <title type="text" />
    <content type="html" />
</entry>
""" % (ATOM_10_FEED_NAMESPACE, getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

ATOM_EDIT_BLOG_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="%s">
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
    <author>
        <name/>
    </author>
    <id />
    <updated />
    <title type="text" />
    <content type="html" />
</entry>
""" % (ATOM_10_FEED_NAMESPACE, getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

ATOM_NSS_MAP = {
    u"atom"   : ATOM_10_FEED_NAMESPACE,  #$NON-NLS-1$
    u"atom03" : ATOM_03_FEED_NAMESPACE, #$NON-NLS-1$
    u"app"    : ATOM_10_API_NAMESPACE, #$NON-NLS-1$
    u"pub"    : ATOM_10_API_CONTROL_NAMESPACE, #$NON-NLS-1$
    u"xhtml"  : XHTML_NAMESPACE,  #$NON-NLS-1$
    u"tp"     : SA_ATOM_CATEGORIES_NAMESPACE,  #$NON-NLS-1$
    u"dc"     : DUBLIN_CORE_ELE_NAMESPACE,  #$NON-NLS-1$
    u"gphoto" : GOOGLE_PHOTO,  #$NON-NLS-1$
    u"media"  : YAHOO_MEDIA  #$NON-NLS-1$
}

#================================================
# Atom 1.0 Blog
#================================================
class ZAtom10Blog(ZAtomBlog):

    def __init__(self, attrs = {}):
        ZAtomBlog.__init__(self)
        # copy attributes
        for (n, v) in attrs.iteritems():
            self.setAttribute(n,v, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        id = self.getAttribute(ZAtomBlog.POST_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        name =  self.getAttribute(ZAtomBlog.POST_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        if self.hasAttribute(ZAtomBlog.ID, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE):
            id =  self.getAttribute(ZAtomBlog.ID, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        if self.hasAttribute(ZAtomBlog.TITLE, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE):
            name = self.getAttribute(ZAtomBlog.TITLE, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        url = self.getAttribute(ZAtomBlog.ALT_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        if not url:
            url = self.getAttribute(ZAtomBlog.FEED_LINK, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        self._setId(id)
        self._setName(name)
        self._setUrl(url)
    # end __init__()

# Note: need author name, email
#
#  GDATA
#
#<link rel="http://schemas.google.com/g/2005#feed" type="application/atom+xml" href="..."/>
#    Specifies the URI where the complete Atom feed can be retrieved.
#<link rel="http://schemas.google.com/g/2005#post" type="application/atom+xml" href="..."/>
#    Specifies the Atom feed's PostURI (where new entries can be posted).
#<link rel="self" type="..." href="..."/>
#    Contains the URI of this resource. The value of the type attribute depends on the requested format. If no data changes in the interim, sending another GET to this URI returns the same response.
#<link rel="previous" type="application/atom+xml" href="..."/>
#    Specifies the URI of the previous chunk of this query result set, if it is chunked.
#<link rel="next" type="application/atom+xml" href="..."/>
#    Specifies the URI of the next chunk of this query result set, if it is chunked.
#<link rel="edit" type="application/atom+xml" href="..."/>
#    Specifies the Atom entry's EditURI (where you send an updated entry).
#
# 0.3
#<link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.post" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
#  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.feed" href="http://www.typepad.com/t/atom/weblog/blog_id=100597" title="joey" />
#  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.upload" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=upload" title="joey" />
#  <link xmlns="http://purl.org/atom/ns#" type="application/atom+xml" rel="service.categories" href="http://www.typepad.com/t/atom/weblog/blog_id=100597/svc=categories" title="joey" />
# note: al
#  <link xmlns="http://purl.org/atom/ns#" type="text/html" rel="alternate" href="http://pidge.blogs.com/joey/" title="joey" />

# 1.0 feed
#- <feed xmlns="http://www.w3.org/2005/Atom" xmlns:idx="urn:atom-extension:indexing" idx:index="no">
#  <id>urn:lj:livejournal.com:atom1:sandun</id>
#  <title>ZDev Journal</title>
#  <subtitle>All about world of Z!</subtitle>
#- <author>
#  <name>Sandun Jay</name>
#  </author>
#  <link rel="alternate" type="text/html" href="http://sandun.livejournal.com/" />
#  <link rel="self" type="application/x.atom+xml" href="http://www.livejournal.com/interface/atom/feed" />
#  <updated>2005-09-19T23:47:47Z</updated>
#  <link rel="service.feed" type="application/x.atom+xml" href="http://www.livejournal.com/interface/atom/feed" title="ZDev Journal" />
#  <link rel="service.post" type="application/x.atom+xml" href="http://www.livejournal.com/interface/atom/post" title="Create a new entry" />

# 1.0 introspection
#   <?xml version="1.0" encoding='utf-8'?>
#   <service xmlns="http://purl.org/atom/app#">
#     <workspace title="Main Site" >
#       <!-- coll can appear more than once -->
#       <collection
#         title="My Blog Entries"
#         href="http://example.org/reilly/main" />
#       <collection
#         title="Pictures"
#         href="http://example.org/reilly/pic" >
#         <accept>image/*</accept>
#       </collection>
#     </workspace>
#     <workspace title="Side Bar Blog">
#       <collection title="Remaindered Links"
#         href="http://example.org/reilly/list" />
#     </workspace>
#   </service>



#================================================
# Atom 1.0 Blog/Feed Entry
#================================================
class ZAtom10BlogEntry(ZAtomBlogEntry):
    # Constructs an Atom blog entry object from an Atom XML entry node.
    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZAtomBlogEntry.__init__(self, entryNode, prefix)
    # end __init__()

    def _isDraft(self):
        pubDraftVal = self.getNode().selectSingleNodeText(u"pub:control/pub:draft", u"no") #$NON-NLS-1$  #$NON-NLS-2$
        pubDraftVal = pubDraftVal.strip().lower()
        rVal = u"yes" == pubDraftVal  #$NON-NLS-1$
        return rVal
    # end _isDraft()
# end ZAtom10BlogEntry()

#--------------------------------------------
# new entry
#--------------------------------------------
class ZAtom10EntryDocument(ZAtomEntryDocument):

    def __init__(self):
        ZAtomEntryDocument.__init__(self)

    def _initNode(self, dom):
        dom.loadXML(ATOM_NEW_BLOG_ENTRY_TEMPLATE)
        dom.setNamespaceMap(ATOM_NSS_MAP)

    def _setDraft(self, bDraft):
        controlEle = self.getDom().selectSingleNode(u"/atom:entry/pub:control") #$NON-NLS-1$
        if not controlEle:
            controlEle = self.getDom().createElement(u"control", ATOM_10_API_CONTROL_NAMESPACE) #$NON-NLS-1$
            self.getDom().selectSingleNode(u"/atom:entry").appendChild(controlEle) #$NON-NLS-1$
        draftEle = controlEle.selectSingleNode(u"pub:draft") #$NON-NLS-1$
        if not draftEle:
            draftEle = self.getDom().createElement(u"draft", ATOM_10_API_CONTROL_NAMESPACE) #$NON-NLS-1$
            controlEle.appendChild(draftEle)

        if bDraft:
            draftEle.setText(u"yes") #$NON-NLS-1$
        else:
            draftEle.setText(u"no") #$NON-NLS-1$
    # end _setDraft()
# end ZAtom10EntryDocument()    

#--------------------------------------------
# edit entry
#--------------------------------------------
class ZAtom10EditDocument(ZAtom10EntryDocument):

    def __init__(self):
        ZAtom10EntryDocument.__init__(self)

    def _initNode(self, dom):
        dom.loadXML(ATOM_EDIT_BLOG_ENTRY_TEMPLATE)
        dom.setNamespaceMap(ATOM_NSS_MAP)

    def _setDateStr(self, dateTimeStr):
        # For edit entry, set the updated time.
        ZAtom10EntryDocument._setUpdatedDateStr(self, dateTimeStr)

#================================
# V.1.0 request
#================================

class ZAtom10Request(ZAtom10RequestBase):

    def __init__(self, url, username, password):
        ZAtom10RequestBase.__init__(self, url, username, password)
    # end __init__()

    def _setDomNSS(self, dom):
        dom.setNamespaceMap(ATOM_NSS_MAP)
    # end _setDomNSS()
# end ZAtom10Request

#================================
# V.1.0 category request
#================================
class ZAtom10CategoryListRequest(ZAtom10Request):
    def __init__(self, url, username, password):
        ZAtom10Request.__init__(self, url, username, password)
    # end __init__()

    def _getCategoryNodes(self):
        return self.getDom().selectNodes(u"atom:category") #$NON-NLS-1$

    def getCategoryList(self):
        rVal = []
        # test for Atom 1.0 categories
        categories = self._getCategoryNodes()
        if categories and len(categories) > 0:
            for catNode in categories:
                term = getNoneString( catNode.getAttribute(u"term")) #$NON-NLS-1$
                label = catNode.getAttribute(u"label") #$NON-NLS-1$
                scheme = catNode.getAttribute(u"scheme") #$NON-NLS-1$
                if term: #$NON-NLS-1$
                    rVal.append( ZAtomCategory(term, label, scheme) )
        else:
            # test for Six Apart subjects (e.g. live journal)
            categories = self.getDom().selectNodes(u"/tp:categories/dc:subject") #$NON-NLS-1$
            if categories and len(categories) > 0:
                for catNode in categories:
                    rVal.append(ZAtomCategory( catNode.getText()) )
        return rVal


#================================
# V.1.0 blog list request
#================================
class ZAtom10BlogListRequest(ZAtom10Request):
    def __init__(self, url, username, password):
        ZAtom10Request.__init__(self, url, username, password)
    # end __init__()

    # Gets the list of returned blogs.
    def getBlogList(self):
        u"Gets the list of returned blogs." #$NON-NLS-1$
        # Note: The rel, and type fields may have mixed cased values. Our comparisions should be case-insensitive.
        # To get the blog list, we need to discover the following fields:
        # required links: service.post and service.edit
        # title and id of blog
        # optional: service.categories service.upload (if supported by server)
        #
        # For Atom 1.0, not all servers use the Atom  publishing API's service/collection scheme.
        # Most impls (to date) use one of the following:
        # 1. /feed/link in Atom 1.0 NS. In this case, its a Atom feed. Extract the title, id etc. from the feed.
        # 2. Google/blogger format when each blog is return as a <entry> i.e. select nodes //feed/entry
        # 3. /feed/link(s) in Atom 0.3 NS. In this case, the title is the link title attribute, there are multiple links with the same
        #   name/title for each endpoint.
        # 4. Atom publishing API discovery /service/workspace/collection.

        # 1. Test for Atom 1.0 /feed/link
        rVal = self._getAtom10()
        if not rVal or len(rVal) == 0:
            # 2. Test for Blogger.com Atom 1.0
            rVal = self. _getBloggerAtom10()
        if not rVal or len(rVal) == 0:
            # 3. Test for Atom 0.3 format.
            rVal = self._getAtom03()
        if not rVal or len(rVal) == 0:
            #  Test for Atom 1.0 with out namespace.
            rVal = self._getAtom10(u"") #$NON-NLS-1$

        if not rVal or len(rVal) == 0:
            rVal = []
        return map(ZAtom10Blog, rVal)
    # end getBlogList()

    def _getAtom10(self, prefix=u"atom:"):  #$NON-NLS-1$
        # find service.post and service.feed links
        attrMap = {}
        relTypes = ZAtomRelTypes()
        #TODO: find uploadLink and categoriesLink.
        for node in self.getDom().selectNodes(u"/%sfeed/%slink" % (prefix, prefix)): #$NON-NLS-1$
            rel = node.getAttribute(u"rel") #$NON-NLS-1$
            type = node.getAttribute(u"type") #$NON-NLS-1$
            if relTypes.isFeedLink(rel, type):
                attrMap[ZAtomBlog.FEED_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isPostLink(rel,type):
                attrMap[ZAtomBlog.POST_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isUploadLink(rel,type):
                attrMap[ZAtomBlog.UPLOAD_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isCategoriesLink(rel,type):
                attrMap[ZAtomBlog.CATEGORIES_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isAlternateLink(rel,type):
                attrMap[ZAtomBlog.ALT_LINK] = node.getAttribute(u"href") #$NON-NLS-1$


        if not attrMap.has_key(ZAtomBlog.FEED_LINK) and attrMap.has_key(ZAtomBlog.POST_LINK):
            # feed url is same as this url.
            attrMap[ZAtomBlog.FEED_LINK] = self.url
        # check for required post link
        rVal = []
        if attrMap.has_key(ZAtomBlog.FEED_LINK) and attrMap.has_key(ZAtomBlog.POST_LINK):
            # this is a atom 1.0 feed.
            elem = self.getDom().selectSingleNode(u"/%sfeed/%sid"  % (prefix, prefix)) #$NON-NLS-1$
            if elem:
                attrMap[ZAtomBlog.ID] = elem.getText()
            elem = self.getDom().selectSingleNode(u"/%sfeed/%stitle" % (prefix, prefix))  #$NON-NLS-1$
            if elem:
                attrMap[ZAtomBlog.TITLE] = elem.getText()
            rVal = [attrMap]
        return rVal


    def _getAtom03(self):
        # find service.post and service.feed links
        titleMap = {}
        relTypes = ZAtomRelTypes()
        bPostLinkFound = False
        bFeedLinkFound = False #@UnusedVariable
        for node in self.getDom().selectNodes(u"/atom03:feed/atom03:link"): #$NON-NLS-1$
            attrMap = None
            title = node.getAttribute(u"title") #$NON-NLS-1$
            if titleMap.has_key(title):
                attrMap = titleMap[title]
            else:
                attrMap = {}
                titleMap[title] = attrMap
                attrMap[ZAtomBlog.TITLE] = title

            rel = node.getAttribute(u"rel") #$NON-NLS-1$
            type = node.getAttribute(u"type") #$NON-NLS-1$

            if relTypes.isFeedLink(rel, type):
                attrMap[ZAtomBlog.FEED_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
                bFeedLinkFound = True #@UnusedVariable
            elif relTypes.isPostLink(rel,type):
                attrMap[ZAtomBlog.POST_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
                attrMap[ZAtomBlog.ID] = attrMap[ZAtomBlog.POST_LINK]
                bPostLinkFound = True
            elif relTypes.isUploadLink(rel,type):
                attrMap[ZAtomBlog.UPLOAD_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isCategoriesLink(rel,type):
                attrMap[ZAtomBlog.CATEGORIES_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
            elif relTypes.isAlternateLink(rel,type):
                attrMap[ZAtomBlog.ALT_LINK] = node.getAttribute(u"href") #$NON-NLS-1$
        rVal = []
        if bPostLinkFound:
            rVal = titleMap.values()
        return rVal


    def _getBloggerAtom10(self, prefix=u"atom:"):  #$NON-NLS-1$
        # find service.post and service.feed links in entry elements
        postRel = u"http://schemas.google.com/g/2005#post"  #$NON-NLS-1$
        feedRel = u"http://schemas.google.com/g/2005#feed" #$NON-NLS-1$
        rVal = []
        for entryNode in self.getDom().selectNodes(u"//%sentry" % prefix): #$NON-NLS-1$
            # check to Blogger service and feed links
            postLinkNode = entryNode.selectSingleNode(u"""%slink[@rel="%s" and @type="application/atom+xml"]""" % (prefix, postRel) ) #$NON-NLS-1$
            feedLinkNode = entryNode.selectSingleNode(u"""%slink[@rel="%s" and @type="application/atom+xml"]""" % (prefix, feedRel) )  #$NON-NLS-1$
            altLinkNode = entryNode.selectSingleNode(u"""%slink[@rel="alternate" and @type="text/html"]""" % prefix) #$NON-NLS-1$
            if not postLinkNode or not feedLinkNode:
                continue
            attrMap = {}
            attrMap[ZAtomBlog.FEED_LINK] = feedLinkNode.getAttribute(u"href") #$NON-NLS-1$
            attrMap[ZAtomBlog.POST_LINK] = postLinkNode.getAttribute(u"href") #$NON-NLS-1$
            attrMap[ZAtomBlog.ALT_LINK] = altLinkNode.getAttribute(u"href") #$NON-NLS-1$
            # Blogger does not have a categoires link. We use feed link instead.
            attrMap[ZAtomBlog.CATEGORIES_LINK] = attrMap[ZAtomBlog.FEED_LINK]
            elem = entryNode.selectSingleNode(u"%sid"  % prefix) #$NON-NLS-1$
            if elem:
                attrMap[ZAtomBlog.ID] = elem.getText()
            else:
                attrMap[ZAtomBlog.ID] = attrMap[ZAtomBlog.POST_LINK]
            elem = entryNode.selectSingleNode(u"%stitle" % prefix)  #$NON-NLS-1$
            if elem:
                attrMap[ZAtomBlog.TITLE] = elem.getText()
            elem = entryNode.selectSingleNode(u"%sauthor/%sname" % (prefix, prefix))  #$NON-NLS-1$
            if elem:
                attrMap[ZAtomBlog.AUTHOR] = elem.getText()
            rVal.append(attrMap)
        return rVal


#================================
# V.1.0 blog feed request
#================================
class ZAtom10FeedRequest(ZAtom10FeedRequestBase):

    def __init__(self, url, username, password):
        ZAtom10FeedRequestBase.__init__(self, url, username, password)
    # end __init__()

    def _setDomNSS(self, dom):
        dom.setNamespaceMap(ATOM_NSS_MAP)
    # end _setDomNSS()

    def _getEntryList(self):
        # Map the blog entry constructor onto the list of entry XML nodes.
        return map(ZAtom10BlogEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end _getEntryList()
# end ZAtom10FeedRequest

#-------------------------------------------------------------
# Class Definition for an Atom API GET Entry Request.
#
# This class is not strictly necessary, as a GET request to
# an Atom Entry's service.edit link will simply return an
# Atom Feed with only one entry.  However, the class is used
# to make the coding of the application clearer.
#-------------------------------------------------------------
class Atom10BlogEntryRequest(ZAtom10FeedRequest):

    def __init__(self, url, username, password):
        ZAtom10FeedRequest.__init__(self, url, username, password)
    # end __init__()

    # Gets the blog entry as a wrapper object.
    def getEntry(self):
        u"Get a blog entry object." #$NON-NLS-1$
        return ZAtom10BlogEntry(self.getDom().selectSingleNode(u"//atom:entry")) #$NON-NLS-1$
    # end getEntry()

# end AtomBlogEntryRequest

#-------------------------------------------------------------
# Class Definition for an Atom API POST Create Entry Request.
#
# This class creates a new Blog Entry on the server.
#-------------------------------------------------------------
class ZAtom10CreateEntryRequest(ZAtom10Request):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom10Request.__init__(self, url, username, password)
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
        if node:
            return ZAtom10BlogEntry(node, prefix)
        # try Atom 0.3 namespace.
        node = self.getDom().selectSingleNode(u"/atom03:entry") #$NON-NLS-1$
        prefix = u"atom03:" #$NON-NLS-1$
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
class ZAtom10EditEntryRequest(ZAtom10CreateEntryRequest):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom10CreateEntryRequest.__init__(self, url, username, password)
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
class ZAtom10DeleteEntryRequest(ZAtom10Request):

    # Constructs an Atom create entry request.
    def __init__(self, url, username, password):
        # Init the super class with the various params
        ZAtom10Request.__init__(self, url, username, password)
        self._setMethod(HTTP_DELETE)
    # end __init__()

    # Tests the response object to make sure the request succeeded.
    def _atomResponseIsGood(self, resp):
        u"Tests the response object to make sure the request succeeded." #$NON-NLS-1$
        return resp.status == 410 or ZAtom10Request._atomResponseIsGood(self, resp)
    # end _responseIsGood()

    # Delete requests probably return no data - so override the _processResponseData() method.
    def _processResponseData(self, resp, txt): #@UnusedVariable
        return ZAtom10Request._createEmptyFeed(self)
    # end _processResponseData()


# end AtomDeleteEntryRequest

#================================================
# Atom Server base class.
#================================================

class ZAtom10Server(ZAtomServer):

    def __init__(self, username, password, apiUrl, authType):
        ZAtomServer.__init__(self, username, password, apiUrl, authType)


    def listAtomEntries(self, feedLink, maxEntries=-1):
        u"""Returns list of AtomBlogEntry objects for the given feed link.""" #$NON-NLS-1$
        rVal = []
        if maxEntries < 1:
            maxEntries = 10000
        self._debug(u"Atom listAtomEntries begin. Max entries = %d. Fetching first page." % maxEntries)#$NON-NLS-1$
        # get feed (normally page 1)
        page = 1
        atomRequest = self._createListEntriesRequest(feedLink)
        self._sendAtomRequest(atomRequest)
        entries = atomRequest.getEntries()
        self._debug(u"Atom listAtomEntries request page:%d, entries: %d, uri %s" % (page, len(entries), feedLink)) #$NON-NLS-1$
        rVal.extend( entries )        
        elem = atomRequest.getDom().selectSingleNode(u"/atom:feed/atom:entry/atom:id") #$NON-NLS-1$
        prevReqEntryId = None
        if elem:
            prevReqEntryId = elem.getText()
        # get other pages
        dbgmsg = u"Atom listAtomEntries result page=%d count=%d, hasMore=%s" % (page, len(entries), atomRequest._hasMore()) #$NON-NLS-1$
        self._debug(dbgmsg)
        while atomRequest._hasMore() and len(rVal) < maxEntries:
            try:
                self._debug(u"Atom listAtomEntries request nextPage:%d, next=%s, self=%s" % (page+1, atomRequest._getNextHref(), atomRequest._getSelfHref())) #$NON-NLS-1$
                atomRequest = self._createListEntriesRequest(atomRequest._getNextHref())
                self._sendAtomRequest(atomRequest)
                elem = atomRequest.getDom().selectSingleNode(u"/atom:feed/atom:entry/atom:id") #$NON-NLS-1$
                entryId = None
                if elem:
                    entryId = elem.getText()
                # for blogger, paging does not work - so, keep track of 1st entry id of each page (i.e break if same feed is returned for each page)
                if prevReqEntryId and entryId and entryId == prevReqEntryId:
                    self._debug(u"Atom listAtomEntries paging error. Entry id in page %d is same as in page %d" % (page+1, page)) #$NON-NLS-1$
                    break
                entries = atomRequest.getEntries()
                dbgmsg = u"Atom listAtomEntries result page=%d count=%d, hasMore=%s" % (page+1, len(entries), atomRequest._hasMore()) #$NON-NLS-1$
                self._debug(dbgmsg)
                if len(entries) == 0:
                    # assume end of paging if there are no entries.
                    self._debug(u"Atom listAtomEntries paging error: No entries found in collection.") #$NON-NLS-1$
                    break
                page = page + 1
                prevReqEntryId = entryId
                rVal.extend( entries )

            except:
                self.exception()
                break
        self._debug(u"Atom listAtomEntries end. pages:%d, entries:%d  maxrequested:%d" % (page,len(rVal), maxEntries))#$NON-NLS-1$
        return rVal

    def _createNewEntryDocument(self):
        return ZAtom10EntryDocument()

    def _createEditEntryDocument(self):
        return ZAtom10EditDocument()

    def _createDeleteEntryDocument(self):
        return ZAtom10EditDocument()

    def _createListBlogsRequest(self):
        atomRequest = ZAtom10BlogListRequest( self.getApiUrl(), self.getUsername(), self.getPassword() )
        return atomRequest

    def _createGetEntryRequest(self, editLink):
        atomRequest = Atom10BlogEntryRequest(editLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createListEntriesRequest(self, feedLink):
        atomRequest = ZAtom10FeedRequest(feedLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createListCategoriesRequest(self, categoriesLink):
        atomRequest = ZAtom10CategoryListRequest(categoriesLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createNewEntryRequest(self, postLink, atomNewEntry): #@UnusedVariable
        atomRequest = ZAtom10CreateEntryRequest(postLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createUpdateEntryRequest(self, editLink, atomEditEntry):        #@UnusedVariable
        atomRequest = ZAtom10EditEntryRequest(editLink, self.getUsername(), self.getPassword())
        return atomRequest

    def _createDeleteEntryRequest(self, deleteLink, atomDeleteEntry): #@UnusedVariable
        atomRequest = ZAtom10DeleteEntryRequest(deleteLink, self.getUsername(), self.getPassword())
        return atomRequest

#================================================
# Google Blogger Atom Server class.
#================================================

#------------------------------------------------------
# Install Auth manager for Google login
#-------------------------------------------------------
ZAuthenticationManager().registerHandler(ZGoogleLoginAuthHandler.SCHEME, ZGoogleLoginAuthHandler)

class ZBloggerAtom10CategoryListRequest(ZAtom10CategoryListRequest):
    def __init__(self, url, username, password, feedLink):
        ZAtom10CategoryListRequest.__init__(self, url, username, password)
        self.feedLink = feedLink
    # end __init__()
    def _getCategoryNodes(self):
        xpath = u"/atom:feed/atom:entry/atom:link[@rel='http://schemas.google.com/g/2005#feed' and @href='%s']" % self.feedLink         #$NON-NLS-1$
        linkNode = self.getDom().selectSingleNode(xpath)
        if linkNode:
            return linkNode.parentNode.selectNodes(u"atom:category") #$NON-NLS-1$
        else:
            return self.getDom().selectNodes(u"atom:category") #$NON-NLS-1$

class ZCachedBloggerAtom10CategoryListRequest(ZBloggerAtom10CategoryListRequest):
    def __init__(self, dom, url, username, password, feedLink):
        ZBloggerAtom10CategoryListRequest.__init__(self, url, username, password, feedLink)
        self.dom = dom
        self._setDomNSS(self.dom)

class ZBloggerAtom10Server(ZAtom10Server):

    def __init__(self, username, password, apiUrl, authType):
        ZAtom10Server.__init__(self, username, password, apiUrl, authType)
        self.listBlogsDom = None

    def _createListCategoriesRequest(self, categoriesLink):
        categoryRequest = ZBloggerAtom10CategoryListRequest(self.getApiUrl(), self.getUsername(), self.getPassword(), categoriesLink)
        return categoryRequest

    def _initBloggerDocument(self, atomDoc):
        # set the category scheme used by blogger
        atomDoc.setCategoryScheme(u"http://www.blogger.com/atom/ns#")#$NON-NLS-1$

    def _initNewEntryDocument(self, atomDoc):
        self._initBloggerDocument(atomDoc)

    def _initEditEntryDocument(self, atomDoc):
        self._initBloggerDocument(atomDoc)

    def listBlogs(self):
        u"""Overrides base to cache response documents""" #$NON-NLS-1$
        self.listBlogsDom = None
        atomRequest = self._createListBlogsRequest()
        self._sendAtomRequest(atomRequest)
        blogList = atomRequest.getBlogList()
        if blogList and len(blogList) > 0:
            # cache response
            self.listBlogsDom = atomRequest.getDom()
        del atomRequest
        self._debug(u"Atom List Blogs - returned a list of %d blogs." % len(blogList)) #$NON-NLS-1$
        return blogList

    def listCategories(self, categoriesLink):
        u"""Overrides to use cached results if available.""" #$NON-NLS-1$
        rval = []
        if self.listBlogsDom:
            atomRequest = ZCachedBloggerAtom10CategoryListRequest(self.listBlogsDom, self.getApiUrl(), self.getUsername(), self.getPassword(), categoriesLink)
            rval = atomRequest.getCategoryList()
            del atomRequest
        else:
            rval = ZAtom10Server.listCategories(self, categoriesLink)
        return rval


#================================================
# SixApart Vox
#================================================


class ZVoxAtom10BlogListRequest(ZAtom10BlogListRequest):
    def __init__(self, url, username, password):
        ZAtom10BlogListRequest.__init__(self, url, username, password)

    def getBlogList(self):
        blogList = ZAtom10BlogListRequest.getBlogList(self)
        for blog in blogList:
            altLink = blog.getAlternateLink()
            if altLink and not blog.getFeedLink():
                feedLink = altLink.rstrip(u"/") + u"/library/posts/atom.xml"  #$NON-NLS-1$ #$NON-NLS-2$
                blog.setAttribute(ZAtomBlog.FEED_LINK, feedLink, IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE)
        return blogList

class VoxAtom10Server(ZAtom10Server):

    def __init__(self, username, password, apiUrl, authType):
        ZAtom10Server.__init__(self, username, password, apiUrl, authType)

    def _createListBlogsRequest(self):
        atomRequest = ZVoxAtom10BlogListRequest( self.getApiUrl(), self.getUsername(), self.getPassword() )
        return atomRequest
