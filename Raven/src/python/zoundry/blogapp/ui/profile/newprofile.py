from zoundry.appframework.ui.widgets.controls.common.filechooser import ZFCC_DIRECTORY_TYPE
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
from zoundry.appframework.ui.widgets.controls.validating.vfilechooser import ZValidatingFileChooserCtrl
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.base.util import fileutil
from zoundry.blogapp.messages import _extstr
import os
import wx


# -------------------------------------------------------------------------------------
# Class used to validate the value of the new profile name.
# -------------------------------------------------------------------------------------
class ZProfileNameValidator(ZBaseControlValidator):

    def __init__(self, profilesModel):
        self.profilesModel = profilesModel
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"newprofile.ProfileNameMissing")) #$NON-NLS-1$

        profile = self.profilesModel.getProfile(value)
        if profile:
            return self._setReason(_extstr(u"newprofile.ProfileAlreadyExists") % value) #$NON-NLS-1$

        return True
    # end _isValid()

# end ZProfileNameValidator


# -------------------------------------------------------------------------------------
# Class used to validate the value of the new profile path.
# -------------------------------------------------------------------------------------
class ZProfilePathValidator(ZBaseControlValidator):

    def __init__(self):
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"newprofile.ProfilePathMissing")) #$NON-NLS-1$

        if os.path.exists(value):
            return self._isValidExistingDirectory(value)
        else:
            return self._isValidNonExistingDirectory(value)
    # end _isValid()

    def _isValidExistingDirectory(self, value):
        # Is the value a directory?
        if not os.path.isdir(value):
            return self._setReason(_extstr(u"newprofile.NotADirectoryError")) #$NON-NLS-1$

        # Is it an existing Raven profile?
        ravenConfigFilePath = os.path.join(value, u"config", u"user-properties.xml") #$NON-NLS-1$ #$NON-NLS-2$
        if os.path.isfile(ravenConfigFilePath):
            return True

        # If not, the directory must be writable and empty.

        if len(os.listdir(value)) > 0:
            return self._setReason(_extstr(u"newprofile.DirectoryNotEmptyError")) #$NON-NLS-1$

        if not fileutil.isDirectoryWritable(value):
            return self._setReason(_extstr(u"newprofile.DirectoryNotWritableError")) #$NON-NLS-1$

        return True
    # end _isValid()

    def _isValidNonExistingDirectory(self, value):
        parentDir = fileutil.findExistingParentDirectory(value)

        if not fileutil.isDirectoryWritable(parentDir):
            return self._setReason(_extstr(u"newprofile.DirectoryNotWritableError")) #$NON-NLS-1$

        return True
    # end _isValidNonExistingDirectory()

# end ZProfilePathValidator


# -------------------------------------------------------------------------------------
# The New Profile dialog.  This dialog prompts the user for information in order to
# create a new Zoundry Raven Profile.  A profile consists of a name and a path.
# -------------------------------------------------------------------------------------
class ZNewProfileDialog(ZValidatingHeaderDialog):

    def __init__(self, parent, profilesModel):
        self.profilesModel = profilesModel
        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"newprofile.CreateNewProfile")) #$NON-NLS-1$

        # Tell the dialog to resize itself to best-fit its children.
        self.Fit()
    # end __init__()

    def getProfileInfo(self):
        return ( self.profileNameText.GetValue(), self.profilePathCtrl.getPath() )
    # end getProfileInfo()

    def _createNonHeaderWidgets(self):
        self.profileInfoStaticBox = wx.StaticBox(self, label = _extstr(u"newprofile.ProfileInfo")) #$NON-NLS-1$
        self.profileNameLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"newprofile.Name:")) #$NON-NLS-1$
        self.profileNameText = ZValidatingTextCtrl(ZProfileNameValidator(self.profilesModel), self, wx.ID_ANY, size = wx.Size(325, -1))
        self.profileNameText.SetToolTipString(_extstr(u"newprofile.ProfileNameTooltip")) #$NON-NLS-1$
        self.profilePathLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"newprofile.Path:")) #$NON-NLS-1$
        self.profilePathCtrl = ZValidatingFileChooserCtrl(ZProfilePathValidator(), self, ZFCC_DIRECTORY_TYPE, _extstr(u"newprofile.ChooseAProfileLocation")) #$NON-NLS-1$
        self.profilePathCtrl.SetToolTipString(_extstr(u"newprofile.ProfilePathTooltip")) #$NON-NLS-1$
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        # populate with something?
        pass
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        # Flexible grid sizer where all of the label->text ctrl pairs will live
        flexGridSizer = wx.FlexGridSizer(3, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        # NOTE: Called so that the import profile dialog can add widgets.
        self._layoutAdditionalNonHeaderWidgets(flexGridSizer)
        flexGridSizer.Add(self.profileNameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.profileNameText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.profilePathLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.profilePathCtrl, 0, wx.EXPAND | wx.RIGHT, 5)

        # Static box sizer that has a label of "Profile Info"
        staticBoxSizer = wx.StaticBoxSizer(self.profileInfoStaticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 5)
        return staticBoxSizer
    # end _layoutNonHeaderWidgets()

    def _layoutAdditionalNonHeaderWidgets(self, sizer): #@UnusedVariable
        pass
    # end _layoutAdditionalNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.profileNameText)
        self._bindValidatingWidget(self.profilePathCtrl)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self.profileNameText.SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return _extstr(u"newprofile.NewProfile") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"newprofile.DialogUseMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/profile/new_dialog/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def setProfilePath(self, path):
        self.profilePathCtrl.setPath(path)
    # end setProfilePath()

    def setProfileName(self, name):
        self.profileNameText.SetValue(name)
    # end setProfileName()

# end ZNewProfileDialog
