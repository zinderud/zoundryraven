from zoundry.appframework.util.portableutil import isPortableEnabled
from zoundry.appframework.constants import IZAppCommandLineParameterKeys
from zoundry.appframework.global_services import getCommandLineParameters
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.util import fileutil
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.fileutil import resolveRelativePath
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
import os

DEFAULT_PROFILES_XML = u"""<?xml version="1.0" encoding="UTF-8"?>
<profiles />
""" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# The profile model interface.
# ------------------------------------------------------------------------------
class IZProfileModel:

    def getName(self):
        u"""getName() -> string
        Returns the name of the profile.""" #$NON-NLS-1$
    # end getName()

    def getPath(self):
        u"""getPath() -> string
        Returns the path to the profile.""" #$NON-NLS-1$
    # end getPath()

# end IZProfileModel


# ------------------------------------------------------------------------------
# A simple impl of a profile model.
# ------------------------------------------------------------------------------
class ZSimpleProfileModel(IZProfileModel):

    def __init__(self, path):
        self.name = u"unknown" #$NON-NLS-1$
        self.path = path
    # end __init__()

    def getName(self):
        return self.name
    # end getName()

    def getPath(self):
        return self.path
    # end getPath()

# end ZSimpleProfileModel


# ------------------------------------------------------------------------------
# A model of a single profile managed by the profile manager.
# ------------------------------------------------------------------------------
class ZProfileModel(IZProfileModel):

    def __init__(self, node):
        self.node = node
    # end __init__()

    def getName(self):
        return self.node.getAttribute(u"name", u"unknown") #$NON-NLS-1$ #$NON-NLS-2$
    # end getName()

    def getPath(self):
        return self.node.getText()
    # end getPath()

    def setPath(self, path):
        self.node.setText(path)
    # end setPath()

# end ZProfileModel


