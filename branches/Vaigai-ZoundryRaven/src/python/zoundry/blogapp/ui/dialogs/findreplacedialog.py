from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ---------------------------------------------------------------------------------------
# The standard modal dialog used for findinf and replacing text
# ---------------------------------------------------------------------------------------
class ZFindReplaceDialog(ZBaseDialog, ZPersistentDialogMixin):

    def __init__(self, parent, findReplaceModel):
        self.findReplaceModel = findReplaceModel
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"findreplacedialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZSpellCheckDialog") #$NON-NLS-1$ #$NON-NLS-2$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.FIND_REPLACE_DIALOG, True, True)

        if getNoneString( self.findReplaceModel.getFindText() ) is not None:
            # since there is a search term preselected, initiate the find process.
            runnable = ZMethodRunnable(self._doFindNext)
            fireUIExecEvent(runnable, self)
    # end __init__()

    def _getButtonTypes(self):
        return ZBaseDialog.CLOSE_BUTTON
    # end _getButtonTypes()

    def _createContentWidgets(self):
        # labels
        self.findLabel = wx.StaticText(self, -1,_extstr(u"findreplacedialog.FindWhat") + u":", size=wx.Size(-1,20)) #$NON-NLS-1$ #$NON-NLS-2$
        self.replaceLabel = wx.StaticText(self, -1,_extstr(u"findreplacedialog.ReplaceWith") + u":", size=wx.Size(-1,20)) #$NON-NLS-1$ #$NON-NLS-2$
        self.notFoundLabel = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$
        self.notFoundLabel.SetForegroundColour(wx.RED)

        # buttons
        self.findBtn = wx.Button(self, -1, _extstr(u"findreplacedialog.Find")) #$NON-NLS-1$
        self.replaceFindBtn = wx.Button(self, -1, _extstr(u"findreplacedialog.ReplaceFind")) #$NON-NLS-1$
        self.replaceAllBtn = wx.Button(self, -1, _extstr(u"findreplacedialog.ReplaceAll")) #$NON-NLS-1$

        # find option checkboxes
        self.matchCaseChk = wx.CheckBox(self, -1, _extstr(u"findreplacedialog.MatchCase")) #$NON-NLS-1$
        self.matchWordChk = wx.CheckBox(self, -1, _extstr(u"findreplacedialog.MatchWholeWord")) #$NON-NLS-1$

        # find replace text combo controls.
        self.findwordCntrl = wx.ComboBox(self, -1, size=wx.Size(-1,20), style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.replacewordCntrl = wx.ComboBox(self, -1,  size=wx.Size(-1,20), style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        self._refreshCombos()

        text = getSafeString( self.findReplaceModel.getFindText() )
        self.findwordCntrl.SetValue( text )
        if len(text) == 0:
            self.findwordCntrl.SetFocus()
        else:
            self.replacewordCntrl.SetFocus()
    # end _populateContentWidgets()

    def _refreshCombos(self):
        oldText = self.findwordCntrl.GetValue()
        self.findwordCntrl.Clear()
        for text in self.findReplaceModel.getFindTextHistory():
            self.findwordCntrl.Append(text)
        self.findwordCntrl.SetValue(oldText)
        
        oldText = self.replacewordCntrl.GetValue()
        self.replacewordCntrl.Clear()
        for text in self.findReplaceModel.getReplaceTextHistory():
            self.replacewordCntrl.Append(text)
        self.replacewordCntrl.SetValue(oldText)
    # end _refreshCombos()

    def _layoutContentWidgets(self):
        # empty label as a filler
        filler = wx.StaticText(self,-1,label=u' ',size=wx.Size(-1,20)) #$NON-NLS-1$
        # layout buttons horizontaly
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.findBtn, 0, wx.ALIGN_CENTRE |wx.ALL, 2)
        buttonSizer.Add(self.replaceFindBtn, 0, wx.ALIGN_CENTRE |wx.ALL, 2)
        buttonSizer.Add(self.replaceAllBtn, 0, wx.ALIGN_CENTRE |wx.ALL, 2)

        # layout findWhat, matchCase/Word and replaceWhat in a 3 row x 2 col layout
        flexsizer = wx.FlexGridSizer(4,2,4,4)
        flexsizer.AddGrowableCol(1) # text control columns are growable
        # margin:
        m = 3
        # row 1: find what
        flexsizer.AddMany([
            (self.findLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, m),
            (self.findwordCntrl, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, m)
            ])
        # row 2: checkbox controls
        flexsizer.AddMany([
            (self.matchCaseChk, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, m),
            (self.matchWordChk, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, m)
            ])

        # row 3: checkbox controls
        flexsizer.AddMany([
            (filler, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, m),
            (self.notFoundLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, m)
            ])

        # row 4:replace what
        flexsizer.AddMany([
            (self.replaceLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, m),
            (self.replacewordCntrl, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, m)
            ])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(flexsizer,1, wx.EXPAND |  wx.ALIGN_LEFT |wx.ALL, 4)
        sizer.AddSizer(buttonSizer, 0, wx.ALIGN_RIGHT |wx.ALL, 4)
        return sizer
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT_ENTER, self.onFindTextEnter, self.findwordCntrl)
        self.Bind(wx.EVT_TEXT_ENTER, self.onReplaceTextEnter, self.replacewordCntrl)
        self.Bind(wx.EVT_TEXT, self.onReplaceText, self.replacewordCntrl)
        self.Bind(wx.EVT_BUTTON, self.onFind, self.findBtn)
        self.Bind(wx.EVT_BUTTON, self.onReplaceFind, self.replaceFindBtn)
        self.Bind(wx.EVT_BUTTON, self.onReplaceAll, self.replaceAllBtn)
    # end  _bindWidgetEvents()

    def onFindTextEnter(self, event): #@UnusedVariable
        self._doFindNext()
    # end onFindTextEnter()

    def onReplaceText(self, event): #@UnusedVariable
        self._updateReplaceButtonsUi()
    # end onReplaceText()

    def onReplaceTextEnter(self, event): #@UnusedVariable
        pass
    # end onReplaceTextEnter()

    def onFind(self, event): #@UnusedVariable
        self._doFindNext()
    # end onFind()

    def onReplaceFind(self, event): #@UnusedVariable
        self._doReplace(False)
        self._doFindNext()
    # end onReplaceFind()

    def onReplaceAll(self, event): #@UnusedVariable
        self._doReplace(True)
        self._doFindNext()
    # end onReplaceAll()

    def _updateReplaceButtonsUi(self):
        text = self.replacewordCntrl.GetValue()
        bEnable = False
        if text and len(text) > 0:
            bEnable = True
        bEnable = bEnable and self.findReplaceModel.getFindResult()
        self.replaceFindBtn.Enable(bEnable)
        self.replaceAllBtn.Enable(bEnable)
    # end _updateReplaceButtonsUi()

    def _doFindNext(self):
        # invoke controller and find next word
        caseSensitive = self.matchCaseChk.GetValue()
        matchWord = self.matchWordChk.GetValue()
        text = getNoneString( self.findwordCntrl.GetValue() )
        self.notFoundLabel.SetLabel(u"")#$NON-NLS-1$
        if text:
            found = self.findReplaceModel.find(text, matchWord, caseSensitive)
            self._updateReplaceButtonsUi()
            self._refreshCombos()
            if not found:
                # show not found.
                self.notFoundLabel.SetLabel(_extstr(u"findreplacedialog.NotFound")) #$NON-NLS-1$
    # end _doFindNext()

    def _doReplace(self, bReplaceAll):
        # invoke controller to replace
        replaceword = self.replacewordCntrl.GetValue()
        self.findReplaceModel.replace(replaceword, bReplaceAll)
        self._refreshCombos()
    # end _doReplace()

# end ZFindReplaceDialog())