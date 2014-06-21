from zoundry.base.util.urlutil import getUriFromFilePath
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.dnd.dnd import IZDnDHandler
import os

# ------------------------------------------------------------------------------
# Base class for the image file DnD Handlers.
# ------------------------------------------------------------------------------
class ZBaseFileDnDHandler(IZDnDHandler):
    
    def __init__(self):
        pass
    # end __init__()

    def _getMimeTypeService(self):
        return getApplicationModel().getService(IZAppServiceIDs.MIMETYPE_SERVICE_ID)
    # end _getMimeTypeService()

    def _getMimeType(self, fileName):
        ext = os.path.splitext(fileName)[1]
        if ext:
            ext = ext[1:]
            return self._getMimeTypeService().getMimeType(ext)
        return None
    # end _getMimeType()
    
    def _getFileMetaData(self, fileName):
        u"""Returns (url, shortName, absPath, size, schemaDate).""" #$NON-NLS-1$
        url = None
        shortName = None 
        absPath = None
        size = None
        schemaDate = None
        try:
            (shortName, absPath, size, schemaDate) = getFileMetaData(fileName) #@UnusedVariable
            if shortName:
                shortName = convertToUnicode(shortName)
            url = getUriFromFilePath(absPath)        
        except:
            pass
        return (url, shortName, absPath, size, schemaDate)
    # _getFileMetaData()    

# end ZBaseFileDnDHandler
