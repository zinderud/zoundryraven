# ----------------------------------------------------------------------------------------
# The interface to the resource store.
# Resource store is the central place to store user resoures such as images, files etc.
# ----------------------------------------------------------------------------------------
from zoundry.base.util.types.attrmodel import IZAttributeModel
from zoundry.appframework.engine.service import IZService

#-------------------------------------------------------------------
# IZResourceStoreEntry : interface to resource
#------------------------------------------------------------------
class IZResourceStoreEntry(IZAttributeModel):

    SOURCE_TYPE_FILE = u"file" #$NON-NLS-1$
    SOURCE_TYPE_URL  = u"url" #$NON-NLS-1$

    def getId(self):
        u"""getId() -> string
        Returns id (filename) within resource store.
        """ #$NON-NLS-1$
        pass
    # end getId()

    def getName(self):
        u"""getName() -> string
        Returns local name of this resource.
        """         #$NON-NLS-1$
        pass
    # end getName()

    def getFilePath(self):
        u"""getFilePath() -> string
        Returns file path to this resource.
        """         #$NON-NLS-1$
        pass
    # end getFile

    def getSourcePath(self):
        u"""getSourcePath() -> string
        Returns the original (source) file path or URL to this resource.
        """         #$NON-NLS-1$
        pass
    # end getSourcePath

    def getSourceType(self):
        u"""getSourceType() -> string
        Returns the original type - file or url.
        """         #$NON-NLS-1$
        pass
    # end getSourceType
# end IZResourceStoreEntry

#-------------------------------------------------------------------
# IZResourceStore : interface to resource store
#-------------------------------------------------------------------
class IZResourceStore(IZService):

    def addResource(self, filePath, zstreamWrapperListener): #@UnusedVariable
        u"""addResource(string, IZStreamWrapperListener) -> IZResourceStoreEntry
        Add the resource file and returns IZResourceStoreEntry.
        """ #$NON-NLS-1$
        pass
    # end addResource()

    def getResource(self, resourceId): #@UnusedVariable
        u"""getResource(string) -> IZResourceStoreEntry
        Returns the resource.
        """ #$NON-NLS-1$
        pass
    # end getResource()

# end IZResourceStore