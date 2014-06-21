from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Represents a mime type loaded by the mime type service.
# ------------------------------------------------------------------------------
class IZMimeType:

    def getExtension(self):
        u"""getExtension() -> string
        Returns the extension associated with the mime type.""" #$NON-NLS-1$
    # end getExtension()

    def getType(self):
        u"""getType() -> string
        Gets the mime type's 'type' which is the first
        component of the mime type.""" #$NON-NLS-1$
    # end getType()

    def getSubType(self):
        u"""getSubType() -> string
        Gets the mime type's 'subtype' which is the second
        component of the mime type.""" #$NON-NLS-1$
    # end getSubType()

    def toString(self):
        u"""toString() -> string
        Returns a string representation of the mime type.""" #$NON-NLS-1$
    # end toString()

# end IZMimeType


# ------------------------------------------------------------------------------
# This interface defines the mime type service.  The mime type service is
# responsible for managing the list of mime types known to the system.  It gets
# these mime types from a .xml config file in the resources directory.
# ------------------------------------------------------------------------------
class IZMimeTypeService(IZService):

    def getMimeTypes(self):
        u"""getMimeTypes() -> IZMimeType[]
        Gets a list of all the mime types known to the service.""" #$NON-NLS-1$
    # end getMimeTypes()

    def getMimeType(self, extension):
        u"""getMimeType(string) -> IZMimeType
        Gets a single mime type by extension.""" #$NON-NLS-1$
    # end getMimeType()

# end IZMimeTypeService
