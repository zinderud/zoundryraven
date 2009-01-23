from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.profile.userprefs import ZUserPreferences
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.guid import generate
from zoundry.base.util.sysprops import ZSystemProperties
import os.path

# Define some 'types' of user profile impls.
USER_PROFILE_TYPE_FILE = u"file" #$NON-NLS-1$


# The default user properties.
DEFAULT_USER_PROPERTIES = u"""<?xml version="1.0" encoding="UTF-8"?>
<user-properties />
""" #$NON-NLS-1$

# -----------------------------------------------------------------------------
# This interface represents the user's profile.  The user profile provides 
# access to various bits of information specific to the currently selected
# profile.
# -----------------------------------------------------------------------------
class IZUserProfile:

    def getPreferences(self):
        u"Returns the IZUserPreferences object." #$NON-NLS-1$
    # end getPreferences()

    def getProperties(self):
        u"Gets the user properties (ZSystemProperties)." #$NON-NLS-1$
    # end getProperties()

    def getTempDirectory(self):
        u"Returns the path to the profile's temp directory." #$NON-NLS-1$
    # end getTempDirectory()

    def getLogDirectory(self):
        u"Returns the path to the profile's log directory." #$NON-NLS-1$
    # end getLogDirectory()

    def getDirectory(self, dirName):
        u"Returns the path to the profile's named sub-directory." #$NON-NLS-1$
    # end getDirectory()
    
    def getGuid(self):
        u"Returns the profile's guid, which uniquely identifies this profile." #$NON-NLS-1$
    # end getGuid()

# end IZUserProfile


# ---------------------------------------------------------------------------------
# This is a file-based user profile class.  This class is a concrete implementation
# of a user profile and is backed by some folder/directory on the local file system.
# ---------------------------------------------------------------------------------
class ZFileUserProfile(IZUserProfile):

    def __init__(self, data):
        self.userProfileDirectory = os.path.abspath(unicode(data))
        self.properties = None
        self.preferences = None
    # end __init__()

    def getPreferences(self):
        if self.preferences is None:
            self.preferences = ZUserPreferences(self.getProperties())
        return self.preferences
    # end getPreferences()

    def getProperties(self):
        if not self.properties:
            self.properties = self._createProperties()
        return self.properties
    # end getProperties()

    def getGuid(self):
        prefs = self.getPreferences()
        guid = prefs.getUserPreference(IZAppUserPrefsKeys.GUID)
        if not guid:
            guid = generate()
            prefs.setUserPreference(IZAppUserPrefsKeys.GUID, guid)
        return guid
    # end getGuid()

    def getDirectory(self, dirName):
        return self._getNamedDirectory(dirName)
    # end getDirectory()

    def getTempDirectory(self):
        return self._getNamedDirectory(u"temp") #$NON-NLS-1$
    # end getTempDirectory()

    def getLogDirectory(self):
        return self._getNamedDirectory(u"log") #$NON-NLS-1$
    # end getLogDirectory()

    def _getNamedDirectory(self, name):
        dirName = os.path.join(self.userProfileDirectory, name)
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
        return dirName
    # end _getNamedDirectory()

    def _getNamedFile(self, dirName, fileName):
        return os.path.join(self._getNamedDirectory(dirName), fileName)
    # end _getNamedDirectory()

    def _createProperties(self):
        userPropsFilename = self._getNamedFile(u"config", u"user-properties.xml") #$NON-NLS-2$ #$NON-NLS-1$
        if not os.path.isfile(userPropsFilename):
            self._writeEmptyUserPropertiesFile(userPropsFilename)
        metaData = getFileMetaData(userPropsFilename)
        # If the file size is 0, write out an empty one (defect 596)
        if metaData[2] == 0:
            self._writeEmptyUserPropertiesFile(userPropsFilename)

        return ZSystemProperties(userPropsFilename)
    # end _createProperties()

    def _writeEmptyUserPropertiesFile(self, fileName):
        f = open(fileName, u"w") #$NON-NLS-1$
        f.write(DEFAULT_USER_PROPERTIES)
        f.close()
    # end _writeEmptyUserPropertiesFile()

# end ZFileUserProfile


# ---------------------------------------------------------------------------------
# The user profile factory.  This factory can create user profile objects given a
# type of user profile and init data for the profile.  For example, it can create
# a file-based user profile if called with a type of 'file' and init data
# consisting of the user profile directory.
# ---------------------------------------------------------------------------------
class ZUserProfileFactory:

    def __init__(self):
        self.typeRegistry = {
            USER_PROFILE_TYPE_FILE : ZFileUserProfile
        }
    # end __init()

    def createUserProfile(self, type, data):
        c = self.typeRegistry[type]
        if not c:
            raise ZAppFrameworkException(_extstr(u"user.CouldNotCreateUserProfile") % type) #$NON-NLS-1$
        try:
            return c(data)
        except Exception, ex:
            raise ZAppFrameworkException(_extstr(u"user.CouldNotCreateUserProfile") % type, ex) #$NON-NLS-1$
    # end createUserProfile()

# end ZUserProfileFactory
