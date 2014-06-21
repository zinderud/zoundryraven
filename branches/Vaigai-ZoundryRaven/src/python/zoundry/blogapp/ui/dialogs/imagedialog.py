from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageAlignMenuLabels
from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageBorderMenuLabels

from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZCssLengthSelectionValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZFileUrlSelectionValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZIntegerSelectionValidator
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------
# The Edit Image Properties dialog.  This dialog allows the user to edit the
# properties of an image.
# ------------------------------------------------------------------------------
class ZImageDialog(ZValidatingHeaderDialog, ZPersistentDialogMixin):
    
    def __init__(self, parent, model):
        # model is instance of ZEditImageModel.
        self.model = model
        self.aspectRatio = 0.0
        
        title = _extstr(u"imagedialog.EditImageInformation") #$NON-NLS-1$
        if not self.model.isEditMode():
            title = _extstr(u"imagedialog.InsertImage") #$NON-NLS-1$
        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZImageDialog") #$NON-NLS-1$

        bestHeight = self.GetBestSizeTuple()[1]
        self.SetMinSize(wx.Size(-1, bestHeight))

        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.IMAGE_DIALOG, True, True)
    # end __init__()

    def _createNonHeaderWidgets(self):
        self.imagePropsStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagedialog.ImageProperties")) #$NON-NLS-1$
        self.sizeStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagedialog.Size")) #$NON-NLS-1$
        self.alignmentStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagedialog.Alignment")) #$NON-NLS-1$
        self.borderStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagedialog.Border")) #$NON-NLS-1$

        self.srcLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Src")) #$NON-NLS-1$ #$NON-NLS-2$
        self.altTextLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.ALTText")) #$NON-NLS-1$ #$NON-NLS-2$
        self.titleLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Title")) #$NON-NLS-1$ #$NON-NLS-2$
        self.classLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Class")) #$NON-NLS-1$ #$NON-NLS-2$

        self.widthLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Width")) #$NON-NLS-1$ #$NON-NLS-2$
        self.heightLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Height")) #$NON-NLS-1$ #$NON-NLS-2$
        wildcard = u"Image files|*.gif;*.jpg;*.png;*.jpeg" #$NON-NLS-1$
        self.filePicker = wx.FilePickerCtrl(self, wildcard=wildcard,style=wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST )#|wx.FLP_USE_TEXTCTRL)

        self.srcText = ZValidatingTextCtrl(ZFileUrlSelectionValidator(_extstr(u"imagedialog.InvalidImageURLError")), self, wx.ID_ANY) #$NON-NLS-1$
        self.altText = wx.TextCtrl(self, wx.ID_ANY)
        self.titleText = wx.TextCtrl(self, wx.ID_ANY)
        self.classText = wx.TextCtrl(self, wx.ID_ANY)

        self.lockAspect = wx.CheckBox(self,wx.ID_ANY, u"%s" % _extstr(u"imagedialog.LockAspect")) #$NON-NLS-2$ #$NON-NLS-1$
        flags = ZIntegerSelectionValidator.ALLOW_EMPTY | ZIntegerSelectionValidator.ALLOW_ZERO | ZIntegerSelectionValidator.POSITIVE_ONLY
        self.widthText = ZValidatingTextCtrl(ZIntegerSelectionValidator(flags=flags), self, wx.ID_ANY)
        self.heightText = ZValidatingTextCtrl(ZIntegerSelectionValidator(flags=flags), self, wx.ID_ANY)

        alignments = []
        for aname in ZImageAlignMenuLabels.ALIGN_KEYWORDS:
            alignments.append( ZImageAlignMenuLabels.ALIGN_LABELS[aname] ) #$NON-NLS-1$
        self.alignChoices = wx.Choice(self, wx.ID_ANY, (100, 50), choices = alignments)

        self.borderStyleLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Style")) #$NON-NLS-1$ #$NON-NLS-2$
        self.borderWidthLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Width")) #$NON-NLS-1$ #$NON-NLS-2$
        self.borderColorLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Color")) #$NON-NLS-1$ #$NON-NLS-2$
        
        borders = []
        for bname in ZImageBorderMenuLabels.BORDER_KEYWORDS:
            borders.append( ZImageBorderMenuLabels.BORDER_LABELS[bname] )
        
        self.borderStyles = wx.Choice(self, wx.ID_ANY, (200, 50), choices = borders)

        self.borderWidthValidator = ZCssLengthSelectionValidator()
        self.borderWidthText = ZValidatingTextCtrl(self.borderWidthValidator, self, wx.ID_ANY)
        self.borderColorPicker = wx.ColourPickerCtrl(self)

        self.marginStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagedialog.Margin")) #$NON-NLS-1$
        self.marginLeftLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Left")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginRightLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Right")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginTopLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Top")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginBotLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagedialog.Bottom")) #$NON-NLS-1$ #$NON-NLS-2$

        self.marginTopText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY)
        self.marginBotText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY)
        self.marginLeftText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY)
        self.marginRightText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY)
    # end _createNonHeaderWidgets()

    def _initAspectRatio(self):
        try:
            self.aspectRatio = (float(self.widthText.GetValue() ) / float(self.heightText.GetValue() ))
        except:
            self.aspectRatio = 0.0
        self.lockAspect.SetValue(self.aspectRatio > 0)
        self.lockAspect.Enable(self.aspectRatio > 0)
    # end _initAspectRatio()

    def _populateNonHeaderWidgets(self):
        self.srcText.SetValue( getSafeString( self.model.getAttribute(u"src") ) ) #$NON-NLS-1$
        self.altText.SetValue( getSafeString( self.model.getAttribute(u"alt") ) ) #$NON-NLS-1$
        self.titleText.SetValue( getSafeString( self.model.getAttribute(u"title") ) ) #$NON-NLS-1$
        self.classText.SetValue( getSafeString( self.model.getAttribute(u"class") ) ) #$NON-NLS-1$

        self.widthText.SetValue( getSafeString( self.model.getAttribute(u"width") ) ) #$NON-NLS-1$
        self.heightText.SetValue( getSafeString( self.model.getAttribute(u"height") ) ) #$NON-NLS-1$
        self._initAspectRatio()

        (top, right, bot, left) = self.model.getMargins()
        self.marginTopText.SetValue(getSafeString(top))
        self.marginRightText.SetValue(getSafeString(right))
        self.marginBotText.SetValue(getSafeString(bot))
        self.marginLeftText.SetValue(getSafeString(left))

        (width, style, cssColor) = self.model.getBorder()
        if cssColor:
            color = wx.Colour(cssColor.getRed(), cssColor.getGreen(), cssColor.getBlue())
            self.borderColorPicker.SetColour(color)
        self.borderWidthText.SetValue(getSafeString(width))
        style = getSafeString(style).lower()
        idx = 0
        try:
            idx = ZImageBorderMenuLabels.BORDER_KEYWORDS.index( style )
        except:
            idx = 0
        self.borderStyles.SetSelection(idx)
        self._updateBorderControlsState()

        align = getSafeString( self.model.getAttribute(u"align") ) #$NON-NLS-1$
        # align = None, Left etc.
        # find index within keywords
        idx = 0
        try:
            idx = ZImageAlignMenuLabels.ALIGN_KEYWORDS.index( align.lower() )
        except:
            idx = 0
        self.alignChoices.SetSelection(idx)

    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        # Image Properties
        srcAndFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        srcAndFileSizer.Add(self.srcText, 1, wx.EXPAND | wx.ALL, 1)
        srcAndFileSizer.Add(self.filePicker, 0, wx.ALL, 1)

        imagePropsGridSizer = wx.FlexGridSizer(4, 2, 2, 2)
        imagePropsGridSizer.AddGrowableCol(1)
        imagePropsGridSizer.Add(self.srcLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        imagePropsGridSizer.AddSizer(srcAndFileSizer, 1, wx.EXPAND | wx.ALL, 1)

        imagePropsGridSizer.Add(self.altTextLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        imagePropsGridSizer.Add(self.altText, 1, wx.EXPAND | wx.ALL, 1)
        imagePropsGridSizer.Add(self.titleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        imagePropsGridSizer.Add(self.titleText, 1, wx.EXPAND | wx.ALL, 1)
        imagePropsGridSizer.Add(self.classLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        imagePropsGridSizer.Add(self.classText, 1, wx.EXPAND | wx.ALL, 1)

        imagePropsStaticBoxSizer = wx.StaticBoxSizer(self.imagePropsStaticBox, wx.VERTICAL)
        imagePropsStaticBoxSizer.AddSizer(imagePropsGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        # Size
        sizeGridSizer = wx.FlexGridSizer(2, 2, 2, 2)
        sizeGridSizer.Add(self.widthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.widthText, 1, wx.EXPAND | wx.ALL, 1)
        sizeGridSizer.Add(self.heightLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        sizeGridSizer.Add(self.heightText, 1, wx.EXPAND | wx.ALL, 1)

        sizeStaticBoxSizer = wx.StaticBoxSizer(self.sizeStaticBox, wx.VERTICAL)
        sizeStaticBoxSizer.Add(self.lockAspect, 0,  wx.EXPAND | wx.ALL, 5)
        sizeStaticBoxSizer.AddSizer(sizeGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        alignmentStaticBoxSizer = wx.StaticBoxSizer(self.alignmentStaticBox, wx.VERTICAL)
        alignmentStaticBoxSizer.Add(self.alignChoices, 1, wx.EXPAND | wx.ALL, 5)

        # Border
        borderGridSizer = wx.FlexGridSizer(3, 2, 2, 2)
        borderGridSizer.Add(self.borderStyleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderStyles, 1, wx.EXPAND | wx.ALL, 1)
        borderGridSizer.Add(self.borderWidthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderWidthText, 1, wx.EXPAND | wx.ALL, 1)
        borderGridSizer.Add(self.borderColorLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderColorPicker, 0,wx.ALL, 1)
        borderStaticBoxSizer = wx.StaticBoxSizer(self.borderStaticBox, wx.VERTICAL)
        borderStaticBoxSizer.AddSizer(borderGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        marginGridSizer = wx.FlexGridSizer(4, 4, 2, 2)
        marginGridSizer.Add(self.marginTopLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginTopText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginLeftLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginLeftText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginBotLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginBotText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginRightLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginRightText, 1, wx.EXPAND | wx.ALL, 1)
        marginStaticBoxSizer = wx.StaticBoxSizer(self.marginStaticBox, wx.VERTICAL)
        marginStaticBoxSizer.AddSizer(marginGridSizer, 1, wx.EXPAND | wx.ALL, 5)


        # Size + Alignment Box Sizer
        sizeAndAlignmentBoxSizer = wx.FlexGridSizer(2, 2, 2, 2)
        sizeAndAlignmentBoxSizer.AddSizer(sizeStaticBoxSizer, 1, wx.EXPAND | wx.ALL, 2)
        sizeAndAlignmentBoxSizer.AddSizer(borderStaticBoxSizer, 1, wx.EXPAND | wx.ALL, 2)
        sizeAndAlignmentBoxSizer.AddSizer(alignmentStaticBoxSizer, 1, wx.EXPAND | wx.ALL, 2)
        sizeAndAlignmentBoxSizer.AddSizer(marginStaticBoxSizer, 1, wx.EXPAND | wx.ALL, 2)

        # Dialog Sizer
        dialogBoxSizer = wx.BoxSizer(wx.VERTICAL)
        dialogBoxSizer.AddSizer(imagePropsStaticBoxSizer, 0, wx.EXPAND | wx.ALL, 5)
        dialogBoxSizer.AddSizer(sizeAndAlignmentBoxSizer, 0, wx.EXPAND | wx.ALL, 5)

        return dialogBoxSizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFilePickerChanged, self.filePicker)
        self.Bind(wx.EVT_CHOICE, self.onBorderStyleChanged, self.borderStyles)
        self.Bind(wx.EVT_TEXT, self.onImageWidthChange, self.widthText)
        self.Bind(wx.EVT_TEXT, self.onImageHeightChange, self.heightText)

        self._bindValidatingWidget(self.srcText)
        self._bindValidatingWidget(self.widthText)
        self._bindValidatingWidget(self.heightText)
        self._bindValidatingWidget(self.borderWidthText)
        self._bindValidatingWidget(self.marginTopText)
        self._bindValidatingWidget(self.marginRightText)
        self._bindValidatingWidget(self.marginBotText)
        self._bindValidatingWidget(self.marginLeftText)

        self.Bind(wx.EVT_BUTTON, self.onOK, self.FindWindowById(wx.ID_OK))
    # end _bindWidgetEvents()

    def _updateModel(self):
        self.model.setAttribute(u"src", self.srcText.GetValue().strip() ) #$NON-NLS-1$
        self.model.setAttribute(u"alt", self.altText.GetValue().strip() ) #$NON-NLS-1$
        self.model.setAttribute(u"title", self.titleText.GetValue().strip() ) #$NON-NLS-1$
        self.model.setAttribute(u"class", self.classText.GetValue().strip() ) #$NON-NLS-1$

        idx = self.alignChoices.GetSelection()
        if idx >=0 and idx < len(ZImageAlignMenuLabels.ALIGN_KEYWORDS):
            align = ZImageAlignMenuLabels.ALIGN_KEYWORDS[idx]
            self.model.setAttribute(u"align", align.lower() ) #$NON-NLS-1$

        # Width and height
        width = 0
        height = 0
        try:
            width = int(self.widthText.GetValue())
            height = int(self.heightText.GetValue())
        except:
            pass
        if width > 0 and height > 0:
            self.model.setAttribute(u"width", u"%d" % width ) #$NON-NLS-1$ #$NON-NLS-2$
            self.model.setAttribute(u"height", u"%d" % height ) #$NON-NLS-1$ #$NON-NLS-2$
        # Margin
        t = self.marginTopText.GetValue().strip()
        r = self.marginRightText.GetValue().strip()
        b = self.marginBotText.GetValue().strip()
        l = self.marginLeftText.GetValue().strip()
        self.model.setMargins(t,r,b,l)
        # Border
        style = ZImageBorderMenuLabels.BORDER_KEYWORDS[0] # default is None
        idx = self.borderStyles.GetSelection()
        if idx >=0 and idx < len(ZImageBorderMenuLabels.BORDER_KEYWORDS):
            style = ZImageBorderMenuLabels.BORDER_KEYWORDS[idx]
        width = self.borderWidthText.GetValue().strip()
        cssHexColor = self.borderColorPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.model.setBorder(width, style, cssHexColor)
    # end updateModel

    def onOK(self, event):
        self._updateModel()
        event.Skip()
    # end onOK()

    def onImageHeightChange(self, event): #@UnusedVariable
        if self.lockAspect.IsChecked() and self.aspectRatio > 0:
            try:
                height = int(self.heightText.GetValue())
                width = int(height * self.aspectRatio)
                self.widthText.ChangeValue(unicode(width))
            except:
                pass
            event.Skip()
    # end onImageHeightChange()

    def onImageWidthChange(self, event): #@UnusedVariable
        if self.lockAspect.IsChecked() and self.aspectRatio > 0:
            try:
                width = int(self.widthText.GetValue())
                height = int(width / self.aspectRatio)
                self.heightText.ChangeValue(unicode(height))
            except:
                pass
            event.Skip()
    # end onImageWidthChange()

    def _updateBorderControlsState(self):
        enable = self.borderStyles.GetCurrentSelection() > 0
        if enable:
            self.borderWidthValidator.setFlags(0)
        else:
            self.borderWidthValidator.setFlags(ZCssLengthSelectionValidator.ALLOW_EMPTY)
            self.borderWidthText.validate()

        if enable and not self.borderWidthText.GetValue():
            self.borderWidthText.SetValue(u"1px") #$NON-NLS-1$
        self.borderWidthText.Enable(enable)
        self.borderColorPicker.Enable(enable)
    # end _updateBorderControlsState()

    def onBorderStyleChanged(self, event): #@UnusedVariable
        self._updateBorderControlsState()
    # end onBorderStyleChanged

    def onFilePickerChanged(self, event):
        path = getNoneString( event.GetPath())
        if path:
            self.srcText.SetValue(path)
        event.Skip()
    # end onFilePickerChanged

    def _getHeaderTitle(self):
        if self.model.isEditMode():
            return _extstr(u"imagedialog.Edit_Image") #$NON-NLS-1$
        else:
            return _extstr(u"imagedialog.Insert_Image") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        if self.model.isEditMode():
            return _extstr(u"imagedialog.ImageDialogEditDescription") #$NON-NLS-1$
        else:
            return _extstr(u"imagedialog.ImageDialogInsertDescription") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/image/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

# end ZImageDialog
