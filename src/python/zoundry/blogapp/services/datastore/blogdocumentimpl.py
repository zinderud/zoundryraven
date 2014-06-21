from zoundry.base.util.dateutil import getNoneDate
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.types.attrmodel import ZModelWithAttributes
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.services.datastore.blogdocument import IZBlogDocument
from zoundry.blogapp.services.datastore.blogdocument import IZBlogInfo
from zoundry.blogapp.services.datastore.blogdocument import IZCustomMetaData
from zoundry.blogapp.services.datastore.blogdocument import IZPubMetaData
from zoundry.blogapp.services.datastore.blogdocument import IZPublishInfo
from zoundry.blogapp.services.datastore.blogdocument import IZTagwords
from zoundry.blogapp.services.datastore.blogdocument import IZTrackback
from zoundry.blogapp.services.datastore.blogdocument import IZWeblogPingSite
from zoundry.blogapp.services.datastore.documentimpl import ZDocument

# ------------------------------------------------------------------------------
# Trackback.
# ------------------------------------------------------------------------------
class ZTrackback(ZModelWithAttributes, IZTrackback):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
    # end __init__()

    def getUrl(self):
        return self.getAttribute(u"url") #$NON-NLS-1$
    # end getUrl()

    def setUrl(self, url):
        self.setAttribute(u"url", url) #$NON-NLS-1$
    # end setUrl()

    def isSent(self):
        return self.getSentDate() is not None
    # end isSent

    def setSentDate(self, sentDate):
        u"setSentDate(ZSchemaDateTime) -> void" #$NON-NLS-1$
        self.setAttribute(u"sent-date", unicode(sentDate)) #$NON-NLS-1$
    # end setSentDate

    def getSentDate(self):
        u"getSentDate() -> ZSchemaDateTime" #$NON-NLS-1$
        dt = self.getAttribute(u"sent-date") #$NON-NLS-1$
        return getNoneDate( dt )
    # end getSentDate

# end ZTrackback

# ------------------------------------------------------------------------------
# Weblog ping
# ------------------------------------------------------------------------------
class ZWeblogPingSite(ZModelWithAttributes, IZWeblogPingSite):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
    # end __init__()

    def getName(self):
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def getUrl(self):
        return self.getAttribute(u"url") #$NON-NLS-1$
    # end getUrl()

# end ZWeblogPingSite


# ------------------------------------------------------------------------------
# The Tagwords.
# ------------------------------------------------------------------------------
class ZTagwords(IZTagwords):

    def __init__(self):
        self.url = None
        self.wordList = []
    # end __init__()

    def getUrl(self):
        return self.url
    # end getUrl()

    def setUrl(self, url):
        self.url = url
    # end setUrl()

    def getValue(self):
        # return csv string
        return u",".join( self.wordList ) #$NON-NLS-1$
    # end getValue()

    def setValue(self, value):
        # set a comma separated list of words
        self.wordList = []
        value = getNoneString(value)
        if not value:
            return
        lowerList = []
        for word in value.split(u","): #$NON-NLS-1$
            word = word.strip()
            lowerword = word.lower()
            if lowerword not in lowerList:
                lowerList.append(lowerword)
                self.wordList.append(word)
        self.wordList.sort()
    # end setValue()

    def getTagwords(self):
        # Returns a list of words
        return self.wordList
    # end getTagwords()

# end ZTagwords

