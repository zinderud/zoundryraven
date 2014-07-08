
# ------------------------------------------------------------------------------
# An interface that all search filters must extend.
# ------------------------------------------------------------------------------
class IZSearchFilter:

    SORT_ORDER_ASC = u"ASC" #$NON-NLS-1$
    SORT_ORDER_DESC = u"DESC" #$NON-NLS-1$

    def matches(self, ido):
        u"Returns True if the given index data object matches this filter." #$NON-NLS-1$
    # end matches()

    def getSortOrder(self):
        u"Returns the order in which to sort the result." #$NON-NLS-1$
    # end getSortOrder()

    def getSortBy(self):
        u"Returns the field that should be used to sort by." #$NON-NLS-1$
    # end getSortBy()

    def clone(self):
        u"Returns a copy of the filter." #$NON-NLS-1$
    # end clone()

# end IZSearchFilter


# ------------------------------------------------------------------------------
# Extends the search filter interface to provide some common methods for
# search filters that deal with information related to blogs and blog accounts.
# ------------------------------------------------------------------------------
class IZBlogBasedSearchFilter(IZSearchFilter):

    UNPUBLISHED_ACCOUNT_ID = u"__unpublished__" #$NON-NLS-1$
    UNPUBLISHED_BLOG_ID = u"__unpublished__" #$NON-NLS-1$
    UNPUBLISHED_POSTS = u"__unpublished_drafted__" #pitchaimuthu

    def getAccountIdCriteria(self):
        u"Returns the account id used to narrow the search results." #$NON-NLS-1$
    # end getAccountIdCriteria()

    def getBlogIdCriteria(self):
        u"Returns the blog id used to narrow the search results." #$NON-NLS-1$
    # end getBlogIdCriteria()

    def getBlogEntryIdCriteria(self):
        u"Returns the published data blog-entry id used to narrow the search results." #$NON-NLS-1$
    # end getBlogEntryIdCriteria()

# end IZBlogBasedSearchFilter


# ------------------------------------------------------------------------------
# An interface that all document search filters must implement.  A document
# search filter is used by the index to define what documents to search for.
# ------------------------------------------------------------------------------
class IZDocumentSearchFilter(IZBlogBasedSearchFilter):

    SORT_BY_TITLE = u"Title" #$NON-NLS-1$
    SORT_BY_CREATION_TIME = u"CreationTime" #$NON-NLS-1$
    SORT_BY_MODIFIED_TIME = u"LastModifiedTime" #$NON-NLS-1$

    def getTitleCriteria(self):
        u"Returns the title criteria used to narrow the search results." #$NON-NLS-1$
    # end getTitleCriteria()

    def getCreationTimeStartCriteria(self):
        u"Returns the start of the creation-time period criteria." #$NON-NLS-1$
    # end getCreationTimeStartCriteria()

    def getCreationTimeEndCriteria(self):
        u"Returns the end of the creation-time period criteria." #$NON-NLS-1$
    # end getCreationTimeEndCriteria()

    def getLastModifiedTimeStartCriteria(self):
        u"Returns the start of the creation-time period criteria." #$NON-NLS-1$
    # end getLastModifiedTimeStartCriteria()

    def getLastModifiedTimeEndCriteria(self):
        u"Returns the end of the creation-time period criteria." #$NON-NLS-1$
    # end getLastModifiedTimeEndCriteria()

    def getDraftCriteria(self):
        u"Returns the draft flag value to use to narrow the search results." #$NON-NLS-1$
    # end getDraftCriteria()

    def getImageURLCriteria(self):
        u"Returns the image URL criteria to use to narrow the search results." #$NON-NLS-1$
    # end getImageURLCriteria()

    def getLinkURLCriteria(self):
        u"Returns the image URL criteria to use to narrow the search results." #$NON-NLS-1$
    # end getLinkURLCriteria()

    def getTagIdCriteria(self):
        u"Returns the tag id criteria to use to narrow the search results." #$NON-NLS-1$
    # end getTagIdCriteria()
# end IZDocumentSearchFilter


