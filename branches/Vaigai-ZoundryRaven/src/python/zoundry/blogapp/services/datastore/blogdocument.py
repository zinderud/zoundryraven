from zoundry.blogapp.services.common import IZAttributeModel
from zoundry.blogapp.services.datastore.document import IZDocument

# -----------------------------------------------------------------------------------------
# The interface for a Trackback.
# -----------------------------------------------------------------------------------------
class IZTrackback(IZAttributeModel):

    def getUrl(self):
        u"Gets the ping address." #$NON-NLS-1$
    # end getUrl()

    def isSent(self):
        u"isSent() -> bool" #$NON-NLS-1$
    # end isSent

    def getSentDate(self):
        u"getSentDate() -> ZSchemaDateTime" #$NON-NLS-1$
    # end getSentDate

# end IZTrackback

# -----------------------------------------------------------------------------------------
# The interface for a weblog ping service
# -----------------------------------------------------------------------------------------
class IZWeblogPingSite(IZAttributeModel):

    def getName(self):
        u"Gets the display name." #$NON-NLS-1$
    # end getName()

    def getUrl(self):
        u"Gets the ping Url." #$NON-NLS-1$
    # end getUrl()
# end IZWeblogPing


# -----------------------------------------------------------------------------------------
# The interface for a Tagwords.
# -----------------------------------------------------------------------------------------
class IZTagwords:

    def getUrl(self):
        u"Gets the url." #$NON-NLS-1$
    # end getUrl()

    def setUrl(self, url):
        u"Sets the url." #$NON-NLS-1$
    # end setUrl()

    def getValue(self):
        u"Returns a comma separated list of tagwords." #$NON-NLS-1$
    # end getValue()

    def setValue(self, value):
        u"Sets a comma separated list of tagwords." #$NON-NLS-1$
    # end setValue()

    def getTagwords(self):
        u"""getTagwords() -> sorted string list of unique tag words
        """ #$NON-NLS-1$

# end IZTagwords


# -----------------------------------------------------------------------------------------
# The interface for blog information from a document.
# -----------------------------------------------------------------------------------------
class IZPublishInfo(IZAttributeModel):

    def getBlogEntryId(self):
        u"Gets the blog entry id." #$NON-NLS-1$
    # end getBlogEntryId()

    def getPublishedTime(self):
        u"Returns the issued-time." #$NON-NLS-1$
        # FIXME (PJ) add support for updated-time
    # end getPublishedTime()

    def getSynchTime(self):
        u"""Returns the last synch time (the time that this pub info
        was created by either synchronizing or publishing).""" #$NON-NLS-1$
    # end getSynchTime()

    def isDraft(self):
        u"Returns whether this is a draft or not." #$NON-NLS-1$
    # end isDraft()

    def getUrl(self):
        u"Returns the permalink for the blog entry." #$NON-NLS-1$
    # end getUrl()

    def getTrackbacks(self):
        u"Gets the list of trackbacks." #$NON-NLS-1$
    # end getTrackbacks()

    def addTrackback(self, trackback):
        u"Adds the trackback." #$NON-NLS-1$
    # end addTrackback()

# end IZPublishInfo


# -----------------------------------------------------------------------------------------
# The interface for blog information from a document.
# -----------------------------------------------------------------------------------------
class IZBlogInfo:

    def getAccountId(self):
        u"Gets the account id of the blog." #$NON-NLS-1$
    # end getAccountId()

    def setAccountId(self, accountId):
        u"Sets the account id of the blog." #$NON-NLS-1$
    # end setAccountId()

    def getBlogId(self):
        u"Gets the id of the blog." #$NON-NLS-1$
    # end getBlogId()

    def setBlogId(self, blogId):
        u"Sets the id of the blog." #$NON-NLS-1$
    # end setBlogId()

    def getPublishInfo(self):
        u"Gets the publishing information from this blog." #$NON-NLS-1$
    # end getPublishInfo()

    def setPublishInfo(self, pubInfo):
        u"Sets the publishing information on this blog." #$NON-NLS-1$
    # end setPublishInfo()

    def getCategories(self):
        u"Gets the list of categories for this blog." #$NON-NLS-1$
    # end getCategories()

    def addCategory(self, category):
        u"Adds a category to the list of categories for this blog." #$NON-NLS-1$
    # end addCategory()

# end IZBlogInfo


# ------------------------------------------------------------------------------
# Interface to which defines data model for addtional
# custom meta data.
# ------------------------------------------------------------------------------
class IZCustomMetaData(IZAttributeModel):
    pass
# end IZCustomMetaData

