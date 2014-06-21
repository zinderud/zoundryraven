import os.path
from zoundry.base.util.urlutil import getFilePathFromUri
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.xhtml.xhtmlanalyzers import IZXhtmlAnalyser
from zoundry.base.util.fileutil import isSameDrive
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getCommandLineParameters
from zoundry.appframework.util.osutilfactory import getOSUtil

PORTABLE_ENABLED = None

# ------------------------------------------------------------------------------
# Returns true if the application is in 'portable' mode.
# ------------------------------------------------------------------------------
def isPortableEnabled():
    u"""Returns true if the --portable command line option is set to enabled.""" #$NON-NLS-1$
    global PORTABLE_ENABLED
    if PORTABLE_ENABLED is None:
        PORTABLE_ENABLED = False

        # If the OS Util thinks we're installed as a portable app, then it is
        # probably true, unless overridden by the cmd line.
        osutil = getOSUtil()
        if osutil.isInstalledAsPortable():
            PORTABLE_ENABLED = True
    
        # The command line parameter can always override the value.
        cmdLineParams = getCommandLineParameters()
        if cmdLineParams is not None and u"portable" in cmdLineParams: #$NON-NLS-1$
            PORTABLE_ENABLED = cmdLineParams[u"portable"] == u"true" #$NON-NLS-1$ #$NON-NLS-2$

    return PORTABLE_ENABLED
# end isPortableEnabled()

# ------------------------------------------------------------------------------
# Returns true if the application is in 'portable' mode
# and the given file path is in the same drive or device as the
# as the user profile.
# Note: This method will always return true if isPortableEnabled() = false.
# (i.e. do not care about paths if app is not in a portable mode).
# ------------------------------------------------------------------------------

def isPathPortable(path):
    if not path or not isPortableEnabled():
        return True
    # compare give path (drive) to that of resorucestore in the current profile.
    resStoreDir = getApplicationModel().getUserProfile().getDirectory(u"resourcestore") #$NON-NLS-1$
    return isSameDrive(path, resStoreDir)
# end isPathPortable()


#------------------------------------------------------------------------
# Contains information about the xhtml element that has
# a path that is not portable.
#------------------------------------------------------------------------
class ZXhtmlPortablePathElementInfo:
    
    def __init__(self, element, attrName, path):
        self.element = element
        self.attrName = attrName
        self.path = path
    # end __init__
    
    def getElement(self):
        return self.element
    # end getElement()
    
    def getPath(self):
        return self.path
    # end getPath()
    
    def setPath(self, newPath):
        newPath = getSafeString(newPath)
        self.element.setAttribute(self.attrName, newPath)
    # end setNewPath        
     
# end ZXhtmlPortablePathElementInfo
# --------------------------------------------------------------------------
# XHTML document anaylyser for detecting paths that
# are not portable.
# --------------------------------------------------------------------------
class ZXhtmlContentPortablePathAnalyser(IZXhtmlAnalyser):

    def __init__(self):
        self.elems = []
        self.hrefNames = [u"a", u"link",] #$NON-NLS-1$ #$NON-NLS-2$ 
        self.srcNames = [u"img",u"script"] #$NON-NLS-1$ #$NON-NLS-2$         
    # end __init__()
    
    def hasNonPortablePaths(self):
        u"""hasNonPortablePaths() -> bool
        Returns true if there were any paths that were not portable.
        """ #$NON-NLS-1$
        return len(self.elems) > 0
    # end hasNonPortablePaths
    
    def getNonPortablePathElementInfos(self):
        u"""getNonPortablePathElementInfos() -> list of ZXhtmlPortablePathElementInfo
        """ #$NON-NLS-1$
        return self.elems
    # end getNonPortablePathElementInfos
    
    def analyseElement(self, node):
        attrName = None        
        if node.localName.lower() in self.hrefNames: #$NON-NLS-1$
            attrName = u"href" #$NON-NLS-1$
        elif node.localName.lower() in self.srcNames: #$NON-NLS-1$
            attrName = u"src" #$NON-NLS-1$
        if attrName:
            path = self._getLocalFilePath(node, attrName)
            if not isPathPortable(path):
                info = ZXhtmlPortablePathElementInfo(node, attrName, path)
                self.elems.append(info)
                # local path exist.                    
    # end analyseElement
    
    def _getLocalFilePath(self, element, attrName):
        path = getNoneString( element.getAttribute(attrName) )
        # check if the path is a local resource (file://) and if it exists
        localFilePath = getFilePathFromUri(path)
        if localFilePath and os.path.isfile(localFilePath):
            return localFilePath
        else:
            return None
        # end _getLocalFilePath        
# end ZXhtmlContentPortablePathAnalyser
