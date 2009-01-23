from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.widgets.dialogs.progress import ZShowProgressDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.appframework.util.osutilfactory import ZOSUtilFactory
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.util import fileutil
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.profile.wlwimporter import ZLiveWriterProfileImporter
from zoundry.blogapp.profile.zbwimporter import ZBlogWriterProfileImporter
from zoundry.blogapp.ui.profile.importprofile import ZImportWLWProfileDialog
from zoundry.blogapp.ui.profile.importprofile import ZImportZBWProfileDialog
import os
import wx

# ------------------------------------------------------------------------------
# Action for importing a profile from Zoundry Blog Writer.
# ------------------------------------------------------------------------------
class ZBaseImportAction(ZMenuAction):

    def __init__(self, manager, model):
        self.manager = manager
        self.model = model
    # end __init__()

# end ZImportFromZBWAction


# ------------------------------------------------------------------------------
# Action for importing a profile from Zoundry Blog Writer.
# ------------------------------------------------------------------------------
class ZImportFromZBWAction(ZBaseImportAction):

    def __init__(self, manager, model):
        ZBaseImportAction.__init__(self, manager, model)
    # end __init__()

    def getDisplayName(self):
        return u"From Zoundry Blog Writer..." #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return u"Import your Zoundry Blog Writer profile into Raven." #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        try:
            dialog = ZImportZBWProfileDialog(self.manager, self.model)
            dialog.setProfileName(_extstr(u"importactions.ImportedZBWProfile")) #$NON-NLS-1$
            dialog.setJoeyProfilePath(self._detectZBWProfilePath())
            defaultProfilePath = self.manager._createProfilePath(u"ImportedProfileZBW") #$NON-NLS-1$
            if not os.path.exists(defaultProfilePath):
                dialog.setProfilePath(defaultProfilePath)
            dialog.CentreOnParent()
            if dialog.ShowModal() == wx.ID_OK:
                profileInfo = dialog.getProfileInfo()
                joeyProfilePath = dialog.getPathToJoeyProfile()
                importer = ZBlogWriterProfileImporter(joeyProfilePath, profileInfo[1], self.manager.systemProfile)
                if ZShowProgressDialog(self.manager, _extstr(u"manager.ImportingZBW1XProfile"), importer) == wx.ID_OK: #$NON-NLS-1$
                    self.model.createProfile(profileInfo)
                    self.manager.profilesListView.refresh()
                    self.manager.profilesListView.Select(self.manager._getProfileIndex(profileInfo[0]), True)
                else:
                    # Cancelled - remove any files we may have created.
                    fileutil.deleteDirectory(profileInfo[1], False)
            dialog.Destroy()
        except Exception, e:
            ZShowExceptionMessage(self.manager, e)
    # end runAction()

    def _detectZBWProfilePath(self):
        osutil = getOSUtil()
        if osutil.getOperatingSystemId() == u"win32": #$NON-NLS-1$
            from zoundry.blogapp.profile.zbwimporter import getZBWProfilePath
            path = getZBWProfilePath()
            if path:
                return path
        return u"" #$NON-NLS-1$
    # end _detectZBWProfilePath()

# end ZImportFromZBWAction


# ------------------------------------------------------------------------------
# Action for importing a profile from Windows Live Writer.
# ------------------------------------------------------------------------------
class ZImportFromWLWAction(ZBaseImportAction):

    def __init__(self, manager, model):
        ZBaseImportAction.__init__(self, manager, model)
    # end __init__()

    def getDisplayName(self):
        return u"From Windows Live Writer..." #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return u"Import your Windows Live Writer profile into Raven." #$NON-NLS-1$
    # end getDescription()

    def isVisible(self, context): #@UnusedVariable
        return ZOSUtilFactory()._isWin32()
    # end isVisible()

    def isEnabled(self, context): #@UnusedVariable
        from zoundry.blogapp.profile.wlwimporter import isLiveWriterInstalled
        return isLiveWriterInstalled()
    # end isEnabled()

    def runAction(self, actionContext): #@UnusedVariable
        try:
            dialog = ZImportWLWProfileDialog(self.manager, self.model)
            dialog.setProfileName(_extstr(u"importactions.ImportedWLWProfile")) #$NON-NLS-1$
            defaultProfilePath = self.manager._createProfilePath(u"ImportedProfileWLW") #$NON-NLS-1$
            if not os.path.exists(defaultProfilePath):
                dialog.setProfilePath(defaultProfilePath)
            dialog.CentreOnParent()
            if dialog.ShowModal() == wx.ID_OK:
                profileInfo = dialog.getProfileInfo()
                importer = ZLiveWriterProfileImporter(None, profileInfo[1], self.manager.systemProfile)
                if ZShowProgressDialog(self.manager, _extstr(u"importactions.ImportingWLWProfile"), importer) == wx.ID_OK: #$NON-NLS-1$
                    self.model.createProfile(profileInfo)
                    self.manager.profilesListView.refresh()
                    self.manager.profilesListView.Select(self.manager._getProfileIndex(profileInfo[0]), True)
                else:
                    # Cancelled - remove any files we may have created.
                    fileutil.deleteDirectory(profileInfo[1], False)
            dialog.Destroy()
        except Exception, e:
            ZShowExceptionMessage(self.manager, e)
    # end runAction()

# end ZImportFromWLWAction


# ------------------------------------------------------------------------------
# Action that will look for the presence of Zoundry Blog Writer 1.0 or Windows
# Live Writer.  If either of those is present, the action will prompt the user
# to import.
# ------------------------------------------------------------------------------
class ZDetectImportAction(ZBaseImportAction):

    def __init__(self, manager, model):
        ZBaseImportAction.__init__(self, manager, model)
    # end __init__()

    def runAction(self, context): #@UnusedVariable
        # Don't attempt to auto-import unless we have no profiles.
        if ZOSUtilFactory()._isWin32() and self.model.getNumProfiles() == 0:
            if self._isZoundryBlogWriterInstalled():
                self._doImportFromZBW(context)
            if self._isLiveWriterInstalled():
                self._doImportFromWLW(context)
    # end runAction()

    def _isZoundryBlogWriterInstalled(self):
        from zoundry.blogapp.profile.zbwimporter import isZoundryBlogWriterInstalled
        return isZoundryBlogWriterInstalled()
    # end _isZoundryBlogWriterInstalled()

    def _isLiveWriterInstalled(self):
        from zoundry.blogapp.profile.wlwimporter import isLiveWriterInstalled
        return isLiveWriterInstalled()
    # end _isLiveWriterInstalled()

    def _doImportFromZBW(self, context):
        if ZShowYesNoMessage(self.manager, _extstr(u"importactions.ZBWDetectedMessage"), _extstr(u"importactions.ZBWDetectedTitle")): #$NON-NLS-2$ #$NON-NLS-1$
            action = ZImportFromZBWAction(self.manager, self.model)
            action.runAction(context)
    # end _doImportFromZBW()

    def _doImportFromWLW(self, context):
        if ZShowYesNoMessage(self.manager, _extstr(u"importactions.WLWDetectedMessage"), _extstr(u"importactions.WLWDetectedTitle")): #$NON-NLS-2$ #$NON-NLS-1$
            action = ZImportFromWLWAction(self.manager, self.model)
            action.runAction(context)
    # end _doImportFromWLW()

# end ZDetectImportAction