# ------------------------------------------------------------------------------
# An interface that all image search filters must implement.  An image
# search filter is used by the index to define what images to search for.
# ------------------------------------------------------------------------------
class IZImageSearchFilter(IZBlogBasedSearchFilter):

    SORT_BY_HOST = u"Host" #$NON-NLS-1$

    def getHostCriteria(self):
        u"Returns the host criteria used to narrow the search results." #$NON-NLS-1$
    # end getHostCriteria()

# end IZImageSearchFilter


# ------------------------------------------------------------------------------
# An interface that all link search filters must implement.  An link
# search filter is used by the index to define what links to search for.
# ------------------------------------------------------------------------------
class IZLinkSearchFilter(IZBlogBasedSearchFilter):

    SORT_BY_HOST = u"Host" #$NON-NLS-1$

    def getHostCriteria(self):
        u"Returns the host criteria used to narrow the search results." #$NON-NLS-1$
    # end getHostCriteria()

# end IZLinkSearchFilter

# ------------------------------------------------------------------------------
# An interface that all tag search filters must implement.  A tag
# search filter is used by the index to define what tag to search for.
# ------------------------------------------------------------------------------
class IZTagSearchFilter(IZBlogBasedSearchFilter):

    SORT_BY_TAG = u"TagWord" #$NON-NLS-1$

    def getTagCriteria(self):
        u"Returns the tagword criteria used to narrow the search results." #$NON-NLS-1$
    # end getTagCriteria()
# end IZTagSearchFilter

# ------------------------------------------------------------------------------
# An interface for returning a data object for Document publishing data.  Each
# document IDO may have 0 or more instances of IZPubDataIDO.
# ------------------------------------------------------------------------------
class IZPubDataIDO:

    def getAccountId(self):
        u"Returns the account id." #$NON-NLS-1$
    # end getAccountId()

    def getBlogId(self):
        u"Returns the blog id." #$NON-NLS-1$
    # end getBlogId()

    def getBlogEntryId(self):
        u"Returns the blog entry id." #$NON-NLS-1$
    # end getBlogEntryId()

    def getPublishedTime(self):
        u"Returns the issued time." #$NON-NLS-1$
    # end getPublishedTime()

    def getSynchTime(self):
        u"Returns the synch time." #$NON-NLS-1$
    # end getSynchTime()

    def getDraft(self):
        # FIXME rename to isDraft()
        u"Returns the draft flag." #$NON-NLS-1$
    # end getDraft()

    def getUrl(self):
        u"Returns the permalink." #$NON-NLS-1$
    # end getUrl()

# end IZPubDataIDO


# ------------------------------------------------------------------------------
# An interface for returning a data object that can be associated with a blog.
# ------------------------------------------------------------------------------
class IZBlogBasedIDO:

    def getPubDataIDOs(self):
        u"Gets a list of all IZPubDataIDO objects associated with this blog based IDO." #$NON-NLS-1$
    # end getPubDataIDOs()

    def getPubDataIDO(self, blogId):
        u"Gets the IZPubDataIDO instance for the given blog (if any)." #$NON-NLS-1$
    # end getPubDataIDO()

    def getAccountIds(self):
        u"Gets a list of account ids for the data object (due to the 1-many mapping of document to account)." #$NON-NLS-1$
    # end getAccountIds()

    def getBlogIds(self):
        u"Gets a list of blog ids for the data object (due to the 1-many mapping of document to blogs)." #$NON-NLS-1$
    # end getBlogIds()

    def getBlogEntryIds(self):
        u"Gets a list of blog entry IDs for the data object." #$NON-NLS-1$
    # end getBlogEntryIds()

# end IZBlogBasedIDO


# ------------------------------------------------------------------------------
# An interface for returning link data from the index.
# ------------------------------------------------------------------------------
class IZLinkIDO(IZBlogBasedIDO):

    def getDocumentId(self):
        u"Gets the document id of the document that owns this link." #$NON-NLS-1$
    # end getUrl()

    def getUrl(self):
        u"Gets the link's url." #$NON-NLS-1$
    # end getUrl()

    def getHost(self):
        u"Gets the link's host." #$NON-NLS-1$
    # end getHost()

    def getPath(self):
        u"Gets the link's path." #$NON-NLS-1$
    # end getPath()

    def getRel(self):
        u"Gets the link's rel." #$NON-NLS-1$
    # end getRel()

    def getTitle(self):
        u"Gets the link's title." #$NON-NLS-1$
    # end getTitle()

    def getContent(self):
        u"Gets the link's content." #$NON-NLS-1$
    # end getContent()

    def getHitCount(self):
        u"Gets the link's hit count." #$NON-NLS-1$
    # end getHitCount()

