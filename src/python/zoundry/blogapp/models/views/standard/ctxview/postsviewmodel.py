from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.docindex.index import IZDocumentSearchFilter


# ------------------------------------------------------------------------------
# A wrapper around the document IDO list to provide a clean way to add, remove,
# sort, etc all of the entries in the list.  This is particularly useful when an
# event is fired from the index indicating that a new document IDO was added,
# removed, etc.  In that case, this wrapper is used to add or remove the
# document IDO, rather than having to re-query the index.
#
# FIXME (EPW) extend/use the ZSortedList class
# ------------------------------------------------------------------------------
class ZDocumentIDOListWrapper:

    def __init__(self, entries, filter):
        self.entries = entries
        self.documentFilter = filter
    # end __init__()

    def addDocumentIDO(self, documentIDO):
        if self.documentFilter.matches(documentIDO):
            self.entries.append(documentIDO)
            self.sort()
            return True
        else:
            return False
    # end addDocumentIDO()

    def removeDocumentIDO(self, documentIDO):
        for docIDO in self.entries:
            if docIDO.getId() == documentIDO.getId():
                self.entries.remove(docIDO)
                return True
        return False
    # end removeDocumentIDO()

    def _compareIDOs(self, docIDO1, docIDO2):
        data1 = docIDO1.getCreationTime()
        data2 = docIDO2.getCreationTime()

        sortBy = self.documentFilter.getSortBy()
        sortOrder = self.documentFilter.getSortOrder()
        if sortBy == IZDocumentSearchFilter.SORT_BY_TITLE:
            data1 = docIDO1.getTitle()
            data2 = docIDO2.getTitle()
        elif sortBy == IZDocumentSearchFilter.SORT_BY_MODIFIED_TIME:
            data1 = docIDO1.getLastModifiedTime()
            data2 = docIDO2.getLastModifiedTime()

        # Flip the sort if the order is DESC
        if sortOrder == IZDocumentSearchFilter.SORT_ORDER_DESC:
            _temp = data1
            data1 = data2
            data2 = _temp

        rval = 0
        if data1 < data2:
            rval = -1
        elif data1 > data2:
            rval = 1
        return rval
    # end _compareIDOs

    def sort(self):
        self.entries.sort(self._compareIDOs)
    # end sort()

    def __len__(self):
        return len(self.entries)
    # end __len__()

    def __contains__(self, key):
        return key in self.entries
    # end __contains__()

    def __iter__(self):
        return self.entries.__iter__()
    # end __iter__()

    def __getitem__(self, key):
        return self.entries[key]
    # end __getitem__()

# end ZDocumentIDOListWrapper


# ------------------------------------------------------------------------------
# The model associated with the context view for the Standard Perspective when
# a blog has been selected by the user.  This model provides access to all data
# that needs to be displayed by that view (list of blog entries, search
# capabalities, etc...).
# ------------------------------------------------------------------------------
class ZContextInfoPostsModel:

    def __init__(self, filter):
        self.currentFilter = filter
        self.entries = None

        self.engine = getApplicationModel().getEngine()
        self.indexService = self.engine.getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
    # end __init__()

    def getCurrentFilter(self):
        return self.currentFilter
    # end getCurrentFilter()

    def setTitleCriteria(self, titleCriteria):
        self.currentFilter.setTitleCriteria(titleCriteria)
    # end setTitleCriteria()

    def clearTitleCriteria(self):
        self.currentFilter.setTitleCriteria(None)
    # end clearTitleCriteria()

    def setDraftCriteria(self, draft = True):
        self.currentFilter.setDraftCriteria(draft)
    # end setDraftCriteria()

    def clearDraftCriteria(self):
        self.currentFilter.setDraftCriteria(None)
    # end clearDraftCriteria()

    def setDateRangeCriteria(self, startDate, endDate):
        self.currentFilter.setLastModifiedTimeStartCriteria(startDate)
        self.currentFilter.setLastModifiedTimeEndCriteria(endDate)
    # end setDateRangeCriteria()

    def clearDateRangeCriteria(self):
        self.currentFilter.setLastModifiedTimeStartCriteria(None)
        self.currentFilter.setLastModifiedTimeEndCriteria(None)
    # end clearDateRangeCriteria()

    def getEntries(self):
        if self.entries is None:
            indexResults = self.indexService.findDocuments(self.currentFilter)
            self.entries = ZDocumentIDOListWrapper(indexResults, self.currentFilter)
        return self.entries
    # end getEntries()

    def getEntry(self, index):
        return self.entries[index]
    # end getEntry()

    # Called by the view to re-query the index.  This is usually done when the search criteria
    # has changed (e.g. by typing a word in the search field).
    def refresh(self):
        # Force a re-query of the index.
        self.entries = None
        self.getEntries()
    # end refresh()

    # Called by the view when it receives an event indicating that a new document IDO was
    # added to the index.  Returns True if the model's state was changed.
    def addEntry(self, documentIDO):
        if self.entries is not None:
            return self.entries.addDocumentIDO(documentIDO)
        return False
    # end addEntry()

    # Called by the view when it receives an event indicating that a new document IDO was
    # removed from the index.  Returns True if the model's state was changed.
    def removeEntry(self, documentIDO):
        if self.entries is not None:
            return self.entries.removeDocumentIDO(documentIDO)
        return False
    # end removeEntry()

    # Called by the view when it receives an event indicating that a new document IDO was
    # updated.  Returns True if the model's state was changed.
    def updateEntry(self, documentIDO):
        if self.entries is not None:
            self.entries.removeDocumentIDO(documentIDO)
            return self.entries.addDocumentIDO(documentIDO)
        return False
    # end updateEntry()

# end ZContextInfoPostsModel
