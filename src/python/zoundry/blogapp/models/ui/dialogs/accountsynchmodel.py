from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisherFromAccount
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel

# -----------------------------------------------------------------------------------------
# The model behind the New Publisher Site Wizard.
# -----------------------------------------------------------------------------------------
class ZAccountSynchModel:

    def __init__(self, account):
        self.account = account
        self.publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        self.accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.mediaStoreService = getApplicationModel().getService((IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID))        
 
    def listAllBlogs(self):
        # return list of account blogs - both local and online
        publisher = createBlogPublisherFromAccount(self.account, self.publisherService)
        onlineBlogs = publisher.listBlogs()
        rval = []
        rval.extend(self.account.getBlogs())
        for blog in onlineBlogs:
            add = True
            for temp in self.account.getBlogs():
                if temp.getId() == blog.getId():
                    #  blog exists locally with in the account.
                    add = False
                    break
            if add:
                rval.append(blog)                
        return rval