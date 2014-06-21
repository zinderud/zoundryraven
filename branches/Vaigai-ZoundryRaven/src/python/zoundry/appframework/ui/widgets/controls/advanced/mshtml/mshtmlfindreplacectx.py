from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import getDispElement
from zoundry.appframework.ui.widgets.controls.advanced.support.findreplacectx import ZBaseEditControlFindReplaceTextContext

#----------------------------------------------------------------------------
# FindReplace controller context
#----------------------------------------------------------------------------
class ZMshtmlEditControlFindReplaceTextContext(ZBaseEditControlFindReplaceTextContext):

    def __init__(self, mshtmlEditControl, initialText):
        ZBaseEditControlFindReplaceTextContext.__init__(self)
        self.mshtmlEditControl = mshtmlEditControl
        self.initialText = initialText
        self.findRange = None
        self.currRange = None
        self.ieWord = None
    # end __init__()

    def _setIeWord(self, word):
        u"""Sets the word (without modifications such as strip or lowercase) found in IE.""" #$NON-NLS-1$
        self.ieWord = word
    # end _setIeWord()

    def _getIeWord(self):
        return self.ieWord
    # end _getIeWord()

    def _initialize(self):
        self._reset()
        # init word with current selection
        self.setText(self.initialText)
    # end _cleanup()

    def _cleanup(self):
        self._setIeWord(None)
        self.findRange = None
        self.currRange = None
    # end _cleanup()

    def _reset(self):
        self.mshtmlEditControl.selectNone()
        doc = self.mshtmlEditControl._getMshtmlControl().getIHTMLDocument()
        mshtmlBodyDispElement = getDispElement(doc.body)
        self.findRange = mshtmlBodyDispElement.createTextRange()
        self.currRange = None
    # end _reset()

    def _findNext(self):
        rTextRange = None
        self._setIeWord(None)
        text = self.getText()
        if text is not None:
            rTextRange = self._findText(text)
        return rTextRange is not None
    # end _findNext()

    def _getControlFlags(self):
        flags = 0
        if self.isMatchWord():
            flags = flags | 2
        if self.isCaseSensitive():
            flags = flags | 4
        return flags
    # end  _getControlFlags()

    def _findText(self, text):
        # find given text in current range and return the current range.
        if not self.findRange:
            return None
        # flags
        flags = self._getControlFlags()
        textlen = len(self.findRange.text)
        if self.findRange.findText(text, textlen, flags):
            # text found
            self.currRange = self.findRange.duplicate()
            self.findRange.moveEnd(u"textedit") #$NON-NLS-1$
            self.findRange.moveStart(u"word") #$NON-NLS-1$
            return self.findRange
        else:
            self.currRange = None
            self.mshtmlEditControl.selectNone()
            return None
    # end _findText()

    def _replace(self, replaceText, replaceAll):
        if replaceText is None:
            return
        flags = self._getControlFlags()
        text = self.getText()
        textlen = len(self.findRange.text)
        count = 1
        self._replaceText(self.currRange, replaceText)
        if self.currRange and replaceAll and text:
            while self.currRange.findText(text, textlen, flags):
                count = count + 1
                rng = self.currRange.duplicate()
                self.currRange.moveEnd(u"textedit") #$NON-NLS-1$
                self.currRange.moveStart(u"word") #$NON-NLS-1$
                self._replaceText(rng, replaceText)
    # end _replace()

    def _replaceText(self, textRange, replaceText):
        if textRange and replaceText is not None:
            textRange.text = replaceText
    # end _replaceText

    def _higlightText(self, on): #@UnusedVariable
        if self.currRange:
            if on:
                self.currRange.scrollIntoView()
                self.currRange.select()
            else:
                self.mshtmlEditControl.selectNone()
    # end _higlightText()
# end ZMshtmlEditControlFindReplaceTextContext