from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.appframework.ui.dialogs.bgtaskprogressdialog import ZBackgroundTaskProgressDialog
from zoundry.appframework.ui.dialogs.validationreport import ZValidationReportDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowErrorMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.base.util.command import IZCommandActivityListener
from zoundry.base.util.validatables import ZConfigValidationReporter
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.accountstore.account import IZBlogFromAccount
from zoundry.blogapp.services.accountstore.accountimpl import ZAccountAPIInfo
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogAccount
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZCreateOrUpdateBlogMediaStoragesCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZDeleteEntryCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZDownloadEntriesCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZListBlogsCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZListCategoriesCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZPublishEntryCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import ZUpdateEntryCommand
from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisherFromAccount
from zoundry.blogapp.services.pubsystems.blog.validators import ZBlogPublisherAccountInfoValidator
from zoundry.blogapp.services.pubsystems.blog.validators import ZBlogPublishingValidator
from zoundry.blogapp.ui.dialogs.accountsynchdialog import ZSynchronizeAccountBlogsDialog
from zoundry.blogapp.ui.dialogs.deletepostsdialog import ZShowConfirmDeletePostFromMultipleBlogsDialog
from zoundry.blogapp.ui.dialogs.publishingdialog import ZBlogPublishingDialog
from zoundry.blogapp.ui.util.blogutil import getBlogFromBlogInfo
from zoundry.blogapp.ui.util.blogutil import getBlogFromPubMetaData
from zoundry.blogapp.ui.wizards.publishersitewizard import ZNewPublisherSiteWizard
import wx

# ------------------------------------------------------------------------------------
# Module containing utility classes for publishing stuff.
# ------------------------------------------------------------------------------------
TEST_COUNTER = 0

# ------------------------------------------------------------------------------------
# Convenience method for validating blog account info.
# ------------------------------------------------------------------------------------
class ZPublisherUiValidator:

    def _uiValidate(self, parentWindow, validationReporter):
        rval = True
        if validationReporter.hasErrors() or validationReporter.hasWarnings():
            title = _extstr(u"publisherutil.PublishingConfiguration") #$NON-NLS-1$
            desc = _extstr(u"publisherutil.PublishingConfigurationMessage") #$NON-NLS-1$
            dlg = ZValidationReportDialog(parentWindow, validationReporter, title, desc, u"images/dialogs/blogpub/header_image.png") #$NON-NLS-1$
            rval = dlg.ShowModal() == wx.ID_OK
            dlg.Destroy()
        return rval
    # end validationReporter

    def validateBlogs(self, parentWindow, zblogList):
        validator = ZBlogPublisherAccountInfoValidator()
        validator.setBlogs(zblogList)
        validationReporter = ZConfigValidationReporter()
        validator.validateConfiguration(validationReporter)
        return self._uiValidate(parentWindow, validationReporter)
    # end validateBlog

    def validatePublishing(self, parentWindow, zBlogDocument, pubMetaDataList ):
        validator = ZBlogPublishingValidator(zBlogDocument, pubMetaDataList)
        validationReporter = ZConfigValidationReporter()
        validator.validateConfiguration(validationReporter)
        return self._uiValidate(parentWindow, validationReporter)
    # end validatePublishing

# end ZPublisherUiValidator()

#-------------------------------------------------------------------
# Base Utils class that is used to synch up with blog server
#-------------------------------------------------------------------
class ZPublisherUiUtilBase:

    def _validateBlogType(self, parent,  blog):
        if not isinstance(blog, IZBlogFromAccount):
            ZShowErrorMessage(parent, u"Unsupported Blog", u"Unsupported Blog (Expected IZBlogFromAccount) %s" % blog.getId()) #$NON-NLS-2$ #$NON-NLS-1$
            return False
        else:
            return True
    # end _validateBlogType()

    def _addBackgroundTask(self, task, parent, title, description, imagePath):
        bgTaskService = getApplicationModel().getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        bgTaskService.addTask(task)
        if parent and title:
            # Show the bg task in a bg task progress dialog
            if not description:
                description = title
            if not imagePath:
                imagePath = u"images/dialogs/bgtask/header_image.png" #$NON-NLS-1$
            dialog = ZBackgroundTaskProgressDialog(parent, task, title, description, imagePath)
            dialog.ShowModal()
            dialog.Destroy()
    # end _addBackgroundTask()

