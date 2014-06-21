from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.util import crypt
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.validatables import IZConfigValidatable
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.blogapp.services.pubsystems.blog.blogpubprocessor import ZBlogDocumentPublishProcessor
from zoundry.blogapp.ui.util.blogutil import getBlogFromPubMetaData

#----------------------------------------------
# Validates blog account information
#----------------------------------------------
class ZBlogPublisherAccountInfoValidator(IZConfigValidatable):

    def __init__(self):
        self.blogList = []
    # end __init__()

    def setBlogs(self, blogList):
        self.blogList = []
        for blog in blogList:
            self.addBlog(blog)
    # end setBlogs()

    def addBlog(self, blog):
        if blog:
            self.blogList.append(blog)
    # end addBlog()

    def addBlogsFromPubMetaData(self, pubMetaDataList):
        for pubMetaData in pubMetaDataList:
            blog = getBlogFromPubMetaData( pubMetaData )
            self.addBlog(blog)
    # end addBlogsFromPubMetaData()

    def validateConfiguration(self, validationReporter): #@UnusedVariable
        for blog in self.blogList:
            self._validateBlog(blog, validationReporter)
    # end validateConfiguration()

    def _validateBlog(self, blog, validationReporter):
        zaccount = blog.getAccount()
        if not zaccount:
            # defect 534 work around - should not get here
            logger = getLoggerService()
            logger.error(u"Account information not available for Blog ID %s" % blog.getId() ) #$NON-NLS-1$
            validationReporter.addError(u"Blog Account", u"Account information not available for blog %s" % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$
            return

        username = zaccount.getAttribute(u"username")#$NON-NLS-1$
        if not getNoneString(username):
            validationReporter.addError(u"Blog Account", u"Username is missing for blog %s" % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$
        cyppass = zaccount.getAttribute(u"password")#$NON-NLS-1$
        if not getNoneString(cyppass):
            validationReporter.addError(u"Blog Account", u"Password is missing for blog %s" % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$
        else:
            password = None
            try:
                password = crypt.decryptCipherText(cyppass, PASSWORD_ENCRYPTION_KEY)
            except:
                pass
            if not getNoneString(password):
                validationReporter.addError(u"Blog Account", u"Invalid password set for blog %s. Please set the blog account password." % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$

        apiInfo = zaccount.getAPIInfo()
        url = apiInfo.getUrl()
        if not getNoneString(url):
            validationReporter.addError(u"Blog Account", u"Blog API URL is required for blog %s" % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$

        siteId = apiInfo.getType()
        if not getNoneString(siteId):
            validationReporter.addError(u"Blog Account", u"Blog API type is required for blog %s" % blog.getName() ) #$NON-NLS-1$ #$NON-NLS-2$
    # end _validateBlog

# end class ZBlogPublisherAccountInfoValidator

#----------------------------------------------
# Validates blog account information as well as reports any data
# that are required but missing (e.g. media store, missing images).
#----------------------------------------------
class ZBlogPublishingValidator(ZBlogPublisherAccountInfoValidator):

    def __init__(self, zBlogDocument, pubMetaDataList):
        self.zBlogDocument = zBlogDocument
        self.pubMetaDataList = pubMetaDataList
        ZBlogPublisherAccountInfoValidator.__init__(self)
        self.addBlogsFromPubMetaData(pubMetaDataList)
    # end __init__()

    def validateConfiguration(self, validationReporter): #@UnusedVariable
        if len(self.blogList) == 0:
            validationReporter.addError(u"Blog Account", u"Please select a blog account.") #$NON-NLS-1$ #$NON-NLS-2$
        # call  base class to validate blog account info
        ZBlogPublisherAccountInfoValidator.validateConfiguration(self, validationReporter)
        # validator pub processi.
        for pubMetaData in self.pubMetaDataList:
            zblog = getBlogFromPubMetaData( pubMetaData )
            processor = ZBlogDocumentPublishProcessor(zblog, self.zBlogDocument, pubMetaData, None)
            processor.validateConfiguration(validationReporter)
    # end validateConfiguration()
# end ZBlogPublisherAccountInfoValidator

