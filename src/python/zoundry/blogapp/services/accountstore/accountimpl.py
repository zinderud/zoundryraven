from zoundry.base.util.types.attrmodel import ZModelWithAttributes
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.profile.userprefs import ZUserPreferencesBase
from zoundry.appframework.util import crypt
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.blogapp.services.accountstore.account import IZAccount
from zoundry.blogapp.services.accountstore.account import IZAccountAPIInfo
from zoundry.blogapp.services.accountstore.account import IZBlogAccount
from zoundry.blogapp.services.accountstore.account import IZBlogFromAccount


ACCOUNT_PREFERENCES_NAMESPACE = u"urn:zoundry:account-prefs" #$NON-NLS-1$
BLOG_PREFERENCES_NAMESPACE = u"urn:zoundry:blog-prefs" #$NON-NLS-1$

PREF_KEY_MEDIA_UPLOAD_METHOD = u"media-upload-method" #$NON-NLS-1$
PREF_KEY_MEDIA_UPLOAD_STORE = u"media-upload-store" #$NON-NLS-1$
PREF_KEY_TEMPLATE = u"template" #$NON-NLS-1$

# -----------------------------------------------------------------------------------------
# An implementation of an IZUserPreferences for a ZAccount.
# -----------------------------------------------------------------------------------------
class ZAccountPreferences(ZUserPreferencesBase):

    def __init__(self, account):
        self.account = account
        self.userPreferences = getApplicationModel().getUserProfile().getPreferences()

        ZUserPreferencesBase.__init__(self)
    # end __init__()

    def _getUserPreference(self, key):
        value = self.account.getAttribute(key, ACCOUNT_PREFERENCES_NAMESPACE)
        if value is None:
            value = self.userPreferences.getUserPreference(key)
        return value
    # end _getUserPreference()

    def _setUserPreference(self, key, value):
        self.account.setAttribute(key, value, ACCOUNT_PREFERENCES_NAMESPACE)
    # end _setUserPreference()

    def _removeUserPreference(self, key):
        self.account.removeAttribute(key, ACCOUNT_PREFERENCES_NAMESPACE)
    # end _removeUserPreference()

# end ZAccountPreferences


# -----------------------------------------------------------------------------------------
# An implementation of an IZUserPreferences for a Blog.
# -----------------------------------------------------------------------------------------
class ZBlogPreferences(ZUserPreferencesBase):

    def __init__(self, accountPrefs, blog):
        self.accountPrefs = accountPrefs
        self.blog = blog

        ZUserPreferencesBase.__init__(self)
    # end __init__()

    def _getUserPreference(self, key):
        value = self.blog.getAttribute(key, BLOG_PREFERENCES_NAMESPACE)
        if value is None:
            value = self.accountPrefs.getUserPreference(key)
        return value
    # end _getUserPreference()

    def _setUserPreference(self, key, value):
        self.blog.setAttribute(key, value, BLOG_PREFERENCES_NAMESPACE)
    # end _setUserPreference()

    def _removeUserPreference(self, key):
        self.blog.removeAttribute(key, BLOG_PREFERENCES_NAMESPACE)
    # end _removeUserPreference()

# end ZBlogPreferences


# -----------------------------------------------------------------------------------------
# Class that models the api-info section of the account.xml file.
# -----------------------------------------------------------------------------------------
class ZAccountAPIInfo(ZModelWithAttributes, IZAccountAPIInfo):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
    # end __init__()

    def getType(self):
        return self.getAttribute(u"type") #$NON-NLS-1$
    # end getType()

    def setType(self, type):
        self.setAttribute(u"type", type) #$NON-NLS-1$
    # end setType()

    def getUrl(self):
        return self.getAttribute(u"url") #$NON-NLS-1$
    # end getUrl()

    def setUrl(self, url):
        self.setAttribute(u"url", url) #$NON-NLS-1$
    # end setUrl()

