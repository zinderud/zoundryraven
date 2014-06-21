from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZCssLengthSelectionValidator
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZIntegerSelectionValidator
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.blogapp.messages import _extstr
import wx


# ------------------------------------------------------------------------------
# The new table (create table) dialog
# ------------------------------------------------------------------------------
class ZInsertTableDialog(ZBaseDialog):

    def __init__(self, parent, model):
        # model is instance of ZTableModel.
        self.model = model
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"tabledialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZInsertTableDialog") #$NON-NLS-1$ #$NON-NLS-2$
        bestHeight = self.GetBestSizeTuple()[1]
        self.SetSize(wx.Size(-1, bestHeight))
    # end __init__()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def _createContentWidgets(self):
        self.settingsStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"tabledialog.TableSettings")) #$NON-NLS-1$
        if self.model.isInsertMode():
            self.rowsLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.Rows")) #$NON-NLS-1$ #$NON-NLS-2$
            self.rowsText = ZValidatingTextCtrl(ZIntegerSelectionValidator(flags=ZIntegerSelectionValidator.POSITIVE_ONLY), self, wx.ID_ANY)
            self.colsLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.Cols")) #$NON-NLS-1$ #$NON-NLS-2$
            self.colsText = ZValidatingTextCtrl(ZIntegerSelectionValidator(flags=ZIntegerSelectionValidator.POSITIVE_ONLY), self, wx.ID_ANY)

        flags = ZCssLengthSelectionValidator.ALLOW_EMPTY

        self.paddingLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.CellPadding")) #$NON-NLS-1$ #$NON-NLS-2$
        self.paddingText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=flags), self, wx.ID_ANY)
        self.spacingLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.CellSpacing")) #$NON-NLS-1$ #$NON-NLS-2$
        self.spacingText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=flags), self, wx.ID_ANY)
        self.borderLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.Border")) #$NON-NLS-1$ #$NON-NLS-2$
        self.borderText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=flags), self, wx.ID_ANY)
        self.widthLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"tabledialog.Width")) #$NON-NLS-1$ #$NON-NLS-2$
        self.widthText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(), self, wx.ID_ANY)
    # end _createNonHeaderWidgets()

    def _populateContentWidgets(self):
        if self.model.isInsertMode():
            self.rowsText.SetValue( str(self.model.getRows()) )
            self.colsText.SetValue( str(self.model.getCols()) )

        self.borderText.SetValue( getSafeString(self.model.getBorder()) )
        self.paddingText.SetValue( getSafeString(self.model.getPadding()) )
        self.spacingText.SetValue( getSafeString(self.model.getSpacing()) )
        self.widthText.SetValue( getSafeString( self.model.getWidth()) )
    # end _populateNonHeaderWidgets()

    def _layoutContentWidgets(self):
        nrows = 3
        if self.model.isInsertMode():
            nrows = 2
        sizeGridSizer = wx.FlexGridSizer(nrows, 4, 2, 2)

        if self.model.isInsertMode():
            sizeGridSizer.Add(self.rowsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
            sizeGridSizer.Add(self.rowsText, 1, wx.EXPAND | wx.ALL, 1)
            sizeGridSizer.Add(self.colsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
            sizeGridSizer.Add(self.colsText, 1, wx.EXPAND | wx.ALL, 1)

        sizeGridSizer.Add(self.paddingLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.paddingText, 1, wx.EXPAND | wx.ALL, 1)

        sizeGridSizer.Add(self.spacingLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.spacingText, 1, wx.EXPAND | wx.ALL, 1)

        sizeGridSizer.Add(self.borderLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.borderText, 1, wx.EXPAND | wx.ALL, 1)

        sizeGridSizer.Add(self.widthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.widthText, 1, wx.EXPAND | wx.ALL, 1)

        staticBoxSizer = wx.StaticBoxSizer(self.settingsStaticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(sizeGridSizer, 1, wx.EXPAND | wx.ALL, 1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 4)
        return sizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onOK, self.FindWindowById(wx.ID_OK) )
    # end _bindWidgetEvents()


    def _updateModel(self):
        if self.model.isInsertMode():
            self.model.setRows( int(self.rowsText.GetValue() ) )
            self.model.setCols( int(self.colsText.GetValue() ) )

        if getNoneString( self.borderText.GetValue() ):
            self.model.setBorder( self.borderText.GetValue() )
        else:
            self.model.setBorder(None)

        if getNoneString( self.widthText.GetValue() ):
            self.model.setWidth( self.widthText.GetValue() )
        else:
            self.model.setWidth(None)

        if getNoneString( self.paddingText.GetValue() ):
            self.model.setPadding( self.paddingText.GetValue())
        else:
            self.model.setPadding(None)

        if getNoneString( self.spacingText.GetValue() ):
            self.model.setSpacing(self.spacingText.GetValue())
        else:
            self.model.setSpacing(None)

    # end _updateModel()

    def onOK(self, event):
        # persist settings to model.
        self._updateModel()
        event.Skip()
    # end onOK()

# end ZInsertTableDialog
