from zoundry.blogapp.services.accountstore.account import IZBlogFromAccount
from zoundry.blogpub.atom.atomapi import ZAtomBlogEntry
from zoundry.blogpub.atom.atomapi import ZAtomBlog
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.services.pubsystems.publisher import ZPublisherException
from zoundry.blogapp.services.pubsystems.blog.blogpublisher import ZBlogPublisher
#------------------------------------------------------------------------------
# Atom implementation of izblog publisher
#------------------------------------------------------------------------------

class ZAtomBlogPublisher(ZBlogPublisher):

    def __init__(self):
        ZBlogPublisher.__init__(self)

    def _getCategoriesLink(self, zblog):
        atomLink = zblog.getAttribute(ZAtomBlog.CATEGORIES_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not atomLink:
            atomLink = zblog.getAttribute(ZAtomBlog.FEED_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
            if not atomLink:
                atomLink = zblog.getAttribute(ZAtomBlog.POST_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
            # append /svc=  used by SixApart servers
            atomLink = atomLink + u"/svc=categories" #$NON-NLS-1$
        return atomLink

    def _getAuthor(self, zblogEntry, zblog, server): #@UnusedVariable
        author = None
#        if zblogEntry:
#            author = blogEntry.getPublishedInfoByBlog(blog).getExtAttribute(u"atom-author") #$NON-NLS-1$
        if not author:
            author = zblog.getAttribute(ZAtomBlog.AUTHOR, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not author:
            author = server.getUsername()
        if not author:
            # should not get here.
            author = u"ZoundryRavenUser" #$NON-NLS-1$
        return author

    def _listBlogs(self):
        server = self._getServer()
        blogs = server.listBlogs()
        return blogs

    def _listCategories(self, zblog, serverBlogId): #@UnusedVariable
        categoriesLink = self._getCategoriesLink(zblog)
        if not categoriesLink:
            raise ZPublisherException(u"Categories link not available for blog %s" % serverBlogId) #$NON-NLS-1$
        server = self._getServer()
        categories = server.listCategories(categoriesLink)
        return categories

    def _listEntries(self, zblog, serverBlogId, maxEntries): #@UnusedVariable
        feedLink = None
        # Work around for Blogger. Blogger's Atom API uses the 'Posts URI' link to download posts instead of the 'Feeds URI' link.
        if isinstance(zblog, IZBlogFromAccount):
            account = zblog.getAccount()
            apiInfo = account.getAPIInfo() 
            apiType = apiInfo.getType()
            if apiType == u"zoundry.blogapp.pubsystems.publishers.site.blogger.atom10": #$NON-NLS-1$
                feedLink = zblog.getAttribute(ZAtomBlog.POST_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not feedLink:        
            feedLink = zblog.getAttribute(ZAtomBlog.FEED_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not feedLink:
            feedLink = zblog.getAttribute(ZAtomBlog.POST_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        server = self._getServer()
        if not feedLink:
            feedLink = server.getApiUrl()    
        entries = server.listAtomEntries(feedLink, maxEntries)
        return entries
    
    def _postEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        postLink = zblog.getAttribute(ZAtomBlog.POST_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not postLink:
            raise ZPublisherException(u"Post link not available for blog %s" % serverBlogId) #$NON-NLS-1$        
        server = self._getServer()
        atomRespEntry = server.newPost(postLink, zserverBlogEntry)
        return atomRespEntry

    def _updateEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        editLink = zserverBlogEntry.getAttribute(ZAtomBlogEntry.EDIT_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not editLink:
            raise ZPublisherException(u"Edit link not available for blog %s" % serverBlogId) #$NON-NLS-1$                
        server = self._getServer()
        atomRespEntry = server.updatePost(editLink, zserverBlogEntry.getId(), zserverBlogEntry)
        return atomRespEntry

    def _deleteEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        u"""Subclasses must implement this method to delete  an entry"""  #$NON-NLS-1$
        editLink = zserverBlogEntry.getAttribute(ZAtomBlogEntry.EDIT_LINK, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE)
        if not editLink:
            raise ZPublisherException(u"Edit link not available for blog %s" % serverBlogId) #$NON-NLS-1$                
        server = self._getServer()
        return  server.deletePost(editLink, zserverBlogEntry.getId())
    
# end ZAtomBlogPublisher