# end ZAccountAPIInfo


# -----------------------------------------------------------------------------------------
# A blog that was defined in a ZAccount.  Each ZAccount will have zero or more instances
# of this class.
# -----------------------------------------------------------------------------------------
class ZBlogFromAccount(ZModelWithAttributes, IZBlogFromAccount):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
        self.id = None
        self.categories = []
        self.preferences = None
        self.account = None
    # end __init__()

    def getId(self):
        return self.id
    # end getId()

    def setId(self, id):
        self.id = id
    # end setId()

    def getName(self):
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        self.setAttribute(u"name", name) #$NON-NLS-1$
    # end setName()

    def getUrl(self):
        return self.getAttribute(u"url") #$NON-NLS-1$
    # end getName()

    def setUrl(self, url):
        self.setAttribute(u"url", url) #$NON-NLS-1$
    # end setName()

    def getCategories(self):
        return self.categories
    # end getCategories()

    def addCategory(self, category):
        self.categories.append(category)
    # end addCategory()

    def removeCategory(self, category):
        foundCategory = None
        for cat in self.categories:
            if cat.getId() == category.getId():
                foundCategory = cat
        if foundCategory:
            self.categories.remove(foundCategory)
        return foundCategory is not None
    # end removeCategory()

    def getAccount(self):
        return self.account
    # end getAccount()

    def setAccount(self, account):
        self.account = account
    # end setAccount()

    def getPreferences(self):
        return self.preferences
    # end getPreferences()

    def setPreferences(self, preferences):
        self.preferences = preferences
    # end setPreferences()

    def getMediaUploadMethod(self):
        return self.getPreferences().getUserPreference(PREF_KEY_MEDIA_UPLOAD_METHOD) #$NON-NLS-1$
    # end getMediaUploadMethod()

    def setMediaUploadMethod(self, uploadMethod):  #@UnusedVariable
        self.getPreferences().setUserPreference(PREF_KEY_MEDIA_UPLOAD_METHOD, uploadMethod) #$NON-NLS-1$
    # end setMediaUploadMethod()

    def getMediaUploadStorageId(self):
        return self.getPreferences().getUserPreference(PREF_KEY_MEDIA_UPLOAD_STORE) #$NON-NLS-1$
    # end getMediaUploadStorageId()

    def setMediaUploadStorageId(self, storeId):  #@UnusedVariable
        self.getPreferences().setUserPreference(PREF_KEY_MEDIA_UPLOAD_STORE, storeId) #$NON-NLS-1$
    # end setMediaUploadStorageId()

    def getTemplateId(self):
        return self.getPreferences().getUserPreference(PREF_KEY_TEMPLATE) #$NON-NLS-1$
    # end getTemplateId()

    def setTemplateId(self, templateId):
        self.getPreferences().setUserPreference(PREF_KEY_TEMPLATE, templateId) #$NON-NLS-1$
    # end setTemplateId()

# end ZBlogFromAccount


# -----------------------------------------------------------------------------------------
# This is the object that models a single account.  An account is represented by a
# directory on disk with, at minimum, an account.xml file in it.  This class can be used
# to modify the contents of the account, but to save it, the account must be passed back
# to the ZAccountStore (use the saveAccount() method).
# -----------------------------------------------------------------------------------------
class ZAccount(ZModelWithAttributes, IZAccount):

    def __init__(self, accountDirectory):
        ZModelWithAttributes.__init__(self)

        self.accountDirectory = accountDirectory
        self.id = None
        self.apiInfo = None
        self.preferences = self._createPreferences()
    # end __init__()

    def _createPreferences(self):
        return ZAccountPreferences(self)
    # end _createPreferences()

    def getDirectoryPath(self):
        return self.accountDirectory
    # end getDirectoryPath()

    def setDirectoryPath(self, path):
        self.accountDirectory = path
    # end setDirectoryPath()

    def getId(self):
        return self.id
    # end getId()

    def setId(self, id):
        self.id = id
    # end setId()

    def getName(self):
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        self.setAttribute(u"name", name) #$NON-NLS-1$
    # end setName()

    def getAPIInfo(self):
        return self.apiInfo
    # end getAPIInfo()

    def setAPIInfo(self, apiInfo):
        self.apiInfo = apiInfo
    # end setAPIInfo()

    def getPreferences(self):
        return self.preferences
    # end getPreferences()

