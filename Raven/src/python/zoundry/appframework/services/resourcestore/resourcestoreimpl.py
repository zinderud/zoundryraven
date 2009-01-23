from zoundry.base.util.fileutil import copyFile
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.services.resourcestore.resourcestore import IZResourceStore #@UnresolvedImport
from zoundry.appframework.services.resourcestore.resourcestore import IZResourceStoreEntry #@UnresolvedImport
from zoundry.appframework.services.resourcestore.resourcestoreio import loadStoreEntry
from zoundry.appframework.services.resourcestore.resourcestoreio import saveStoreEntry
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.guid import generate
from zoundry.base.util.text.textutil import sanitizeFileName
from zoundry.base.util.types.attrmodel import ZModelWithAttributes
import os #@Reimport
import stat

#-------------------------------------------------------------------
# IZResourceStoreEntry implementation
#------------------------------------------------------------------
class ZResourceStoreEntry (ZModelWithAttributes, IZResourceStoreEntry):

    def __init__(self, id, localFile):
        ZModelWithAttributes.__init__(self)
        self.setAttribute(u"id", id) #$NON-NLS-1$
        self.localFile = localFile
    # end __init__()

    def getId(self):
        return self.getAttribute(u"id") #$NON-NLS-1$
    # end getId()

    def getName(self):
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def getFilePath(self):
        return self.localFile
    # end getFilePath

    def getSourcePath(self):
        return self.getAttribute(u"source-path") #$NON-NLS-1$
    # end getSourcePath

    def getSourceType(self):
        return self.getAttribute(u"source-type") #$NON-NLS-1$
    # end getSourceType

# end ZResourceStoreEntry