# end ZPublisherUiUtilBase


#-------------------------------------------------------------------
# Util class which displays a wizard and then creates a new account
#-------------------------------------------------------------------
class ZNewPublisherSiteUiUtil(ZPublisherUiUtilBase):

    def createNewSite(self, parent):
        accName = None
        siteId = None
        username = None
        password = None
        url = None
        uploadmethod = None
        mediastorageId = None
        blogList = []

        # create and show wizard
        wizard = ZNewPublisherSiteWizard(parent)
        wizard.CenterOnParent()
        rval = wizard.showWizard()
        if rval == wx.ID_OK and wizard.getSiteId():
            accName = wizard.getAccountName()
            siteId = wizard.getSiteId()
            username = wizard.getUsername()
            password = wizard.getPassword()
            url = wizard.getApiUrl()
            uploadmethod = wizard.getMediaUploadMethod()
            mediastorageId = wizard.getMediaStorageId()
            blogList = wizard.getSelectedBlogs()
        wizard.Destroy()

        #  create account and list blogs
        if siteId:
            try:
                self._createNewAccountFromWizard(parent, accName, siteId, username, password, url, uploadmethod, mediastorageId, blogList)
            except Exception, e:
                ZShowExceptionMessage(parent, e)
    # end createNewSite()

    def createTestAccount(self, parent):
        mediastorageId = None
        blogList = []
        siteId = u"zoundry.blogapp.pubsystems.publishers.site.wordpress" #$NON-NLS-1$
        import time
        t  = time.time() / 1000
        url = u"http://bill/blogs/wordpress/pjayanetti/xmlrpc.php" #$NON-NLS-1$
        accName = u"PJTest-%d" % t #$NON-NLS-1$
        global TEST_COUNTER
        if TEST_COUNTER % 2 == 1:
            accName = u"EricTest-%d" % t #$NON-NLS-1$
            url = u"http://bill/blogs/wordpress/ewittmann/xmlrpc.php" #$NON-NLS-1$
        TEST_COUNTER = TEST_COUNTER + 1
        username = u"admin" #$NON-NLS-1$
        password = u"admin" #$NON-NLS-1$
        uploadmethod = u"publisher" #$NON-NLS-1$

        try:
            self._createNewAccountFromWizard(accName, siteId, username, password, url, uploadmethod, mediastorageId, blogList)
        except Exception, e:
            ZShowExceptionMessage(parent, e)
    # end createTestAccount()

    def _createNewAccountFromWizard(self, parent, accName, siteId, username, password, url, uploadmethod, mediastorageId, blogList):
        # create account obj
        account = self.createAccount(accName, siteId, username, password, url, uploadmethod, mediastorageId)
        # add and save in store
        self.addAccount(account)
        # create bg task
        newAccSyncBgTask = ZNewAccountSynchupBackgroundTask()
        newAccSyncBgTask.initialize(account, blogList)
        title = u"Download Account Blogs" #$NON-NLS-1$
        desc = u"Downloading %d blogs for '%s' account" % (len(blogList), accName) #$NON-NLS-1$
        self._addBackgroundTask(newAccSyncBgTask, parent, title, desc, None)
    # end _createNewAccountFromWizard()

    def createAccount(self, name, siteId, username, password, url, uploadmethod, mediastorageId):
        account = ZBlogAccount(None)
        account.setName(name)
        account.setUsername(username)
        account.setPassword(password)
        if uploadmethod:
            account.setMediaUploadMethod(uploadmethod)
        if mediastorageId:
            account.setMediaUploadStorageId(mediastorageId)
        apiinfo = ZAccountAPIInfo()
        apiinfo.setType(siteId)
        apiinfo.setUrl(url)
        account.setAPIInfo(apiinfo)
        return account
    # end createAccount()

    def addAccount(self, account):
        accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accStoreService.addAccount(account)
    # end addAccount()

