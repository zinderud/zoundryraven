from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
import wx

# -------------------------------------------------------------------------------------
# Convenience function for creating a password entry dialog, displaying it, and then
# returning the password that was entered (or None if cancelled).
# -------------------------------------------------------------------------------------
def ZShowPasswordEntryDialog(parent, title):
    u"""ZShowPasswordEntryDialog(wx.Window, string) -> string
    Convenience function that pops up a dialog for getting an
    password from the user.""" #$NON-NLS-1$

    rval = None

    dlg = ZPasswordEntryDialog(parent, title)
    dlg.CentreOnParent()
    if dlg.ShowModal() == wx.ID_OK:
        rval = dlg.getPassword()

    if parent is not None:
        parent.RemoveChild(dlg)

    dlg.Destroy()
    return rval
# end ZShowPasswordEntryDialog()


# -------------------------------------------------------------------------------------
# A dialog that will prompt the user to enter a password.
# -------------------------------------------------------------------------------------
class ZPasswordEntryDialog(ZHeaderDialog):

    def __init__(self, parent, title):
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, title)
        # Tell the dialog to resize itself to best-fit its children.
    
        self.Fit()
    # end __init__()

    def getPassword(self):
        return self.passwordText.GetValue()
    # end getPassword()

    def _createNonHeaderWidgets(self):
        self.passwordLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"password.Password:")) #$NON-NLS-1$
        self.passwordText = wx.TextCtrl(self, wx.ID_ANY, size=wx.Size(300, -1), style = wx.TE_PASSWORD)
        self.staticLine = wx.StaticLine(self)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        pass
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        flexGridSizer = wx.FlexGridSizer(3, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.passwordLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        flexGridSizer.Add(self.passwordText, 0, wx.EXPAND | wx.ALL, 5)

        boxSizer = wx.BoxSizer(wx.VERTICAL)
        boxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 8)
        boxSizer.Add(self.staticLine, 0, wx.EXPAND)
        
        return boxSizer
    # end _layoutNonHeaderWidgets()

    def _getNonHeaderContentBorder(self):
        return 0
    # end _getNonHeaderContentBorder()

    def _getHeaderTitle(self):
        return _extstr(u"password.PasswordEntry") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"password.PasswordDialogHeaderMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/widgets/pass_dialog/lock.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _setInitialFocus(self):
        self.passwordText.SetFocus()
    # end _setInitialFocus()

# end ZPasswordEntryDialog
