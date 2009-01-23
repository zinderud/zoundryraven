from StringIO import StringIO
from zoundry.blogapp.services.docindex.index import IZDocumentSearchFilter
import string

# ------------------------------------------------------------------------------
# An interface that all SQL query builders must implement.
# ------------------------------------------------------------------------------
class IZSQLQueryBuilder:

    def build(self):
        u"Called to build the appropriate SQL query." #$NON-NLS-1$
    # end build()

# end IZSQLQueryBuilder


# ------------------------------------------------------------------------------
# A base class for SQL Query Builders.
# ------------------------------------------------------------------------------
class ZBaseSQLQueryBuilder(IZSQLQueryBuilder):

    def __init__(self, filter):
        self.filter = filter
        self.countOnly = False
    # end __init__()

    def build(self, countOnly = False):
        self.countOnly = countOnly

        self.buffer = StringIO()
        self._build()
        rval = self.buffer.getvalue() + u"" #$NON-NLS-1$
        self.buffer.close()
        return rval
    # end build()

    def _build(self):
        self._buildSelect()
        self._buildFrom()
        self._buildWhere()
        self._buildOrderBy()
    # end _build()

    def _buildWhere(self):
        whereClauses = self._getWhereClauses()

        if len(whereClauses) > 0:
            self.buffer.write(u" WHERE ") #$NON-NLS-1$
            self.buffer.write(string.join(whereClauses, u" AND ")) #$NON-NLS-1$
    # end _buildSelect()

    def _getWhereClauses(self):
        whereClauses = []
        if self.filter.getAccountIdCriteria() is not None:
            if self.filter.getAccountIdCriteria() == IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID:
                whereClauses.append(u"pd.AccountId IS NULL") #$NON-NLS-1$
            else:
                whereClauses.append(u"pd.AccountId = '%s'" % unicode(self.filter.getAccountIdCriteria())) #$NON-NLS-1$
        if self.filter.getBlogIdCriteria() is not None:
            if self.filter.getBlogIdCriteria() == IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID:
                whereClauses.append(u"pd.BlogId IS NULL") #$NON-NLS-1$
            else:
                whereClauses.append(u"pd.BlogId = '%s'" % unicode(self.filter.getBlogIdCriteria())) #$NON-NLS-1$
        if self.filter.getBlogEntryIdCriteria() is not None:
            whereClauses.append(u"pd.BlogEntryId = '%s'" % unicode(self.filter.getBlogEntryIdCriteria())) #$NON-NLS-1$

        return whereClauses
    # end _getWhereClauses

# end ZBaseSQLQueryBuilder