# end ZNewPublisherSiteUiUtil


#-------------------------------------------------------------------
# Utils class that is used to synch up with blog server
#-------------------------------------------------------------------
class ZPublisherSiteSynchUiUtil(ZPublisherUiUtilBase):
    # Maximum # of posts to download.
    MAX_POSTS_DOWNLOAD = 5000
    NEW_ACC_POSTS_DOWNLOAD = 200

    def synchronizeAccount(self, parent, account):
        dlg = ZSynchronizeAccountBlogsDialog(parent, account)
        rval = dlg.ShowModal()        
        blogs = dlg.getSelectedBlogList()
        dlg.Destroy()
        if not ZPublisherUiValidator().validateBlogs(parent, blogs):
            return
        if rval == wx.ID_OK and blogs:
            accSyncBgTask = ZNewAccountSynchupBackgroundTask()
            accSyncBgTask.initialize(account, blogs)
            title = u"Update Account Blogs" #$NON-NLS-1$
            desc = u"Updating %d blogs for '%s' account" % (len(blogs), account.getName()) #$NON-NLS-1$
            self._addBackgroundTask(accSyncBgTask, parent, title, desc, None)
    # end synchronizeAccount()

    def downloadPosts(self, parent, blog, numposts): #@UnusedVariable
        # assert blog type
        if not self._validateBlogType(parent, blog):
            return

        if not ZPublisherUiValidator().validateBlogs(parent, [blog]):
            return

        account = blog.getAccount()
        downloadPostsBgTask = ZDownloadRecentPostsBackgroundTask()
        downloadPostsBgTask.initialize(account, blog, numposts)
        title = u"Download Recent Posts" #$NON-NLS-1$
        desc = u"Downloading %d recent posts from blog '%s'" % (numposts, blog.getName()) #$NON-NLS-1$
        self._addBackgroundTask(downloadPostsBgTask, parent, title, desc, None)
    # end downloadPosts()

