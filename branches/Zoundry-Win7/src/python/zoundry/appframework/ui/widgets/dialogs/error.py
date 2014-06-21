from wx.html import HW_NO_SELECTION 
from wx.html import HW_SCROLLBAR_NEVER 
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
import wx

ERROR_HTML = u"""
  <html>
    <body link="#666699">
      <table cellspacing="0" cellpadding="5" bgcolor="#FFFFFF">
        <tr>
          <td valign="top"><img src="%(error_image)s"></td>
          <td valign="top">
            <font size="-1"><b>%(error_header)s: </b>'%(error_message)s'</font>
          </td>
        </tr>
      </table>
    </body>
  </html>
""" #$NON-NLS-1$

MODE_COMPACT = 0
MODE_EXPANDED = 1

COMPACT_DIALOG_HEIGHT = 135
EXPANDED_DIALOG_HEIGHT = 450
DIALOG_WIDTH = 550


# -------------------------------------------------------------------------------------
# A dialog that can nicely display an error of some sort (for example, a stack trace
# when an Exception is caught).  This dialog displays the error message as the text of 
# the dialog, along with a way to also view the details of the error.
# -------------------------------------------------------------------------------------
class ZErrorDialog(ZBaseDialog):

    def __init__(self, parent, errorMessage, errorDetail):
        self.parent = parent
        self.errorMessage = errorMessage
        self.errorDetail = errorDetail
        self.mode = MODE_COMPACT
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"error_dialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,  size=wx.Size(DIALOG_WIDTH, COMPACT_DIALOG_HEIGHT)) #$NON-NLS-1$
    # end __init__()

    def _createButtons(self):
        detailsButtonName = _extstr(u"error_dialog.Details") + u" >>" #$NON-NLS-2$ #$NON-NLS-1$
        self._createExpandedWidgets()

        # The details/ok buttons.
        self.detailsButton = wx.Button(self, wx.ID_ANY, detailsButtonName)
        self.okButton = wx.Button(self, wx.ID_OK, _extstr(u"Close")) #$NON-NLS-1$

        # Wrap them in a sizer.
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.detailsButton, 0, wx.ALL, 1)
        buttonSizer.Add(self.okButton, 0, wx.ALL, 1)
        return buttonSizer
    # end _createButtons()

    def _createContentWidgets(self):
        self.errorHTML = self._createErrorHTMLControl()
        self.errorStaticLine = wx.StaticLine(self)
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        self.errorHTML.SetPage(self._loadErrorHTML())
        self.errorDetailTextBox.SetValue(self.errorDetail)
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.errorHTML, 0, wx.EXPAND)
        box.Add(self.errorStaticLine, 0, wx.EXPAND)

        # Create/add the static box sizer if the dialog has been expanded.
        staticBoxSizer = wx.StaticBoxSizer(self.errorDetailStaticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.errorDetailTextBox, 1, wx.EXPAND | wx.ALL, 2)
        self.errorDetailPanel.SetAutoLayout(True)
        self.errorDetailPanel.SetSizer(staticBoxSizer)
        self.errorDetailPanel.Layout()
        # Initial state of "Details" panel is hidden.
        self.errorDetailPanel.Show(False)

        box.Add(self.errorDetailPanel, 1, wx.EXPAND | wx.ALL, 5)

        return box
    # end _layoutContentWidgets()

    def _setInitialFocus(self):
        self.detailsButton.SetFocus()
    # end _setInitialFocus()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onDetails, self.detailsButton)
    # end _bindWidgetEvents()

    def _createErrorHTMLControl(self):
        html = ZHTMLControl(self, size=wx.Size(-1, 64), style = HW_SCROLLBAR_NEVER | HW_NO_SELECTION)
        html.SetBorders(1)
        return html
    # end _createHeaderHTMLControl()

    def _createExpandedWidgets(self):
        self.errorDetailPanel = wx.Panel(self, wx.ID_ANY)
        self.errorDetailStaticBox = wx.StaticBox(self.errorDetailPanel, label = _extstr(u"error_dialog.ErrorDetail")) #$NON-NLS-1$
        self.errorDetailTextBox = wx.TextCtrl(self.errorDetailPanel, wx.ID_ANY, style = wx.TE_READONLY | wx.HSCROLL | wx.TE_MULTILINE)
    # end _createExpandedWidgets()

    def _loadErrorHTML(self):
        global RESOURCE_REGISTRY
        return ERROR_HTML % {
            u"error_header" : _extstr(u"error_dialog.Error"), #$NON-NLS-1$ #$NON-NLS-2$
            u"error_message" : self.errorMessage, #$NON-NLS-1$
            u"error_image" : getResourceRegistry().getImagePath(u"images/widgets/error_dialog/error.png") #$NON-NLS-1$ #$NON-NLS-2$
        }
    # end _loadHeaderHTML()

    def onDetails(self, event): #@UnusedVariable
        detailsButtonName = _extstr(u"error_dialog.Details") + u" >>" #$NON-NLS-2$ #$NON-NLS-1$
        if self.mode == MODE_COMPACT:
            self.mode = MODE_EXPANDED
            self.errorDetailPanel.Show(True)
            self.SetSize(wx.Size(DIALOG_WIDTH, EXPANDED_DIALOG_HEIGHT))
            detailsButtonName = u"<< " + _extstr(u"error_dialog.Details") #$NON-NLS-2$ #$NON-NLS-1$
        else:
            self.mode = MODE_COMPACT
            self.errorDetailPanel.Show(False)
            self.SetSize(wx.Size(DIALOG_WIDTH, COMPACT_DIALOG_HEIGHT))
        self.detailsButton.SetLabel(detailsButtonName)

        self.Layout()
    # end onDetails()

# end ZErrorDialog


# -------------------------------------------------------------------------------------
# A dialog that can nicely display an exception that was caught in a "catch" block.
# Simply construct this dialog with the exception object, and Bob is your uncle.
# -------------------------------------------------------------------------------------
class ZExceptionDialog(ZErrorDialog):
    
    def __init__(self, parent, zexception):
        ZErrorDialog.__init__(self, parent, zexception.getMessage(), zexception.getStackTrace())
    # end __init__()
    
# end ZExceptionDialog


# -------------------------------------------------------------------------------------
# A dialog that can nicely display an exception that was caught in a "catch" block.
# Simply construct this dialog with the exception object, and Bob is your uncle.
# -------------------------------------------------------------------------------------
class ZExceptionWithFeedbackDialog(ZExceptionDialog):

    def __init__(self, parent, zexception):
        ZExceptionDialog.__init__(self, parent, zexception)
    # end __init__()

    def _createButtons(self):
        detailsButtonName = _extstr(u"error_dialog.Details") + u" >>" #$NON-NLS-2$ #$NON-NLS-1$
        self._createExpandedWidgets()

        # The details/ok/Report buttons.
        self.detailsButton = wx.Button(self, wx.ID_ANY, detailsButtonName)
        self.okButton = wx.Button(self, wx.ID_CANCEL, _extstr(u"Close")) #$NON-NLS-1$
        self.reportButton = wx.Button(self, wx.ID_OK, _extstr(u"erroraction.Report")) #$NON-NLS-1$

        # Wrap them in a sizer.
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.detailsButton, 0, wx.ALL, 1)
        buttonSizer.Add(self.okButton, 0, wx.ALL, 1)
        buttonSizer.Add(self.reportButton, 0, wx.ALL, 1)
        return buttonSizer
    # end _createButtons()

# end ZExceptionWithFeedbackDialog
