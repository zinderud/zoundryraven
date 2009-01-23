from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.appframework.util import crypt
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.base.net.http import ZHttpProxyConfiguration
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.global_services import setApplicationModel
from zoundry.appframework.global_services import setCommandLineParameters
from zoundry.appframework.profile.system import SYSTEM_PROFILE_TYPE_FILE
from zoundry.appframework.profile.system import ZSystemProfileFactory
from zoundry.appframework.profile.user import USER_PROFILE_TYPE_FILE
from zoundry.appframework.profile.user import ZUserProfileFactory
from zoundry.appframework.resources.registry import ZSystemResourceRegistry
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionWithFeedback
from zoundry.appframework.util.cmdline import ZCommandLineParameters
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.constants import IZI18NConstants
from zoundry.base.exceptions import ZException
from zoundry.blogapp.blogthis import checkCmdLineForBlogThis
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.blogappmodelimpl import ZBlogApplicationModel
from zoundry.blogapp.models.profile.manager import ZProfileManagerModel
from zoundry.blogapp.services.singleton.rpcclient import ZRavenRPCClient
from zoundry.appframework.util.portableutil import isPortableEnabled
import os
import sys
import wx


# This is the "main" entry point to the Raven application.  The steps involved in launching
# the application are:
# 
# 0) Set up global environment settings
# 1) Create system profile
# 2) Create user profile
# 3) Open 'splash screen'
# 4) Create the plugin registry (load plugins)
# 5) Create Engine
# 6) Start Engine
# 7) Close 'splash screen'
# 8) Create Application UI
#