#-------------------------------------------------------------------
# Utils class that is used to delete an entry
#-------------------------------------------------------------------
class ZDeleteEntryUiUtil(ZPublisherUiUtilBase):

    # What this does:
    # 1) if document is not published
    #      - show simple yes/no dialog
    #      - if yes, delete local copy
    # 2) if document is published to 1 blog
    #      - show custom yes/no dialog
    #      - custom dialog has checkbox "also delete local copy"
    #      - if yes, delete remote copy
    #      - if 'also delete local copy' checkbox was checked, delete local copy
    # 3) if document is published to multiple blogs
    #      - show custom yes/no dialog
    #      - list all blogs that the document is published to
    #      - pre-select (check) the blog passed to this method
    #      - have a checkbox on custom dialog: "also delete local copy"
    #      - 'delete local copy' checkbox will be unchecked by default
    #      - 'delete local copy' checkbox will be auto-checked if all blogs
    #        are checked (most likely no point in keeping the local document
    #        if it is being deleted from all blogs)
    #      - if yes, delete remote copy/copies
    #      - if 'also delete local copy' checkbox was checked, delete local copy
    def deletePosts(self, parent, blog, zblogDocumentList): #@UnusedVariable
        zblogDocument = None
        if zblogDocumentList is not None and len(zblogDocumentList) > 0:
            zblogDocument = zblogDocumentList[0]
        if not zblogDocument:
            ZShowErrorMessage(parent, _extstr(u"deleteentryuiutil.DeleteDocumentError.title"), _extstr(u"deleteentryuiutil.DeleteDocumentNotFound.message")) #$NON-NLS-2$ #$NON-NLS-1$
            return
        if blog and not self._validateBlogType(parent, blog):
            return

        blogInfos = zblogDocument.getBlogInfoList()

        if not zblogDocument.isPublished():
            self._deleteUnpublishedPost(parent, zblogDocument)
        else:
            self._deleteMultiPublishedPost(parent, zblogDocument, blogInfos, blog)
    # end deletePosts()

    def _deleteUnpublishedPost(self, parent, zblogDocument):
        question = _extstr(u"publisherutil.DeleteUnpublishedPostMessage") % zblogDocument.getTitle() #$NON-NLS-1$
        title = _extstr(u"publisherutil.DeleteUnpublishedPostTitle") #$NON-NLS-1$
        if ZShowYesNoMessage(parent, question, title):
            docStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
            docStore.removeDocument(zblogDocument.getId())
    # end _deleteUnpublishedPost()

    def _deleteMultiPublishedPost(self, parent, zblogDocument, blogInfos, blog):
        blogs = []
        for blogInfo in blogInfos:
            b = getBlogFromBlogInfo(blogInfo)
            blogs.append(b)

        (rBool, alsoDeleteLocal, blogsToDeleteFrom) = ZShowConfirmDeletePostFromMultipleBlogsDialog(parent, zblogDocument, blog, blogs)
        if rBool:
            if not ZPublisherUiValidator().validateBlogs(parent, blogsToDeleteFrom):
                return

            if alsoDeleteLocal and not blogsToDeleteFrom:
                docStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
                docStore.removeDocument(zblogDocument.getId())
            else:
                task = ZDeletePostBackgroundTask()
                task.initialize(blogsToDeleteFrom, zblogDocument, alsoDeleteLocal)
                title = _extstr(u"publisherutil.DeletingOnlinePost") #$NON-NLS-1$
                desc = _extstr(u"publisherutil.DeletingPostFromBlogs") % (zblogDocument.getTitle(), len(blogsToDeleteFrom)) #$NON-NLS-1$
                self._addBackgroundTask(task, parent, title, desc, None)
    # end _deleteMultiPublishedPost()

# end ZDeleteEntryUiUtil


#-------------------------------------------------------------------
# Utils class that is used to post and update entries
#-------------------------------------------------------------------
class ZPublishEntryUiUtil(ZPublisherUiUtilBase):

    def publishPost(self, parent, blog, zblogDocument, pubMetaDataList = []): #@UnusedVariable
#        # FIXME (PJ) Handle case for local drafts -> zblog = None
        if pubMetaDataList is None or len(pubMetaDataList) == 0:
            dialog = ZBlogPublishingDialog(parent, zblogDocument, blog)
            rval = dialog.ShowModal()
            dialog.Destroy()
            if rval != wx.ID_OK:
                return
            pubMetaDataList = dialog.getPubMetaDataList()

        tmpList = []
        desc = None
        for pubMetaData in pubMetaDataList:
            blog = getBlogFromPubMetaData( pubMetaData )
            if blog is None:
                ZShowErrorMessage(parent, _extstr(u"publishentryuiutil.PublishDocumentError.title"), _extstr(u"publishentryuiutil.PublishDocumentNotFound.message")) #$NON-NLS-2$ #$NON-NLS-1$
                continue
            if not self._validateBlogType(parent, blog):
                continue
            tmpList.append(pubMetaData)
            if desc is None:
                desc = u"Publishing post '%s' to blog '%s'" % (zblogDocument.getTitle(),  blog.getName()) #$NON-NLS-1$
        if len(tmpList) > 0:
            # validate settings
            if not ZPublisherUiValidator().validatePublishing(parent, zblogDocument, tmpList):
                return
            task = ZPublishPostBackgroundTask()
            task.initialize(zblogDocument, tmpList)
            title = u"Publish Post" #$NON-NLS-1$
            if len(tmpList) > 1:
                desc = u"Publishing post to %d blogs" % len(tmpList) #$NON-NLS-1$
            self._addBackgroundTask(task, parent, title, desc, None)
    # end publishPost()

