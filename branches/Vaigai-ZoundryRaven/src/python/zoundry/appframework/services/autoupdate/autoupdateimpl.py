from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.autoupdate.autoupdate import IZAutoUpdateService
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.util.zthread import ZThread
import string
import time

# ------------------------------------------------------------------------------
# Class encapsulating the "latest version info" pulled down from the Zoundry
# web site.
# ------------------------------------------------------------------------------
class ZLatestVersionInfo:

    def __init__(self, versionDoc):
        self.buildDate = versionDoc.selectSingleNodeText(u"/version/version-date") #$NON-NLS-1$
        self.major = string.atoi(versionDoc.selectSingleNodeText(u"/version/major-version")) #$NON-NLS-1$
        self.minor = string.atoi(versionDoc.selectSingleNodeText(u"/version/minor-version")) #$NON-NLS-1$
        self.build = string.atoi(versionDoc.selectSingleNodeText(u"/version/build-version")) #$NON-NLS-1$
        self.modifier = versionDoc.selectSingleNodeText(u"/version/version-modifier") #$NON-NLS-1$
    # end __init__()

    def getFullVersionString(self):
        ver = u"%d.%d.%d %s" % (self.major, self.minor, self.build, self.modifier) #$NON-NLS-1$
        return ver.strip()
    # end getFullVersionString()

    def getBuildDate(self):
        return self.buildDate
    # end getBuildDate()

    def getMajorVersion(self):
        return self.major
    # end getMajorVersion()

    def getMinorVersion(self):
        return self.minor
    # end getMinorVersion()

    def getBuild(self):
        return self.build
    # end getBuild()

# end ZLatestVersionInfo


# ------------------------------------------------------------------------------
# Helper class to show an info message on the UI thread.
# ------------------------------------------------------------------------------
class ZAutoUpdateMessageRunner(IZRunnable):
    
    def __init__(self, title, message, isUpToDate):
        self.isUpToDate = isUpToDate
        self.title = title
        self.message = message
    # end __init__()

    def run(self):
        appModel = getApplicationModel()
        if self.isUpToDate:
            ZShowInfoMessage(appModel.getTopWindow(), self.message, self.title)
        else:
            if ZShowYesNoMessage(appModel.getTopWindow(), self.message, self.title):
                osutil = getOSUtil()
                osutil.openUrlInBrowser(u"http://www.zoundryraven.com/download.html") #$NON-NLS-1$
    # end run()

# end ZAutoUpdateMessageRunner


# ------------------------------------------------------------------------------
# Implementation for the auto-update service.
#
# FIXME (EPW) need a check-for-updates preference page
# ------------------------------------------------------------------------------
class ZAutoUpdateService(IZAutoUpdateService):

    def __init__(self):
        self.versionXmlUrl = u"http://www.zoundry.com/raven/updates/latest-version.xml?ref=ZoundryRaven&guid=%s&build=%s" #$NON-NLS-1$

        self.logger = None
        self.stopped = False
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"Auto-Update Service started.") #$NON-NLS-1$
        self.stopped = False

        runner = ZAutoUpdateRunnable(self, True)
        thread = ZThread(runner, u"AutoUpdate", True) #$NON-NLS-1$
        thread.start()
    # end start()

    def stop(self):
        self.stopped = True
    # end stop()

    def checkForUpdate(self, onlyPromptWhenNewVersionIsAvailable = True):
        runner = ZAutoUpdateRunnable(self, onlyPromptWhenNewVersionIsAvailable)
        thread = ZThread(runner, u"AutoUpdate", True) #$NON-NLS-1$
        thread.start()
    # end checkForUpdate()

    def _doCheckForUpdate(self, onlyPromptWhenNewVersionIsAvailable = True):
        appModel = getApplicationModel()
        appVersion = appModel.getVersion()
        latestVersion = self.getLatestVersionInfo()

        if latestVersion and appVersion.getBuild() < latestVersion.getBuild():
            currVer = appVersion.getFullVersionString()
            latestVer = latestVersion.getFullVersionString()
            msg = _extstr(u"autoupdateimpl.NewVersionMessage") % (currVer, latestVer) #$NON-NLS-1$
            title = _extstr(u"autoupdateimpl.NewVersionAvailable") #$NON-NLS-1$
            fireUIExecEvent(ZAutoUpdateMessageRunner(title, msg, False), appModel.getTopWindow())
        elif not onlyPromptWhenNewVersionIsAvailable:
            msg = _extstr(u"autoupdateimpl.AlreadyUpToDateMsg") #$NON-NLS-1$
            title = _extstr(u"autoupdateimpl.AlreadyUpToDateTitle") #$NON-NLS-1$
            fireUIExecEvent(ZAutoUpdateMessageRunner(title, msg, True), appModel.getTopWindow())
    # end _doCheckForUpdate()

    def getLatestVersionInfo(self):
        appModel = getApplicationModel()
        build = unicode(appModel.getVersion().getBuild())
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        guid = userPrefs.getUserPreference(IZAppUserPrefsKeys.GUID, u"") #$NON-NLS-1$
        url = self.versionXmlUrl % (guid, build)
        self.logger.debug(u"Getting latest version at URL: %s" % url) #$NON-NLS-1$
        request = ZSimpleXmlHTTPRequest(url)
        try:
            if request.send():
                return ZLatestVersionInfo(request.getResponse())
        except Exception, e:
            self.logger.exception(e)
        return None
    # end getLatestVersionInfo()

# end ZAutoUpdateService


# ------------------------------------------------------------------------------
# Runnable responsible for doing the auto-update check in the background.
# ------------------------------------------------------------------------------
class ZAutoUpdateRunnable(IZRunnable):
    
    def __init__(self, service, onlyPromptWhenNewVersionIsAvailable, delay = 0):
        self.service = service
        self.onlyPromptWhenNewVersionIsAvailable = onlyPromptWhenNewVersionIsAvailable
        self.delay = delay
    # end __init__()

    def run(self):
        if self.delay > 0:
            time.sleep(self.delay)
        if not self.service.stopped:
            self.service._doCheckForUpdate(self.onlyPromptWhenNewVersionIsAvailable)
    # end run()

# end ZAutoUpdateRunnable
