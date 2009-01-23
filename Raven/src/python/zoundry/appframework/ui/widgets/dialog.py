from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.commonevents import ZEVT_UIEXEC
import wx

# -------------------------------------------------------------------------------------
# A base class for Zoundry dialogs.  This base class assists in the creation of the
# dialog in a clean way by calling "create widgets", "populate widgets", "layout
# widgets", and finally "create event map".
# -------------------------------------------------------------------------------------
class ZBaseDialog(wx.Dialog):

    # The codes to indicate which buttons to display.
    OK_BUTTON = 1
    CANCEL_BUTTON = 2
    YES_BUTTON = 4
    NO_BUTTON = 8
    APPLY_BUTTON = 16
    CLOSE_BUTTON = 32

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZDialog"): #$NON-NLS-1$
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)

        self._initDialog()
    # end __init__()

    def _initDialog(self):
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        self._setInitialFocus()

        self.Bind(ZEVT_UIEXEC, self.onUIExec)
    # end _initDialog()

    def _createWidgets(self):
        self._createContentWidgets()
        self.standardButtons = self._createButtons()
    # end _createWidgets()

    def _populateWidgets(self):
        self._populateContentWidgets()
    # end _populateWidgets()

    def _layoutWidgets(self):
        # Subclass should layout its content into a sizer
        sizer = self._layoutContentWidgets()

        # Create the overall box sizer
        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(sizer, 1, wx.EXPAND)
        box.AddSizer(self.standardButtons, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutWidgets()

    def _createButtons(self):
        u"Called to create the OK/Cancel buttons (or Yes/No, etc...).  Should return a sizer." #$NON-NLS-1$
        buttonBits = self._getButtonTypes()
        buttonSizer = wx.StdDialogButtonSizer()
        if (buttonBits & ZBaseDialog.OK_BUTTON) > 0:
            okButton = wx.Button(self, wx.ID_OK, self._getOKButtonLabel())
            buttonSizer.AddButton(okButton)
        if (buttonBits & ZBaseDialog.CANCEL_BUTTON) > 0:
            cancelButton = wx.Button(self, wx.ID_CANCEL, self._getCancelButtonLabel())
            buttonSizer.AddButton(cancelButton)
        if (buttonBits & ZBaseDialog.APPLY_BUTTON) > 0:
            applyButton = wx.Button(self, wx.ID_APPLY, self._getApplyButtonLabel())
            buttonSizer.AddButton(applyButton)
        if (buttonBits & ZBaseDialog.YES_BUTTON) > 0:
            yesButton = wx.Button(self, wx.ID_YES, self._getYesButtonLabel())
            buttonSizer.AddButton(yesButton)
        if (buttonBits & ZBaseDialog.NO_BUTTON) > 0:
            noButton = wx.Button(self, wx.ID_NO, self._getNoButtonLabel())
            buttonSizer.AddButton(noButton)
        if (buttonBits & ZBaseDialog.CLOSE_BUTTON) > 0:
            closeButton = wx.Button(self, wx.ID_CANCEL, self._getCloseButtonLabel())
            buttonSizer.AddButton(closeButton)
        buttonSizer.Realize()
        return buttonSizer
    # end _createButtons()

    def _createContentWidgets(self):
        u"Called to create the content widgets (everything but the standard ok/cancel type buttons)." #$NON-NLS-1$
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        u"Subclasses should implement this method to populate widgets." #$NON-NLS-1$
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        u"Subclasses can implement this to layout the content widgets (should return a sizer)" #$NON-NLS-1$
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        u"Subclasses should implement this method to create the event map." #$NON-NLS-1$
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        u"Called to set the focus on some initial widget." #$NON-NLS-1$
    # end _setInitialFocus()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def _enableOkButton(self, enable = True):
        okButton = self.FindWindowById(wx.ID_OK)
        if okButton:
            okButton.Enable(enable)
            return
        applyButton = self.FindWindowById(wx.ID_APPLY)
        if applyButton:
            applyButton.Enable(enable)
    # end _enableOkButton()

    def _enableApplyButton(self, enable = True):
        applyButton = self.FindWindowById(wx.ID_APPLY)
        if applyButton:
            applyButton.Enable(enable)
    # end _enableApplyButton()

    def _enableCancelButton(self, enable = True):
        cancelButton = self.FindWindowById(wx.ID_CANCEL)
        if cancelButton:
            cancelButton.Enable(enable)
    # end _enableCancelButton()

    def _enableYesButton(self, enable = True):
        yesButton = self.FindWindowById(wx.ID_YES)
        if yesButton:
            yesButton.Enable(enable)
    # end _enableYesButton()

    def _enableNoButton(self, enable = True):
        noButton = self.FindWindowById(wx.ID_NO)
        if noButton:
            noButton.Enable(enable)
    # end _enableNoButton()

    def _getCloseButtonLabel(self):
        return _extstr(u"Close") #$NON-NLS-1$
    # end _getCloseButtonLabel()

    def _getNoButtonLabel(self):
        return _extstr(u"dialog.NoButtonLabel") #$NON-NLS-1$
    # end _getNoButtonLabel()

    def _getYesButtonLabel(self):
        return _extstr(u"dialog.YesButtonLabel") #$NON-NLS-1$
    # end _getYesButtonLabel()

    def _getApplyButtonLabel(self):
        return _extstr(u"Apply") #$NON-NLS-1$
    # end _getApplyButtonLabel()

    def _getCancelButtonLabel(self):
        return _extstr(u"Cancel") #$NON-NLS-1$
    # end _getCancelButtonLabel()

    def _getOKButtonLabel(self):
        return _extstr(u"OK") #$NON-NLS-1$
    # end _getOKButtonLabel()

    def _bindOkButton(self, callback):
        self.Bind(wx.EVT_BUTTON, callback, self.FindWindowById(wx.ID_OK))
    # end _bindOkButton()

    def _bindApplyButton(self, callback):
        self.Bind(wx.EVT_BUTTON, callback, self.FindWindowById(wx.ID_APPLY))
    # end _bindApplyButton()

    def _bindCancelButton(self, callback):
        self.Bind(wx.EVT_BUTTON, callback, self.FindWindowById(wx.ID_CANCEL))
    # end _bindCancelButton()

    def _bindYesButton(self, callback):
        self.Bind(wx.EVT_BUTTON, callback, self.FindWindowById(wx.ID_YES))
    # end _bindYesButton()

    def _bindNoButton(self, callback):
        self.Bind(wx.EVT_BUTTON, callback, self.FindWindowById(wx.ID_NO))
    # end _bindNoButton()

    def _bindRefreshEvent(self, callback):
        self.Bind(ZEVT_REFRESH, callback, self)
    # end _bindRefreshEvent()

    def _getOkButton(self):
        return self.FindWindowById(wx.ID_OK)
    # end _getOkButton()

    def _getApplyButton(self):
        return self.FindWindowById(wx.ID_APPLY)
    # end _getApplyButton()

    def _getCancelButton(self):
        return self.FindWindowById(wx.ID_CANCEL)
    # end _getCancelButton()

    def _getYesButton(self):
        return self.FindWindowById(wx.ID_YES)
    # end _getYesButton()

    def _getNoButton(self):
        return self.FindWindowById(wx.ID_NO)
    # end _getNoButton()

    def onUIExec(self, event):
        event.getRunnable().run()
    # end onUIExec()

# end ZBaseDialog