#-------------------------------------------------------------------
# Utils class that is used to synch up with blog server
#-------------------------------------------------------------------
class ZPublisherSiteSynchronizer:

    def __init__(self):
        pass
    # end __init__()

    def updateBlogList(self, account, selectedBlogList, izcommandActivityListener): #@UnusedVariable
        accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        # create publisher
        publisher = createBlogPublisherFromAccount(account, publisherService)

        # update account's blog list from server
        cmd = ZListBlogsCommand(publisher, account, selectedBlogList)
        cmd.addListener(izcommandActivityListener)
        cmd.listBlogs();
        # save account with the new blog lists.
        accStoreService.saveAccount(account)
    # end updateBlogList()

    def createMediaStorages(self, account, izcommandActivityListener):
        accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        # create publisher
        publisher = createBlogPublisherFromAccount(account, publisherService)
        cmd = ZCreateOrUpdateBlogMediaStoragesCommand(publisher, mediaStoreService, account)
        cmd.addListener(izcommandActivityListener)
        cmd.doCommand()
        accStoreService.saveAccount(account)
    # end createMediaStorages()

    def updateCategories(self, account, blogList, izcommandActivityListener):
        accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        publisher = createBlogPublisherFromAccount(account, publisherService)
        blogList = self._getFilteredAccBlogList(account, blogList)
        cmd = ZListCategoriesCommand(publisher, account, blogList)
        cmd.addListener(izcommandActivityListener)
        cmd.doCommand()
        accStoreService.saveAccount(account)

    def downloadPosts(self, account, blogList, maxDocs, izcommandActivityListener):
        docIndexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        dataStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        publisher = createBlogPublisherFromAccount(account, publisherService)

        blogList = self._getFilteredAccBlogList(account, blogList)
        cmd = ZDownloadEntriesCommand(dataStoreService, docIndexService, publisher, account, blogList, maxDocs)
        cmd.addListener(izcommandActivityListener)
        cmd.doCommand()
    # end downloadPosts()

    def _getFilteredAccBlogList(self, account, blogFilterList):
        # return list of account blogs given the filter list. If the filter list is empty
        # then the first account blog is returned.
        rval = []
        if not blogFilterList or len(blogFilterList) == 0:
            # use first blog in account
            accBlogs = account.getBlogs()
            if accBlogs and len(accBlogs) > 0:
                rval.append(accBlogs[0])
        else:
            # get list of acc blogs based on filter list
            for accBlog in account.getBlogs():
                for tmp in blogFilterList:
                    if (accBlog.getId() == tmp.getId()) \
                        or (accBlog.getName() == tmp.getName() and accBlog.getUrl() == tmp.getUrl()):
                        rval.append(accBlog)
        return rval
    # end _getFilteredAccBlogList()

# end ZPublisherSiteSynchronizer


