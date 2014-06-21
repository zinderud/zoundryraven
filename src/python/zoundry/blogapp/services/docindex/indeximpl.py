from zoundry.blogapp.services.docindex.index import IZTagSearchFilter
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.services.docindex.index import IZBlogBasedIDO
from zoundry.blogapp.services.docindex.index import IZBlogBasedSearchFilter
from zoundry.blogapp.services.docindex.index import IZDocumentIDO
from zoundry.blogapp.services.docindex.index import IZDocumentSearchFilter
from zoundry.blogapp.services.docindex.index import IZImageIDO
from zoundry.blogapp.services.docindex.index import IZImageSearchFilter
from zoundry.blogapp.services.docindex.index import IZLinkIDO
from zoundry.blogapp.services.docindex.index import IZLinkSearchFilter
from zoundry.blogapp.services.docindex.index import IZPubDataIDO
from zoundry.blogapp.services.docindex.index import IZSearchFilter
from zoundry.blogapp.services.docindex.index import IZTagIDO

# ------------------------------------------------------------------------------
# Base class for search filter impls.
# ------------------------------------------------------------------------------
class ZSearchFilter(IZSearchFilter):

    def __init__(self):
        self.sortBy = IZDocumentSearchFilter.SORT_BY_CREATION_TIME
        self.sortOrder = IZSearchFilter.SORT_ORDER_DESC
    # end __init__()

    def getSortOrder(self):
        return self.sortOrder
    # end getSortOrder()

    def setSortOrder(self, sortOrder):
        self.sortOrder = sortOrder
    # end setSortOrder()

    def getSortBy(self):
        return self.sortBy
    # end getSortBy()

    def setSortBy(self, sortBy):
        self.sortBy = sortBy
    # end setSortBy()

# end ZSearchFilter


# ------------------------------------------------------------------------------
# Base class for search filter impls that include blog information/criteria.
# ------------------------------------------------------------------------------
class ZBlogBasedSearchFilter(ZSearchFilter, IZBlogBasedSearchFilter):

    def __init__(self):
        ZSearchFilter.__init__(self)

        self.accountId = None
        self.blogId = None
        self.blogEntryId = None
    # end __init__()

    def clone(self):
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"clone") #$NON-NLS-1$
    # end clone()

    def getAccountIdCriteria(self):
        return self.accountId
    # end getAccountIdCriteria()

    def setAccountIdCriteria(self, accountId):
        self.accountId = accountId
    # end setAccountIdCriteria()

    def getBlogIdCriteria(self):
        return self.blogId
    # end getBlogIdCriteria()

    def setBlogIdCriteria(self, blogId):
        self.blogId = blogId
    # end setBlogIdCriteria()

    def getBlogEntryIdCriteria(self):
        return self.blogEntryId

    def setBlogEntryIdCriteria(self, entryId):
        self.blogEntryId = entryId

    def matches(self, ido):
        isMatch = True
        accountIds = ido.getAccountIds()
        blogIds = ido.getBlogIds()
        # If the accountId is set to "unpublished"
        if self.accountId == IZBlogBasedSearchFilter.UNPUBLISHED_ACCOUNT_ID:
            if accountIds is not None and len(accountIds) > 0:
                isMatch = False
        # If the accountId is set to some actual account
        elif self.accountId is not None:
            if not accountIds:
                isMatch = False
            elif not self.accountId in accountIds:
                isMatch = False

        # If the blogId is set to "unpublished"
        if self.blogId == IZBlogBasedSearchFilter.UNPUBLISHED_BLOG_ID:
            if blogIds is not None and len(blogIds) > 0:
                isMatch = False
        # If the blogId is set to some actual blog
        elif self.blogId is not None:
            if not blogIds:
                isMatch = False
            elif not self.blogId in blogIds:
                isMatch = False

        return isMatch
    # end matches()

# end ZBlogBasedSearchFilter


