from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
from zoundry.blogapp.ui.util.tagsiteutil import deserializeTagSiteList
from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPubMetaData
from zoundry.blogapp.ui.util.pingsiteutil import deserializePingSiteList

# ------------------------------------------------------------------------------
# Convenience function for determining if the given capability is suported by
# the given blog.
# ------------------------------------------------------------------------------
def isCapabilitySupportedByBlog(capability, blog):
    pubType = blog.getAccount().getAPIInfo().getType()
    publishService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
    publisherSite = publishService.getPublisherSite(pubType)
    capabilities = publisherSite.getCapabilities()
    return capabilities.hasCapability(capability)
# end isCapabilitySupportedByBlog()


# ------------------------------------------------------------------------------
# Convenience function for getting an IZBlogFromAccount given the account id
# and blog id.
# ------------------------------------------------------------------------------
def getBlogFromIds(accountId, blogId):
    accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
    account = accountStore.getAccountById(accountId)
    if account is not None:
        return account.getBlogById(blogId)
    return None
# end getBlogFromIds()


# ------------------------------------------------------------------------------
# Convenience function for getting an IZBlogFromAccount given the IZPubMetaData.
# Returns None if not found.
# ------------------------------------------------------------------------------
def getBlogFromPubMetaData(izPubMetaData):
    accId = izPubMetaData.getAccountId()
    blog = None
    if accId is not None:
        blogId = izPubMetaData.getBlogId()
        blog = getBlogFromIds(accId, blogId)
    return blog
# end getBlogFromPubMetaData()


# ------------------------------------------------------------------------------
# Convenience function for getting an IZBlogFromAccount given the IZBlogInfo.
# Returns None if not found.
# ------------------------------------------------------------------------------
def getBlogFromBlogInfo(blogInfo):
    accId = blogInfo.getAccountId()
    blogId = blogInfo.getBlogId()
    return getBlogFromIds(accId, blogId)
# end getBlogFromPubMetaData()


# ------------------------------------------------------------------------------
# Convenience function for getting IZBlogFromAccount given a IZBlogDocument.
# Returns None if not found or the blog has no meta info or pub data.
# ------------------------------------------------------------------------------
def getBlogFromDocument(document):
    u"""getBlogFromDocument(IZBlogDocument) -> IZBlogFromAccount
    Gets the blog for the given document.  This will return
    inconsisten results if the document has been published
    to multiple blogs.""" #$NON-NLS-1$
    pubMetaDatas = document.getPubMetaDataList()
    if pubMetaDatas:
        return getBlogFromPubMetaData(pubMetaDatas[0])
    blogInfos = document.getBlogInfoList()
    if blogInfos:
        return getBlogFromBlogInfo(blogInfos[0])
    return None
# end getBlogFromDocument()


# ------------------------------------------------------------------------------
# Convenience function for creating a default ZPubMetaData object for a given
# blog.  This will load the initial state of the pub meta data object with
# defaults found in the blog's preferences.  If no blog is found, returns None.
# ------------------------------------------------------------------------------
def createDefaultPubMetaData(accountId, blogId):
    blog = getBlogFromIds(accountId, blogId)
    return createDefaultPubMetaDataForBlog(blog)
# end createDefaultPubMetaData()


# ------------------------------------------------------------------------------
# Convenience function for creating a default ZPubMetaData object for a given
# blog.  This will load the initial state of the pub meta data object with
# defaults found in the blog's preferences.  If no blog is found, returns None.
# ------------------------------------------------------------------------------
def createDefaultPubMetaDataForBlog(blog):
    if blog:
        pubMetaData = ZPubMetaData()
        pubMetaData.setAccountId(blog.getAccount().getId())
        pubMetaData.setBlogId(blog.getId())

        blogPrefs = blog.getPreferences()
        pubMetaData.setAddPoweredBy(blogPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY, False))
        pubMetaData.setForceReUploadImages(blogPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD, False))
        pubMetaData.setUploadTNsOnly(blogPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY, False))
        pubMetaData.setAddLightbox(blogPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX, False))
        pingSitesStr = blogPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, None)
        pingSites = deserializePingSiteList(pingSitesStr)
        pubMetaData.setPingServices(pingSites)
        tagSitesStr = blogPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, None)
        tagSites = deserializeTagSiteList(tagSitesStr)
        pubMetaData.setTagspaceUrls(tagSites)
        return pubMetaData
    else:
        return None
# end createDefaultPubMetaData()


# ------------------------------------------------------------------------------
# Given a document and a blog id, returns the blog info or None if not found.
# ------------------------------------------------------------------------------
def _getBlogInfo(document, blogId = None):
    if document:
        blogInfo = None
        # Get the blogInfo for the blog Id we're interested in,
        # or simply get the first blogInfo if no blog id is given.
        if blogId:
            blogInfo = document.getBlogInfo(blogId)
        else:
            blogInfos = document.getBlogInfoList()
            if blogInfos:
                blogInfo = blogInfos[0]
    return blogInfo
# end _getBlogInfo()


# ------------------------------------------------------------------------------
# Gets the url of the given blog post document.
# ------------------------------------------------------------------------------
def getBlogPostUrl(document, blogId = None):
    u"""getBlogPostUrl(IZDocument, blogId?) -> string
    Gets the url of the given blog post document.""" #$NON-NLS-1$
    if not blogId:
        blogInfo = _getBlogInfo(document, None)
        if blogInfo:
            blogId = blogInfo.getBlogId()
    if blogId:
        return document.getPublishedUrl(blogId)
    else:
        return None
# end getBlogPostUrl()


# ------------------------------------------------------------------------------
# Returns custom meta data attribute from pub meta data
# ------------------------------------------------------------------------------
def getCustomMetaDataAttribute(izPubMetaData, namespace, attrName):
    izCustomMetaData = izPubMetaData.getCustomMetaData(namespace) #$NON-NLS-1$
    return izCustomMetaData.getAttribute(attrName)
# end getCustomMetaDataAttribute

# ------------------------------------------------------------------------------
# Sets custom meta data attribute on pub meta data
# ------------------------------------------------------------------------------
def setCustomMetaDataAttribute(izPubMetaData, namespace, attrName, attrValue):
    if not attrName:
        return
    izCustomMetaData = izPubMetaData.getCustomMetaData(namespace) #$NON-NLS-1$
    if attrValue is None:
        izCustomMetaData.removeAttribute(attrName)
    else:
        izCustomMetaData.setAttribute(attrName, attrValue)
# end  setCustomMetaDataAttribute

# ------------------------------------------------------------------------------
# Returns WordPress custom meta data attribute from pub meta data
# ------------------------------------------------------------------------------
def getCustomWPMetaDataAttribute(izPubMetaData, attrName):
    # WP custom data
    return getCustomMetaDataAttribute(izPubMetaData, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE, attrName) #$NON-NLS-1$
# end getCustomWPMetaDataAttribute

# ------------------------------------------------------------------------------
# Sets WordPress custom meta data attribute on pub meta data
# ------------------------------------------------------------------------------
def setCustomWPMetaDataAttribute(izPubMetaData, attrName, attrValue):
    setCustomMetaDataAttribute(izPubMetaData, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE, attrName, attrValue)
# end  setCustomWPMetaDataAttribute

# ------------------------------------------------------------------------------
# Returns WordPress ns data from publish-info
# ------------------------------------------------------------------------------
def getWPPublishedInfoAttribute(izPublishedInfo, attrName):
    value = izPublishedInfo.getAttribute(attrName, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE)
    return value
# end getWPBlogInfoAttribute