#-------------------------------------------------------------------
# Background task (on new account creation) which updates the list
# of blogs, categories and if needed, download recent posts from
# selected blogs.
#-------------------------------------------------------------------
class ZNewAccountSynchupBackgroundTask(ZBackgroundTask, IZCommandActivityListener):

    def __init__(self):
        ZBackgroundTask.__init__(self)
        self.customAttributes = {}

    def initialize(self, account, selectedBlogs):
        # FIXME (PJ) use accId instead of acount
        self.account = account
        self.selectedBlogs = selectedBlogs
        self.setName(_extstr(u"publishersynch.AccountSynchBgTask.name")) #$NON-NLS-1$

    def getAccount(self):
        return self.account

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        pass
    # end _doCancel()

    def _fireStartEvent(self):
        self.setNumWorkUnits(100)
        ZBackgroundTask._fireStartEvent(self)
    # end _fireStartEvent()

    def _run(self):
        if not self.getAccount():
            # FIXME (PJ) raise ex or log warning.
            return
        # FIXME (PJ) on udating cats, and downloading posts, do it on a per blog basis to allow the user to cancel.
        # Handle bg task cancel
        # Also consider using zcommand group and zasync command if needed.

        # Ask EPW: customAttributes; bgtask::isRunning()
        self._incrementWork(u"starting...", 5) #$NON-NLS-1$
        # synch up blog list froom server and save account
        self._updateBlogList()
        # synch categories and save
        self._updateCategories()
        # download posts from the list of blogs selected in the wizard's 'confirm page'
        self._downloadPosts()
        self._incrementWork(u"done...", 5) #$NON-NLS-1$
    # end _run()

    def _updateBlogList(self):
        if self.isCancelled():
            return
        self._incrementWork(_extstr(u"publishersynch.updatingbloglist"), 1, True) #$NON-NLS-1$
        syncher = ZPublisherSiteSynchronizer()
        syncher.updateBlogList( self.getAccount(), self.selectedBlogs, self )
        syncher.createMediaStorages( self.getAccount(), self )
        self._incrementWork(_extstr(u"publishersynch.updatingbloglist"), 9, False) #$NON-NLS-1$
    # end _updateBlogList()

    def _updateCategories(self):
        if self.isCancelled():
            return
        self._incrementWork(_extstr(u"publishersynch.updatingcategories"), 1, True) #$NON-NLS-1$
        syncher = ZPublisherSiteSynchronizer()
        blogs = self.getAccount().getBlogs()
        syncher.updateCategories(self.getAccount(), blogs, self)
        self._incrementWork(_extstr(u"publishersynch.updatingcategories"), 19, False) #$NON-NLS-1$
    # end _updateCategories()

    def _downloadPosts(self):
        if self.isCancelled():
            return
        # download posts from the list of blogs selected in the wizard's 'confirm page'
        # re-create selected list by matchng up blog users.
        self._incrementWork(_extstr(u"publishersynch.downloadingposts"), 1, True) #$NON-NLS-1$
        syncher = ZPublisherSiteSynchronizer()
        syncher.downloadPosts(self.getAccount(), self.selectedBlogs, ZPublisherSiteSynchUiUtil.NEW_ACC_POSTS_DOWNLOAD, self)
        self._incrementWork(_extstr(u"publishersynch.downloadingposts"), 59, False) #$NON-NLS-1$
    # end _downloadPosts()

    def onBeginCommand(self, command, totalWorkamount): #@UnusedVariable
        pass
    # end onBeginCommand()

    def onCommandActivity(self, command, message, workamount, logMessage): #@UnusedVariable
        pass
    # end onCommandActivity()

    def onEndCommand(self, command): #@UnusedVariable
        pass
    # end onEndCommand()

    def onLogActivity(self, command, message): #@UnusedVariable
        self._writeToLog(message)
    # end onLogActivity()

# end


