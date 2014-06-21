from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
import wx

# -------------------------------------------------------------------------------------
# Convenience function for creating a simple data entry dialog, displaying it, and then
# returning the data that was entered (or None if cancelled).
# -------------------------------------------------------------------------------------
def ZShowDataEntryDialog(parent, title, label):
    u"""ZShowDataEntryDialog(wx.Window, string, string) -> string
    Convenience function for getting some data input from
    the user.  Returns None if the user cancels.""" #$NON-NLS-1$

    rval = None

    dlg = ZDataEntryDialog(parent, title, label)
    dlg.CentreOnParent()
    if dlg.ShowModal() == wx.ID_OK:
        rval = dlg.getData()

    if parent is not None:
        parent.RemoveChild(dlg)

    dlg.Destroy()
    return rval
# end ZShowDataEntryDialog()


# -------------------------------------------------------------------------------------
# A dialog that will prompt the user to enter some information/data.
# -------------------------------------------------------------------------------------
class ZDataEntryDialog(ZHeaderDialog):

    def __init__(self, parent, title, label):
        self.title = title
        self.label = label

        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, title)

        self.Fit()
    # end __init__()

    def getData(self):
        return self.dataWidget.GetValue()
    # end getData()

    def _createDataWidget(self):
        return wx.TextCtrl(self, wx.ID_ANY, size=wx.Size(280, -1))
    # end _createDataWidget()

    def _populateDataWidget(self):
        pass
    # end _populateDataWidget()

    def _createNonHeaderWidgets(self):
        self.dataLabel = wx.StaticText(self, wx.ID_ANY, self.label)
        self.dataWidget = self._createDataWidget()
        self.staticLine = wx.StaticLine(self)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self._populateDataWidget()
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        flexGridSizer = wx.FlexGridSizer(3, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.dataLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        flexGridSizer.Add(self.dataWidget, 0, wx.EXPAND | wx.ALL, 5)

        boxSizer = wx.BoxSizer(wx.VERTICAL)
        boxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 8)
        boxSizer.Add(self.staticLine, 0, wx.EXPAND)

        return boxSizer
    # end _layoutNonHeaderWidgets()

    def _getNonHeaderContentBorder(self):
        return 0
    # end _getNonHeaderContentBorder()

    def _getHeaderTitle(self):
        return self.title
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"input.GenericInputDialogMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/widgets/input_dialog/input.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _setInitialFocus(self):
        self.dataWidget.SetFocus()
    # end _setInitialFocus()

# end ZDataEntryDialog