# ------------------------------------------------------------------------------
# An implementation of a document search filter.
# ------------------------------------------------------------------------------
class ZDocumentSearchFilter(ZBlogBasedSearchFilter, IZDocumentSearchFilter):

    def __init__(self):
        ZBlogBasedSearchFilter.__init__(self)

        self.title = None
        self.creationTimeStart = None
        self.creationTimeEnd = None
        self.lastModifiedTimeStart = None
        self.lastModifiedTimeEnd = None
        self.draft = None
        self.imageURL = None
        self.linkURL = None
        self.tagId = None
        self.setSortBy(IZDocumentSearchFilter.SORT_BY_CREATION_TIME)
        self.setSortOrder(IZSearchFilter.SORT_ORDER_DESC)
    # end __init__()

    def clone(self):
        newFilter = ZDocumentSearchFilter()
        newFilter.title = self.title
        newFilter.creationTimeStart = self.creationTimeStart
        newFilter.creationTimeEnd = self.creationTimeEnd
        newFilter.lastModifiedTimeStart = self.lastModifiedTimeStart
        newFilter.lastModifiedTimeEnd = self.lastModifiedTimeEnd
        newFilter.accountId = self.accountId
        newFilter.blogId = self.blogId
        newFilter.blogEntryId = self.blogEntryId
        newFilter.draft = self.draft
        newFilter.imageURL = self.imageURL
        newFilter.linkURL = self.linkURL
        newFilter.tagId = self.tagId
        newFilter.sortBy = self.sortBy
        newFilter.sortOrder = self.sortOrder
        return newFilter
    # end clone()

    def getTitleCriteria(self):
        return self.title
    # end getTitleCriteria()

    def setTitleCriteria(self, title):
        self.title = title
    # end setTitleCriteria()

    def getCreationTimeStartCriteria(self):
        return self.creationTimeStart
    # end getCreationTimeStartCriteria()

    def setCreationTimeStartCriteria(self, creationTimeStart):
        self.creationTimeStart = creationTimeStart
    # end setCreationTimeStartCriteria()

    def getCreationTimeEndCriteria(self):
        return self.creationTimeEnd
    # end getCreationTimeEndCriteria()

    def setCreationTimeEndCriteria(self, creationTimeEnd):
        self.creationTimeEnd = creationTimeEnd
    # end setCreationTimeEndCriteria()

    def getLastModifiedTimeStartCriteria(self):
        return self.lastModifiedTimeStart
    # end getLastModifiedTimeStartCriteria()

    def setLastModifiedTimeStartCriteria(self, lastModifiedTimeStart):
        self.lastModifiedTimeStart = lastModifiedTimeStart
    # end setLastModifiedTimeStartCriteria()

    def getLastModifiedTimeEndCriteria(self):
        return self.lastModifiedTimeEnd
    # end getLastModifiedTimeEndCriteria()

    def setLastModifiedTimeEndCriteria(self, lastModifiedTimeEnd):
        self.lastModifiedTimeEnd = lastModifiedTimeEnd
    # end setLastModifiedTimeEndCriteria()

    def getDraftCriteria(self):
        return self.draft
    # end getDraftCriteria()

    def setDraftCriteria(self, draft):
        self.draft = draft
    # end setDraftCriteria()

    def getImageURLCriteria(self):
        return self.imageURL
    # end getImageURLCriteria()

    def setImageURLCriteria(self, imageURL):
        self.imageURL = imageURL
    # end setImageURLCriteria()

    def getLinkURLCriteria(self):
        return self.linkURL
    # end getLinkURLCriteria()

    def setLinkURLCriteria(self, linkURL):
        self.linkURL = linkURL
    # end setLinkURLCriteria()

    def getTagIdCriteria(self):
        return self.tagId
    # end getTagIdCriteria()
    
    def setTagIdCriteria(self, tagId):
        self.tagId = tagId
    # end setTagIdCriteria()

    def matches(self, documentIDO):
        isMatch = ZBlogBasedSearchFilter.matches(self, documentIDO)
        if self.title and not self.title in documentIDO.getTitle():
            isMatch = False
        elif self.creationTimeStart and documentIDO.getCreationTime() < self.creationTimeStart:
            isMatch = False
        elif self.creationTimeEnd and documentIDO.getCreationTime() > self.creationTimeEnd:
            isMatch = False
        elif self.lastModifiedTimeStart and documentIDO.getLastModifiedTime() < self.lastModifiedTimeStart:
            isMatch = False
        elif self.lastModifiedTimeEnd and documentIDO.getLastModifiedTime() > self.lastModifiedTimeEnd:
            isMatch = False
        # FIXME (EPW) ... isDraft()
        elif self.draft and not documentIDO.isDraft() == self.draft:
            isMatch = False
        return isMatch
    # end matches()

