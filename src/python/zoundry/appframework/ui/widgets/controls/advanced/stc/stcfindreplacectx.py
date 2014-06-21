from zoundry.appframework.ui.widgets.controls.advanced.support.findreplacectx import ZBaseEditControlFindReplaceTextContext
from wx.stc import *
#----------------------------------------------------------------------------
# FindReplace controller context for STC Editor
#----------------------------------------------------------------------------
class ZStyledXhtmlEditControlFindReplaceTextContext(ZBaseEditControlFindReplaceTextContext):

    def __init__(self, stcCtrl, initialText):
        ZBaseEditControlFindReplaceTextContext.__init__(self)
        self.stcCtrl = stcCtrl
        self.initialText = initialText
        # match start and end
        self.startPos = 0
        self.endPos = 0
        # find start pos
        self.findPos = 0        
    # end __init__()

    def _StcSelectNone(self):
        (start,end) = self.stcCtrl.GetSelection() #@UnusedVariable
        self.stcCtrl.SetSelection(start,start)
    # end _StcSelectNone()
    
    def _StcFindText(self,text, startPos=0, wholeWord=False, matchCase=False):
        # called by the find/replace controller model. Returns the position found or -1 otherwise.
        flags = 0
        if wholeWord:
            flags = flags | STC_FIND_WHOLEWORD
        if matchCase:
            flags = flags | STC_FIND_MATCHCASE 
        endPos = self.stcCtrl.GetTextLength()
        rVal = self.stcCtrl.FindText(startPos, endPos,text, flags)
        return rVal
    # end _StcFindText

    def _StcReplaceText(self, replaceText, startPos, endPos):
        # replaces the given range with the replaceText.
        if replaceText and startPos >= 0 and endPos > startPos:
            self.stcCtrl.SetTargetStart(startPos)
            self.stcCtrl.SetTargetEnd(endPos)
            self.stcCtrl.ReplaceTarget(replaceText)
    # end _StcReplaceText

    def _initialize(self):
        self._reset()
        # init word with current selection
        self.setText(self.initialText)
    # end _cleanup()

    def _cleanup(self):
        self._reset()
    # end _cleanup()

    def _reset(self):
        self.startPos = 0
        self.endPos = 0
        # find start pos
        self.findPos = 0
        self.stcCtrl.SetCurrentPos(0)
        self._StcSelectNone()
    # end _reset()

    def _findNext(self):
        text = self.getText()
        if not text:
            return False
        rVal = self._StcFindText(text, self.findPos, self.isMatchWord(), self.isCaseSensitive())
        if rVal != -1:
            self.startPos = rVal
            self.endPos = self.startPos + len(text)
            self.findPos = rVal + len(text)
        return rVal != -1
    # end _findNext()

    def _replace(self, replaceText, replaceAll):
        if replaceText is None:
            return
        text = self.getText()            
        self._StcReplaceText(replaceText, self.startPos, self.endPos)
        # update 'next' find position
        self.findPos = self.startPos + len(replaceText)
        if replaceAll:            
            nextpos = self._StcFindText(text, self.findPos, self.isMatchWord(), self.isCaseSensitive())
            while nextpos != -1:
                startpos = nextpos
                endpos = startpos + len(text)
                self._StcReplaceText(replaceText, startpos,endpos)
                self.findPos = startpos + len(replaceText)
                nextpos = self._StcFindText(text, self.findPos, self.isMatchWord(), self.isCaseSensitive())
        # clear start/end pos.
        self.startPos  = 0
        self.endPos = 0
    # end _replace()

    def _higlightText(self, on): #@UnusedVariable
        if on and self.startPos >=0 and self.endPos > self.startPos:
            self.stcCtrl.SetCurrentPos(self.startPos)
            self.stcCtrl.SetSelectionStart(self.startPos)            
            self.stcCtrl.MoveCaretInsideView()
            self.stcCtrl.EnsureCaretVisible()            
            self.stcCtrl.SetSelection(self.startPos, self.endPos)
        else:
            self._StcSelectNone()        
    # end _higlightText()
# end ZStyledXhtmlEditControlFindReplaceTextContext