# ------------------------------------------------------------------------------
# Class containing the information that the user has entered in the publishing
# dialog (or the blog post editor).
# ------------------------------------------------------------------------------
class IZPubMetaData(IZAttributeModel):

    def getAccountId(self):
        u"""getAccountId() -> accountId
        Gets the account id.""" #$NON-NLS-1$
    # end getAccountId()

    def getBlogId(self):
        u"""getBlogId() -> blogId
        Gets the blog id.""" #$NON-NLS-1$
    # end getBlogId()

    def isPublishAsDraft(self):
        u"""isPublishAsDraft() -> boolean
        Returns True if the 'publish as draft' option is set.""" #$NON-NLS-1$
    # end isPublishAsDraft()

    def getPublishTime(self):
        u"""getPublishTime() -> ZSchemaDateTime
        Returns the time to use for publishing, or None if no
        time is specified (will use "now").""" #$NON-NLS-1$
    # end getPublishTime()

    def isUploadTNsOnly(self):
        u"""isUploadTNsOnly() -> boolean
        Returns True if only image thumbnails should be uploaded
        (not the full original images).""" #$NON-NLS-1$
    # end isUploadTNsOnly()

    def isForceReUploadImages(self):
        u"""isForceReUploadImages() -> boolean
        Returns True if the images should be re-uploaded
        even if they are not dirty.""" #$NON-NLS-1$
    # end isForceReUploadImages()

    def isAddLightbox(self):
        u"""isAddLightbox() -> boolean
        Returns True if links to images should be tagged with rel=lightbox.""" #$NON-NLS-1$
    # end isAddLightbox()

    def isAddPoweredBy(self):
        u"""isAddPoweredBy() -> boolean
        Returns True if the 'Powered By Zoundry' footer
        should be added when publishing.""" #$NON-NLS-1$
    # end isAddPoweredBy()

    def getCategories(self):
        u"""getCategories() -> IZCategory[]
        Returns the list of categories to use for publishing.""" #$NON-NLS-1$
    # end getCategories()

    def getPingServices(self):
        u"""getPingServices() -> ping service[]
        Returns the list of ping services to use when publishing.""" #$NON-NLS-1$
    # end getPingServices()

    def getTrackbacks(self):
        u"Returns a list of IZTrackback objects for this document." #$NON-NLS-1$
    # end getTrackbacks()

    def getTagspaceUrls(self):
        u"Returns a list of tag space (e.g. technorati) urls for this document." #$NON-NLS-1$
    # end getTagspaceUrls()

    def getCustomMetaData(self, namespace):
        u"""getCustomMetaData(string) -> IZCustomMetaData
        Returns a IZCustomMetaData for the given name space. If a custom data is not available then a new object is created
        and returned.
        """ #$NON-NLS-1$
    #end getCustomMetaData

    def getCustomMetaDataNamespaces(self):
        u"""getCustomMetaDataNameSpaces()  -> string[]""" #$NON-NLS-1$
    # end getCustomMetaDataNamespaces()

# end IZPubMetaData


# -----------------------------------------------------------------------------------------
# The Zoundry Raven blog document interface.  All implementations of documents (basically
# blog entries) must implement this interface.
# -----------------------------------------------------------------------------------------
class IZBlogDocument(IZDocument):

    def getTitle(self):
        u"Gets the document's title." #$NON-NLS-1$
    # end getTitle()

    def setTitle(self, title):
        u"Sets the document's title." #$NON-NLS-1$
    # end setTitle()

    def getBlogInfoList(self):
        u"Returns a list of ZBlogInfo objects.  These objects contain information about this document that is specific to a particular blog." #$NON-NLS-1$
    # end getBlogInfoList()

    def addBlogInfo(self, blogInfo):
        u"Adds the blog info to the document." #$NON-NLS-1$
    # end addBlogInfo()

    def getBlogInfo(self, blogId):
        u"""getBlogInfo(string) -> IZBlogInfo or None
        Returns blog info for the given blog-id or None if not found.""" #$NON-NLS-1$
    # end addBlogInfo()

    def removeBlogInfo(self, blogId):
        u"""removeBlogInfo(string) -> bool
        Deletes the blog info given blog id and returns boolean true if successful.""" #$NON-NLS-1$
    # end removeBlogInfo()

    def getPubMetaDataList(self):
        u"""getPubMetaDataList() -> IZPubMetaData
        Returns a list of IZPubMetaData objects.  These objects contain
        options for publishing to a single blog.""" #$NON-NLS-1$
    # end getPubMetaDataList()

    def setPubMetaDataList(self, pubMetaDataList):
        u"""setPubMetaDataList(IZPubMetaData[]) -> None
        Sets all of the pub meta data objects on the
        document.""" #$NON-NLS-1$
    # end setPubMetaDataList()

    def addPubMetaData(self, pubMetaData):
        u"""addPubMetaData(IZPubMetaData) -> None
        Adds a pub meta data object to the list.""" #$NON-NLS-1$
    # end addPubMetaData()

    def isPublished(self):
        u"""isPublished() -> bool
        Returns true if the document has been published a blog i.e. has pub info.
        """ #$NON-NLS-1$
    # end isPublished()

    def isPublishedToBlog(self, blogId):
        u"""isPublishedToBlog(string) -> bool
        Returns true if the document has been published to the given blog
        """ #$NON-NLS-1$
    # end isPublishedToBlog()

    def getPublishedUrl(self, blogId):
        u"""getPublishedURL(string) -> string
        Returns URL to the post given Blog ID.
        Returns None if the document is not published to the blog.
        """ #$NON-NLS-1$
    # end getPublishedUrl()

    def isPublishable(self):
        u"""isPublishable() -> bool
        Returns true if the blog has been configured for publishing
        i.e either has one or more pub meta data or was previously published
        and has one or more blog info.""" #$NON-NLS-1$
    # end isPublishable()

    def getTagwordsList(self):
        u"Returns a list of IZTagwords objects for this document." #$NON-NLS-1$
    # end getTagwordsList()

    def addTagwords(self, tagwords):
        u"""addTagwords(IZTagwords) -> void
        Adds the tagwords to the set of tagwords for this document.""" #$NON-NLS-1$
    # end addTagwords()

    def getTagwords(self, tagspaceUrl):
        u"""getTagwords(string) -> IZTagwords or None
        Returns IZTagwords for given url e.g. technorati""" #$NON-NLS-1$
    # end getTagwords()

    def getTrackbacks(self):
        u"Gets the list of trackbacks." #$NON-NLS-1$
    # end getTrackbacks()

    def addTrackback(self, trackback):
        u"Adds the trackback." #$NON-NLS-1$
    # end addTrackback()

# end IZBlogDocument
