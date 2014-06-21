from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZFileUrlSelectionValidator
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# --------------------------------------------------------------------------------
# The Edit Hyperlink dialog.  This dialog allows the user to edit the properties
# of a hyperlink.
# --------------------------------------------------------------------------------
class ZLinkDialog(ZValidatingHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent, model):
        self.model = model
        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"linkdialog.EnterLinkInfo"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZLinkDialog") #$NON-NLS-2$ #$NON-NLS-1$

        bestHeight = self.GetBestSizeTuple()[1]
        self.SetMinSize(wx.Size(-1, bestHeight))

        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.LINK_DIALOG, True, True)
    # end __init__()

    def _createNonHeaderWidgets(self):
        wildcard = u"all files|*.*" #$NON-NLS-1$
        self.filePicker = wx.FilePickerCtrl(self, wildcard=wildcard,style=wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST )#|wx.FLP_USE_TEXTCTRL)
        
        self.urlLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"linkdialog.URL")) #$NON-NLS-1$ #$NON-NLS-2$
        self.titleLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"linkdialog.Title")) #$NON-NLS-1$ #$NON-NLS-2$
        self.targetLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"linkdialog.Target")) #$NON-NLS-1$ #$NON-NLS-2$
        self.classLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"linkdialog.Class")) #$NON-NLS-1$ #$NON-NLS-2$
        self.relLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"linkdialog.Rel")) #$NON-NLS-1$ #$NON-NLS-2$

        self.urlText = ZValidatingTextCtrl(ZFileUrlSelectionValidator(_extstr(u"linkdialog.InvalidURLError")), self, wx.ID_ANY) #$NON-NLS-1$
        self.titleText = wx.TextCtrl(self, wx.ID_ANY)
        self.newWindowCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"linkdialog.OpenInNewWindow")) #$NON-NLS-1$
        self.targetText = wx.TextCtrl(self, wx.ID_ANY)
        self.classText = wx.TextCtrl(self, wx.ID_ANY)
        self.relText = wx.TextCtrl(self, wx.ID_ANY)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self.urlText.SetValue( getSafeString( self.model.getAttribute(u"href") ) ) #$NON-NLS-1$
        self.titleText.SetValue( getSafeString( self.model.getAttribute(u"title") ) ) #$NON-NLS-1$
        self.targetText.SetValue( getSafeString( self.model.getAttribute(u"target") ) ) #$NON-NLS-1$
        self.newWindowCB.SetValue( self.model.isOpenInNewWindow() )
        self.classText.SetValue( getSafeString( self.model.getAttribute(u"class") ) ) #$NON-NLS-1$
        self.relText.SetValue( getSafeString( self.model.getAttribute(u"rel") ) ) #$NON-NLS-1$

        if not self.model.isEditMode() and not self.urlText.GetValue():
            self.urlText.SetValue(u'http://') #$NON-NLS-1$
    # end _populateNonHeaderWidgets()

    def _updateModel(self):
        self.model.setAttribute(u"href", self.urlText.GetValue().strip()) #$NON-NLS-1$
        self.model.setAttribute(u"title", self.titleText.GetValue().strip() ) #$NON-NLS-1$
        self.model.setAttribute(u"class", self.classText.GetValue().strip() ) #$NON-NLS-1$
        self.model.setAttribute(u"rel", self.relText.GetValue().strip()) #$NON-NLS-1$
        if self.newWindowCB.IsChecked():
            target = self.targetText.GetValue().strip()
            if target == u"": #$NON-NLS-1$
                target = u"_blank" #$NON-NLS-1$
            self.model.setAttribute(u"target", target) #$NON-NLS-1$
        elif self.model.isOpenInNewWindow():
            # remove target attr.
            self.model.setAttribute(u"target", None) #$NON-NLS-1$
    # end _updateModel()

    def _layoutNonHeaderWidgets(self):
        hrefAndFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        hrefAndFileSizer.Add(self.urlText, 1, wx.EXPAND | wx.ALL, 1)
        hrefAndFileSizer.Add(self.filePicker, 0, wx.ALL, 1)        
        
        flexGridSizer = wx.FlexGridSizer(6, 2, 2, 2)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.urlLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.AddSizer(hrefAndFileSizer, 1, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(self.titleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.titleText, 1, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY, u""), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2) #$NON-NLS-1$
        flexGridSizer.Add(self.newWindowCB, 1, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(self.targetLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.targetText, 1, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(self.classLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.classText, 1, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(self.relLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.relText, 1, wx.EXPAND | wx.ALL, 2)

        staticBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _extstr(u"linkdialog.LinkProperties")), wx.VERTICAL) #$NON-NLS-1$
        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.targetText.Enable(False)

        return staticBoxSizer
    # end _layoutNonHeaderWidgets()

    def _setInitialFocus(self):
        self.urlText.SetFocus()
        if not self.model.isEditMode() and self.urlText.GetValue() and u"http://" != self.urlText.GetValue(): #$NON-NLS-1$
            self.urlText.SetSelection(-1, -1)
        else:
            self.urlText.SetInsertionPointEnd()
    # end _setInitialFocus()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.urlText)
        self.Bind(wx.EVT_CHECKBOX, self.onNewWindowCB, self.newWindowCB)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.FindWindowById(wx.ID_OK))
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFilePickerChanged, self.filePicker)
    # end _bindWidgetEvents()

    def onOK(self, event):
        # persist settings to model.
        self._updateModel()
        event.Skip()
    # end onOK()
        
    def onFilePickerChanged(self, event):
        path = getNoneString( event.GetPath())
        if path:
            self.urlText.SetValue(path)
        event.Skip()
    # end onFilePickerChanged        

    def onNewWindowCB(self, event):
        self.targetText.Enable(event.IsChecked())
    # end onNewWindowCB()

    def _getHeaderTitle(self):
        if self.model.isEditMode():
            return _extstr(u"linkdialog.EditHyperlink") #$NON-NLS-1$
        else:
            return _extstr(u"linkdialog.CreateHyperlink") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"linkdialog.LinkDialogDescription") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/link/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

# end ZLinkDialog
