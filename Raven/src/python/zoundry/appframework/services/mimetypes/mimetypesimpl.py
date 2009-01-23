from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.services.mimetypes.mimetypes import IZMimeType
from zoundry.appframework.services.mimetypes.mimetypes import IZMimeTypeService
from zoundry.base.zdom.dom import ZDom
import string

# ------------------------------------------------------------------------------
# Implements a mime type object.
# ------------------------------------------------------------------------------
class ZMimeType(IZMimeType):

    def __init__(self, type, extension):
        (type, subtype) = type.split(u"/") #$NON-NLS-1$
        self.type = type
        self.subtype = subtype
        self.extension = extension
    # end __init__()

    def getExtension(self):
        return self.extension
    # end getExtension()

    def getType(self):
        return self.type
    # end getType()

    def getSubType(self):
        return self.subtype
    # end getSubType()

    def toString(self):
        return u"%s/%s" %(self.type, self.subtype) #$NON-NLS-1$
    # end toString()

# end ZDnDSource


# ------------------------------------------------------------------------------
# Implementation of the mime type service.
# ------------------------------------------------------------------------------
class ZMimeTypeService(IZMimeTypeService):

    def __init__(self):
        self.handlers = []
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.mimeTypes = self._loadMimeTypes(applicationModel)
        self.logger.debug(u"Mime Type Service started [%d types loaded]." % len(self.mimeTypes)) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.handlers = []
    # end stop()

    def _loadMimeTypes(self, applicationModel):
        rval = {}
        
        mimeTypeFile = applicationModel.getResourceRegistry().getResourcePath(u"mimetypes.xml") #$NON-NLS-1$
        mimeTypeDom = ZDom()
        mimeTypeDom.load(mimeTypeFile)
        mimeTypeDom.setNamespaceMap({ u"mt" : IZAppNamespaces.RAVEN_MIMETYPES_NAMESPACE }) #$NON-NLS-1$
        
        mimeTypeNodes = mimeTypeDom.selectNodes(u"/mt:mime-types/mt:mime-type") #$NON-NLS-1$
        for mimeTypeNode in mimeTypeNodes:
            type = mimeTypeNode.selectSingleNodeText(u"mt:type") #$NON-NLS-1$
            ext = mimeTypeNode.selectSingleNodeText(u"mt:extension") #$NON-NLS-1$
            rval[ext] = ZMimeType(type, ext)
            
        return rval
    # end _loadMimeTypes()

    def getMimeTypes(self):
        return self.mimeTypes.values()
    # end getMimeTypes()

    def getMimeType(self, extension):
        ext = string.lower(extension)
        if ext in self.mimeTypes:
            return self.mimeTypes[ext]
        return None
    # end getMimeType()

# end ZMimeTypeService