# ------------------------------------------------------------------------------
# Utility class that keeps a list of unique tag words.
# ------------------------------------------------------------------------------
class ZTagwordsSet:

    def __init__(self):
        self.tagwords = []
        self.lowerList = []
    # end __init__()

    def addZTagwordObjectList(self, zTagwordObjectList):
        for zTagwordObject in zTagwordObjectList:
            self.addZTagwordObject( zTagwordObject )
    #end addZTagwordObjectList

    def addZTagwordObject(self, zTagwordObject):
        # add tags in given ZTagwords object
        self.addTagwords( zTagwordObject.getTagwords() )
    #end addZTagwordObject

    def addTagwordsCSVList(self, csvWordList):
        # adds a list of tags to a collection if they do not already exist
        self.addTagwords( csvWordList.split(u",") ) #$NON-NLS-1$
    # end addTagwordsCSVList
    #
    def addTagwords(self, wordList):
        # adds a list of tags to a collection if they do not already exist
        for word in wordList:
            word = word.strip()
            lowercase = word.lower()
            if lowercase in self.lowerList:
                continue
            self.lowerList.append(lowercase)
            self.tagwords.append(word)
    # end addTagwords

    def getTagwordsAsCSV(self):
        # returns a CSV list of words
        return u",".join(self.tagwords) #$NON-NLS-1$
    # end getTagwordsAsCSV()

    def getTagwords(self):
        return self.tagwords
    # end getTagwords()
# end ZTagwordsSet()