# -----------------------------------------------------------------------------------
# The main Raven Application class.  This is the first object to be created and run
# by the main method.  See above documentation for what this will do.
# -----------------------------------------------------------------------------------
class RavenApplication:

    def __init__(self):
        self._initGlobalSettings()
        self.systemProfile = self._createSystemProfile()
        self.resourceRegistry = ZSystemResourceRegistry(self.systemProfile)

        self.applicationModel = ZBlogApplicationModel()
        self.applicationModel.setSystemProfile(self.systemProfile)
        self.applicationModel.setResourceRegistry(self.resourceRegistry)

        setApplicationModel(self.applicationModel)

    # end __init__()

    # Set up global settings like path to bundle files, etc.
    def _initGlobalSettings(self):
        cmdLineParams = ZCommandLineParameters(sys.argv[1:])
        setCommandLineParameters(cmdLineParams)

        # Add an uncaught exception hook so that we can display a dialog if something bad happens.
        sys.excepthook = self.handleException

        # If the application is installed (not in dev-mode), redirect stderr and stdout.
        # FIXME (EPW) hook up the stderr/stdout to the logger at some point
        if getOSUtil().isInstalledAsExe():
            stdPath = getOSUtil().getApplicationDataDirectory()
            if isPortableEnabled():
                stdPath = getOSUtil().getInstallDirectory()

            stdoutFile = os.path.join(stdPath, u"stdout.txt") #$NON-NLS-1$
            stderrFile = os.path.join(stdPath, u"stderr.txt") #$NON-NLS-1$
            sys.stderr = open(stderrFile, u"w")  #$NON-NLS-1$
            sys.stdout = open(stdoutFile, u"w") #$NON-NLS-1$

        # Set up the string bundle path.
        installDir = os.path.join(getOSUtil().getInstallDirectory(), u"system/bundles") #$NON-NLS-1$
        os.environ[IZI18NConstants.BUNDLE_PATH_ENV_VAR] = installDir

        # The MakeActiveXClass wrapper must be explicitely imported or
        # else instantiating the mshtml wrapper will hard-crash :(
        # FIXME (EPW) move this into an osutil init phase - to eliminate a dependency on Win32 stuff
        from wx.lib.activexwrapper import MakeActiveXClass #@UnusedImport
                
    # end _initGlobalSettings()
    
    def _initProxyConfiguration(self):
        # Get proxy settings from user prefs.        
        userProfile = self.applicationModel.getUserProfile()
        prefs = userProfile.getPreferences()
        enabled = prefs.getUserPreferenceBool(IZAppUserPrefsKeys.PROXY_ENABLE, False)
        host = prefs.getUserPreference(IZAppUserPrefsKeys.PROXY_HOST, u"") #$NON-NLS-1$
        port = prefs.getUserPreferenceInt(IZAppUserPrefsKeys.PROXY_PORT, u"") #$NON-NLS-1$
        username = prefs.getUserPreference(IZAppUserPrefsKeys.PROXY_USERNAME, u"") #$NON-NLS-1$
        password = prefs.getUserPreference(IZAppUserPrefsKeys.PROXY_PASSWORD, u"") #$NON-NLS-1$
        if password:
            password = crypt.decryptCipherText(password, PASSWORD_ENCRYPTION_KEY)
        proxy = ZHttpProxyConfiguration()
        proxy.setEnable(enabled)
        proxy.setHost(host)
        if port > 0:
            proxy.setPort(port)
        proxy.setProxyAuthorization(username, password)
    # end _initProxyConfiguration()

    def handleException(self, type, value, tb):
        # Log the exception in the logger
        zexception = None
        if isinstance(value, ZException):
            zexception = value
        elif isinstance(value, Exception):
            zexception = ZException(rootCause = value)
        else:
            zexception = ZException(unicode(value), None, (type, value, tb))
        getLoggerService().exception(zexception)
        # Show the error to the user.
        ZShowExceptionWithFeedback(getApplicationModel().getTopWindow(), zexception)
    # end handleException()

    def run(self):
        from zoundry.blogapp.startup import RavenApplicationStartup
        from zoundry.blogapp.ui.appwindow import ZRavenApplicationWindow
        from zoundry.blogapp.ui.splash import ZStartupWindow

        client = ZRavenRPCClient()

        # First, check for blogThis
        blogThisInfo = checkCmdLineForBlogThis()
        if blogThisInfo is not None:
            client.blogThis(blogThisInfo)

        # Only allow one instance of the application to be running.
        if client.getVersion() is not None:
            client.bringToFront()
            return

        # Create the user profile (return if none is found/chosen)
        userProfile = self._createUserProfile()
        if not userProfile:
            return
        self.applicationModel.setUserProfile(userProfile)
        
        # set http proxy settings based on userprofile config
        self._initProxyConfiguration()

        # Startup the Engine (load plugins, etc...)
        splashApp = wx.PySimpleApp()
        try:
            splashWindow = ZStartupWindow()
            appStartup = RavenApplicationStartup(self.applicationModel, splashWindow)
            appStartup.start()
            splashApp.MainLoop()

            if appStartup.hasStartupErrors():
                raise ZBlogAppException(_extstr(u"raven.StartupErrorsFoundMsg")) #$NON-NLS-1$
        except Exception, e:
            ZShowExceptionMessage(None, e)
        del splashApp

        # Create the main application window.
        mainApp = wx.PySimpleApp()
        try:
            mainWindow = ZRavenApplicationWindow()
            self.applicationModel.setTopWindow(mainWindow)
            mainApp.MainLoop()
        except Exception, e:
            ZShowExceptionMessage(None, e)
        del mainApp

        # Now that the UI has been closed, we need to stop the engine.
        self.applicationModel.getEngine().stop()
    # end run()

    def _createSystemProfile(self):
        factory = ZSystemProfileFactory()
        path = os.path.join(getOSUtil().getInstallDirectory(), u"system") #$NON-NLS-1$
        return factory.createSystemProfile(SYSTEM_PROFILE_TYPE_FILE, path)
    # end _createSystemProfile()

    def _createUserProfile(self):
        from zoundry.blogapp.ui.profile.manager import ZUserProfileManager

        profile = None
        profileModel = ZProfileManagerModel()

        # Choose a profile, either by popping up the dialog, by taking the
        # default, or by honoring the command line param.
        if profileModel.isCommandLineSpecified():
            profile = profileModel.getCommandLineProfile()
        if profileModel.isBypassDialog():
            defaultProfileName = profileModel.getDefaultProfileName()
            profile = profileModel.getProfile(defaultProfileName)

        # Pop up the user profile manager (allows for creating new profiles and choosing a profile to use).
        if not profile:
            rvalMap = {}
            userProfileApp = wx.PySimpleApp()
            ZUserProfileManager(rvalMap, profileModel, self.systemProfile)
            userProfileApp.MainLoop()
            # If nothing set, then cancel was hit and we should just return.
            if not rvalMap.has_key(u"user-profile-name"): #$NON-NLS-1$
                return
            profileName = rvalMap[u"user-profile-name"] #$NON-NLS-1$
            profile = profileModel.getProfile(profileName)

        if not profile:
            raise ZBlogAppException(_extstr(u"raven.ErrorFindingProfile")) #$NON-NLS-1$

        factory = ZUserProfileFactory()
        return factory.createUserProfile(USER_PROFILE_TYPE_FILE, profile.getPath()) #$NON-NLS-1$
    # end _createUserProfile()

# end RavenApplication


# The Main entry point into the Raven application.  This creates a new instances of the
# RavenApplication class and then runs it.
def main():
    try:
        app = RavenApplication()
        app.run()
    except Exception, e:
        ZException(e).printStackTrace()
        # Need to do something here - show some kind of UI message.
        raise e
# end main()

main()

