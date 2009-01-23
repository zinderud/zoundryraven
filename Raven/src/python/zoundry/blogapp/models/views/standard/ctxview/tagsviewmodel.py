from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel

# --------------------------------------------------------------------------------------
# The model associated with the context view for the Standard Perspective when a blog
# has been selected by the user.  This model provides access to all data that needs to
# be displayed by that view.
# --------------------------------------------------------------------------------------
class ZContextInfoTagsModel:

    def __init__(self, filter):
        self.currentFilter = filter
        # map -> tagId:: (tagIDO, hitCount)
        self.tagsMap = None
        self.minCount = -1
        self.maxCount = -1
        self.engine = getApplicationModel().getEngine()
        self.indexService = self.engine.getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
    # end __init__()
    
    def _reset(self):
        self.tagsMap = None
        self.minCount = -1
        self.maxCount = -1

    def getCurrentFilter(self):
        return self.currentFilter
    # end getCurrentFilter()

    def setTagCriteria(self, tagwordCriteria):
        self.currentFilter.setTagCriteria(tagwordCriteria)
    # end setHostCriteria()

    def clearTagCriteria(self):
        self.currentFilter.setTagCriteria(None)
    # end clearHostCriteria()

    def getTagIDO(self, tagId):
        tagIdo = None
        if tagId and self.tagsMap is not None and self.tagsMap.has_key( tagId ):            
            (tagIdo, hitcount) = self.tagsMap[tagId ]         #@UnusedVariable
        return tagIdo
        
    def getTagsMap(self):
        if self.tagsMap is None:
            self.tagsMap = {}
            indexResults = self.indexService.findTags(self.currentFilter)
            self._processIndexResult(indexResults)
        return self.tagsMap
    # end getTags()

    # Called by the view to re-query the index.  This is usually done when the search criteria
    # has changed (e.g. by typing a word in the search field).
    def refresh(self):
        # Force a re-query of the index.
        self._reset()
        self.getTagsMap()
    # end refresh()

    # Called by the view when it receives an event indicating that a new tag IDO was
    # added to the index.  Returns True if the model's state was changed.
    def addTag(self, tagIDO):
        return self.updateTag(tagIDO)
    # end addTag()

    # Called by the view when it receives an event indicating that a new tag IDO was
    # removed from the index.  Returns True if the model's state was changed.
    def removeTag(self, tagIDO):        
        if tagIDO and self.tagsMap is not None:            
            if self.tagsMap.has_key( tagIDO.getId() ):
                (tmpIdo, hitcount) = self.tagsMap[ tagIDO.getId() ] 
                # dec hit count
                hitcount = hitcount -1
                if hitcount > 0:
                    self.tagsMap[ tmpIdo.getId() ] = (tmpIdo, hitcount)
                else:
                    del self.tagsMap[ tmpIdo.getId() ]
                return True        
        return False
    # end removeTag()

    # Called by the view when it receives an event indicating that a new tag IDO was
    # updated.  Returns True if the model's state was changed.
    def updateTag(self, tagIDO):
        if self.currentFilter and self.currentFilter.matches(tagIDO):
            return self._updateTagMap(tagIDO) > 0
        return False
    # end updateTag()

    def _updateTagMap(self, tagIdo):
        # updates the tag map and hitcount. Hitcount > 0 for a succesful update. 
        hitcount = 0
        if tagIdo and self.tagsMap is not None:            
            if self.tagsMap.has_key( tagIdo.getId() ):
                (tmpIdo, hitcount) = self.tagsMap[ tagIdo.getId() ] #@UnusedVariable
            hitcount = hitcount +1
            self.tagsMap[ tagIdo.getId() ] = (tagIdo, hitcount)
        return hitcount       
        
    def _processIndexResult(self, indexResult):
        self.minCount = 9999999
        self.maxCount = 0        
        for ido in indexResult:
            hitcount = self._updateTagMap(ido)
            if self.minCount > hitcount:
                self.minCount = hitcount
            if self.maxCount < hitcount:
                self.maxCount = hitcount
            
    # end _processIndexResult()

# end ZContextInfoTagModel