# ------------------------------------------------------------------------------
# The blog publishing information from a document.
# ------------------------------------------------------------------------------
class ZPublishInfo(ZModelWithAttributes, IZPublishInfo):

    def __init__(self):
        ZModelWithAttributes.__init__(self)

        self.trackbacks = []
    # end __init__()

    def getBlogEntryId(self):
        return self.getAttribute(u"blog-entry-id") #$NON-NLS-1$
    # end getBlogEntryId()

    def setBlogEntryId(self, blogEntryId):
        self.setAttribute(u"blog-entry-id", blogEntryId) #$NON-NLS-1$
    # end setBlogEntryId()

    def getPublishedTime(self):
        dt = self.getAttribute(u"published-time") #$NON-NLS-1$
        if not dt:
            dt = self.getAttribute(u"issued-date") #$NON-NLS-1$
        return getNoneDate( dt )
    # end getPublishedTime()

    def setPublishedTime(self, publishedTime):
        self.setAttribute(u"published-time", unicode(publishedTime)) #$NON-NLS-1$
    # end setPublishedTime()

    def getSynchTime(self):
        dt = self.getAttribute(u"synchronized-time") #$NON-NLS-1$
        return getNoneDate( dt )
    # end getSynchTime()

    def setSynchTime(self, synchTime):
        self.setAttribute(u"synchronized-time", unicode(synchTime)) #$NON-NLS-1$
    # end setSynchTime()

    def isDraft(self):
        return self.getAttributeBool(u"draft", None, False) #$NON-NLS-1$
    # end isDraft()

    def setDraft(self, draftFlag):
        self.setAttributeBool(u"draft", draftFlag) #$NON-NLS-1$
    # end setDraft()

    def setUrl(self, url):
        if url:
            self.setAttribute(u"url", url) #$NON-NLS-1$

    def getUrl(self):
        permalink = self.getAttribute(u"url") #$NON-NLS-1$
        if not permalink:
            permalink = self.getAttribute(u"alt-link", IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
        return permalink
    # end getUrl()

    def getTrackbacks(self):
        return self.trackbacks
    # end getTrackbacks()

    def addTrackback(self, trackback):
        if not trackback:
            return
        # check if it exists - if so, replace
        for idx in range(len(self.trackbacks)):
            tb = self.trackbacks[idx]
            if tb.getUrl() == trackback.getUrl():
                self.trackbacks[idx] = trackback
                return
        self.trackbacks.append(trackback)
    # end addTrackback()

# end ZPublishInfo


# ------------------------------------------------------------------------------
# The blog information from a document.
# ------------------------------------------------------------------------------
class ZBlogInfo(IZBlogInfo):

    def __init__(self):
        self.accountId = None
        self.blogId = None
        self.publishInfo = None
        self.categories = []
    # end __init__()

    def getAccountId(self):
        return self.accountId
    # end getAccountId()

    def setAccountId(self, accountId):
        self.accountId = accountId
    # end setAccountId()

    def getBlogId(self):
        return self.blogId
    # end getBlogId()

    def setBlogId(self, blogId):
        self.blogId = blogId
    # end setBlogId()

    def getPublishInfo(self):
        return self.publishInfo
    # end getPublishInfo()

    def setPublishInfo(self, pubInfo):
        self.publishInfo = pubInfo
    # end setPublishInfo()

    def getCategories(self):
        return self.categories
    # end getCategories()

    def addCategory(self, category):
        # FIXME (PJ) check for duplicate categories i.e. add/append vs update/replace
        exists = False
        for c in self.categories:
            if c.getId() == category.getId():
                exists = True
                break
        if not exists:
            self.categories.append(category)
    # end addCategory()

# end ZBlogInfo

# ------------------------------------------------------------------------------
# Interface to which defines data model for addtional
# custom meta data.
# ------------------------------------------------------------------------------
class ZCustomMetaData(ZModelWithAttributes, IZCustomMetaData):
    def __init__(self):
        ZModelWithAttributes.__init__(self)
    # end __init__()
# end ZCustomMetaData

# ------------------------------------------------------------------------------
# Class containing the information that the user has entered in the publishing
# dialog (or the blog post editor).
# ------------------------------------------------------------------------------
class ZPubMetaData(ZModelWithAttributes, IZPubMetaData):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
        self.categories = []
        self.pingServices = []
        self.trackbacks = []
        self.tagspaceUrls = []
        self.customMetaData = {}
    # end __init__()

    def getAccountId(self):
        return self.getAttribute(u"account-id") #$NON-NLS-1$
    # end getAccountId()

    def setAccountId(self, accountId):
        self.setAttribute(u"account-id", accountId) #$NON-NLS-1$
    # end setAccountId()

    def getBlogId(self):
        return self.getAttribute(u"blog-id") #$NON-NLS-1$
    # end getBlogId()

    def setBlogId(self, blogId):
        self.setAttribute(u"blog-id", blogId) #$NON-NLS-1$
    # end setBlogId()

    def isPublishAsDraft(self):
        return self.getAttributeBool(u"publish-as-draft", None, False) #$NON-NLS-1$
    # end isPublishAsDraft()

    def setPublishAsDraft(self, flag):
        self.setAttributeBool(u"publish-as-draft", flag) #$NON-NLS-1$
    # end setPublishAsDraft()

    def getPublishTime(self):
        return self.getAttributeDate(u"publish-time") #$NON-NLS-1$
    # end getPublishTime()

    def setPublishTime(self, pubTime):
        self.setAttribute(u"publish-time", pubTime) #$NON-NLS-1$
    # end setPublishTime()

    def isUploadTNsOnly(self):
        return self.getAttributeBool(u"upload-tns-only", None, False) #$NON-NLS-1$
    # end isUploadTNsOnly()

    def setUploadTNsOnly(self, flag):
        self.setAttributeBool(u"upload-tns-only", flag) #$NON-NLS-1$
    # end setUploadTNsOnly()

    def isForceReUploadImages(self):
        return self.getAttributeBool(u"force-img-upload", None, False) #$NON-NLS-1$
    # end isForceReUploadImages()

    def setForceReUploadImages(self, flag):
        self.setAttributeBool(u"force-img-upload", flag) #$NON-NLS-1$
    # end setForceReUploadImages()

    def isAddLightbox(self):
        return self.getAttributeBool(u"add-lightbox", None, False) #$NON-NLS-1$
    # end isAddLightbox()

    def setAddLightbox(self, flag):
        self.setAttributeBool(u"add-lightbox", flag) #$NON-NLS-1$
    # end setAddLightbox()

    def isAddPoweredBy(self):
        return self.getAttributeBool(u"add-powered-by", None, False) #$NON-NLS-1$
    # end isAddPoweredBy()

    def setAddPoweredBy(self, flag):
        self.setAttributeBool(u"add-powered-by", flag) #$NON-NLS-1$
    # end setAddPoweredBy()

    def getCategories(self):
        # return list of IZCategory objects
        return self.categories
    # end getCategories()

    def addCategory(self, category):
        # add IZCategory object
        if not category in self.categories:
            self.categories.append(category)
    # end addCategory()

    def setCategories(self, categories):
        # set list of IZCategory objects
        self.categories = categories
    # end setCategories()

    def getPingServices(self):
        # return list of IZWeblogPingSite objects
        return self.pingServices
    # end getPingServices()

    def addPingService(self, pingService):
        self.pingServices.append(pingService)
    # end addPingService()

    def setPingServices(self, pingServices):
        # sets list of IZWeblogPingSite objects
        self.pingServices = pingServices
    # end setPingServices()

    def getTrackbacks(self):
        return self.trackbacks
    # end getTrackbacks()

    def setTrackbacks(self, trackbacks):
        if trackbacks:
            self.trackbacks = trackbacks
        else:
            self.trackbacks = []
    # end setTrackbacks

    def addTrackback(self, trackback):
        if not trackback:
            return
        # check if it exists - if so, do nothing
        for tb in self.trackbacks:
            if tb.getUrl() == trackback.getUrl():
                return
        self.trackbacks.append(trackback)
    # end addTrackback()

    def getTagspaceUrls(self):
        return self.tagspaceUrls
    # end getTagspaceUrls()

    def setTagspaceUrls(self, urlList):
        self.tagspaceUrls = urlList
    # end setTagspaceUrls()

    def addTagspaceUrl(self, url):
        if url and url not in self.tagspaceUrls:
            self.tagspaceUrls.append(url)
    # end addTagspaceUrl()

    def getCustomMetaData(self, namespace):
        if namespace and self.customMetaData.has_key(namespace):
            customData = self.customMetaData[namespace]
        else:
            customData = ZCustomMetaData()
            self.customMetaData[namespace] = customData
        return customData
    #end getCustomMetaData

    def setCustomMetaData(self, namespace, izCustomMetaData):
        if namespace and izCustomMetaData:
            self.customMetaData[namespace] = izCustomMetaData
    #end setCustomMetaData

    def getCustomMetaDataNamespaces(self):
        u"""getCustomMetaDataNameSpaces()  -> string[]""" #$NON-NLS-1$
        return self.customMetaData.keys()
    # end getCustomMetaDataNamespaces()

# end ZPubMetaData


# ------------------------------------------------------------------------------
# The Zoundry Raven document impl.  Base class for all implementations of
# documents.
# ------------------------------------------------------------------------------
class ZBlogDocument(ZDocument, IZBlogDocument):

    def __init__(self):
        ZDocument.__init__(self)
        self.blogInfoList = []
        self.pubMetaDataList = []
        self.tagwordsList = []
        self.trackbacks = []
    # end __init__()

    def getTitle(self):
        return self.getAttribute(u"title") #$NON-NLS-1$
    # end getTitle()

    def setTitle(self, title):
        self.setAttribute(u"title", title) #$NON-NLS-1$
    # end setTitle()

    def getBlogInfoList(self):
        return self.blogInfoList
    # end getBlogInfoList()

    def addBlogInfo(self, blogInfo):
        replaced = False
        for idx in range( len(self.blogInfoList) ):
            tmpInfo = self.blogInfoList[idx]
            if tmpInfo.getBlogId() == blogInfo.getBlogId():
                self.blogInfoList[idx] = blogInfo
                replaced = True
                break
        if not replaced:
            self.blogInfoList.append(blogInfo)
    # end addBlogInfo()

    def setBlogInfoList(self, blogInfoList):
        self.blogInfoList = blogInfoList
    # end setBlogInfoList()

    def getBlogInfo(self, blogId):
        rval = None
        if getNoneString(blogId):
            for tmp in self.getBlogInfoList():
                if tmp.getBlogId() == blogId:
                    rval = tmp
                    break
        return rval
    # end getBlogInfo()

    def removeBlogInfo(self, blogId):
        rval = False
        if getNoneString(blogId):
            for idx in range( len(self.blogInfoList) ):
                tmpInfo = self.blogInfoList[idx]
                if tmpInfo.getBlogId() == blogId:
                    del self.blogInfoList[idx]
                    rval = True
                    break

        return rval
    #end removeBlogInfo

    def getPubMetaDataList(self):
        return self.pubMetaDataList
    # end getPubMetaDataList()

    def setPubMetaDataList(self, pubMetaDataList):
        self.pubMetaDataList = pubMetaDataList
    # end setPubMetaDataList()

    def addPubMetaData(self, pubMetaData):
        replaced = False
        for idx in range( len(self.pubMetaDataList) ):
            tmpMD = self.pubMetaDataList[idx]
            if tmpMD.getBlogId() == pubMetaData.getBlogId():
                self.pubMetaDataList[idx] = pubMetaData
                replaced = True
                break
        if not replaced:
            self.pubMetaDataList.append(pubMetaData)
    # end addPubMetaData()

    def isPublished(self):
        blogInfoList = self.getBlogInfoList()
        return blogInfoList is not None and len(blogInfoList) > 0
    # end isPublished()

    def isPublishedToBlog(self, blogId):
        rval = self.isPublished() and self.getBlogInfo(blogId) is not None
        return rval
    # end isPublishedToBlog()

    def getPublishedUrl(self, blogId):
        rval = None
        if self.isPublishedToBlog(blogId):
            pubInfo = self.getBlogInfo(blogId).getPublishInfo()
            if pubInfo is not None:
                return getNoneString( pubInfo.getUrl() )
        return rval
    # end getPublishedUrl()

    def isPublishable(self):
        pubMetaDataList = self.getPubMetaDataList()
        hasMetaData = pubMetaDataList is not None and len(pubMetaDataList) > 0
        return self.isPublished() or hasMetaData
    # end isPublishable()

    def getTagwordsList(self):
        return self.tagwordsList
    # end getTagwordsList()

    def _getTagwordsUrl(self, izTagwordsObj):
        tagUrl = None
        if izTagwordsObj and izTagwordsObj.getUrl():
            # remove trailing slashes.
            tagUrl = izTagwordsObj.getUrl().rstrip(u"/")  #$NON-NLS-1$
        return tagUrl
    # end _getTagwordsUrl

    def addTagwords(self, izTagwordsObj):
        tagUrl = self._getTagwordsUrl(izTagwordsObj)
        if not tagUrl:
            # FIXME (PJ) raise ex
            return
        # check if tagwords set already exists by comparing the url
        for idx in range( len(self.tagwordsList) ):
            tempUrl = self._getTagwordsUrl( self.tagwordsList[idx] )
            if tagUrl == tempUrl:
                # replace
                self.tagwordsList[idx] = izTagwordsObj
                return
        # add new list
        self.tagwordsList.append(izTagwordsObj)
    # end addTagwords()

    def getTagwords(self, tagspaceUrl):
        if not tagspaceUrl:
            return None
        tagspaceUrl = tagspaceUrl.rstrip(u"/")  #$NON-NLS-1$
        for idx in range( len(self.tagwordsList) ):
            tempZtagwords = self.tagwordsList[idx]
            tempUrl = self._getTagwordsUrl(tempZtagwords)
            if tagspaceUrl == tempUrl:
                return tempZtagwords
        return None
    # end IZTagwords()

    def getTrackbacks(self):
        return self.trackbacks
    # end getTrackbacks()

    def setTrackbacks(self, trackbacks):
        self.trackbacks = trackbacks
    # end setTrackbacks

    def addTrackback(self, trackback):
        # FIXME (PJ) check for duplicate trackbacks i.e. add/append vs update/replace
        self.trackbacks.append(trackback)
    # end addTrackback()
# end ZBlogDocument
