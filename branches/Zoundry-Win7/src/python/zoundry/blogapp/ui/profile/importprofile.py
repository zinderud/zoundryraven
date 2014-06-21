from zoundry.appframework.ui.widgets.controls.common.filechooser import ZFCC_DIRECTORY_TYPE
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
from zoundry.appframework.ui.widgets.controls.validating.vfilechooser import ZValidatingFileChooserCtrl
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.profile.newprofile import ZNewProfileDialog
import os
import wx

# -------------------------------------------------------------------------------------
# Class used to validate the value of the Joey Profile Path text box.
# -------------------------------------------------------------------------------------
class ZProfileJoeyPathValidator(ZBaseControlValidator):

    def __init__(self):
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"importprofile.ZBW1XProfileMissing")) #$NON-NLS-1$

        if not os.path.exists(value):
            return self._setReason(_extstr(u"importprofile.ZBW1XProfileMissing")) #$NON-NLS-1$

        configPath = os.path.join(value, u"joey-user-config.xml") #$NON-NLS-1$
        if not os.path.exists(configPath):
            return self._setReason(_extstr(u"importprofile.ZBW1XProfileMissing")) #$NON-NLS-1$

        return True
    # end _isValid()

# end ZProfileJoeyPathValidator


# ------------------------------------------------------------------------------
# Dialog that lets the user specify an existing Zoundry Blog Writer 1.x profile
# to import.  This dialog extensd the new profile dialog and overrides various
# methods in order to add the additional "old profile path" input.
# ------------------------------------------------------------------------------
class ZImportZBWProfileDialog(ZNewProfileDialog):

    def __init__(self, parent, profilesModel):
        ZNewProfileDialog.__init__(self, parent, profilesModel)
    # end __init__()

    def getPathToJoeyProfile(self):
        return self.profileJoeyPathCtrl.getPath()
    # end getPathToJoeyProfile()

    def _createNonHeaderWidgets(self):
        self.profileJoeyPathLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"importprofile.OldProfilePath:")) #$NON-NLS-1$
        self.profileJoeyPathCtrl = ZValidatingFileChooserCtrl(ZProfileJoeyPathValidator(), self, ZFCC_DIRECTORY_TYPE, _extstr(u"importprofile.ChoosePathDialogTitle")) #$NON-NLS-1$
        self.profileJoeyPathCtrl.SetToolTipString(_extstr(u"importprofile.EnterZBW1XPathTooltip")); #$NON-NLS-1$
        ZNewProfileDialog._createNonHeaderWidgets(self)
    # end _createNonHeaderWidgets()

    def _layoutAdditionalNonHeaderWidgets(self, sizer): #@UnusedVariable
        sizer.Add(self.profileJoeyPathLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.profileJoeyPathCtrl, 0, wx.EXPAND | wx.RIGHT, 5)
    # end _layoutAdditionalNonHeaderWidgets()
    
    def setJoeyProfilePath(self, joeyProfilePath):
        self.profileJoeyPathCtrl.setPath(joeyProfilePath)
    # end setJoeyProfilePath()

    def _bindWidgetEvents(self):
        ZNewProfileDialog._bindWidgetEvents(self)

        self._bindValidatingWidget(self.profileJoeyPathCtrl)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self.profileJoeyPathCtrl.SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return _extstr(u"importprofile.ImportProfile") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"importprofile.ImportDialogHeaderMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/profile/import_dialog/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

# end ZImportZBWProfileDialog


# -------------------------------------------------------------------------------------
# The Import from Windows Live Writer Profile dialog.  This dialog prompts the 
# user for information in order to import a WLW profile into Raven.
# -------------------------------------------------------------------------------------
class ZImportWLWProfileDialog(ZNewProfileDialog):

    def __init__(self, parent, profilesModel):
        ZNewProfileDialog.__init__(self, parent, profilesModel)
    # end __init__()

    def _getHeaderTitle(self):
        return _extstr(u"importprofile.ImportHeader") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"importprofile.ImportMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/profile/new_dialog/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

# end ZImportWLWProfileDialog