#-------------------------------------------------------------------
# Background task (on new account creation) which updates the list
# of blogs, categories and if needed, download recent posts from
# selected blogs.
#-------------------------------------------------------------------
class ZDownloadRecentPostsBackgroundTask(ZBackgroundTask, IZCommandActivityListener):

    def __init__(self):
        ZBackgroundTask.__init__(self)
        self.customAttributes = {}

    def initialize(self, account, blog, numposts):
        # FIXME (PJ) use accId instead of acount
        self.account = account
        self.blog = blog
        if numposts < 1:
            numposts = 20
        self.numposts = numposts
        self.setName(_extstr(u"publishersynch.DownloadBgTask.name")) #$NON-NLS-1$
    # end initialize()

    def getAccount(self):
        return self.account
    # end getAccount()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        pass
    # end _doCancel()

    def _fireStartEvent(self):
        self.setNumWorkUnits(100)
        ZBackgroundTask._fireStartEvent(self)

    def _run(self):
        if not self.getAccount():
            # FIXME (PJ) raise ex or log warning.
            return

        # Ask EPW: customAttributes; bgtask::isRunning()
        self._incrementWork(u"starting...", 5) #$NON-NLS-1$
        # synch categories and save
        self._updateCategories()
        # download posts from the list of blogs selected in the wizard's 'confirm page'
        self._downloadPosts()
        self._incrementWork(u"done...", 5) #$NON-NLS-1$
    # end _run()

    def _updateCategories(self):
        if self.isCancelled():
            return
        self._incrementWork(_extstr(u"publishersynch.updatingcategories"), 1, True) #$NON-NLS-1$
        syncher = ZPublisherSiteSynchronizer()
        blogs = [ self.blog ]
        syncher.updateCategories(self.getAccount(), blogs, self)
        self._incrementWork(_extstr(u"publishersynch.updatingcategories"), 19, False) #$NON-NLS-1$
    # end _updateCategories()

    def _downloadPosts(self):
        if self.isCancelled():
            return
        # download posts from the list of blogs selected in the wizard's 'confirm page'
        # re-create selected list by matchng up blog users.
        self._incrementWork(_extstr(u"publishersynch.downloadingposts"), 1, True) #$NON-NLS-1$
        syncher = ZPublisherSiteSynchronizer()
        blogs = [ self.blog ]
        syncher.downloadPosts(self.getAccount(),  blogs , self.numposts, self)
        self._incrementWork(_extstr(u"publishersynch.downloadingposts"), 69, False) #$NON-NLS-1$
    # end _downloadPosts()

    def onBeginCommand(self, command, totalWorkamount): #@UnusedVariable
        pass
    # end onBeginCommand()

    def onCommandActivity(self, command, message, workamount, logMessage): #@UnusedVariable
        pass
    # end onCommandActivity()

    def onEndCommand(self, command): #@UnusedVariable
        pass
    # end onEndCommand()

    def onLogActivity(self, command, message): #@UnusedVariable
        self._writeToLog(message)
    # end onLogActivity()

# end ZDownloadRecentPostsBackgroundTask


#-------------------------------------------------------------------
# Background task to delete a post
#-------------------------------------------------------------------
class ZDeletePostBackgroundTask(ZBackgroundTask, IZCommandActivityListener):

    def __init__(self):
        ZBackgroundTask.__init__(self)
        self.customAttributes = {}
        self.currentCommand = None
        self.commands = None
        self.blogs = []
        self.document = None
        self.deleteLocal = False
        self.currWorkAmount = 0
    # end __init__()

    def initialize(self, blogs, document, deleteLocal):
        self.blogs = blogs
        self.document = document
        self.deleteLocal = deleteLocal
        self.setName(_extstr(u"deleteentryuiutil.DeleteBgTask.name")) #$NON-NLS-1$
    # end initialize()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        if self.currentCommand:
            self.currentCommand.cancel()
    # end _doCancel()

    def _fireStartEvent(self):
        if self.blogs:
            self.setNumWorkUnits(len(self.blogs) * 3)
        else:
            self.setNumWorkUnits(2)
        ZBackgroundTask._fireStartEvent(self)
    # end _fireStartEvent()

    def _run(self):
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        dataStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        publisher = None
        self.commands = []
        if self.blogs:
            for blog in self.blogs:
                account = blog.getAccount()
                publisher = createBlogPublisherFromAccount(account, publisherService)
                command = ZDeleteEntryCommand(publisher, dataStoreService, account, blog, self.document, False)
                command.addListener( self )
                self.commands.append(command)
        else:
            command = ZDeleteEntryCommand(None, dataStoreService, None, None, self.document, True)
            command.addListener( self )
            self.commands.append(command)

        if self.deleteLocal and self.commands:
            self.commands[len(self.commands) - 1].setDeleteLocalEntry(True)

        # Now run all of the commands.
        for command in self.commands:
            self.currentCommand = command
            if self.isCancelled():
                return
            else:
                self.currentCommand.doCommand()
    # end _run()

    def onBeginCommand(self, command, totalWorkamount): #@UnusedVariable
        #self.setNumWorkUnits(totalWorkamount)
        self.currWorkAmount = 0
    # end onBeginCommand()

    def onCommandActivity(self, command, message, workamount, logMessage): #@UnusedVariable
        self._incrementWork(message, self.currWorkAmount, logMessage) #$NON-NLS-1$
        self.currWorkAmount = workamount
    # end onCommandActivity()

    def onEndCommand(self, command): #@UnusedVariable
        amount = self.getNumWorkUnits() - self.getNumCompletedWorkUnits()
        self._incrementWork(u"", amount, False) #$NON-NLS-1$
    # end onEndCommand()

    def onLogActivity(self, command, message): #@UnusedVariable
        self._writeToLog(message)
    # end onLogActivity()

