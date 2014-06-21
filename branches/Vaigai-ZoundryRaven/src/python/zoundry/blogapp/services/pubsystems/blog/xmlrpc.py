from zoundry.blogapp.services.pubsystems.blog.blogpublisher import ZBlogPublisher

#------------------------------------------------------------------------------
# xml-rpc implementation of izblog publisher
#------------------------------------------------------------------------------
class ZXmlRpcBlogPublisher(ZBlogPublisher):

    def __init__(self):
        ZBlogPublisher.__init__(self)

    def _listBlogs(self):
        server = self._getServer()
        blogs = server.getBlogs()
        return blogs

    def _listCategories(self, zblog, serverBlogId): #@UnusedVariable
        server = self._getServer()
        categories = server.getCategories(serverBlogId)
        return categories

    def _listEntries(self, zblog, serverBlogId, maxEntries): #@UnusedVariable
        server = self._getServer()
        entries = server.getRecentPosts(serverBlogId, maxEntries)
        return entries

    def _postEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        server = self._getServer()
        # call server post with edit=False
        server.post(serverBlogId, zserverBlogEntry, False, zserverBlogEntry.isDraft())
        return zserverBlogEntry

    def _updateEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        server = self._getServer()
        # call server post with edit=False
        server.post(serverBlogId, zserverBlogEntry, True, zserverBlogEntry.isDraft())
        return zserverBlogEntry

    def _deleteEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        u"""Subclasses must implement this method to delete  an entry"""  #$NON-NLS-1$
        server = self._getServer()
        return server.deletePost(serverBlogId, zserverBlogEntry.getId() )

    def _uploadFile(self, zblog, serverBlogId, srcFilename, destFilename, serverMediaUploadListener): #@UnusedVariable
        server = self._getServer()
        url = server.uploadFile(serverBlogId,  srcFilename, destFilename, serverMediaUploadListener)
        return url

# end ZXmlRpcBlogPublisher