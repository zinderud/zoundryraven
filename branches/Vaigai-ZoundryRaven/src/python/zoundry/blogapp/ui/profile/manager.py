from zoundry.appframework.util.portableutil import isPortableEnabled
from wx.html import HW_NO_SELECTION #@UnresolvedImport
from wx.html import HW_SCROLLBAR_NEVER #@UnresolvedImport
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.events.commonevents import ZEVT_UIEXEC
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoCancelMessage
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.profile.importactions import ZDetectImportAction
from zoundry.blogapp.ui.profile.importactions import ZImportFromWLWAction
from zoundry.blogapp.ui.profile.importactions import ZImportFromZBWAction
from zoundry.blogapp.ui.profile.newprofile import ZNewProfileDialog
import os
import wx
import zoundry.appframework.messages

ICON_IMAGES = [
    u"images/profile/manager/icon16x16.png", #$NON-NLS-1$
    u"images/profile/manager/icon24x24.png", #$NON-NLS-1$
    u"images/profile/manager/icon32x32.png", #$NON-NLS-1$
    u"images/profile/manager/icon48x48.png" #$NON-NLS-1$
]

# FIXME (EPW) link to online help Re: profiles
HEADER_HTML = u"""
  <html>
    <body link="#666699">
      <table cellspacing="0" cellpadding="8" bgcolor="#FFFFFF" width="100%%">
        <tr>
          <td>
            <font size="-1"><b>%(header_header)s - </b></font>
            <font size="-1">%(header_message)s</font>
          </td>
          <td><img src="%(header_image)s"></td>
        </tr>
      </table>
    </body>
  </html>
""" #$NON-NLS-1$

