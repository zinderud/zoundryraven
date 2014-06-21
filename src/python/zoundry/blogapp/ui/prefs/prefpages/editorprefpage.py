from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------------
# A user preference page impl for the General user prefs section.
# ------------------------------------------------------------------------------------
class ZEditorPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.label = wx.StaticText(self, wx.ID_ANY, u"Editor General Preferences") #$NON-NLS-1$
    # end createWidgets()

    def bindWidgetEvents(self):
        pass
    # end bindWidgetEvents()

    def populateWidgets(self):
        pass
    # end populateWidgets()

    def layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()        
    # end layoutWidgets()


    def apply(self):
        return ZApplicationPreferencesPrefPage.apply(self)
    # end apply()

# end ZEditorPreferencePage

#--------------------------------------------------------------------------------
PREVIEW_HTML = u"""<html xmlns=""><head><title>ZEditorPreferencePage</title></head>
<body style="margin:5px;padding:5px;%s">
<p>ABCDEFGHIJKLMNOPQRSTUVWXYZ <br/>
0123456789
</p>
<p>
   Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed wisi.
   Nulla at dolor et diam molestie consequat.
   Vestibulum sed tellus vitae tortor sollicitudin mollis.
</p>
</body>
</html>""" #$NON-NLS-1$
# ------------------------------------------------------------------------------------
# A user preference page impl for Editor Fonts
# ------------------------------------------------------------------------------------
class ZEditorFontPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        fontsEnum = wx.FontEnumerator()
        fontsEnum.EnumerateFacenames()
        self.systemFontNames = fontsEnum.GetFacenames()
        self.systemFontNames.sort()
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def _getUserPrefFontName(self):
        fontName = getSafeString( self.session.getUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_NAME, u"") ) #$NON-NLS-1$
        return fontName
    # end _getUserPrefFontName()

    def _setUserPrefFontName(self, fontName):
        fontName = getSafeString(fontName)   
        prev = self._getUserPrefFontName()
        if fontName != prev:     
            self.session.setUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_NAME, fontName)
    # end _setUserPrefFontName()

    def _getUserPrefFontSize(self):
        fontSize = getSafeString( self.session.getUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_SIZE, u"") ) #$NON-NLS-1$
        return fontSize
    # end _getUserPrefFontSize()

    def _setUserPrefFontSize(self, fontSize):
        fontSize = getSafeString(fontSize)
        prev = self._getUserPrefFontSize()
        if fontSize != prev:             
            self.session.setUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_SIZE, fontSize)
    # end _setUserPrefFontSize()

    def createWidgets(self):
        self.sizeStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"fontdialog.FontSettings")) #$NON-NLS-1$
        self.previewStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"fontdialog.FontPreview")) #$NON-NLS-1$
        self.fontLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.FontName")) #$NON-NLS-1$ #$NON-NLS-2$
        self.sizeLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"fontdialog.FontSize")) #$NON-NLS-1$ #$NON-NLS-2$

        sizes = u"Default,10px,12px,14px,16px,18px,22px,24px,26px,28px,36px".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
        self.sizeChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = sizes)

        fonts = [u"Default"] #$NON-NLS-1$
        fonts.extend(self.systemFontNames)
        self.fontChoices = wx.Choice(self, wx.ID_ANY, (100, -1), choices = fonts)
        self.previewCntrl = ZHTMLViewControl(self, wx.ID_ANY)
    # end createWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHOICE, self.onFontChoiceChanged, self.fontChoices)
        self.Bind(wx.EVT_CHOICE, self.onSizeChoiceChanged, self.sizeChoices)
    # end bindWidgetEvents()

    def populateWidgets(self):
        self._selectChoiceItem(self.fontChoices,  self._getUserPrefFontName() )
        self._selectChoiceItem(self.sizeChoices,  self._getUserPrefFontSize() )
        self._updatePreview()
    # end populateWidgets()

    def layoutWidgets(self):
        sizeGridSizer = wx.FlexGridSizer(2, 2, 1, 1)
        sizeGridSizer.Add(self.fontLabel, 0, wx.ALL, 1)
        sizeGridSizer.Add(self.sizeLabel, 0, wx.ALL, 1)
        sizeGridSizer.Add(self.fontChoices, 1, wx.EXPAND | wx.ALL, 1)
        sizeGridSizer.Add(self.sizeChoices, 1, wx.EXPAND | wx.ALL, 1)

        sizeStaticBoxSizer = wx.StaticBoxSizer(self.sizeStaticBox, wx.VERTICAL)
        sizeStaticBoxSizer.AddSizer(sizeGridSizer, 1, wx.EXPAND | wx.ALL, 1)

        previewStaticBoxSizer = wx.StaticBoxSizer(self.previewStaticBox, wx.VERTICAL)
        previewStaticBoxSizer.Add(self.previewCntrl, 1, wx.EXPAND | wx.ALL, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(sizeStaticBoxSizer, 0, wx.EXPAND | wx.ALL, 4)
        sizer.AddSizer(previewStaticBoxSizer, 2, wx.EXPAND | wx.ALL, 4)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def _updatePreview(self):
        style = u"" #$NON-NLS-1$
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

    def onFontChoiceChanged(self, event): #@UnusedVariable
        self._updatePreview()
        fontName = self.fontChoices.GetStringSelection()
        self._setUserPrefFontName(fontName)
    # end onFontChoiceChanged()

    def onSizeChoiceChanged(self, event): #@UnusedVariable
        self._updatePreview()
        fontSize = self.sizeChoices.GetStringSelection()
        self._setUserPrefFontSize(fontSize)
    # end onSizeChoiceChanged()

    def apply(self):
        return ZApplicationPreferencesPrefPage.apply(self)
    # end apply()

# end ZEditorFontPreferencePage
