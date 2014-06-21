from zoundry.blogapp.services.docindex.providers.pysqlite.indexsql import ZPySQLTagIDO
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.services.docindex.providers.pysqlite.indexsql import ZPySQLDocumentIDO
from zoundry.blogapp.services.docindex.providers.pysqlite.indexsql import ZPySQLImageIDO
from zoundry.blogapp.services.docindex.providers.pysqlite.indexsql import ZPySQLLinkIDO
from zoundry.blogapp.services.docindex.providers.pysqlite.indexsql import ZPySQLPubDataIDO

# -------------------------------------------------------------------------------------------
# An interface for handling query results in the pysql provider.  When a SQL SELECT is 
# performed, an instance of a query handler is used to convert the result set to some other
# object or list of objects.
# -------------------------------------------------------------------------------------------
class IZQueryHandler:
    
    def handle(self, rows):
        u"Called to handle the result of a query.  This method can return anything, but typically returns a list of objects." #$NON-NLS-1$
    # end handle()
    
# end IZQueryHandler


# -------------------------------------------------------------------------------------------
# An impl of a query handler that is used for queries that return a single value.
# -------------------------------------------------------------------------------------------
class ZSingleItemQueryHandler(IZQueryHandler):

    # There should be a single row with a single column.
    def handle(self, rows):
        return rows[0][0]
    # end handle()

# end ZSingleItemQueryHandler


# -------------------------------------------------------------------------------------------
# A base class for query handlers that convert the each row in the result to a single object
# and return that list.  In other words, this always produces a list that is the same size
# as the number of rows in the result.
# -------------------------------------------------------------------------------------------
class ZListQueryHandler(IZQueryHandler):
    
    def handle(self, rows):
        return map(self._handleRow, rows)
    # end handle()
    
    def _handleRow(self, row):
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_handleRow") #$NON-NLS-1$
    # end _handleRow()
    
# end ZListQueryHandler


# -------------------------------------------------------------------------------------------
# An extension of the basic list handler that takes a method and calls that method for each
# row in the result.
# -------------------------------------------------------------------------------------------
class ZMethodMappedListQueryHandler(ZListQueryHandler):
    
    def __init__(self, method):
        self.method = method
    # end __init__()
    
    def _handleRow(self, row):
        return self.method(row)
    # end _handleRow()
    
# end ZMethodMappedListQueryHandler


# -------------------------------------------------------------------------------------------
# A query handler that gets used for converting a result into a list of blog based IDO 
# instances.  The specific sub type of the blog based IDO is passed in to the handler's
# constructor.  This class must be extended in order to supply the IDO map key (which
# uniquely identifies/correlates an IDO instance).
# -------------------------------------------------------------------------------------------
class ZBlogBasedIDOListQueryHandler(IZQueryHandler):
    
    def __init__(self, idoType, pubDataColumnOffset):
        self.idoType = idoType
        self.pubDataColumnOffset = pubDataColumnOffset
        self.blogBasedIDOMap = {}
        self.blogBasedIDOList = []
    # end __init__()
    
    def handle(self, rows):
        for row in rows:
            self._handleRow(row)
        return self.blogBasedIDOList
    # end handle()
    
    def _handleRow(self, row):
        blogBasedIDO = self._getBlogBasedIDO(row)
        if len(row) > self.pubDataColumnOffset and row[self.pubDataColumnOffset] is not None:
            pdIDO = ZPySQLPubDataIDO(row, self.pubDataColumnOffset)
            blogBasedIDO.addPubDataIDO(pdIDO)
    # end _handleRow()

    def _getBlogBasedIDO(self, row):
        blogBasedIDO = self.idoType(row)
        mapKey = self._getIDOMapKey(blogBasedIDO)
        if mapKey in self.blogBasedIDOMap:
            blogBasedIDO = self.blogBasedIDOMap[mapKey]
        else:
            self.blogBasedIDOMap[mapKey] = blogBasedIDO
            self.blogBasedIDOList.append(blogBasedIDO)
        return blogBasedIDO
    # end _getBlogBasedIDO()
    
    def _getIDOMapKey(self, ido):
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_getIDOMapKey") #$NON-NLS-1$
    # end _getIDOMapKey()

# end ZBlogBasedIDOListQueryHandler


# -------------------------------------------------------------------------------------------
# A query handler that gets used for converting a result into a list of document IDO 
# instances. 
# -------------------------------------------------------------------------------------------
class ZDocumentIDOListQueryHandler(ZBlogBasedIDOListQueryHandler):

    def __init__(self):
        ZBlogBasedIDOListQueryHandler.__init__(self, ZPySQLDocumentIDO, 4)
    # end __init__()
    
    def _getIDOMapKey(self, ido):
        return ido.getId()
    # end _getIDOMapKey()

# end ZDocumentIDOListQueryHandler


# -------------------------------------------------------------------------------------------
# A query handler that gets used for converting a result into a list of link IDO instances. 
# -------------------------------------------------------------------------------------------
class ZLinkIDOListQueryHandler(ZBlogBasedIDOListQueryHandler):

    def __init__(self):
        ZBlogBasedIDOListQueryHandler.__init__(self, ZPySQLLinkIDO, 8)
    # end __init__()
    
    def _getIDOMapKey(self, ido):
        return u"%s:%s:[%d]" % (ido.getDocumentId(), ido.getUrl(), ido.getHitCount()) #$NON-NLS-1$
    # end _getIDOMapKey()

# end ZLinkIDOListQueryHandler


# -------------------------------------------------------------------------------------------
# A query handler that gets used for converting a result into a list of image IDO instances. 
# -------------------------------------------------------------------------------------------
class ZImageIDOListQueryHandler(ZBlogBasedIDOListQueryHandler):

    def __init__(self):
        ZBlogBasedIDOListQueryHandler.__init__(self, ZPySQLImageIDO, 6)
    # end __init__()
    
    def _getIDOMapKey(self, ido):
        return u"%s:%s:[%d]" % (ido.getDocumentId(), ido.getUrl(), ido.getHitCount()) #$NON-NLS-1$
    # end _getIDOMapKey()

# end ZImageIDOListQueryHandler

# -------------------------------------------------------------------------------------------
# A query handler that gets used for converting a result into a list of IZTagIDO instances. 
# -------------------------------------------------------------------------------------------
class ZTagIDOListQueryHandler(ZBlogBasedIDOListQueryHandler):

    def __init__(self):
        ZBlogBasedIDOListQueryHandler.__init__(self, ZPySQLTagIDO, 3)
    # end __init__()
    
    def _getIDOMapKey(self, ido):
        return u"%s:%s" % (ido.getDocumentId(), ido.getId()) #$NON-NLS-1$
    # end _getIDOMapKey()
# end ZTagIDOListQueryHandler
