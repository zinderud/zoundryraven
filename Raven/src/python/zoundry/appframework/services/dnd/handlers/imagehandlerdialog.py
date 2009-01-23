from zoundry.appframework.messages import _extstr
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZCssLengthSelectionValidator
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr as _blogappextstr
#import zoundry.blogapp.messages._extstr as _blogappextstr
from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageAlignMenuLabels
from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageBorderMenuLabels
from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZThumbnailSizeMenuLabels
import re
import wx

# FIXME this is an appframework dialog - but it uses lots of blogapp stuff.  Fix this.

# ------------------------------------------------------------------------------
# User prefs keys.
# ------------------------------------------------------------------------------
class IZThumbnailImageDialogPrefKeys:
    GENERATE_FLAG = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.generate-tn" #$NON-NLS-1$
    SIZE = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.size" #$NON-NLS-1$
    ALIGNMENT = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.alignment" #$NON-NLS-1$
    BORDER_STYLE = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.border.style" #$NON-NLS-1$
    BORDER_WIDTH = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.border.width" #$NON-NLS-1$
    BORDER_COLOR = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.border.color" #$NON-NLS-1$
    MARGIN_TOP = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.margin.top" #$NON-NLS-1$
    MARGIN_BOTTOM = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.margin.bottom" #$NON-NLS-1$
    MARGIN_LEFT = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.margin.left" #$NON-NLS-1$
    MARGIN_RIGHT = u"zoundry.raven.appframework.services.dnd.image.tn-dialog.margin.right" #$NON-NLS-1$
# end IZThumbnailImageDialogPrefKeys


# ------------------------------------------------------------------------------
# Model used by the thumbnail image dialog to manage its data.
# ------------------------------------------------------------------------------
class ZThumbnailImageDialogModel:

    def __init__(self):
        self.userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self._loadFromPrefs()
    # end __init__()

    def _loadFromPrefs(self):
        self.generateTNFlag = self.userPrefs.getUserPreferenceBool(IZThumbnailImageDialogPrefKeys.GENERATE_FLAG, False)
        self.size = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.SIZE, 250)
        self.alignment = self.userPrefs.getUserPreference(IZThumbnailImageDialogPrefKeys.ALIGNMENT, u"None") #$NON-NLS-1$
        self.borderStyle = self.userPrefs.getUserPreference(IZThumbnailImageDialogPrefKeys.BORDER_STYLE, u"None") #$NON-NLS-1$
        self.borderWidth = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.BORDER_WIDTH, 1)
        color = self.userPrefs.getUserPreference(IZThumbnailImageDialogPrefKeys.BORDER_COLOR, u"(0,0,0)") #$NON-NLS-1$
        self.borderColor = map(int, re.findall(r"(\d+)", color)) #$NON-NLS-1$
        self.marginTop = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.MARGIN_TOP, None)
        self.marginBottom = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.MARGIN_BOTTOM, None)
        self.marginLeft = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.MARGIN_LEFT, None)
        self.marginRight = self.userPrefs.getUserPreferenceInt(IZThumbnailImageDialogPrefKeys.MARGIN_RIGHT, None)
    # end _loadFromPrefs()

    def _saveToPrefs(self):
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.GENERATE_FLAG, self.generateTNFlag)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.SIZE, self.size)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.ALIGNMENT, self.alignment)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.BORDER_STYLE, self.borderStyle)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.BORDER_WIDTH, self.borderWidth)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.BORDER_COLOR, self.borderColor)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.MARGIN_TOP, self.marginTop)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.MARGIN_BOTTOM, self.marginBottom)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.MARGIN_LEFT, self.marginLeft)
        self.userPrefs.setUserPreference(IZThumbnailImageDialogPrefKeys.MARGIN_RIGHT, self.marginRight)
    # end _saveToPrefs()

# end ZThumbnailImageDialogModel