# end ZDocumentSearchFilter

DOCUMENT_FILTER_ALL = ZDocumentSearchFilter()


# ------------------------------------------------------------------------------
# An implementation of a link search filter.
# ------------------------------------------------------------------------------
class ZLinkSearchFilter(ZBlogBasedSearchFilter, IZLinkSearchFilter):

    def __init__(self):
        ZBlogBasedSearchFilter.__init__(self)

        self.documentId = None
        self.host = None
        self.setSortBy(IZLinkSearchFilter.SORT_BY_HOST)
        self.setSortOrder(IZSearchFilter.SORT_ORDER_ASC)
    # end __init__()

    def clone(self):
        newFilter = ZLinkSearchFilter()
        newFilter.accountId = self.accountId
        newFilter.blogId = self.blogId
        newFilter.documentId = self.documentId
        newFilter.host = self.host
        return newFilter
    # end clone()

    def getDocumentIdCriteria(self):
        return self.documentId
    # end getDocumentIdCriteria()

    def setDocumentIdCriteria(self, documentId):
        self.documentId = documentId
    # end setDocumentIdCriteria()

    def getHostCriteria(self):
        return self.host
    # end getHostCriteria()

    def setHostCriteria(self, host):
        self.host = host
    # end setHostCriteria()

    def matches(self, linkIDO):
        isMatch = ZBlogBasedSearchFilter.matches(self, linkIDO)
        if self.documentId and not linkIDO.getDocumentId() == self.documentId:
            isMatch = False
        elif self.host and not self.host in linkIDO.getHost():
            isMatch = False
        return isMatch
    # end matches()

# end ZLinkSearchFilter

LINK_FILTER_ALL = ZLinkSearchFilter()


# ------------------------------------------------------------------------------
# An implementation of an image search filter.
# ------------------------------------------------------------------------------
class ZImageSearchFilter(ZBlogBasedSearchFilter, IZImageSearchFilter):

    def __init__(self):
        ZBlogBasedSearchFilter.__init__(self)

        self.documentId = None
        self.host = None
        self.setSortBy(IZImageSearchFilter.SORT_BY_HOST)
        self.setSortOrder(IZSearchFilter.SORT_ORDER_ASC)
    # end __init__()

    def clone(self):
        newFilter = ZImageSearchFilter()
        newFilter.accountId = self.accountId
        newFilter.blogId = self.blogId
        newFilter.documentId = self.documentId
        newFilter.host = self.host
        return newFilter
    # end clone()

    def getDocumentIdCriteria(self):
        return self.documentId
    # end getDocumentIdCriteria()

    def setDocumentIdCriteria(self, documentId):
        self.documentId = documentId
    # end setDocumentIdCriteria()

    def getHostCriteria(self):
        return self.host
    # end getHostCriteria()

    def setHostCriteria(self, host):
        self.host = host
    # end setHostCriteria()

    def matches(self, imageIDO):
        isMatch = ZBlogBasedSearchFilter.matches(self, imageIDO)
        if self.documentId and not imageIDO.getDocumentId() == self.documentId:
            isMatch = False
        elif self.host and not self.host in imageIDO.getHost():
            isMatch = False
        return isMatch
    # end matches()

# end ZImageSearchFilter

IMAGE_FILTER_ALL = ZImageSearchFilter()


# ------------------------------------------------------------------------------
# An implementation of an tag search filter.
# ------------------------------------------------------------------------------
class ZTagSearchFilter(ZBlogBasedSearchFilter, IZTagSearchFilter):

    def __init__(self):
        ZBlogBasedSearchFilter.__init__(self)
        self.documentId = None
        self.tagword = None
        self.setSortBy(IZTagSearchFilter.SORT_BY_TAG)
        self.setSortOrder(IZSearchFilter.SORT_ORDER_ASC)
    # end __init__()

    def clone(self):
        newFilter = ZTagSearchFilter()
        newFilter.accountId = self.accountId
        newFilter.blogId = self.blogId
        newFilter.documentId = self.documentId
        newFilter.tagword = self.tagword
        return newFilter
    # end clone()

    def getDocumentIdCriteria(self):
        return self.documentId
    # end getDocumentIdCriteria()

    def setDocumentIdCriteria(self, documentId):
        self.documentId = documentId
    # end setDocumentIdCriteria()

    def getTagCriteria(self):
        return self.tagword
    # end getHostCriteria()

    def setTagCriteria(self, tagword):
        self.tagword = tagword
    # end setHostCriteria()

    def matches(self, tagIDO):
        isMatch = ZBlogBasedSearchFilter.matches(self, tagIDO)
        if self.documentId and not tagIDO.getDocumentId() == self.documentId:
            isMatch = False
        elif self.tagword and not self.tagword == tagIDO.getTagword():
            isMatch = False
        return isMatch
    # end matches()

