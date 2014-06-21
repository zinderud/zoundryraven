from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.base.util.sysprops import ZSystemProperties
import os.path

# Define some 'types' of system profile impls.
SYSTEM_PROFILE_TYPE_FILE = u"file" #$NON-NLS-1$


# -----------------------------------------------------------------------------
# This interface represents the application's system profile.  The system 
# profile provides access to various bits of information about the base system, 
# such as various resource locations (i18n files, plugins, etc).  The system
# profile factory is responsible for creating a concrete instance of a system
# profile.
# -----------------------------------------------------------------------------
class IZSystemProfile:

    def getPluginDirectory(self):
        u"Returns the path to the plugins directory." #$NON-NLS-1$
    # end getPluginDirectory()
    
    def getBundleDirectory(self):
        u"Returns the path to the bundles directory." #$NON-NLS-1$
    # end getBundleDirectory()

    def getSchemaDirectory(self):
        u"Returns the path to the schema directory." #$NON-NLS-1$
    # end getSchemaDirectory()

    def getSchema(self, relativePathToSchema):
        u"Gets the path to the given schema (relative to the schema directory)." #$NON-NLS-1$
    # end getSchema()

    def getTransformDirectory(self):
        u"Gets the path to the transform directory." #$NON-NLS-1$
    # end getTransformDirectory()

    def getTransform(self, relativePathToTransform):
        u"Gets the path to the given transform (relative to the transform directory)." #$NON-NLS-1$
    # end getTransform()

    def getResourceDirectory(self):
        u"Gets the path to the resources directory." #$NON-NLS-1$
    # end getResourceDirectory()
    
    def getProperties(self):
        u"Gets the system properties." #$NON-NLS-1$
    # end getProperties()

# end IZSystemProfile


# -----------------------------------------------------------------------------
# A concrete implementation of a ZSystemProfile.  This impl is backed by a
# directory on the local file system.
# -----------------------------------------------------------------------------
class ZFileSystemProfile(IZSystemProfile):

    def __init__(self, data):
        self.systemProfileDirectory = os.path.abspath(unicode(data))
        self.properties = None
    # end __init__()

    def getProperties(self):
        if not self.properties:
            self.properties = self._createProperties()
        return self.properties
    # end getProperties()

    def getTempDirectory(self):
        return self._getNamedDirectory(u"temp") #$NON-NLS-1$
    # end getTempDirectory()

    def getBundleDirectory(self):
        return self._getNamedDirectory(u"bundles") #$NON-NLS-1$
    # end getBundleDirectory()

    def getSchemaDirectory(self):
        return self._getNamedDirectory(u"schemas") #$NON-NLS-1$
    # end getSchemaDirectory()

    def getTransformDirectory(self):
        return self._getNamedDirectory(u"transforms") #$NON-NLS-1$
    # end getSchemaDirectory()

    def getSchema(self, relativePathToSchema):
        return os.path.join(self.getSchemaDirectory(), relativePathToSchema)
    # end getSchema()

    def getTransform(self, relativePathToTransform):
        return os.path.join(self.getTransformDirectory(), relativePathToTransform)
    # end getTransform()

    def getPluginDirectory(self):
        return self._getNamedDirectory(u"plugins") #$NON-NLS-1$
    # end getPluginDirectory()

    def getResourceDirectory(self):
        return self._getNamedDirectory(u"resources") #$NON-NLS-1$
    # end getResourceDirectory()

    def _getNamedDirectory(self, name):
        return os.path.join(self.systemProfileDirectory, name)
    # end _getNamedDirectory()

    def _getNamedFile(self, dirName, fileName):
        return os.path.join(self._getNamedDirectory(dirName), fileName)
    # end _getNamedDirectory()

    def _createProperties(self):
        sysPropsFilename = self._getNamedFile(u"config", u"system-properties.xml") #$NON-NLS-2$ #$NON-NLS-1$
        return ZSystemProperties(sysPropsFilename)
    # end _createProperties()

# end ZFileSystemProfile()


# ---------------------------------------------------------------------------------
# The system profile factory.  This factory can create system profile objects given
# a type of system profile and init data for the profile.  For example, it can
# create a file-based system profile if called with a type of 'file' and init data
# consisting of the system profile directory.
# ---------------------------------------------------------------------------------
class ZSystemProfileFactory:

    def __init__(self):
        self.typeRegistry = {
            SYSTEM_PROFILE_TYPE_FILE : ZFileSystemProfile
        }
    # end __init()

    def createSystemProfile(self, type, data):
        c = self.typeRegistry[type]
        if not c:
            raise ZAppFrameworkException(_extstr(u"system.CouldNotCreateSysProfile") % type) #$NON-NLS-1$
        try:
            return c(data)
        except Exception, ex:
            raise ZAppFrameworkException(_extstr(u"system.CouldNotCreateSysProfile") % type, ex) #$NON-NLS-1$
    # end createSystemProfile()

# end ZSystemProfileFactory
