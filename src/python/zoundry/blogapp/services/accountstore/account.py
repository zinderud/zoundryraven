from zoundry.blogapp.services.common import IZAttributeModel


# -----------------------------------------------------------------------------------------
# Class that models the api-info section of the account.xml file.
# -----------------------------------------------------------------------------------------
class IZAccountAPIInfo(IZAttributeModel):

    def getType(self):
        u"Returns the publisher API site or type." #$NON-NLS-1$
    # end getType()

    def setType(self, type):
        u"Sets the publisher API site or type." #$NON-NLS-1$
    # end setType()

    def getUrl(self):
        u"Returns the API endpoint url." #$NON-NLS-1$
    # end getUrl()

    def setUrl(self, url):
        u"Sets the API endpoint url." #$NON-NLS-1$
    # end setUrl()

# end ZAccountAPIInfo


# -----------------------------------------------------------------------------------------
# Interface that defines a blog.
# -----------------------------------------------------------------------------------------
class IZBlog(IZAttributeModel):

    def getId(self):
        u"Gets the blog id." #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"Sets the blog id." #$NON-NLS-1$
    # end setId()

    def getName(self):
        u"Gets the blog name." #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        u"Sets the blog name." #$NON-NLS-1$
    # end setName()

    def getUrl(self):
        u"Gets the blog url." #$NON-NLS-1$
    # end getUrl()

    def setUrl(self, url):
        u"Sets the blog url." #$NON-NLS-1$
    # end setUrl()

    def getCategories(self):
        u"Gets a list of categories." #$NON-NLS-1$
    # end getCategories()

    def addCategory(self, category):
        u"Adds a category to the blog." #$NON-NLS-1$
    # end addCategory()

    def removeCategory(self, category):
        u"Removes a category from the blog and returns true (if successful)." #$NON-NLS-1$
    # end removeCategory()

    def getPreferences(self):
        u"Returns a IZUserPreferences object for this blog." #$NON-NLS-1$
    # end getPreferences()

    def setMediaUploadMethod(self, uploadMethod):  #@UnusedVariable
        u"""setMediaUploadMethod(string) -> void
        Sets 'publisher' or 'mediastorage' or None for upload
        method.""" #$NON-NLS-1$
    # end setMediaUploadMethod()

    def getMediaUploadMethod(self):
        u"""getMediaUploadMethod() -> string or None
        Returns 'publisher' or 'mediastorage' or None for upload
        method.""" #$NON-NLS-1$
    # end getMediaUploadMethod()

    def setMediaUploadStorageId(self, storeId):  #@UnusedVariable
        u"""setMediaUploadStorageId(string) -> void
        Sets media upload store id if upload method is 'mediastorage'.""" #$NON-NLS-1$
    # end setMediaUploadStorageId()

    def getMediaUploadStorageId(self):
        u"""getMediaUploadStorageId() -> string or None
        Returns media upload store id if upload method is 'mediastorage'.""" #$NON-NLS-1$
    # end getMediaUploadStorageId()

    def getTemplateId(self):
        u"""getTemplateId() -> id or None
        Returns the template id configured for this blog.""" #$NON-NLS-1$
    # end getTemplateId()

    def setTemplateId(self, templateId):
        u"""setTemplateId(id) -> None
        Sets the template id configured for this blog.""" #$NON-NLS-1$
    # end setTemplateId()

# end IZBlog


# ------------------------------------------------------------------------------
# Provides a slightly richer interface for blogs that live within accounts.
# ------------------------------------------------------------------------------
class IZBlogFromAccount(IZBlog):

    def getAccount(self):
        u"""getAccount() -> IZAccount
        Gets the parent account for this blog.""" #$NON-NLS-1$
    # end getAccount()

# end IZBlogFromAccount


# -----------------------------------------------------------------------------------------
# Interface that defines an account.
# -----------------------------------------------------------------------------------------
class IZAccount(IZAttributeModel):

    # FIXME (PJ) add method get/set username; get/set password (which should do the enc/dec cypher work)
    def getId(self):
        u"Gets the account id." #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"Sets the account id." #$NON-NLS-1$
    # end setId()

    def getName(self):
        u"Gets the account name." #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        u"Sets the account name." #$NON-NLS-1$
    # end setName()

    def getPreferences(self):
        u"Returns a IZUserPreferences object for this account." #$NON-NLS-1$
    # end getPreferences()

# end IZAccount


# -----------------------------------------------------------------------------------------
# Interface that defines an blog account.
# -----------------------------------------------------------------------------------------
class IZBlogAccount(IZAccount):

    UPLOAD_METHOD_PUBLISHER = u"publisher" #$NON-NLS-1$
    UPLOAD_METHOD_MEDIASTORE = u"mediastorage" #$NON-NLS-1$

    def getUsername(self):
        u"""getUsername() -> string
        Returns the username.""" #$NON-NLS-1$
    # end getUsername()

    def setUsername(self, username): #@UnusedVariable
        u"""setUsername(string) -> void
        Sets the account username.""" #$NON-NLS-1$
    # end setUsername()

    def getPassword(self):
        u"""getPassword() -> string
        Returns clear text password.""" #$NON-NLS-1$
    # end getPassword()

    def setPassword(self, clearTextPass):  #@UnusedVariable
        u"""setPassword(string) -> void
        Sets the clear text password.""" #$NON-NLS-1$
    # end setPassword()

    def getMediaUploadMethod(self):
        u"""getMediaUploadMethod() -> string or None
        Returns 'publisher' or 'mediastorage' or None for upload
        method.""" #$NON-NLS-1$
    # end getMediaUploadMethod()

    def setMediaUploadMethod(self, uploadMethod):  #@UnusedVariable
        u"""setMediaUploadMethod(string) -> void
        Sets 'publisher' or 'mediastorage' or None for upload
        method.""" #$NON-NLS-1$
    # end setMediaUploadMethod()

    def getMediaUploadStorageId(self):
        u"""getMediaUploadStorageId() -> string or None
        Returns media upload store id if upload method is 'mediastorage'.""" #$NON-NLS-1$
    # end setUsername()

    def setMediaUploadStorageId(self, storeId):  #@UnusedVariable
        u"""setMediaUploadStorageId(string) -> void
        Sets media upload store id if upload method is 'mediastorage'.""" #$NON-NLS-1$
    # end setUsername()

    def getTemplateId(self):
        u"""getTemplateId() -> id or None
        Returns the template id configured for this account.""" #$NON-NLS-1$
    # end getTemplateId()

    def setTemplateId(self, templateId):
        u"""setTemplateId(id) -> None
        Sets the template id configured for this account.""" #$NON-NLS-1$
    # end setTemplateId()

    def addBlog(self, blog):
        u"""addBlog(IZBlog) -> None
        Adds a blog to the account.""" #$NON-NLS-1$
    # end addBlog()

    def removeBlog(self, blog):
        u"""removeBlog(IZBlog) -> None
        Removes a blog from the account.""" #$NON-NLS-1$
    # end removeBlog()

    def getAPIInfo(self):
        u"Gets the API Info." #$NON-NLS-1$
    # end getAPIInfo()

    def setAPIInfo(self, apiInfo):
        u"Sets the API info." #$NON-NLS-1$
    # end setAPIInfo()

    def getBlogs(self):
        u"Gets a list of blogs." #$NON-NLS-1$
    # end getBlogs()

    def getBlogById(self, blogId):
        u"Gets a single blog by its ID." #$NON-NLS-1$
    # end getBlogById()

    def getBlogByName(self, blogName):
        u"Gets a single blog by its name." #$NON-NLS-1$
    # end getBlogByName()

# end IZBlogAccount