# end ZTagSearchFilter

TAG_FILTER_ALL = ZTagSearchFilter()

# ------------------------------------------------------------------------------
# An implementation of a pub data IDO object.
# ------------------------------------------------------------------------------
class ZPubDataIDO(IZPubDataIDO):

    def __init__(self, accountId = None, blogId = None, blogEntryId = None, publishedTime = None, synchTime = None, draft = None, url = None):
        self.accountId = accountId
        self.blogId = blogId
        self.blogEntryId = blogEntryId
        self.publishedTime = publishedTime
        self.synchTime = synchTime
        self.draft = draft
        self.url = url
    # end __init__()

    def getAccountId(self):
        return self.accountId
    # end getAccountId()

    def getBlogId(self):
        return self.blogId
    # end getBlogId()

    def getBlogEntryId(self):
        return self.blogEntryId
    # end getBlogEntryId()

    def getPublishedTime(self):
        return self.publishedTime
    # end getPublishedTime()

    def getSynchTime(self):
        return self.synchTime
    # end getSynchTime()

    def getDraft(self):
        return self.draft
    # end getDraft()

    def getUrl(self):
        return self.url
    # end getUrl()

# end ZPubDataIDO


# ------------------------------------------------------------------------------
# Base class for IDO impls that contain blog and account info.
# ------------------------------------------------------------------------------
class ZBlogBasedIDO(IZBlogBasedIDO):

    def __init__(self, pubDataIDOs = None):
        self.pubDataIDOs = pubDataIDOs

        if not self.pubDataIDOs:
            self.pubDataIDOs = []
    # end __init__()

    def getPubDataIDOs(self):
        return self.pubDataIDOs
    # end getPubDataIDOs()

    def getPubDataIDO(self, blogId):
        for pdIDO in self.pubDataIDOs:
            if pdIDO.getBlogId() == blogId:
                return pdIDO
        return None
    # end getPubDataIDO()

    def getAccountIds(self):
        accountIds = []
        for pubDataIDO in self.pubDataIDOs:
            accountIds.append(pubDataIDO.getAccountId())
        return accountIds
    # end getAccountIds()

    def getBlogIds(self):
        blogIds = []
        for pubDataIDO in self.pubDataIDOs:
            blogIds.append(pubDataIDO.getBlogId())
        return blogIds
    # end getBlogIds()

    def getBlogEntryIds(self):
        blogEntryIds = []
        for pubDataIDO in self.pubDataIDOs:
            blogEntryIds.append(pubDataIDO.getBlogEntryId())
        return blogEntryIds
    # end getBlogEntryIds()

    def addPubDataIDO(self, pubDataIDO):
        self.pubDataIDOs.append(pubDataIDO)
    # end addPubDataIDO()

    def setPubDataIDOs(self, pubDataIDOs):
        self.pubDataIDOs = pubDataIDOs
    # end setPubDataIDOs()

    def _hasPubData(self):
        return self.pubDataIDOs is not None and len(self.pubDataIDOs) > 0
    # end _hasPubData()

    def _getSinglePubData(self):
        # If there are no pub datas, return an empty one.
        if not self._hasPubData():
            return IZPubDataIDO()
        # If there is exactly one pub data, return it.
        if len(self.pubDataIDOs) == 1:
            return self.pubDataIDOs[0]

        raise ZBlogAppException(u"Illegal attempt to treat a IZDocumentIDO as a reference to a single published Document (multiple pubData objects found).") #$NON-NLS-1$
    # end _getSinglePubData()