#-------------------------------------------------------------------
# IZResourceStore : interface to resource store
#-------------------------------------------------------------------
class ZResourceStore(IZResourceStore):

    def __init__(self):
        self.logger = None
        self.storeDir = None
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"ZResourceStore Service started.") #$NON-NLS-1$
        self.storeDir = self.applicationModel.getUserProfile().getDirectory(u"resourcestore") #$NON-NLS-1$
    # end start()

    def stop(self):
        pass
    # end stop()

    def _getStorePath(self, name):
        storeFullPath = os.path.join(self.storeDir, name)
        return storeFullPath
    # end _getStorePath()

    def _exists(self, name):
        return os.path.exists( self._getStorePath(name) )
    # end _exists

    def _saveMeta(self, entry):
        resourceId = entry.getId()
        filePath = self._getStorePath( self._getMetaFileId(resourceId) )
        saveStoreEntry(entry, filePath)
    # end _saveMeta

    def _loadMeta(self, resourceId):
        resourcePath = self._getStorePath( resourceId )
        metaFilePath = self._getStorePath( self._getMetaFileId(resourceId) )
        if not os.path.isfile(metaFilePath):
            return None
        entry = ZResourceStoreEntry(resourceId, resourcePath)
        return loadStoreEntry(entry, metaFilePath)
    # end _loadMetaFile

    def _getMetaFileId(self, resourceId):
        return u"%s.rre.xml" % resourceId #$NON-NLS-1$
    # end _getMetaFileId()

    def _createResourceId(self, fileShortName):
        fileShortName = sanitizeFileName(fileShortName)
        if not os.path.exists( self._getStorePath(fileShortName) ):
            return fileShortName
        (name, ext) = os.path.splitext(fileShortName)
        # ext include "." (dot)
        if not ext:
            ext = u"" #$NON-NLS-1$
        count = 1
        while count < 10000:
            fileShortName = u"%s_%04d%s" % (name, count, ext) #$NON-NLS-1$
            if not os.path.exists( self._getStorePath(fileShortName) ):
                return fileShortName
            count = count + 1
        # filename on numbering failed. used guids
        fileShortName = u"%s_%s%s" % (name, generate(), ext) #$NON-NLS-1$
        return fileShortName
    # end _getFileInfo

    def _getEnv(self, name):
        rval = None
        if os.environ.has_key(name):
            rval = os.environ[name]
        if rval is not None:
            return rval
        else:
            return u""   #$NON-NLS-1$
    # end _getEnv

    def _populateEntryPlatformMetaData(self, entry):
        entry.setAttribute(u"platform-cn", self._getEnv(u"COMPUTERNAME") ) #$NON-NLS-1$ #$NON-NLS-2$
        entry.setAttribute(u"platform-un", self._getEnv(u"USERNAME") ) #$NON-NLS-1$ #$NON-NLS-2$
        entry.setAttribute(u"platform-ud", self._getEnv(u"USERDOMAIN")) #$NON-NLS-1$ #$NON-NLS-2$

        hashcodePropNames = u"COMPUTERNAME, USERDOMAIN , PROCESSOR_IDENTIFIER, PROCESSOR_REVISION, HOMEPATH, USERNAME, LOGONSERVER, HOMEDRIVE, SYSTEMDRIVE, NUMBER_OF_PROCESSORS, PROCESSOR_LEVEL" #$NON-NLS-1$
        hashcodeString = u"" #$NON-NLS-1$
        for propNames in hashcodePropNames.split(u","): #$NON-NLS-1$
            hashcodeString = hashcodeString + self._getEnv( propNames.strip() )
        entry.setAttribute(u"platform-id", unicode( hash(hashcodeString)) )  #$NON-NLS-1$
    # end _populateEntryPlatformMetaData

    def _createNewFileEntryInfo(self, filePath):
        (name, path, fsize, schemadt) =  getFileMetaData(filePath) #@UnusedVariable
        resId = self._createResourceId(name)
        storeEntryPath = self._getStorePath(resId)
        entry = ZResourceStoreEntry(resId, storeEntryPath)
        entry.setAttribute(u"name", name) #$NON-NLS-1$
        entry.setAttribute(u"size", unicode(fsize)) #$NON-NLS-1$
        entry.setAttribute(u"timestamp", unicode(schemadt)) #$NON-NLS-1$
        entry.setAttribute(u"source-path", os.path.abspath(filePath)) #$NON-NLS-1$
        entry.setAttribute(u"source-type", IZResourceStoreEntry.SOURCE_TYPE_FILE)  #$NON-NLS-1$
        try:
            entryStat = os.stat(filePath)
            entry.setAttribute(u"source-st-dev", unicode(entryStat[stat.ST_DEV]) ) #$NON-NLS-1$
            entry.setAttribute(u"source-st-size", unicode(entryStat[stat.ST_SIZE]) ) #$NON-NLS-1$
            entry.setAttribute(u"source-st-mtime", unicode(entryStat[stat.ST_MTIME]) ) #$NON-NLS-1$
            entry.setAttribute(u"source-st-ctime", unicode(entryStat[stat.ST_CTIME]) ) #$NON-NLS-1$
        except:
            raise
        self._populateEntryPlatformMetaData(entry)
        return entry
    # end _createNewFileEntryInfo

    def _createNewUrlEntryInfo(self, url, downloadFilePath):
        (name, path, fsize, schemadt) =  getFileMetaData(downloadFilePath) #@UnusedVariable
        # FIXME (PJ) create name from url filename
        resId = self._createResourceId(name)
        storeEntryPath = self._getStorePath(resId)
        entry = ZResourceStoreEntry(resId, storeEntryPath)
        entry.setAttribute(u"name", name) #$NON-NLS-1$
        entry.setAttribute(u"size", unicode(fsize)) #$NON-NLS-1$
        entry.setAttribute(u"timestamp", unicode(schemadt)) #$NON-NLS-1$
        entry.setAttribute(u"source-path", url) #$NON-NLS-1$
        entry.setAttribute(u"source-type", IZResourceStoreEntry.SOURCE_TYPE_URL)  #$NON-NLS-1$        
        self._populateEntryPlatformMetaData(entry)
        return entry
    # end _createNewUrlEntryInfo
    
    def addResource(self, filePath, zstreamWrapperListener = None): #@UnusedVariable
        # if url, then get shortname from url or create shortname

        if not filePath or not os.path.isfile(filePath):
            return None
        
        # check if this resource is already in the store
        filePath = os.path.abspath(filePath)
        if filePath.startswith( self.storeDir ):
            (name, path, fsize, schemadt) =  getFileMetaData(filePath) #@UnusedVariable
            resourceStoreEntryPath = self._getStorePath(name)
            metaStoreEntryPath = self._getStorePath(self._getMetaFileId(name))
            #  resource and meta xml file aready exists in store
            if os.path.isfile(resourceStoreEntryPath) and os.path.isfile(metaStoreEntryPath):
                return self.getResource(name)
            
        entry = self._createNewFileEntryInfo(filePath)
        copyFile(filePath, entry.getFilePath(), zstreamWrapperListener)
        self._saveMeta(entry)
        return entry
    # end addResource()

    def getResource(self, resourceId):
        return self._loadMeta( resourceId )    
    # end getResource()
    
# end IZResourceStore