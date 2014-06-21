
# ------------------------------------------------------------------------------
# The interface that defines an index provider.
# ------------------------------------------------------------------------------
class IZIndexProvider:

    def create(self, applicationModel):
        u"Called when the provider is created." #$NON-NLS-1$
    # end create()
    
    def clear(self):
        u"Called before a re-index in order to clear out the index." #$NON-NLS-1$
    # end clear()

    def findDocuments(self, documentFilter):
        u"Returns a list of IZDocumentIDO objects that match the document search filter." #$NON-NLS-1$
    # end search()

    def findLinks(self, linkFilter):
        u"Returns a list of IZLinkIDO objects that match the filter." #$NON-NLS-1$
    # end findLinks()

    def findTags(self, tagFilter):
        u"Returns a list of IZTagIDO objects that match the filter." #$NON-NLS-1$
    # end findTags()

    def findImages(self, imageFilter):
        u"Returns a list of IZImageIDO objects that match the filter." #$NON-NLS-1$
    # end findImages()

    def getDocumentCount(self, filter):
        u"Returns a count of the number of documents that match the given filter." #$NON-NLS-1$
    # end getDocumentCount()

    def getTagCount(self, filter):
        u"Returns a count of the number of tags that match the given filter." #$NON-NLS-1$
    # end getTagCount()

    def getLinkCount(self, filter):
        u"Returns a count of the number of links that match the given filter." #$NON-NLS-1$
    # end getLinkCount()

    def getImageCount(self, filter):
        u"Returns a count of the number of images that match the given filter." #$NON-NLS-1$
    # end getImageCount()

    def addDocument(self, document, listeners):
        u"Adds a document to the index." #$NON-NLS-1$
    # end addDocument()

    def updateDocument(self, document, listeners):
        u"Updates the document in the index." #$NON-NLS-1$
    # end updateDocument()

    def removeDocument(self, docId, listeners):
        u"Removes the document with the given id from the index." #$NON-NLS-1$
    # end removeDocument()

    def getNumDocuments(self):
        u"Returns the total number of documents in the index." #$NON-NLS-1$
    # end getNumDocuments()

    def requiresReindex(self):
        u"Returns True if this provider needs to be re-indexed (typically due to versioning of the index)." #$NON-NLS-1$
    # end requiresReindex()
    
    def optimize(self):
        u"Called periodically so that the index can be optimized." #$NON-NLS-1$
    # end optimize()

    def destroy(self):
        u"Called by the document index service when the service is being stopped." #$NON-NLS-1$
    # end destroy()

# end IZIndexProvider
