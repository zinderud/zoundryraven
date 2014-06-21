from zoundry.base.util.urlutil import encodeIDNA
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getCommandLineParameters
from zoundry.base.util.text.textutil import isUnicodePath
import os
import webbrowser

# -------------------------------------------------------------------------------------
# Interface for all implementations of a Zoundry Raven OS Util class.
# -------------------------------------------------------------------------------------
class IZOSUtil:

    def getOperatingSystemId(self):
        u"""getOperatingSystemId() -> string
        Returns an id indicating the OS (win32, linux, mac).""" #$NON-NLS-1$
    # end getOperatingSystemId()

    def getCurrentUserName(self):
        u"""getCurrentUserName() -> string
        Returns the username of the currently logged-in user.""" #$NON-NLS-1$
    # end getCurrentUserName()

    def getApplicationDataDirectory(self):
        u"Returns the path to a directory that can be used for a user's application data (e.g. on Windows: C:/Documents and Settings/<username>/Zoundry/Zoundry Raven)." #$NON-NLS-1$
    # end getApplicationDataDirectory()

    def getInstallDirectory(self):
        u"Returns the path to the installation directory of the application." #$NON-NLS-1$
    # end getInstallDirectory()
    
    def getSystemTempDirectory(self):
        u"Returns the path to the OS system temp directory." #$NON-NLS-1$
    # end getSystemTempDirectory()

    def isInstalledAsExe(self):
        u"Returns True if the application is installed as a .exe (probably Win32 only)." #$NON-NLS-1$
    # end isInstalledAsExe()
    
    def isInstalledAsPortable(self):
        u"Returns True if the application is installed as a portable application." #$NON-NLS-1$
    # end isInstalledAsPortable()

    def openFileInDefaultEditor(self, filePath):
        u"""openFileInDefaultEditor(string) -> None
        Opens the file at the given location in the default editor
        for the platform.""" #$NON-NLS-1$
    # end openFileInDefaultEditor()

    def openUrlInBrowser(self, url):
        u"""openUrlInBrowser(string) -> None
        Opens the given url in the platform's default browser.""" #$NON-NLS-1$
    # end openUrlInBrowser()
    
    def getProxyConfig(self):
        u"""getProxyConfig(string) -> ZOSProxyConfig
        Returns OS proxy settings""" #$NON-NLS-1$
    # end getProxyConfig

# end IZOSUtil

# -------------------------------------------------------------------------------------
# Data struct. that represents the proxy configuration.
# -------------------------------------------------------------------------------------

class ZOSProxyConfig:
    TYPE_HTTP  = u"http" #$NON-NLS-1$
    TYPE_SOCKS = u"socks" #$NON-NLS-1$
    
    def __init__(self, proxyType, proxyEnabled, proxyHost, proxyPort):
        self.proxyType = proxyType
        self.proxyEnabled = proxyEnabled
        self.proxyHost = proxyHost
        self.proxyPort = proxyPort
    # end __init__
    
    def isConfigured(self):
        return self.proxyType is not None
    # end isConfigured()
    
    def isEnabled(self):
        return self.proxyEnabled
    # end 
    
    def getHost(self):
        return self.proxyHost
    # end getHost()
    
    def getPort(self):
        return self.proxyPort
    # end getPort
    
    def getPortInt(self):
        port = 0
        if self.proxyPort and len( self.proxyPort.strip() ) > 2:
            try:
                port = int( self.proxyPort.strip() )
            except:
                pass
        return port
    # end getPortInt    
        
# end ZOSProxyConfig

# -------------------------------------------------------------------------------------
# A base class that OS-specific implementations of IZOSUtil can extend in order to
# inherit some base functionality.
# -------------------------------------------------------------------------------------
class ZOSUtilBase(IZOSUtil):

    def __init__(self):
        self.installDir = None
    # end __init__()

    def getApplicationDataDirectory(self):
        path = self._getApplicationDataDirectory()
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    # end getApplicationDataDirectory()

    def getCurrentUserName(self):
        try:
            username = os.environ[u"USERNAME"] #$NON-NLS-1$
            if not username:
                username = u"_unknown" #$NON-NLS-1$
            return username
        except:
            return None
    # end getCurrentUserName()

    def getSystemTempDirectory(self):
        return os.environ[u"TEMP"] #$NON-NLS-1$
    # end getSystemTempDirectory()

    def getInstallDirectory(self):
        if self.installDir:
            return self.installDir

        # We have 3 cracks at figuring out the install-directory.
        # 1) explicit command line param:  --installdir=path/to/install/dir
        # 2) sub-class dependent lookup
        # 3) path relative to srcroot.py module
        path = self._getCmdLineInstallDirectory()
        if not path:
            path = self._getOSDependentInstallDirectory()
        if not path:
            path = self._getSrcRootInstallDirectory()
        if not path:
            raise ZAppFrameworkException(u"Could not locate application install directory.") #$NON-NLS-1$

        self.installDir = path
        return self.installDir
    # end getInstallDirectory()

    def isInstalledAsExe(self):
        return False
    # end isInstalledAsExe()

    def _getCmdLineInstallDirectory(self):
        cmdLineParams = getCommandLineParameters()
        if u"installdir" in cmdLineParams: #$NON-NLS-1$
            return cmdLineParams[u"installdir"] #$NON-NLS-1$
        return None
    # end _getCmdLineInstallDirectory()

    def _getOSDependentInstallDirectory(self):
        return None
    # end _getOSDependentInstallDirectory()

    def _getSrcRootInstallDirectory(self):
        try:
            import srcroot
            srDir = os.path.dirname(srcroot.__file__)
            if srDir.endswith(u"library.zip"): #$NON-NLS-1$
                srDir = os.path.dirname(srDir)
                return os.path.join(srDir, u"..") #$NON-NLS-1$
            srDir = os.path.join(srDir, u"..", u"..", u"bin") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            return srDir
        except:
            return None
    # end _getSrcRootInstallDirectory()

    def openFileInDefaultEditor(self, filePath):
        os.startfile(filePath)
    # end openFileInDefaultEditor()

    def openUrlInBrowser(self, url):
        # If the URL contains unicode characters, assume it is an international
        # URL and thus encode it using the 'idna' encoding
        if isUnicodePath(url):
            url = encodeIDNA(url)
        webbrowser.open_new(url)
    # end openUrlInBrowser()
    
    def getProxyConfig(self):
        # by default, return ZOSProxyConfig of None type i.e. not configured.
        return ZOSProxyConfig(None, False, u"", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getProxyConfig    

# end ZOSUtilBase