# ------------------------------------------------------------------------------
# Dialog shown to the user when she drops an image onto the editor.  This
# dialog asks the user whether a thumbnail should be generated.  If "yes", then
# specific thumbnail settings can be specified (border, alignment, etc).
# ------------------------------------------------------------------------------
class ZThumbnailImageDialog(ZValidatingHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.model = ZThumbnailImageDialogModel()
        title = _extstr(u"imagehandlerdialog.Generate_Thumbnail") #$NON-NLS-1$
        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZThumbnailImageDialog") #$NON-NLS-1$

        bestHeight = self.GetBestSizeTuple()[1]
        self.SetMinSize(wx.Size(-1, bestHeight))

        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.DND_THUMBNAIL_DIALOG, True, True)
    # end __init__()

    def _createNonHeaderWidgets(self):
        self.doNotGenRadioButton = wx.RadioButton(self, wx.ID_ANY, _extstr(u"imagehandlerdialog.DoNotGenerateOption")) #$NON-NLS-1$
        self.genRadioButton = wx.RadioButton(self, wx.ID_ANY, _extstr(u"imagehandlerdialog.GenerateOption")) #$NON-NLS-1$

        self.tnSettingsGroupBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"imagehandlerdialog.ThumbnailSettings")) #$NON-NLS-1$
        self.sizeLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"imagehandlerdialog.Size")) #$NON-NLS-1$ #$NON-NLS-2$

        sizeChoices = []
        for size in ZThumbnailSizeMenuLabels.SIZE_KEYWORDS:
            sizeChoices.append(ZThumbnailSizeMenuLabels.SIZE_LABELS[size])
        self.sizeChoice = wx.Choice(self, wx.ID_ANY, (100, 50), choices = sizeChoices)

        self.alignLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Alignment")) #$NON-NLS-1$ #$NON-NLS-2$
        alignments = []
        for aname in ZImageAlignMenuLabels.ALIGN_KEYWORDS:
            alignments.append( ZImageAlignMenuLabels.ALIGN_LABELS[aname] ) #$NON-NLS-1$
        self.alignChoice = wx.Choice(self, wx.ID_ANY, (100, 50), choices = alignments)

        self.borderStaticBox = wx.StaticBox(self, wx.ID_ANY, _blogappextstr(u"imagedialog.Border")) #$NON-NLS-1$
        self.borderStyleLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Style")) #$NON-NLS-1$ #$NON-NLS-2$
        self.borderWidthLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Width")) #$NON-NLS-1$ #$NON-NLS-2$
        self.borderColorLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Color")) #$NON-NLS-1$ #$NON-NLS-2$

        borders = []
        for bname in ZImageBorderMenuLabels.BORDER_KEYWORDS:
            borders.append( ZImageBorderMenuLabels.BORDER_LABELS[bname] )
        self.borderStyleChoice = wx.Choice(self, wx.ID_ANY, (200, 50), choices = borders)

        self.borderWidthValidator = ZCssLengthSelectionValidator()
        self.borderWidthText = ZValidatingTextCtrl(self.borderWidthValidator, self, wx.ID_ANY)
        self.borderColorPicker = wx.ColourPickerCtrl(self)

        self.marginStaticBox = wx.StaticBox(self, wx.ID_ANY, _blogappextstr(u"imagedialog.Margin")) #$NON-NLS-1$
        self.marginLeftLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Left")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginRightLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Right")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginTopLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Top")) #$NON-NLS-1$ #$NON-NLS-2$
        self.marginBotLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _blogappextstr(u"imagedialog.Bottom")) #$NON-NLS-1$ #$NON-NLS-2$

        self.marginTopText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY, size=wx.Size(25, -1))
        self.marginBotText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY, size=wx.Size(25, -1))
        self.marginLeftText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY, size=wx.Size(25, -1))
        self.marginRightText = ZValidatingTextCtrl(ZCssLengthSelectionValidator(flags=ZCssLengthSelectionValidator.ALLOW_EMPTY), self, wx.ID_ANY, size=wx.Size(25, -1))
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        genTNFlag = self.model.generateTNFlag
        self.genRadioButton.SetValue(genTNFlag)
        self.doNotGenRadioButton.SetValue(not genTNFlag)
        self._enableWidgets(genTNFlag)

        tnSize = self._recallThumbnailSize()
        idx = 0
        try:
            idx = ZThumbnailSizeMenuLabels.SIZE_KEYWORDS.index( tnSize )
        except:
            idx = 1
        self.sizeChoice.SetSelection(idx)

        (top, right, bot, left) = self._recallMargins()
        self.marginTopText.SetValue(getSafeString(top))
        self.marginRightText.SetValue(getSafeString(right))
        self.marginBotText.SetValue(getSafeString(bot))
        self.marginLeftText.SetValue(getSafeString(left))

        (width, style, cssColor) = self._recallBorder()
        if cssColor:
            red = cssColor[0]
            green = cssColor[1]
            blue = cssColor[2]
            color = wx.Colour(red, green, blue)
            self.borderColorPicker.SetColour(color)
        self.borderWidthText.SetValue(getSafeString(width))
        style = getSafeString(style).lower()
        idx = 0
        try:
            idx = ZImageBorderMenuLabels.BORDER_KEYWORDS.index( style )
        except:
            idx = 0
        self.borderStyleChoice.SetSelection(idx)
        self._updateBorderControlsState()

        align = getSafeString(self._recallAlignment())
        idx = 0
        try:
            idx = ZImageAlignMenuLabels.ALIGN_KEYWORDS.index( align.lower() )
        except:
            idx = 0
        self.alignChoice.SetSelection(idx)
    # end _populateNonHeaderWidgets()

    def _recallThumbnailSize(self):
        return self.model.size
    # end _recallThumbnailSize()

    def _recallMargins(self):
        return (self.model.marginTop, self.model.marginRight, self.model.marginBottom, self.model.marginLeft)
    # end _recallMargins()

    def _recallBorder(self):
        return (self.model.borderWidth, self.model.borderStyle, self.model.borderColor)
    # end _recallBorder()

    def _recallAlignment(self):
        return self.model.alignment
    # end _recallAlignment()

    def _layoutNonHeaderWidgets(self):
        # Border
        borderGridSizer = wx.FlexGridSizer(3, 2, 2, 2)
        borderGridSizer.Add(self.borderStyleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderStyleChoice, 1, wx.EXPAND | wx.ALL, 1)
        borderGridSizer.Add(self.borderWidthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderWidthText, 1, wx.EXPAND | wx.ALL, 1)
        borderGridSizer.Add(self.borderColorLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        borderGridSizer.Add(self.borderColorPicker, 0,wx.ALL, 1)

        # Margins
        marginGridSizer = wx.FlexGridSizer(4, 4, 2, 2)
        marginGridSizer.AddGrowableCol(1)
        marginGridSizer.AddGrowableCol(3)
        marginGridSizer.Add(self.marginTopLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginTopText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginLeftLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginLeftText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginBotLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginBotText, 1, wx.EXPAND | wx.ALL, 1)
        marginGridSizer.Add(self.marginRightLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)
        marginGridSizer.Add(self.marginRightText, 1, wx.EXPAND | wx.ALL, 1)

        borderSizer = wx.StaticBoxSizer(self.borderStaticBox, wx.VERTICAL)
        borderSizer.AddSizer(borderGridSizer, 1, wx.EXPAND | wx.ALL, 2)

        marginSizer = wx.StaticBoxSizer(self.marginStaticBox, wx.VERTICAL)
        marginSizer.AddSizer(marginGridSizer, 1, wx.EXPAND | wx.ALL, 2)

        sizeSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizeSizer.Add(self.sizeLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizeSizer.Add(self.sizeChoice, 0, wx.ALL, 2)

        alignSizer = wx.BoxSizer(wx.HORIZONTAL)
        alignSizer.Add(self.alignLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        alignSizer.Add(self.alignChoice, 0, wx.ALL, 2)

        sizeAndBorderSizer = wx.BoxSizer(wx.VERTICAL)
        sizeAndBorderSizer.AddSizer(sizeSizer, 0, wx.EXPAND | wx.ALL, 1)
        sizeAndBorderSizer.AddSizer(borderSizer, 1, wx.EXPAND | wx.ALL, 1)

        alignAndMarginSizer = wx.BoxSizer(wx.VERTICAL)
        alignAndMarginSizer.AddSizer(alignSizer, 0, wx.EXPAND | wx.ALL, 1)
        alignAndMarginSizer.AddSizer(marginSizer, 1, wx.EXPAND | wx.ALL, 1)

        twoColumnSizer = wx.BoxSizer(wx.HORIZONTAL)
        twoColumnSizer.AddSizer(sizeAndBorderSizer, 2, wx.EXPAND | wx.ALL, 1)
        twoColumnSizer.AddSizer(alignAndMarginSizer, 3, wx.EXPAND | wx.ALL, 1)

        tnSettingsSizer = wx.StaticBoxSizer(self.tnSettingsGroupBox, wx.VERTICAL)
        tnSettingsSizer.AddSizer(twoColumnSizer, 0, wx.EXPAND | wx.ALL, 2)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.doNotGenRadioButton, 0, wx.ALL, 3)
        mainSizer.Add(self.genRadioButton, 0, wx.ALL, 3)
        mainSizer.AddSizer(tnSettingsSizer, 1, wx.EXPAND | wx.ALL, 3)

        return mainSizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CHOICE, self.onBorderStyleChanged, self.borderStyleChoice)
        self.Bind(wx.EVT_RADIOBUTTON, self.onDoNotGenButton, self.doNotGenRadioButton)
        self.Bind(wx.EVT_RADIOBUTTON, self.onGenerateButton, self.genRadioButton)

        self._bindValidatingWidget(self.borderWidthText)
        self._bindValidatingWidget(self.marginTopText)
        self._bindValidatingWidget(self.marginRightText)
        self._bindValidatingWidget(self.marginBotText)
        self._bindValidatingWidget(self.marginLeftText)

        self.Bind(wx.EVT_BUTTON, self.onOK, self.FindWindowById(wx.ID_OK))
    # end _bindWidgetEvents()

    def _enableWidgets(self, enabled = True):
        self.tnSettingsGroupBox.Enable(enabled)
        self.sizeLabel.Enable(enabled)
        self.sizeChoice.Enable(enabled)
        self.alignLabel.Enable(enabled)
        self.alignChoice.Enable(enabled)
        self.borderStaticBox.Enable(enabled)
        self.borderStyleLabel.Enable(enabled)
        self.borderStyleChoice.Enable(enabled)
        self.borderWidthLabel.Enable(enabled)
        self.borderWidthText.Enable(enabled)
        self.borderColorLabel.Enable(enabled)
        self.borderColorPicker.Enable(enabled)
        self.marginStaticBox.Enable(enabled)
        self.marginTopLabel.Enable(enabled)
        self.marginTopText.Enable(enabled)
        self.marginLeftLabel.Enable(enabled)
        self.marginLeftText.Enable(enabled)
        self.marginBotLabel.Enable(enabled)
        self.marginBotText.Enable(enabled)
        self.marginRightLabel.Enable(enabled)
        self.marginRightText.Enable(enabled)
    # end _enableWidgets()

    def _updateModel(self):
        self.model.generateTNFlag = self.genRadioButton.GetValue()

        # TN Size
        idx = self.sizeChoice.GetSelection()
        if idx >=0 and idx < len(ZThumbnailSizeMenuLabels.SIZE_KEYWORDS):
            size = ZThumbnailSizeMenuLabels.SIZE_KEYWORDS[idx]
            self.model.size = size

        # Alignment
        idx = self.alignChoice.GetSelection()
        if idx >=0 and idx < len(ZImageAlignMenuLabels.ALIGN_KEYWORDS):
            align = ZImageAlignMenuLabels.ALIGN_KEYWORDS[idx]
            self.model.alignment = align

        # Margin
        t = self.marginTopText.GetValue().strip()
        r = self.marginRightText.GetValue().strip()
        b = self.marginBotText.GetValue().strip()
        l = self.marginLeftText.GetValue().strip()
        self.model.marginTop = t
        self.model.marginRight = r
        self.model.marginBottom = b
        self.model.marginLeft = l

        # Border
        style = ZImageBorderMenuLabels.BORDER_KEYWORDS[0] # default is None
        idx = self.borderStyleChoice.GetSelection()
        if idx >=0 and idx < len(ZImageBorderMenuLabels.BORDER_KEYWORDS):
            style = ZImageBorderMenuLabels.BORDER_KEYWORDS[idx]
        width = self.borderWidthText.GetValue().strip()
        color = self.borderColorPicker.GetColour()

        self.model.borderStyle = style
        self.model.borderWidth = width
        self.model.borderColor = (color.Red(), color.Green(), color.Blue())
    # end updateModel()

    def onDoNotGenButton(self, event):
        self._enableWidgets(False)
        self.isValid = True
        self._doValid()
        event.Skip()
    # end onDoNotGenButton()

    def onGenerateButton(self, event):
        self._enableWidgets(True)
        self._validate()
        event.Skip()
    # end onGenerateButton()

    def onOK(self, event):
        self._updateModel()
        self.model._saveToPrefs()
        event.Skip()
    # end onOK()

    def _updateBorderControlsState(self):
        enable = self.borderStyleChoice.GetCurrentSelection() > 0
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

    def onBorderStyleChanged(self, event):
        self._updateBorderControlsState()
        event.Skip()
    # end onBorderStyleChanged()

    def getModel(self):
        return self.model
    # end getModel()

    def _getHeaderTitle(self):
        return _extstr(u"imagehandlerdialog.CreateImageThumbnail") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"imagehandlerdialog.CreateImageThumbnailDesc") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/image/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

# end ZImageDialog