# end IZLinkIDO


# ------------------------------------------------------------------------------
# An interface for returning tag data from the index.
# ------------------------------------------------------------------------------
class IZTagIDO:

    def getDocumentId(self):
        u"Gets the document id of the document that owns this tag." #$NON-NLS-1$
    # end getUrl()

    def getId(self):
        u"Gets the tag's id." #$NON-NLS-1$
    # end getId()

    def getTagword(self):
        u"Gets the tagword." #$NON-NLS-1$
    # end getTagword()

# end IZTagIDO


# ------------------------------------------------------------------------------
# An interface for returning image data from the index.
# ------------------------------------------------------------------------------
class IZImageIDO(IZBlogBasedIDO):

    def getDocumentId(self):
        u"""getDocumentId() -> string
        Gets the document id of the document that owns this
        image.""" #$NON-NLS-1$
    # end getUrl()

    def getUrl(self):
        u"""getUrl() -> string
        Gets the image's url.""" #$NON-NLS-1$
    # end getUrl()

    def getHost(self):
        u"""getHost() -> string
        Gets the link's host.""" #$NON-NLS-1$
    # end getHost()

    def getPath(self):
        u"""getPath() -> string
        Gets the link's path.""" #$NON-NLS-1$
    # end getPath()

    def getTitle(self):
        u"""getTitle() -> string
        Gets the image's title.""" #$NON-NLS-1$
    # end getTitle()

    def getHitCount(self):
        u"""getHitCount() -> int
        Gets the image's hit count.""" #$NON-NLS-1$
    # end getHitCount()

# end IZImageIDO


# ------------------------------------------------------------------------------
# An interface for returning document data from the index.
# ------------------------------------------------------------------------------
class IZDocumentIDO(IZBlogBasedIDO):

    def getId(self):
        u"""getId() -> string
        Gets the document id.""" #$NON-NLS-1$
    # end getId()

    def getTitle(self):
        u"""getTitle() -> stirng
        Gets the document's title.""" #$NON-NLS-1$
    # end getTitle()

    def getCreationTime(self):
        u"""getCreationTime() -> ZSchemaDateTime
        Gets the document's creation-time.  This is a convenience
        method, and works if there is only a single pub data IDO
        in the list.""" #$NON-NLS-1$
    # end getCreationTime()

    def getLastModifiedTime(self):
        u"""getLastModifiedTime() -> ZSchemaDateTime
        Gets the document's last-modified-time.  This is a convenience
        method, and works if there is only a single pub data IDO in
        the list.""" #$NON-NLS-1$
    # end getLastModifiedTime()

    def getPublishedTime(self):
        u"""getPublishedTime() -> ZSchemaDateTime
        Gets the time that the document was last 'published'.
        This is a convenience method, and works if there is only a
        single pub data IDO in the list.""" #$NON-NLS-1$
    # end getPublishedTime()

    def getAuthors(self):
        u"""getAuthors() -> string[]
        Returns a list of authors of this document.  This is a
        convenience method, and works if there is only a single
        pub data IDO in the list.""" #$NON-NLS-1$
    # end getAuthors()

    # FIXME (EPW) parameterize all of the "single pub data" convenience methods with the blog id/blog
    def isDraft(self):
        u"""isDraft() -> boolean
        Returns true if this is a draft.  This is a convenience
        method, and works if there is only a single pub data IDO
        in the list.""" #$NON-NLS-1$
    # end isDraft()

    def getUrl(self):
        u"""getUrl() -> string
        Returns the perma-link of this document.  This is a
        convenience method, and works if there is only a single
        pub data IDO in the list.""" #$NON-NLS-1$
    # end getUrl()

    def getSynchTime(self):
        u"""getSynchTime() -> ZSchemaDateTime
        Gets the time that the document was last 'synched' with
        the blog application (used to calculate 'dirty' status).
        This is a convenience method, and works if there is only a
        single pub data IDO in the list.""" #$NON-NLS-1$
    # end getSynchTime()

# end IZDocumentIDO
