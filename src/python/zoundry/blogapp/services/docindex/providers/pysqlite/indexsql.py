from zoundry.base.util.dateutil import getNoneDate
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentIDO
from zoundry.blogapp.services.docindex.indeximpl import ZImageIDO
from zoundry.blogapp.services.docindex.indeximpl import ZLinkIDO
from zoundry.blogapp.services.docindex.indeximpl import ZPubDataIDO
from zoundry.blogapp.services.docindex.indeximpl import ZTagIDO

# ------------------------------------------------------------------------------
# A SQL implementation of a pub data IDO.
# ------------------------------------------------------------------------------
class ZPySQLPubDataIDO(ZPubDataIDO):

    def __init__(self, row, colOffset):
        accountId = row[1 + colOffset]
        blogId = row[2 + colOffset]
        blogEntryId = row[3 + colOffset]
        issuedTime = getNoneDate(row[4 + colOffset])
        synchTime = getNoneDate(row[5 + colOffset])
        draft = row[6 + colOffset] == 1
        permaLink = row[7 + colOffset]

        ZPubDataIDO.__init__(self, accountId, blogId, blogEntryId, issuedTime, synchTime, draft, permaLink)
    # end __init__()

# end ZPySQLPubDataIDO


# ------------------------------------------------------------------------------
# A SQL implementation of a tag 'index data object'.
# ------------------------------------------------------------------------------
class ZPySQLTagIDO(ZTagIDO):

    def __init__(self, row, pubDataIDOs = None):
        ZTagIDO.__init__(self, pubDataIDOs, row[0], row[1], row[2])
    # end __init__()

# end ZPySQLTagIDO


# ------------------------------------------------------------------------------
# A SQL implementation of a document 'index data object'.
# ------------------------------------------------------------------------------
class ZPySQLDocumentIDO(ZDocumentIDO):

    def __init__(self, row, pubDataIDOs = None):
        id = row[0]
        title = row[1]
        creationTime = getNoneDate(row[2])
        lastModifiedTime = getNoneDate(row[3])

        ZDocumentIDO.__init__(self, pubDataIDOs, id, title, creationTime, lastModifiedTime)
    # end __init__()

# end ZPySQLDocumentIDO


# ------------------------------------------------------------------------------
# A SQL implementation of a link 'index data object'.
# ------------------------------------------------------------------------------
class ZPySQLLinkIDO(ZLinkIDO):

    def __init__(self, row, pubDataIDOs = None):
        documentId = row[0]
        url = row[1]
        host = row[2]
        # path is None for links that do not have a path. Eg. http://www.zoundry.com
        path = row[3]
        if path is None:
            path = u"/" #$NON-NLS-1$
        rel = row[4]
        title = row[5]
        content = row[6]
        hitCount = row[7]

        ZLinkIDO.__init__(self, pubDataIDOs, documentId, url, host, path, rel, title, content, hitCount)
    # end __init__()

# end ZPySQLDocumentIDO


# ------------------------------------------------------------------------------
# A SQL implementation of an image 'index data object'.
# ------------------------------------------------------------------------------
class ZPySQLImageIDO(ZImageIDO):

    def __init__(self, row, pubDataIDOs = None):
        documentId = row[0]
        url = row[1]
        host = row[2]
        path = row[3]
        title = row[4]
        hitCount = row[5]

        ZImageIDO.__init__(self, pubDataIDOs, documentId, url, host, path, title, hitCount)
    # end __init__()

# end ZPySQLImageIDO