# --------------------------------------------------------------------------------
# This is the model used by the profile manager.  It provides a view into all of
# the data needed by the manager (list of profiles, ability to create a new
# profile, delete profiles, etc...).
# --------------------------------------------------------------------------------
class ZProfileManagerModel:

    def __init__(self):
        self.osutil = getOSUtil()
        self.profilesDom = self._loadProfilesDom()
    # end __init__()

    def isCommandLineSpecified(self):
        return IZAppCommandLineParameterKeys.ZCMD_KEY_PROFILE in getCommandLineParameters()
    # end isCommandLineSpecified()

    def getCommandLineProfile(self):
        clParams = getCommandLineParameters()
        if IZAppCommandLineParameterKeys.ZCMD_KEY_PROFILE in clParams:
            path = clParams[IZAppCommandLineParameterKeys.ZCMD_KEY_PROFILE]
            if os.path.isdir(path):
                return ZSimpleProfileModel(path)
        return None
    # end getCommandLineProfile()

    def getDefaultProfilesDirectory(self):
        if isPortableEnabled():
            osutil = getOSUtil()
            installDir = osutil.getInstallDirectory()
            profilesDir = os.path.join(installDir, u"profiles") #$NON-NLS-1$
            profilesDir = os.path.abspath(profilesDir)
            return profilesDir
        else:
            return self.osutil.getApplicationDataDirectory()
    # end getDefaultProfilesDirectory()

    def _getProfilesXmlPath(self):
        profilesDir = self.getDefaultProfilesDirectory()
        return os.path.join(profilesDir, u"profiles.xml") #$NON-NLS-1$
    # end _getProfilesXmlPath()

    def getProfiles(self):
        return map(ZProfileModel, self.profilesDom.selectNodes(u"/profiles/profile")) #$NON-NLS-1$
    # end getProfiles()

    def getProfile(self, profileName):
        profileElem = self.profilesDom.selectSingleNode(u"/profiles/profile[@name = \"%s\"]" % profileName) #$NON-NLS-1$
        if profileElem is not None:
            profileModel = ZProfileModel(profileElem)
            path = profileModel.getPath()
            profilesDir = self.getDefaultProfilesDirectory()
            resolvedPath = resolveRelativePath(profilesDir, path)
            profileModel.setPath(resolvedPath)
            return profileModel
        return None
    # end getProfile()

    def getNumProfiles(self):
        return len(self.profilesDom.selectNodes(u"/profiles/profile")) #$NON-NLS-1$
    # end getNumProfiles()

    def getDefaultProfileName(self):
        node = self.profilesDom.selectSingleNode(u"/profiles") #$NON-NLS-1$
        return node.getAttribute(u"default-profile") #$NON-NLS-1$
    # end getDefaultProfileName()

    def setDefaultProfileName(self, profileName):
        node = self.profilesDom.selectSingleNode(u"/profiles") #$NON-NLS-1$
        node.setAttribute(u"default-profile", profileName) #$NON-NLS-1$
        self._saveProfilesDom()
    # end setDefaultProfileName()

    def isBypassDialog(self):
        node = self.profilesDom.selectSingleNode(u"/profiles") #$NON-NLS-1$
        return u"true" == node.getAttribute(u"bypass-dialog") #$NON-NLS-1$ #$NON-NLS-2$
    # end isBypassDialog()

    def setBypassDialog(self, bypassFlag):
        node = self.profilesDom.selectSingleNode(u"/profiles") #$NON-NLS-1$
        node.setAttribute(u"bypass-dialog", unicode(bypassFlag).lower()) #$NON-NLS-1$
        self._saveProfilesDom()
    # end setBypassDialog()

    def deleteProfile(self, profileName, deleteContent = False):
        profileElem = self.profilesDom.selectSingleNode(u"/profiles/profile[@name = \"%s\"]" % profileName) #$NON-NLS-1$
        if not profileElem:
            raise ZBlogAppException(_extstr(u"manager.ProfileNotFound") % profileName) #$NON-NLS-1$

        # Now delete the content...
        if deleteContent:
            path = profileElem.getText()
            fileutil.deleteDirectory(path, True)
        profileElem.parentNode.removeChild(profileElem)
        self._saveProfilesDom()
    # end deleteProfile()

    def createProfile(self, profileInfo):
        (name, path) = profileInfo
        fullPath = path

        # if running in portable mode, the path needs to be stored
        # relative to the profiles.xml file.
        if isPortableEnabled():
            profileDirPath = self.getDefaultProfilesDirectory()
            path = makeRelativePath(profileDirPath, fullPath)

        # Check if we have one with the same name already.
        if self.getProfile(name) is not None:
            raise ZBlogAppException(_extstr(u"manager.ProfileAlreadyExists") % name) #$NON-NLS-1$

        profileElem = self.profilesDom.createElement(u"profile") #$NON-NLS-1$
        profileElem.setAttribute(u"name", name) #$NON-NLS-1$
        profileElem.setText(path)
        self.profilesDom.documentElement.appendChild(profileElem)
        self._saveProfilesDom()

        if not os.path.exists(fullPath):
            os.makedirs(fullPath)
    # end createProfile()

    def _loadProfilesDom(self):
        domPath = self._getProfilesXmlPath()
        dom = ZDom()
        if not os.path.exists(domPath):
            dom.loadXML(DEFAULT_PROFILES_XML)
        else:
            dom.load(domPath)
        return dom
    # end _loadProfilesDom()

    def _saveProfilesDom(self):
        if isPortableEnabled():
            profilesDirPath = self.getDefaultProfilesDirectory()
            if not os.path.exists(profilesDirPath):
                os.makedirs(profilesDirPath)

        domPath = self._getProfilesXmlPath()
        self.profilesDom.save(domPath)
    # end _saveProfilesDom()

    def __len__(self):
        return len(self.profilesDom.selectNodes(u"/profiles/profile")) #$NON-NLS-1$
    # end __len__()

    def __getitem__(self, index):
        profileElem = self.profilesDom.selectSingleNode(u"/profiles/profile[%d]" % (index + 1)) #$NON-NLS-1$
        if profileElem is not None:
            return ZProfileModel(profileElem)
        return None
    # end __init__()

# end ZProfileManagerModel