# end ZDeletePostBackgroundTask


#-------------------------------------------------------------------
# Background task to publish a post
#-------------------------------------------------------------------
class ZPublishPostBackgroundTask(ZBackgroundTask, IZCommandActivityListener):

    def __init__(self):
        ZBackgroundTask.__init__(self)
        self.customAttributes = {}
        self.command = None
        self.document = None
        self.pubMetadataList = []
        self.currWorkAmount = 0
    # end __init__()

    def initialize(self, document, pubMetadataList):
        self.document = document
        self.pubMetadataList = pubMetadataList
        self.setName(_extstr(u"publishentryuiutil.PublishBgTask.name")) #$NON-NLS-1$
    # end initialize()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        if self.command:
            self.command.cancel()
    # end _doCancel()

    def _fireStartEvent(self):
        self.setNumWorkUnits(100)
        ZBackgroundTask._fireStartEvent(self)
    # end _fireStartEvent()

    def _run(self):
        cmdList = []
        workunits = 0
        for pubMetaData in self.pubMetadataList:
            if self.isCancelled():
                break
            blog = getBlogFromPubMetaData(pubMetaData)
            if not blog:
                continue
            account = blog.getAccount()
            if not account:
                continue
            pubCmd = self._createCommand(account, blog, pubMetaData)
            if pubCmd.getTotalWorkUnits() > 0:
                cmdList.append( pubCmd )
                workunits = workunits + pubCmd.getTotalWorkUnits()

        self.setNumWorkUnits(workunits)
        self.currWorkAmount = 0
        self.command = None
        for cmd in cmdList:
            if self.isCancelled():
                break
            self.command = cmd
            self.command.addListener( self )
            self.command.doCommand()
        # finish up
        self._incrementWork(u"", 1, False) #$NON-NLS-1$
    # end _run

    def _createCommand(self, account, blog, pubMetaData):
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        dataStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        publisher = createBlogPublisherFromAccount(account, publisherService)
        # create update or publish command and execute
        command = None
        if self.document.isPublishedToBlog( blog.getId() ):
            command = ZUpdateEntryCommand(publisher, dataStoreService, account, blog, self.document, pubMetaData)
        else:
            command = ZPublishEntryCommand(publisher, dataStoreService, account, blog, self.document, pubMetaData)
        return command
    # end _createCommand()

    def onBeginCommand(self, command, totalWorkamount): #@UnusedVariable
        pass
    # end onBeginCommand()

    def onCommandActivity(self, command, message, workamount, logMessage): #@UnusedVariable
        self._incrementWork(message, self.currWorkAmount, logMessage) #$NON-NLS-1$
        self.currWorkAmount = workamount
    # end onCommandActivity()

    def onEndCommand(self, command): #@UnusedVariable
        self._incrementWork(u"", 0, False) #$NON-NLS-1$
    # end onEndCommand()

    def onLogActivity(self, command, message): #@UnusedVariable
        self._writeToLog(message)
    # end onLogActivity()

# end ZPublishPostBackgroundTask