# end ZAccount

#---------------------------------------------------------------------------
# Blog specific account
#---------------------------------------------------------------------------
class ZBlogAccount(ZAccount, IZBlogAccount):

    def __init__(self, accountDirectory):
        ZAccount.__init__(self, accountDirectory)
        self.blogs = []
    # end __init__()

    def setUsername(self, username):
        self.setAttribute(u"username", username) #$NON-NLS-1$
    # end setUsername()

    def getUsername(self):
        return self.getAttribute(u"username") #$NON-NLS-1$
    # end getUsername()

    def setPassword(self, clearTextPass):
        encpass = crypt.encryptPlainText(clearTextPass.strip(), PASSWORD_ENCRYPTION_KEY)
        self.setAttribute(u"password", encpass) #$NON-NLS-1$
    # end setPassword()

    def getPassword(self):
        encpass = self.getAttribute(u"password") #$NON-NLS-1$
        if encpass:
            return crypt.decryptCipherText(encpass, PASSWORD_ENCRYPTION_KEY)
        else:
            return None
    # end getPassword()

    def setMediaUploadMethod(self, uploadMethod):  #@UnusedVariable
        self.getPreferences().setUserPreference(PREF_KEY_MEDIA_UPLOAD_METHOD, uploadMethod) #$NON-NLS-1$
    # end setMediaUploadMethod()

    def getMediaUploadMethod(self):
        return self.getPreferences().getUserPreference(PREF_KEY_MEDIA_UPLOAD_METHOD) #$NON-NLS-1$
    # end getMediaUploadMethod()

    def setMediaUploadStorageId(self, storeId):  #@UnusedVariable
        self.getPreferences().setUserPreference(PREF_KEY_MEDIA_UPLOAD_STORE, storeId) #$NON-NLS-1$
    # end setMediaUploadStorageId()

    def getMediaUploadStorageId(self):
        return self.getPreferences().getUserPreference(PREF_KEY_MEDIA_UPLOAD_STORE) #$NON-NLS-1$
    # end getMediaUploadStorageId()

    def getTemplateId(self):
        return self.getPreferences().getUserPreference(PREF_KEY_TEMPLATE) #$NON-NLS-1$
    # end getTemplateId()

    def setTemplateId(self, templateId):
        self.getPreferences().setUserPreference(PREF_KEY_TEMPLATE, templateId) #$NON-NLS-1$
    # end setTemplateId()

    def addBlog(self, blog):
        self.blogs.append(blog)
        # Parent the blog
        if isinstance(blog, ZBlogFromAccount):
            blog.setAccount(self)
        blog.setPreferences(self._createBlogPreferences(blog))
    # end addBlog()

    def removeBlog(self, blog):
        idx = 0
        for b in self.getBlogs():
            if b.getId() == blog.getId():
                self.getBlogs().pop(idx)
                return b
            idx = idx + 1
        return None
    # end removeBlog

    def getBlogs(self):
        return self.blogs
    # end getBlogs()

    def getBlogById(self, blogId):
        for blog in self.getBlogs():
            if blog.getId() == blogId:
                return blog
        return None
    # end getBlogById()

    def getBlogByName(self, blogName):
        for blog in self.getBlogs():
            if blog.getName() == blogName:
                return blog
        return None
    # end getBlogByName()

    def _createBlogPreferences(self, blog):
        return ZBlogPreferences(self.preferences, blog)
    # end _createBlogPreferences()

# end ZBlogAccount