# ------------------------------------------------------------------------------
# A class that builds a SQL query for finding documents based on a document
# filter.
# ------------------------------------------------------------------------------
class ZDocumentQueryBuilder(ZBaseSQLQueryBuilder):

    def __init__(self, filter):
        ZBaseSQLQueryBuilder.__init__(self, filter)
    # end __init__()

    def _buildSelect(self):
        self.buffer.write(u"SELECT ") #$NON-NLS-1$
        if self.countOnly:
            self.buffer.write(u"count(DISTINCT doc.DocumentId)") #$NON-NLS-1$
        else:
            self.buffer.write(u"*") #$NON-NLS-1$
    # end _buildSelect()

    def _buildFrom(self):
        self.buffer.write(u" FROM Document AS doc LEFT JOIN PublishedData AS pd ON doc.DocumentId = pd.DocumentId") #$NON-NLS-1$
        if self._shouldJoinImage():
            self.buffer.write(u" LEFT JOIN Image AS image ON doc.DocumentId = image.DocumentId") #$NON-NLS-1$
        if self._shouldJoinLink():
            self.buffer.write(u" LEFT JOIN Link AS link ON doc.DocumentId = link.DocumentId") #$NON-NLS-1$
        if self._shouldJoinTag():
            self.buffer.write(u" LEFT JOIN Tag AS tag ON doc.DocumentId = tag.DocumentId") #$NON-NLS-1$            
    # end _buildFrom()

    def _shouldJoinImage(self):
        return self.filter.getImageURLCriteria() is not None
    # end _shouldJoinImage()

    def _shouldJoinLink(self):
        return self.filter.getLinkURLCriteria() is not None
    # end _shouldJoinLink()

    def _shouldJoinTag(self):
        return self.filter.getTagIdCriteria() is not None
    # end _shouldJoinTag()

    def _buildOrderBy(self):
        if self.countOnly:
            return
        sortCol = self.filter.getSortBy()
        sortOrder = self.filter.getSortOrder()
        if sortCol and sortOrder:
            self.buffer.write(u" ORDER BY %s %s" % (sortCol, sortOrder)) #$NON-NLS-1$
    # end _buildOrderBy()

    def _getWhereClauses(self):
        whereClauses = ZBaseSQLQueryBuilder._getWhereClauses(self)

        if self.filter.getTitleCriteria() is not None:
            whereClauses.append(u"doc.Title LIKE '%%%s%%'" % self.filter.getTitleCriteria()) #$NON-NLS-1$
        if self.filter.getCreationTimeStartCriteria() is not None:
            whereClauses.append(u"doc.CreationTime >= '%s'" % unicode(self.filter.getCreationTimeStartCriteria())) #$NON-NLS-1$
        if self.filter.getCreationTimeEndCriteria() is not None:
            whereClauses.append(u"doc.CreationTime <= '%s'" % unicode(self.filter.getCreationTimeEndCriteria())) #$NON-NLS-1$
        if self.filter.getLastModifiedTimeStartCriteria() is not None:
            whereClauses.append(u"doc.LastModifiedTime >= '%s'" % unicode(self.filter.getLastModifiedTimeStartCriteria())) #$NON-NLS-1$
        if self.filter.getLastModifiedTimeEndCriteria() is not None:
            whereClauses.append(u"doc.LastModifiedTime <= '%s'" % unicode(self.filter.getLastModifiedTimeEndCriteria())) #$NON-NLS-1$
        if self.filter.getDraftCriteria() is not None:
            whereClauses.append(u"pd.Draft = %d" % self.filter.getDraftCriteria()) #$NON-NLS-1$
        if self.filter.getImageURLCriteria() is not None:
            whereClauses.append(u"image.Url = '%s'" % self.filter.getImageURLCriteria()) #$NON-NLS-1$
        if self.filter.getLinkURLCriteria() is not None:
            whereClauses.append(u"link.Url = '%s'" % self.filter.getLinkURLCriteria()) #$NON-NLS-1$
        if self.filter.getTagIdCriteria() is not None:
            whereClauses.append(u"tag.TagId = '%s'" % self.filter.getTagIdCriteria()) #$NON-NLS-1$
            
        return whereClauses
    # end _getWhereClauses()

# end ZDocumentQueryBuilder


# ------------------------------------------------------------------------------
# A class that builds a SQL query for finding links based on a link filter
# ------------------------------------------------------------------------------
class ZLinkQueryBuilder(ZBaseSQLQueryBuilder):

    def __init__(self, filter):
        ZBaseSQLQueryBuilder.__init__(self, filter)
    # end __init__()

    def _buildSelect(self):
        self.buffer.write(u"SELECT ") #$NON-NLS-1$
        if self.countOnly:
            self.buffer.write(u"count(DISTINCT link.Url)") #$NON-NLS-1$
        else:
            self.buffer.write(u"link.*, pd.*") #$NON-NLS-1$
    # end _buildSelect()

    def _buildFrom(self):
        self.buffer.write(u" FROM Link AS link LEFT JOIN PublishedData AS pd ON pd.DocumentId = link.DocumentId") #$NON-NLS-1$
    # end _buildFrom()

    def _buildOrderBy(self):
        if self.countOnly:
            return
        sortCol = self.filter.getSortBy()
        sortOrder = self.filter.getSortOrder()
        if sortCol and sortOrder:
            self.buffer.write(u" ORDER BY %s %s" % (sortCol, sortOrder)) #$NON-NLS-1$
    # end _buildOrderBy()

    def _getWhereClauses(self):
        whereClauses = ZBaseSQLQueryBuilder._getWhereClauses(self)

        if self.filter.getDocumentIdCriteria() is not None:
            whereClauses.append(u"link.DocumentId = '%s'" % self.filter.getDocumentIdCriteria()) #$NON-NLS-1$
        if self.filter.getHostCriteria() is not None:
            whereClauses.append(u"link.Host LIKE '%%%s%%'" % self.filter.getHostCriteria()) #$NON-NLS-1$

        return whereClauses
    # end _getWhereClauses()

