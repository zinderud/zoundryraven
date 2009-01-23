from zoundry.blogapp.services.accountstore.account import IZBlogAccount
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel

#----------------------------------------------------------
# ZAccountUtil
#----------------------------------------------------------
class ZAccountUtil:

    def getBlogsWithOutMediaStore(self, accounts):
        nakedBlogs = []
        for account in accounts:
            accStorageId = account.getMediaUploadStorageId()
            for blog in account.getBlogs():
                blogStoreId = blog.getMediaUploadStorageId()
                if blogStoreId is None and accStorageId is None:
                    nakedBlogs.append(blog)
        return nakedBlogs
    # end getBlogsWithOutMediaStore()

    #----------------------------------------------------------
    # Creates and assigns media storages to blogs that do
    # not have a store assigned.
    #----------------------------------------------------------
    def autoAssignMediaStores(self, accountStore):
        blogList = self.getBlogsWithOutMediaStore( accountStore.getAccounts() )
        self.autoAssignMediaStoreToBlogs(accountStore, blogList)
    # end autoAssignMediaStores
    
    #----------------------------------------------------------
    # Creates and assigns media storages to blogs that do
    # not have a store assigned.
    #----------------------------------------------------------
    def autoAssignMediaStoreToBlogs(self, accountStore, blogList):
        for blog in blogList:
            if self.autoAssignMediaStoreToBlog(blog):
                accountStore.saveAccount( blog.getAccount() )
    # end autoAssignMediaStoreToBlogs    

    #----------------------------------------------------------
    # Assign media store and return true if asssigned.    
    #----------------------------------------------------------
    def autoAssignMediaStoreToBlog(self, blog):
        if blog.getMediaUploadStorageId():
            return False
        apiInfo = blog.getAccount().getAPIInfo()
        siteId = apiInfo.getType()
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        zpublisherSiteDef = publisherService.getPublisherSite(siteId)
        supportsUpload = zpublisherSiteDef.getCapabilities().supportsUploadMedia()
        if self._hasWLWFtp(blog):
            host = blog.getAttribute(u"ftpServer", IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            username = blog.getAttribute(u"ftpUsername", IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            path = blog.getAttribute(u"ftpPath", IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            url = blog.getAttribute(u"ftpUrl", IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            return self._createFtpMediaStorageForBlog(blog, host, username, path, url)
        
        elif not supportsUpload and blog.getAccount().getPassword() and siteId == u"zoundry.blogapp.pubsystems.publishers.site.blogger.atom10": #$NON-NLS-1$
            return self._createPicasaMediaStorageForBlog(blog, blog.getAccount().getUsername(), blog.getAccount().getPassword() )
        
        elif supportsUpload:
            return self._createXmlRpcMediaStorageForBlog(blog)
        
        else:
            return self._createImageShackMediaStorageForBlog(blog)
    # end autoAssignMediaStoreToBlog
        
    def _hasWLWFtp(self, blog):
        fileUploadSupport = blog.getAttribute(u"fileUploadSupport", IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        return fileUploadSupport and fileUploadSupport == u"2" #$NON-NLS-1$
    # end _hasWLWFtp
    
    def _createFtpMediaStorageForBlog(self, zblog, host, username, path, url):
        if not host or not path or not url:
            return False
        username = getSafeString(username)
        # check for previously created ftp store        
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.customftp" #$NON-NLS-1$
        properties = {}
        properties[u"host"] = host #$NON-NLS-1$
        properties[u"port"] = u"21" #$NON-NLS-1$ #$NON-NLS-2$
        properties[u"username"] = username #$NON-NLS-1$
        properties[u"password"] = u"" #$NON-NLS-1$  #$NON-NLS-2$
        properties[u"path"] = path #$NON-NLS-1$ 
        properties[u"url"] = url #$NON-NLS-1$ 
        properties[u"passive"] = u"false" #$NON-NLS-1$ #$NON-NLS-2$
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)        
        storeName = u"FTP %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(IZBlogAccount.UPLOAD_METHOD_MEDIASTORE)
        return True
    # end _createFtpMediaStorageForBlog()  
    
    def _createImageShackMediaStorageForBlog(self, zblog):
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.image-shack" #$NON-NLS-1$
        properties = {}
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"ImageShack %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)        
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(IZBlogAccount.UPLOAD_METHOD_MEDIASTORE)
        return True
    # end _createImageShackMediaStorageForBlog()       
    
    def _createPicasaMediaStorageForBlog(self, zblog, username, password):
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.picasa" #$NON-NLS-1$
        properties = {}
        properties[u"username"] = username #$NON-NLS-1$
        properties[u"password"] = getSafeString(password) #$NON-NLS-1$ 
        properties[u"albumName"] = zblog.getName() #$NON-NLS-1$
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"Picasa %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)        
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(IZBlogAccount.UPLOAD_METHOD_MEDIASTORE)
        return True
    # end _createPicasaMediaStorageForBlog()    
    
    def _createLJMediaStorageForBlog(self, zblog, username, password):
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.ljscrapbook" #$NON-NLS-1$
        properties = {}
        properties[u"username"] = username #$NON-NLS-1$
        properties[u"password"] = getSafeString(password) #$NON-NLS-1$ 
        properties[u"albumName"] = zblog.getName() #$NON-NLS-1$
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"LJ %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)        
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(IZBlogAccount.UPLOAD_METHOD_MEDIASTORE)
        return True
    # end _createLJMediaStorageForBlog()      
    
    def _createXmlRpcMediaStorageForBlog(self, zblog):
        account = zblog.getAccount()
        accountId = account.getId()
        blogId = zblog.getId()
        apiInfo = account.getAPIInfo()
        apiSiteId = apiInfo.getType()
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.blog.metaweblog" #$NON-NLS-1$
        properties = {}
        properties[u"account-id"] = accountId #$NON-NLS-1$
        properties[u"blog-id"] = blogId #$NON-NLS-1$
        properties[u"blog-url"] = zblog.getUrl() #$NON-NLS-1$
        properties[u"api-site-id"] = apiSiteId #$NON-NLS-1$
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"Blog %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(IZBlogAccount.UPLOAD_METHOD_PUBLISHER)
        return True
    # end _createXmlRpcMediaStorageForBlog()        

# end ZAccountUtil