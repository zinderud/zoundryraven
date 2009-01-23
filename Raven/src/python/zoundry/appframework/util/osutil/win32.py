# --------------------------------------------------------------------------------------
# Note, PyDev's organize import feature will remove the @UnresolvedImport comment.  It
# will need to be added back in.
# --------------------------------------------------------------------------------------
from zoundry.base.util.text.textutil import getSafeString
from zoundry.appframework.util.osutil.osutil import ZOSProxyConfig
from zoundry.base.util.text.textutil import getNoneString
from win32com.shell import shell #@UnresolvedImport
from win32com.shell import shellcon #@UnresolvedImport
from zoundry.appframework.util.osutil.osutil import ZOSUtilBase
import _winreg
import os
import sys

# -------------------------------------------------------------------------------------
# A Windows impl of a Zoundry Raven OS Util class.
# -------------------------------------------------------------------------------------
class ZWindowsOSUtil(ZOSUtilBase):

    def __init__(self):
        ZOSUtilBase.__init__(self)
    # end __init__()

    def getOperatingSystemId(self):
        return u"win32" #$NON-NLS-1$
    # end getOperatingSystemId()

    def getSystemTempDirectory(self):
        if os.environ.has_key(u"TEMP") and getNoneString(os.environ[u"TEMP"]): #$NON-NLS-1$ #$NON-NLS-2$
            return os.environ[u"TEMP"] #$NON-NLS-1$
        if os.environ.has_key(u"TMP") and getNoneString(os.environ[u"TMP"]): #$NON-NLS-1$ #$NON-NLS-2$
            return os.environ[u"TMP"] #$NON-NLS-1$            
        return u"%s/Temp" % os.environ[u"SYSTEMROOT"] #$NON-NLS-1$ #$NON-NLS-2$
    # end getSystemTempDirectory()

    def _getApplicationDataDirectory(self):
        appData = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA, False)
        path = os.path.join(appData, u"Zoundry/Zoundry Raven") #$NON-NLS-1$
        return path
    # end _getApplicationDataDirectory()

    def isInstalledAsExe(self):
        # Special py2exe mojo here - indicates we are running via the windows .exe.
        return hasattr(sys, u"frozen") #$NON-NLS-1$
    # end isInstalledAsExe()

    def isInstalledAsPortable(self):
        # We are installed as a portable app if we are a .exe AND there's no 
        # install directory in the registry
        return self.isInstalledAsExe() and self._getRegistryInstallDirectory() is None
    # end isInstalledAsPortable()

    # Two Windows specific attempts at locating the install directory:
    #  1) Check the registry key (put there by the Windows NSIS installer)
    #  2) Check the location of the .exe file
    def _getOSDependentInstallDirectory(self):
        path = self._getRegistryInstallDirectory()
        if not path:
            path = self._getPy2ExeInstallDirectory()
        return path
    # end _getOSDependentInstallDirectory()

    def _getPy2ExeInstallDirectory(self):
        if hasattr(sys, u"frozen"): #$NON-NLS-1$
            return os.path.join(os.path.dirname(sys.executable), u"..") #$NON-NLS-1$
        return None
    # end _getPy2ExeInstallDirectory()

    def _getRegistryInstallDirectory(self):
        try:
            handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, u"Software\\Zoundry Raven") #$NON-NLS-1$
            (val, type) = _winreg.QueryValueEx(handle, u"Path") #$NON-NLS-1$
            _winreg.CloseKey(handle)
            return val
        except:
            # Stupid call will throw if the key doesn't exist.
            return None
    # end _getRegistryInstallDirectory()
    
    def getProxyConfig(self):
        enabled = False
        host = u""  #$NON-NLS-1$
        port = u""  #$NON-NLS-1$
        try:
            handle = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings") #$NON-NLS-1$
            (enableStr, type) = _winreg.QueryValueEx(handle, u"ProxyEnable") #$NON-NLS-1$
            _winreg.CloseKey(handle)
            enableStr = getSafeString(enableStr)
            enabled = enableStr == u"1" #$NON-NLS-1$
        except:
            pass
                
        try:
            handle = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings") #$NON-NLS-1$
            (hostsStr, type) = _winreg.QueryValueEx(handle, u"ProxyServer") #$NON-NLS-1$
            _winreg.CloseKey(handle)
            entries = getSafeString(hostsStr).split(u";") # eg http=127.0.0.1:8888; https=127.0.0.1:8888  #$NON-NLS-1$
            regHostportStr = None # host:port value, if available from registry.
            if len(entries) > 0:
                for entry in entries:
                    # entry = 'scheme=host:port
                    entry = entry.strip()
                    (scheme, regHostportStr) = entry.split(u"=") #$NON-NLS-1$
                    if scheme == u"http": #$NON-NLS-1$
                        break 
            if regHostportStr:
                hp = regHostportStr.strip().split(u":")  #$NON-NLS-1$
                if len(hp) > 0:
                    host = hp[0].strip()
                if len(hp) > 1:
                    port = hp[1].strip()
        except:
            pass 
        return ZOSProxyConfig(ZOSProxyConfig.TYPE_HTTP, enabled, host, port)
    # end getProxyConfig    
    

# end ZWindowsOSUtil