# end ZLinkQueryBuilder


# ------------------------------------------------------------------------------
# A class that builds a SQL query for finding images based on an image filter
# ------------------------------------------------------------------------------
class ZImageQueryBuilder(ZBaseSQLQueryBuilder):

    def __init__(self, filter):
        ZBaseSQLQueryBuilder.__init__(self, filter)
    # end __init__()

    def _buildSelect(self):
        self.buffer.write(u"SELECT ") #$NON-NLS-1$
        if self.countOnly:
            self.buffer.write(u"count(DISTINCT image.Url)") #$NON-NLS-1$
        else:
            self.buffer.write(u"image.*, pd.*") #$NON-NLS-1$
    # end _buildSelect()

    def _buildFrom(self):
        self.buffer.write(u" FROM Image AS image LEFT JOIN PublishedData AS pd ON pd.DocumentId = image.DocumentId") #$NON-NLS-1$
    # end _buildFrom()

    def _buildOrderBy(self):
        if self.countOnly:
            return
        sortCol = self.filter.getSortBy()
        sortOrder = self.filter.getSortOrder()
        if sortCol and sortOrder:
            self.buffer.write(u" ORDER BY %s %s" % (sortCol, sortOrder)) #$NON-NLS-1$
    # end _buildOrderBy()

    def _getWhereClauses(self):
        whereClauses = ZBaseSQLQueryBuilder._getWhereClauses(self)

        if self.filter.getDocumentIdCriteria() is not None:
            whereClauses.append(u"image.DocumentId = '%s'" % self.filter.getDocumentIdCriteria()) #$NON-NLS-1$
        if self.filter.getHostCriteria() is not None:
            whereClauses.append(u"image.Host LIKE '%%%s%%'" % self.filter.getHostCriteria()) #$NON-NLS-1$
        return whereClauses
    # end _getWhereClauses()

# end ZImageQueryBuilder

# ------------------------------------------------------------------------------
# A class that builds a SQL query for finding tags based on an tagword filter
# ------------------------------------------------------------------------------
class ZTagQueryBuilder(ZBaseSQLQueryBuilder):

    def __init__(self, filter):
        ZBaseSQLQueryBuilder.__init__(self, filter)
    # end __init__()

    def _buildSelect(self):
        self.buffer.write(u"SELECT ") #$NON-NLS-1$
        if self.countOnly:
            self.buffer.write(u"count(DISTINCT tag.TagId)") #$NON-NLS-1$
        else:
            self.buffer.write(u"tag.*, pd.*") #$NON-NLS-1$
    # end _buildSelect()

    def _buildFrom(self):
        self.buffer.write(u" FROM Tag AS tag LEFT JOIN PublishedData AS pd ON pd.DocumentId = tag.DocumentId") #$NON-NLS-1$
    # end _buildFrom()

    def _buildOrderBy(self):
        if self.countOnly:
            return
        sortCol = self.filter.getSortBy()
        sortOrder = self.filter.getSortOrder()
        if sortCol and sortOrder:
            self.buffer.write(u" ORDER BY %s %s" % (sortCol, sortOrder)) #$NON-NLS-1$
    # end _buildOrderBy()

    def _getWhereClauses(self):
        whereClauses = ZBaseSQLQueryBuilder._getWhereClauses(self)
        if self.filter.getDocumentIdCriteria() is not None:
            whereClauses.append(u"tag.DocumentId = '%s'" % self.filter.getDocumentIdCriteria()) #$NON-NLS-1$
        if self.filter.getTagCriteria() is not None:
            whereClauses.append(u"tag.TagWord LIKE '%%%s%%'" % self.filter.getTagCriteria()) #$NON-NLS-1$
        return whereClauses
    # end _getWhereClauses()

# end ZTagQueryBuilder
