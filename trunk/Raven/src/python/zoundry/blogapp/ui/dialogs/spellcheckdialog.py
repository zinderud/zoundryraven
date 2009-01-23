from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.messages import _extstr
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
import wx


# ---------------------------------------------------------------------------------------
# The standard modal dialog used for spell check
# ---------------------------------------------------------------------------------------
class ZSpellCheckDialog(ZBaseDialog, ZPersistentDialogMixin):

    def __init__(self, parent, spellCheckModel):
        self.spellCheckModel = spellCheckModel
        ZBaseDialog.__init__(self, parent,wx.ID_ANY, _extstr(u"spellcheckdialog.DialogTitle"), size = wx.Size(350, 340), style =wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZSpellCheckDialog") #$NON-NLS-1$ #$NON-NLS-2$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.SPELLCHECK_DIALOG, False, True)
    # end __init__()

    def _getButtonTypes(self):
        return ZBaseDialog.CLOSE_BUTTON
    # end _getButtonTypes()

    def _createContentWidgets(self):

        self.misspellLabel = wx.StaticText(self, -1,_extstr(u"spellcheckdialog.MisspellWord") + u":", size=wx.Size(-1,20)) #$NON-NLS-1$ #$NON-NLS-2$
        self.replaceLabel = wx.StaticText(self, -1,_extstr(u"spellcheckdialog.ReplaceWith") + u":", size=wx.Size(-1,20)) #$NON-NLS-1$ #$NON-NLS-2$
        self.suggestLabel = wx.StaticText(self, -1,_extstr(u"spellcheckdialog.Suggestions") + u":", size=wx.Size(-1,20)) #$NON-NLS-1$ #$NON-NLS-2$

        self.ignoreBtn = wx.Button(self, -1, _extstr(u"spellcheckdialog.Ignore")) #$NON-NLS-1$
        self.ignoreAllBtn = wx.Button(self, -1, _extstr(u"spellcheckdialog.IgnoreAll")) #$NON-NLS-1$
        self.addBtn = wx.Button(self, -1, _extstr(u"spellcheckdialog.Add")) #$NON-NLS-1$
        self.replaceBtn = wx.Button(self, -1, _extstr(u"spellcheckdialog.Replace")) #$NON-NLS-1$
        self.replaceAllBtn = wx.Button(self, -1, _extstr(u"spellcheckdialog.ReplaceAll")) #$NON-NLS-1$

        self.replacewordCntrl = wx.TextCtrl(id=wx.NewId(), parent=self, size=wx.Size(-1,20), style=wx.TE_PROCESS_ENTER)
        self.suggestionsCntrl = wx.ListBox(id=wx.NewId(), parent=self, style=wx.LB_SINGLE|wx.LB_HSCROLL|wx.LB_NEEDED_SB)

        self.mispellwordCntrl = wx.TextCtrl(id=wx.NewId(), parent=self, style=wx.TE_MULTILINE|wx.TE_RICH2)

    # end _createContentWidgets()

    def _populateContentWidgets(self):
        self._setSpellCheckResult( self.spellCheckModel.getSpellCheckResult() )
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        # empty label as a filler
        filler1 = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$
        filler3 = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$
        filler4 = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$
        filler5 = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$

        # layout ignore, ignoreall, add vertically in a panel.
        buttonSizer1 = wx.BoxSizer(wx.VERTICAL)
        buttonSizer1.Add(self.ignoreBtn, 0, wx.ALIGN_LEFT |wx.ALL, 2)
        buttonSizer1.Add(self.ignoreAllBtn, 0, wx.ALIGN_LEFT |wx.ALL, 2)
        buttonSizer1.Add(self.addBtn, 0, wx.ALIGN_LEFT |wx.ALL, 2)

        # layout replace and replaceall vertically in a panel.
        buttonSizer2 = wx.BoxSizer(wx.VERTICAL)
        buttonSizer2.Add(self.replaceBtn, 0, wx.ALIGN_LEFT |wx.ALL, 2)
        buttonSizer2.Add(self.replaceAllBtn, 0, wx.ALIGN_LEFT |wx.ALL, 2)

        # layout all in a  2col x 6row flex grid.
        sizer = wx.FlexGridSizer(6,2,4,4)
        sizer.AddGrowableCol(0)
        # margin:
        m = 8
        # row 1: label
        sizer.AddMany([
            (self.misspellLabel, 1, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, m),
            (filler1, 0,wx.ALIGN_LEFT| wx.RIGHT, m)
            ])

        # row 2: misspell word control and button panel 1
        sizer.AddMany([
            (self.mispellwordCntrl, 1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND| wx.LEFT, m),
            (buttonSizer1, 0,wx.ALIGN_LEFT | wx.EXPAND| wx.RIGHT, m)
            ])

        # row 3: label
        sizer.AddMany([
            (self.replaceLabel, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL| wx.EXPAND| wx.LEFT | wx.TOP, m),
            (filler3, 0,wx.ALIGN_LEFT| wx.RIGHT, m)
            ])

        # row 4: replace text control
        sizer.AddMany([
            (self.replacewordCntrl, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL| wx.EXPAND| wx.LEFT, m),
            (filler4, 0,wx.ALIGN_LEFT| wx.RIGHT, m)
            ])

        # row 5: label
        sizer.AddMany([
            (self.suggestLabel, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL| wx.EXPAND| wx.LEFT | wx.TOP, m),
            (filler5, 0,wx.ALIGN_LEFT | wx.RIGHT, m)
            ])

        # row 6: suggestions control and button panel 2
        sizer.AddMany([
            (self.suggestionsCntrl, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND| wx.LEFT, m),
            (buttonSizer2, 0,wx.ALIGN_LEFT | wx.EXPAND| wx.RIGHT, m)
            ])

        return sizer
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onIgnore, self.ignoreBtn)
        self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, self.ignoreAllBtn)
        self.Bind(wx.EVT_BUTTON, self.onAddWord, self.addBtn)
        self.Bind(wx.EVT_BUTTON, self.onReplace, self.replaceBtn)
        self.Bind(wx.EVT_BUTTON, self.onReplaceAll, self.replaceAllBtn)

        self.Bind(wx.EVT_TEXT_ENTER, self.onReplaceWordEnterPressed, self.replacewordCntrl)
        self.Bind(wx.EVT_CHAR, self.onReplaceWordKeyPressed, self.replacewordCntrl)
        self.Bind(wx.EVT_LISTBOX, self.onSuggestionListSelection, self.suggestionsCntrl)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onSuggestionListDoubleClick, self.suggestionsCntrl)
    # end _bindWidgetEvents()

    def _doCheckNextWord(self):
        spellCheckResult = self.spellCheckModel.checkNextWord()
        self._setSpellCheckResult(spellCheckResult)
    # end _doNextCheck()

    def _setSpellCheckResult(self, spellCheckResult):
        if spellCheckResult and spellCheckResult.isFinished():
            self.Close()
            return
        self._updateUI(spellCheckResult)
    # end _setSpellCheckResult()

    def _updateUI(self, spellCheckResult):
        # update UI given IZSpellCheckResult (which could be None)
        self._updateMisspelledWordUI(spellCheckResult)
        self._updateSuggestionListUI(spellCheckResult)
        self._updateReplaceButtonsState()
    # end _updateUI()

    def _updateMisspelledWordUI(self, spellCheckResult):
        self.mispellwordCntrl.Clear()
        if not spellCheckResult:
            return
        (sentence, startPos, endPos)= self.spellCheckModel.getMisspelledWordData(spellCheckResult)
        self.mispellwordCntrl.SetValue(sentence)
        if startPos >= 0 and endPos > 0 and endPos > startPos:
            self.mispellwordCntrl.SetStyle(startPos, endPos, wx.TextAttr(u"RED", u"YELLOW"))  #$NON-NLS-1$  #$NON-NLS-2$
    # _updateMisspelledWordUI()

    def _updateSuggestionListUI(self, spellCheckResult):
        self.replacewordCntrl.Clear()
        self.suggestionsCntrl.Clear()
        if not spellCheckResult:
            return

        sList = self.spellCheckModel.getSuggestions(spellCheckResult)
        self.suggestionsCntrl.InsertItems(sList,0)
        if len(sList) > 0:
            self.replacewordCntrl.SetValue(sList[0])
            self.replacewordCntrl.SetSelection(-1,-1)
            self.suggestionsCntrl.SetSelection(0,True)
    # end _updateSuggestionListUI()

    def _updateReplaceButtonsState(self):
        enable = self.suggestionsCntrl.GetCount() > 0 or getNoneString( self.replacewordCntrl.GetValue()) is not None
        self.replaceBtn.Enable(enable)
        self.replaceAllBtn.Enable(enable)
        self.suggestionsCntrl.Enable(self.suggestionsCntrl.GetCount() > 0)
    # end _updateReplaceButtonsState()

    def _doReplace(self, replaceAll):
        word = getNoneString( self.replacewordCntrl.GetValue())
        if word:
            self.spellCheckModel.replace(word, replaceAll)
        self._doCheckNextWord()
    # end _doReplace()

    def _doIgnore(self, ignoreAll):
        self.spellCheckModel.ignore(ignoreAll)
        self._doCheckNextWord()
    # end _doReplace()

    def onIgnore(self, event): #@UnusedVariable
        self._doIgnore(False)
    # end onIgnore

    def onIgnoreAll(self, event): #@UnusedVariable
        self._doIgnore(True)
    # end onIgnoreAll

    def onAddWord(self, event): #@UnusedVariable
        self.spellCheckModel.addWord()
        self._doCheckNextWord()
    # end onAddWord

    def onReplace(self, event): #@UnusedVariable
        self._doReplace(False)
    # end onReplace

    def onReplaceAll(self, event): #@UnusedVariable
        self._doReplace(True)
    # end onReplaceAll

    def onReplaceWordEnterPressed(self, event):
        self.onReplace(event)
    # end onReplaceWordEnterPressed

    def onReplaceWordKeyPressed(self, event): #@UnusedVariable
        self._updateReplaceButtonsState()
    # end onReplaceWordKeyPressed

    def onSuggestionListSelection(self, event): #@UnusedVariable
        if self.suggestionsCntrl.GetStringSelection():
            self.replacewordCntrl.SetValue(self.suggestionsCntrl.GetStringSelection())
    # end onSuggestionListSelection

    def onSuggestionListDoubleClick(self, event): #@UnusedVariable
        if self.suggestionsCntrl.GetStringSelection():
            self.replacewordCntrl.SetValue(self.suggestionsCntrl.GetStringSelection())
            self._doReplace(False)
    # end onSuggestionListDoubleClick

#end ZSpellCheckDialog



