from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.css.csscolor import ZCssColor
from zoundry.blogapp.messages import _extstr
import wx

PREVIEW_HTML = u"""<html xmlns=""><head><title>hello</title></head>
<body style="font-size:12px;margin:0px;padding:0px;">
<p style="%s">
ABCDEFGHIJKLMNOPQRSTUVWXYZ <br/>
0123456789
</p>
</body>
</html>""" #$NON-NLS-1$

# map containing last used settings.
G_USER_FONT_SETTINGS_MAP = {}
# --------------------------------------------------------------------------------
# The Edit Hyperlink dialog.  This dialog allows the user to edit the properties
# of a hyperlink.
# --------------------------------------------------------------------------------
class ZFontDialog(ZBaseDialog):

    def __init__(self, parent, model):
        # model is instance of ZFontModel.
        self.model = model
        fontsEnum = wx.FontEnumerator()
        fontsEnum.EnumerateFacenames()
        self.systemFontNames = fontsEnum.GetFacenames()
        self.systemFontNames.sort()

        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"fontdialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZFontDialog") #$NON-NLS-1$ #$NON-NLS-2$
        #bestHeight = self.GetBestSizeTuple()[1]
        #self.SetMinSize(wx.Size(-1, bestHeight))
    # end __init__()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def _createContentWidgets(self):
        self.sizeStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"fontdialog.FontSettings")) #$NON-NLS-1$
        self.previewStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"fontdialog.FontPreview")) #$NON-NLS-1$
        self.fontLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.FontName")) #$NON-NLS-1$ #$NON-NLS-2$
        self.sizeLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.FontSize")) #$NON-NLS-1$ #$NON-NLS-2$
        self.colorLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.Color")) #$NON-NLS-1$ #$NON-NLS-2$
        self.backgroundLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.BackgroundColor")) #$NON-NLS-1$ #$NON-NLS-2$

        sizes = u"Default,8px,10px,12px,14px,16px,18px,24px,36px".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
        self.sizeChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = sizes)

        fonts = [u"Default"] #$NON-NLS-1$
        fonts.extend(self.systemFontNames)
        self.fontChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = fonts)

        colors = [u"Default"] #$NON-NLS-1$
        self.colorChoicesHasRecent = False
        self.colorChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = colors)
        self.colorPicker = wx.ColourPickerCtrl(self)

        bgColors = [u"Default"] #$NON-NLS-1$
        self.bgColorChoicesHasRecent = False
        self.bgColorChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = bgColors)
        self.bgColorPicker = wx.ColourPickerCtrl(self)

        self.previewCntrl = ZHTMLViewControl(self, wx.ID_ANY)

    # end _createNonHeaderWidgets()

    def _populateContentWidgets(self):

        w3cColors = []
        for (n,v) in ZCssColor.COLOR_NAMES.iteritems(): #@UnusedVariable
            w3cColors.append(n.title())
        w3cColors.sort()

        global G_USER_FONT_SETTINGS_MAP
        colors = [u"Default"] #$NON-NLS-1$
        colors.extend(w3cColors)
        colors.append(u"Custom") #$NON-NLS-1$
        if G_USER_FONT_SETTINGS_MAP.has_key(u"cssColor") and G_USER_FONT_SETTINGS_MAP[u"cssColor"]: #$NON-NLS-1$ #$NON-NLS-2$
            self.colorChoicesHasRecent = True
            colors.append(u"Recent %s" % G_USER_FONT_SETTINGS_MAP[u"cssColor"].getCssColor() ) #$NON-NLS-1$ #$NON-NLS-2$
        else:
            colors.append(u"Recent") #$NON-NLS-1$
        self.colorChoices.Clear()
        for c in colors:
            self.colorChoices.Append(c)

        bgColors = [u"Default"] #$NON-NLS-1$
        bgColors.extend(w3cColors)
        bgColors.append(u"Custom") #$NON-NLS-1$
        if G_USER_FONT_SETTINGS_MAP.has_key(u"cssBgColor") and G_USER_FONT_SETTINGS_MAP[u"cssBgColor"]: #$NON-NLS-1$ #$NON-NLS-2$
            self.bgColorChoicesHasRecent = True
            bgColors.append(u"Recent %s" % G_USER_FONT_SETTINGS_MAP[u"cssBgColor"].getCssColor() ) #$NON-NLS-1$ #$NON-NLS-2$
        else:
            bgColors.append(u"Recent") #$NON-NLS-1$
        self.bgColorChoices.Clear()
        for c in bgColors:
            self.bgColorChoices.Append(c)

        self._selectChoiceItem(self.fontChoices, self.model.getFontName() )
        self._selectChoiceItem(self.sizeChoices, self.model.getFontSize() )
        if self.model.getColor():
            color = wx.Colour(self.model.getColor().getRed(), self.model.getColor().getGreen(), self.model.getColor().getBlue())
            self.colorPicker.SetColour(color)
            self._handleOnPickColorSelection( self.colorChoices, self.colorPicker)

        if self.model.getBackground():
            color = wx.Colour(self.model.getBackground().getRed(), self.model.getBackground().getGreen(), self.model.getBackground().getBlue())
            self.bgColorPicker.SetColour(color)
            self._handleOnPickColorSelection( self.bgColorChoices, self.bgColorPicker)
        self._updatePreview()
    # end _populateNonHeaderWidgets()

    def _layoutContentWidgets(self):
        sizeGridSizer = wx.FlexGridSizer(4, 2, 1, 1)

        sizeGridSizer.Add(self.fontLabel, 0, wx.ALL, 1)
        sizeGridSizer.Add(self.sizeLabel, 0, wx.ALL, 1)
        sizeGridSizer.Add(self.fontChoices, 1, wx.EXPAND | wx.ALL, 1)
        sizeGridSizer.Add(self.sizeChoices, 1, wx.EXPAND | wx.ALL, 1)

        sizeGridSizer.Add(self.colorLabel, 0, wx.ALL, 1)
        sizeGridSizer.Add(self.backgroundLabel, 0, wx.ALL, 1)

        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer1.Add(self.colorChoices, 1,  wx.EXPAND |wx.ALL, 1)
        hsizer1.Add(self.colorPicker, 0, wx.ALL, 1)

        sizeGridSizer.AddSizer(hsizer1, 1,  wx.EXPAND |wx.ALL, 1)

        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(self.bgColorChoices, 1,  wx.EXPAND | wx.ALL, 1)
        hsizer2.Add(self.bgColorPicker, 0, wx.ALL, 1)

        sizeGridSizer.AddSizer(hsizer2, 1,  wx.EXPAND |wx.ALL, 1)

        sizeStaticBoxSizer = wx.StaticBoxSizer(self.sizeStaticBox, wx.VERTICAL)
        sizeStaticBoxSizer.AddSizer(sizeGridSizer, 1, wx.EXPAND | wx.ALL, 1)

        previewStaticBoxSizer = wx.StaticBoxSizer(self.previewStaticBox, wx.VERTICAL)
        previewStaticBoxSizer.Add(self.previewCntrl, 1, wx.EXPAND | wx.ALL, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(sizeStaticBoxSizer, 0, wx.EXPAND | wx.ALL, 4)
        sizer.AddSizer(previewStaticBoxSizer, 2, wx.EXPAND | wx.ALL, 4)
        return sizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onOK, self.FindWindowById(wx.ID_OK) )
        self.Bind(wx.EVT_CHOICE, self.onFontChoiceChanged, self.fontChoices)
        self.Bind(wx.EVT_CHOICE, self.onSizeChoiceChanged, self.sizeChoices)
        self.Bind(wx.EVT_CHOICE, self.onColorChoiceChanged, self.colorChoices)
        self.Bind(wx.EVT_CHOICE, self.onBgColorChoiceChanged, self.bgColorChoices)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorPicked, self.colorPicker)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onBgColorPicked, self.bgColorPicker)
    # end _bindWidgetEvents()

    def _updatePreview(self):
        style = u"" #$NON-NLS-1$
        if self.colorChoices.GetSelection() > 0:
            style = style + u"color:%s; " %  self.colorPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)  #$NON-NLS-1$
        if self.bgColorChoices.GetSelection() > 0:
            style = style + u"background:%s; " %  self.bgColorPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)  #$NON-NLS-1$

        if self.fontChoices.GetSelection() > 0:
            style = style + u"font-family:%s; "  % self.fontChoices.GetStringSelection() #$NON-NLS-1$

        if self.sizeChoices.GetSelection() > 0:
            style = style + u"font-size:%s; "  % self.sizeChoices.GetStringSelection() #$NON-NLS-1$

        self.previewCntrl.setHtmlValue( PREVIEW_HTML % style)
    # end _updatePreview()

    def _selectChoiceItem(self, choiceControl, value):
        selectIdx = 0
        if value:
            value = value.lower().strip()
            for idx in range( choiceControl.GetCount() ):
                s = choiceControl.GetString(idx).lower().strip()
                if s == value:
                    selectIdx = idx
                    break
        choiceControl.Select(selectIdx)
    # end _selectChoiceItem

    def _handleOnColorChoiceSelection(self, choiceControl, colorPickerControl):
        idx = choiceControl.GetSelection()
        max = choiceControl.GetCount()
        # idx = 0: default
        # idx = N-2: Custom
        # idx = N-1: recent
         
        if idx > 0 and idx < (max-2):
            colorName = choiceControl.GetStringSelection().strip().lower()
            cssColor = ZCssColor(colorName)
            color = wx.Colour(cssColor.getRed(), cssColor.getGreen(), cssColor.getBlue())
            colorPickerControl.SetColour(color)
        elif idx == (max-2):
            # custom
            pass
        elif idx == (max-1):
            # recent...
            global G_USER_FONT_SETTINGS_MAP
            cssColor = None
            if self.colorChoices == choiceControl and G_USER_FONT_SETTINGS_MAP.has_key(u"cssColor"): #$NON-NLS-1$ #$NON-NLS-2$
                cssColor = G_USER_FONT_SETTINGS_MAP[u"cssColor"] #$NON-NLS-1$
            elif self.bgColorChoices == choiceControl and G_USER_FONT_SETTINGS_MAP.has_key(u"cssBgColor"): #$NON-NLS-1$ #$NON-NLS-2$
                cssColor = G_USER_FONT_SETTINGS_MAP[u"cssBgColor"] #$NON-NLS-1$
            if cssColor:     
                color = wx.Colour(cssColor.getRed(), cssColor.getGreen(), cssColor.getBlue())
                colorPickerControl.SetColour(color)
        
    # end _handleOnColorChoiceSelection

    def _handleOnPickColorSelection(self, choiceControl, colorPickerControl):
        cssHexColor = colorPickerControl.GetColour().GetAsString(wx.C2S_HTML_SYNTAX).lower()
        max = choiceControl.GetCount()
        # Default is the last-1 choice i.e. "custom".
        idx = max-2
        for i in range(0, max):
            colorName = choiceControl.GetString(i).lower().strip()
            if ZCssColor.COLOR_NAMES.has_key(colorName) and ZCssColor.COLOR_NAMES[colorName].lower() == cssHexColor:
                idx = i
                break
        choiceControl.SetSelection(idx)
    # end _handleOnPickColorSelection

    def _updateModel(self):
        fontName = None
        fontSize = None
        cssColor = None
        cssBgColor = None

        global G_USER_FONT_SETTINGS_MAP

        if self.fontChoices.GetSelection() > 0:
            fontName = self.fontChoices.GetStringSelection()
            G_USER_FONT_SETTINGS_MAP[u"fontName"] = fontName    #$NON-NLS-1$

        if self.sizeChoices.GetSelection() > 0:
            fontSize = self.sizeChoices.GetStringSelection()
            G_USER_FONT_SETTINGS_MAP[u"fontSize"] = fontSize    #$NON-NLS-1$

        if self.colorChoices.GetSelection() > 0:
            cssColor = ZCssColor( self.colorPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX) )
            G_USER_FONT_SETTINGS_MAP[u"cssColor"] = cssColor    #$NON-NLS-1$

        if self.bgColorChoices.GetSelection() > 0:
            cssBgColor = ZCssColor( self.bgColorPicker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX) )
            G_USER_FONT_SETTINGS_MAP[u"cssBgColor"] = cssBgColor    #$NON-NLS-1$

        self.model.setFontName(fontName)
        self.model.setFontSize(fontSize)
        self.model.setColor(cssColor)
        self.model.setBackground(cssBgColor)
    # end _updateModel()

    def onFontChoiceChanged(self, event): #@UnusedVariable
        self._updatePreview()
    # end onFontChoiceChanged()

    def onSizeChoiceChanged(self, event): #@UnusedVariable
        self._updatePreview()
    # end onSizeChoiceChanged()

    def onColorChoiceChanged(self, event): #@UnusedVariable
        self._handleOnColorChoiceSelection( self.colorChoices, self.colorPicker)
        self._updatePreview()
    # end onColorChoiceChanged()

    def onBgColorChoiceChanged(self, event): #@UnusedVariable
        self._handleOnColorChoiceSelection( self.bgColorChoices, self.bgColorPicker)
        self._updatePreview()
    # end onBgColorChoiceChanged()

    def onColorPicked(self, event): #@UnusedVariable
        self._handleOnPickColorSelection( self.colorChoices, self.colorPicker)
        self._updatePreview()
    # end onColorPicked

    def onBgColorPicked(self, event): #@UnusedVariable
        self._handleOnPickColorSelection( self.bgColorChoices, self.bgColorPicker)
        self._updatePreview()
    # end onBgColorPicked

    def onOK(self, event):
        # persist settings to model.
        self._updateModel()
        event.Skip()
    # end onOK()

# end ZFontDialog