# end ZBlogBasedIDO


# ------------------------------------------------------------------------------
# An implementation of a link 'index data object'.
# ------------------------------------------------------------------------------
class ZLinkIDO(ZBlogBasedIDO, IZLinkIDO):

    def __init__(self, pubDataIDOs = None, documentId = None, url = None, host = None, path = None, rel = None, title = None, content = None, hitCount = 0):
        ZBlogBasedIDO.__init__(self, pubDataIDOs)

        self.documentId = documentId
        self.url = url
        self.host = host
        self.path = path
        self.rel = rel
        self.title = title
        self.content = content
        self.hitCount = hitCount
    # end __init__()

    def getDocumentId(self):
        return self.documentId
    # end getUrl()

    def getUrl(self):
        return self.url
    # end getUrl()

    def getHost(self):
        return self.host
    # end getHost()

    def getPath(self):
        return self.path
    # end getPath()

    def getRel(self):
        return self.rel
    # end getRel()

    def getTitle(self):
        return self.title
    # end getTitle()

    def getContent(self):
        return self.content
    # end getContent()

    def getHitCount(self):
        return self.hitCount
    # end getHitCount()

# end ZLinkIDO


# ------------------------------------------------------------------------------
# An implementation of a tag 'index data object'.
# ------------------------------------------------------------------------------
class ZTagIDO(ZBlogBasedIDO, IZTagIDO):

    def __init__(self, pubDataIDOs = None, documentId = None, id = None, tagword = None):
        ZBlogBasedIDO.__init__(self, pubDataIDOs)
        self.documentId = documentId
        self.id = id
        self.tagword = tagword
    # end __init__()

    def getDocumentId(self):
        return self.documentId
    # end getUrl()

    def getId(self):
        return self.id
    # end getId()

    def getTagword(self):
        return self.tagword
    # end getTagword()

# end ZTagIDO


# ------------------------------------------------------------------------------
# An implementation of an image 'index data object'.
# ------------------------------------------------------------------------------
class ZImageIDO(ZBlogBasedIDO, IZImageIDO):

    def __init__(self, pubDataIDOs = None, documentId = None, url = None, host = None, path = None, title = None, hitCount = 0):
        ZBlogBasedIDO.__init__(self, pubDataIDOs)

        self.documentId = documentId
        self.url = url
        self.host = host
        self.path = path
        self.title = title
        self.hitCount = hitCount
    # end __init__()

    def getDocumentId(self):
        return self.documentId
    # end getUrl()

    def getUrl(self):
        return self.url
    # end getUrl()

    def getHost(self):
        return self.host
    # end getHost()

    def getPath(self):
        return self.path
    # end getPath()

    def getTitle(self):
        return self.title
    # end getTitle()

    def getHitCount(self):
        return self.hitCount
    # end getHitCount()

# end ZImageIDO


# ------------------------------------------------------------------------------
# An implementation of a document 'index data object'.
# ------------------------------------------------------------------------------
class ZDocumentIDO(ZBlogBasedIDO, IZDocumentIDO):

    def __init__(self, pubDataIDOs = None, id = None, title = None, creationTime = None, lastModifiedTime = None):
        ZBlogBasedIDO.__init__(self, pubDataIDOs)

        self.id = id
        self.title = title
        self.creationTime = creationTime
        self.lastModifiedTime = lastModifiedTime
    # end __init__()

    def getId(self):
        return self.id
    # end getId()

    def getTitle(self):
        return self.title
    # end getTitle()

    def getCreationTime(self):
        return self.creationTime
    # end getCreationTime()

    def getLastModifiedTime(self):
        return self.lastModifiedTime
    # end getLastModifiedTime()

    def getPublishedTime(self):
        pubData = self._getSinglePubData()
        return pubData.getPublishedTime()
    # end getPublishedTime()

    def getAuthors(self):
        return None
    # end getAuthors()

    def isDraft(self):
        pubData = self._getSinglePubData()
        return pubData.getDraft()
    # end isDraft()

    def getUrl(self):
        pubData = self._getSinglePubData()
        return pubData.getUrl()
    # end getUrl()

    def getSynchTime(self):
        pubData = self._getSinglePubData()
        return pubData.getSynchTime()
    # end getSynchTime()

# end ZDocumentIDO
