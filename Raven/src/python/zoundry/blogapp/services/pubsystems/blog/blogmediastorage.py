from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.mediastorage.mediastorageprovider import IZMediaStorageProvider
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisherFromAccount
from zoundry.blogapp.services.pubsystems.publisher import ZPublisherException
from zoundry.blogpub.blogserverapi import IZBlogServerMediaUploadListener


# -----------------------------------------------------------------------------------
# MediaStorage provider based on blog publisher API
# -----------------------------------------------------------------------------------
class ZBlogPublisherMediaStorageProvider(IZMediaStorageProvider):

    def __init__(self, properties):
        self.properties = properties
    # end __init__()

    def _getAccount(self):
        accountId = None
        if self.properties.has_key(u"account-id"): #$NON-NLS-1$
            accountId = getNoneString( self.properties[u"account-id"]) #$NON-NLS-1$
        if not accountId:
            raise ZPublisherException(u"account-id not available.") #$NON-NLS-1$
        accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        account = accStoreService.getAccountById(accountId)
        if not account:
            raise ZPublisherException(u"Account not found for account-id %s" % accountId) #$NON-NLS-1$
        return account
    # end _getAccount()

    def _getBlog(self, account):
        blogId = None
        if self.properties.has_key(u"blog-id"): #$NON-NLS-1$
            blogId = getNoneString( self.properties[u"blog-id"]) #$NON-NLS-1$
        if not blogId:
            raise ZPublisherException(u"blog-id not available.") #$NON-NLS-1$
        blog = account.getBlogById(blogId)
        if not blog:
            raise ZPublisherException(u"Blog not found for blog-id %s" % blogId) #$NON-NLS-1$
        return blog
    # end _getBlog()

    def uploadFile(self, fileName, fullPath, mediaStoreListener, metaData): #@UnusedVariable
        u"Called to upload a file to the remote media storage.  Returns the URL of the uploaded file." #$NON-NLS-1$
        account = self._getAccount()
        blog = self._getBlog(account)
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        # publisher is instance of IZBlogPublisher
        publisher = createBlogPublisherFromAccount(account,publisherService)
        # FIXME (PJ) verify publisher supports upload.
        listener = None
        if mediaStoreListener:
            listener = ZBlogServerToMediaStorageUploadListenerAdapter(fileName, mediaStoreListener)
        izBlogMediaServerUploadResult = publisher.uploadFile(blog, fullPath, fileName, listener)
        if izBlogMediaServerUploadResult:
            # convert/adapt blog server IzBlogMediaServerUploadResult to raven app IZUploadResponse
            url =  izBlogMediaServerUploadResult.getUrl()
            embedNode = izBlogMediaServerUploadResult.getEmbedFragment()
            metadataNode = izBlogMediaServerUploadResult.getMetaData()
            resp = ZUploadResponse(url, embedNode, metadataNode)
            return resp
        else:
            raise ZPublisherException(u"File upload failed: %s" % fileName) #$NON-NLS-1$
    # end upload()

    def deleteFile(self, fileName, metaData): #@UnusedVariable
        # Not supported
        return None
    # end deleteFile()

    def listFiles(self, relativePath = None): #@UnusedVariable
        # Not supported.
        return None
    # end listFiles()

# end ZBlogPublisherMediaStorageProvider


# -----------------------------------------------------------------------------------
# Listener that adapts from blogpub server upload listnener to media storage upload listener.
# The blog server (xml-rpc) upload process typically has two stages:
# 1. Encode file stream to base64
# 2. Upload base64 content.
# The media storage callback methods onUploadStarted and onUploadChunk will be invoke for each stage.
# -----------------------------------------------------------------------------------
class ZBlogServerToMediaStorageUploadListenerAdapter(IZBlogServerMediaUploadListener):

    def __init__(self, fileName, izMediaStorageUploadListener):
        self.fileName = fileName
        self.mediaStoreUploadListener = izMediaStorageUploadListener

    def onStart(self):
        pass

    def onStartEncode(self, totalBytes): #@UnusedVariable
        # skip base64 encoding notifications
        pass

    def onEncodeChunk(self, bytes): #@UnusedVariable
        # skip base64 encoding notifications
        pass

    def onEndEncode(self):
        # skip base64 encoding notifications
        pass

    def onStartTransfer(self, totalBytes): #@UnusedVariable
        self.mediaStoreUploadListener.onUploadStarted(self.fileName, totalBytes)

    def onTransferChunk(self, bytes):
        self.mediaStoreUploadListener.onUploadChunk(self.fileName, bytes)

    def onEndTransfer(self):
        self.mediaStoreUploadListener.onUploadComplete(self.fileName)

    def onEnd(self):
        pass

    def onFail(self, exception):
        self.mediaStoreUploadListener.onUploadFailed(self.fileName, exception)