# -------------------------------------------------------------------------------------------
# The content provider for the profile list view.  This content provider uses the model to
# provide the actual list view content.
# -------------------------------------------------------------------------------------------
class ZProfileListContentProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model

        cstyle = wx.LIST_FORMAT_LEFT
        self.columnInfo = [
            (_extstr(u"manager.Name"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30), #$NON-NLS-1$
            (_extstr(u"manager.Path"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 70) #$NON-NLS-1$
        ]
    # end __init__()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return 2
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model)
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columnInfo[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        profile = self.model[rowIndex]
        if not profile:
            return u"" #$NON-NLS-1$
        elif columnIndex == 0:
            return profile.getName()
        elif columnIndex == 1:
            return profile.getPath()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

# end ZProfileListContentProvider


# -------------------------------------------------------------------------------------------
# This dialog allows the user to choose, create, and delete profiles.  The user MUST choose
# a profile using this dialog in order to run the Raven application.
# -------------------------------------------------------------------------------------------
class ZUserProfileManager(wx.Frame):

    # Note: rvalMap is a map that holds all of the return values of this manager (if any).  This is
    # a workaround since once the window has closed, we cannot call methods on it anymore.
    def __init__(self, rvalMap, model, systemProfile):
        self.rvalMap = rvalMap
        self.model = model
        self.systemProfile = systemProfile
        self.selectedIndex = -1
        self.importMenuModel = self._createImportMenuModel()
        title = _extstr(u"manager.WindowTitle") #$NON-NLS-1$
        portable = _extstr(u"manager.Portable") #$NON-NLS-1$
        if isPortableEnabled():
            title = u"%s (%s)" % (title, portable) #$NON-NLS-1$

        wx.Frame.__init__(self, None, wx.ID_ANY, title, size=wx.Size(400, 325),
                          style = wx.DEFAULT_FRAME_STYLE)
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        self.CentreOnScreen()
        self.SetIcons(getResourceRegistry().getIconBundle(ICON_IMAGES))
        self.Show(True)

        # Auto-select the 'default' profile.
        defaultName = self.model.getDefaultProfileName()
        if defaultName:
            self.profilesListView.Select(self._getProfileIndex(defaultName), True)

        # Now set focus on the profileListView
        self.profilesListView.SetFocus()

        # Fire a UI exec event - detect ZBW or WLW on startup
        fireUIExecEvent(ZMethodRunnable(self.onDetectImport), self)
    # end __init__()

    def _getProfileIndex(self, profileName):
        for i in range(0, len(self.model)):
            profile = self.model[i]
            if profile.getName() == profileName:
                return i
        return -1
    # end _getProfileIndex()

    def _createWidgets(self):
        self.panel = wx.Panel(self, wx.ID_ANY)

        # The header
        self.headerHTML = self._createHeaderHTMLControl()
        self.headerStaticLine = wx.StaticLine(self.panel)

        # The "Profiles" static section
        self.staticBox = wx.StaticBox(self.panel, label = _extstr(u"manager.Profiles")) #$NON-NLS-1$
        self.profilesListView = self._createProfilesListControl()
        self.addButton = wx.Button(self.panel, wx.ID_ANY, _extstr(u"manager.New")) #$NON-NLS-1$
        self.importButton = wx.Button(self.panel, wx.ID_ANY, _extstr(u"manager.Import")) #$NON-NLS-1$
        self.deleteButton = wx.Button(self.panel, wx.ID_ANY, _extstr(u"manager.Delete")) #$NON-NLS-1$
        self.deleteButton.Enable(False)

        self.bypassCheckBox = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"manager.DoNotShowProfileDialog")) #$NON-NLS-1$
        self.bypassCheckBox.SetToolTipString(_extstr(u"manager.BypassCheckboxTooltip")) #$NON-NLS-1$
        self.bypassStaticLine = wx.StaticLine(self.panel)

        # The ok/cancel buttons.
        self.okButton = wx.Button(self.panel, wx.ID_OK, zoundry.appframework.messages._extstr(u"OK")) #$NON-NLS-1$
        self.okButton.Enable(False)
        self.cancelButton = wx.Button(self.panel, wx.ID_CANCEL, zoundry.appframework.messages._extstr(u"Cancel")) #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        self.profileButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.profileButtonSizer.Add(self.addButton, 0, wx.ALL, 1)
        self.profileButtonSizer.Add(self.importButton, 0, wx.ALL, 1)
        self.profileButtonSizer.Add(self.deleteButton, 0, wx.ALL, 1)

        self.staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        self.staticBoxSizer.Add(self.profilesListView, 1, wx.EXPAND | wx.ALL, 2)
        self.staticBoxSizer.AddSizer(self.profileButtonSizer, 0, wx.ALL, 2)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add(self.okButton, 0, wx.ALL, 1)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALL, 1)

        # Now create the overall box sizer
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.headerHTML, 0, wx.EXPAND)
        box.Add(self.headerStaticLine, 0, wx.EXPAND)
        box.AddSizer(self.staticBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.Add(self.bypassCheckBox, 0, wx.ALL, 8)
        box.Add(self.bypassStaticLine, 0, wx.EXPAND)
        box.AddSizer(self.buttonSizer, 0, wx.ALIGN_RIGHT |wx.ALL, 5)
        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(box)
        self.panel.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_UIEXEC, self.onUIExec)

        # Bind the OK/Cancel button events.
        self.Bind(wx.EVT_BUTTON, self.onOk, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelButton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOk, self.profilesListView)

        # Bind the Add/Delete profile button events.
        self.Bind(wx.EVT_BUTTON, self.onAddProfile, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.onImportProfile, self.importButton)
        self.Bind(wx.EVT_BUTTON, self.onDeleteProfile, self.deleteButton)

        # Bind the Profiles list control events.
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onProfileSelected, self.profilesListView)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onProfileDeselected, self.profilesListView)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        self.headerHTML.SetPage(self._loadHeaderHTML())
    # end _populateWidgets()

    def _createHeaderHTMLControl(self):
        html = ZHTMLControl(self.panel, size = wx.Size(-1, 64), style = HW_SCROLLBAR_NEVER | HW_NO_SELECTION)
        html.SetBorders(1)
        return html
    # end _createHeaderHTMLControl()

    def _createProfilesListControl(self):
        # Now create the list control.
        provider = ZProfileListContentProvider(self.model)
        return ZListViewEx(provider, self.panel, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_HRULES | wx.LC_SINGLE_SEL)
    # end _createProfilesListControl()

    def _loadHeaderHTML(self):
        return HEADER_HTML % {
            u"header_header" : _extstr(u"manager.Profiles"), #$NON-NLS-1$ #$NON-NLS-2$
            u"header_message" : _extstr(u"manager.DialogUseMsg"), #$NON-NLS-1$ #$NON-NLS-2$
            u"header_image" : getResourceRegistry().getImagePath(u"images/profile/manager/header_image.png") #$NON-NLS-1$ #$NON-NLS-2$
        }
    # end _loadHeaderHTML()

    def onOk(self, event):
        profile = self.model[self.selectedIndex]
        self.rvalMap[u"user-profile-name"] = profile.getName() #$NON-NLS-1$
        self.model.setDefaultProfileName(profile.getName())
        self.model.setBypassDialog(self.bypassCheckBox.IsChecked())
        self.Close()
        event.Skip()
    # end onOK()

    def onCancel(self, event):
        self.Close()
        event.Skip()
    # end onCancel()

    def onDetectImport(self):
        osutil = getOSUtil()
        if osutil.getOperatingSystemId() == u"win32": #$NON-NLS-1$
            action = ZDetectImportAction(self, self.model)
            context = ZMenuActionContext(self)
            action.runAction(context)
            pass
    # end onDetectImport()

    def onAddProfile(self, event):
        try:
            dialog = ZNewProfileDialog(self, self.model)
            if self.model.getNumProfiles() == 0:
                defaultPath = self._createDefaultProfilePath()
                dialog.setProfilePath(defaultPath)
                dialog.setProfileName(_extstr(u"manager.MyProfile")) #$NON-NLS-1$
            dialog.CentreOnParent()
            if dialog.ShowModal() == wx.ID_OK:
                profileInfo = dialog.getProfileInfo()
                self.model.createProfile(profileInfo)
                self.profilesListView.refresh()
                self.profilesListView.Select(self._getProfileIndex(profileInfo[0]), True)
            dialog.Destroy()
        except Exception, e:
            ZShowExceptionMessage(self, e)
        event.Skip()
    # end onAddProfile()

    def onImportProfile(self, event):
        context = ZMenuActionContext(self)
        menu = ZModelBasedMenu(self.importMenuModel, context, self)
        (w, h) = self.importButton.GetSizeTuple() #@UnusedVariable
        pos = wx.Point(1, h - 2)
        self.importButton.PopupMenu(menu, pos)
        event.Skip()
    # end onImportProfile()

    def onDeleteProfile(self, event):
        try:
            item = self.profilesListView.GetItem(self.selectedIndex, 0)
            profileName = item.GetText()

            # Prompt the user - do you want to delete all the files too?
            rval = ZShowYesNoCancelMessage(self, _extstr(u"manager.DeleteProfileConfirmMsg") % profileName, _extstr(u"manager.DeleteProfileTitle")) #$NON-NLS-2$ #$NON-NLS-1$
            if rval != wx.ID_CANCEL:
                self.model.deleteProfile(profileName, rval == wx.ID_YES)
                self.profilesListView.DeleteItem(self.selectedIndex)
        except Exception, e:
            ZShowExceptionMessage(self, e)
        event.Skip()
    # end onDeleteProfile()

    def onProfileSelected(self, event):
        self.okButton.Enable(True)
        self.deleteButton.Enable(True)
        self.selectedIndex = event.GetIndex()
        event.Skip()
    # end onProfileSelected()

    def onProfileDeselected(self, event):
        self.okButton.Enable(False)
        self.deleteButton.Enable(False)
        self.selectedIndex = -1
        event.Skip()
    # end onProfileDeselected()

    def onUIExec(self, event):
        event.getRunnable().run()
    # end onUIExec()

    def _createDefaultProfilePath(self):
        return self._createProfilePath(u"My Profile") #$NON-NLS-1$
    # end _createDefaultProfilePath()

    def _createProfilePath(self, name):
        profilesDir = self.model.getDefaultProfilesDirectory()
        return os.path.normpath(os.path.join(profilesDir, name))
    # end _createProfilePath()

    def _createImportMenuModel(self):
        menuModel = ZMenuModel()
        zbwId = menuModel.addMenuItemWithAction(_extstr(u"manager.FromZBW"), 0, ZImportFromZBWAction(self, self.model), None) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(zbwId, getResourceRegistry().getBitmap(u"images/common/zbw/BlogWriter.ico")) #$NON-NLS-1$
        wlwId = menuModel.addMenuItemWithAction(_extstr(u"manager.FromWLW"), 0, ZImportFromWLWAction(self, self.model), None) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(wlwId, getResourceRegistry().getBitmap(u"images/common/wlw/LiveWriter.png")) #$NON-NLS-1$
        return menuModel
    # end _createImportMenuModel()

# end ZUserProfileManager
