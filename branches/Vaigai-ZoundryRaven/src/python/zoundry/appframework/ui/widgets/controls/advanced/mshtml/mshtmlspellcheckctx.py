from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import ZBaseEditControlSpellCheckContext
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import getDispElement

#----------------------------------------------------------------------------
# SpellCheck controller context
#----------------------------------------------------------------------------
class ZMshtmlEditControlSpellCheckContext(ZBaseEditControlSpellCheckContext):

    def __init__(self, mshtmlEditControl):
        ZBaseEditControlSpellCheckContext.__init__(self)
        self.mshtmlEditControl = mshtmlEditControl
        self.startRange = None
        self.endRange = None
        self.currRange = None
        self.ieWord = None
        self.ieSentence = None
        self.wordCount = 0
    # end __init__()



    def _initialize(self):
        doc = self.mshtmlEditControl._getMshtmlControl().getIHTMLDocument()
        mshtmlBodyDispElement = getDispElement(doc.body)
        self.startRange = mshtmlBodyDispElement.createTextRange()
        self.startRange.collapse(True)
        self.currRange = mshtmlBodyDispElement.createTextRange()
        self.currRange.collapse(True)
        self.endRange = mshtmlBodyDispElement.createTextRange()
        self.endRange.collapse(False)
        self._resetWordCount()
    # end _initialize()

    def _cleanup(self):
        ZBaseEditControlSpellCheckContext._cleanup(self)
        self.startRange = None
        self.endRange = None
        self.currRange = None
        self.ieWord = None
    # end _cleanup()

    def _prepareResult(self, spellcheckResult): #@UnusedVariable
        ZBaseEditControlSpellCheckContext._prepareResult(self, spellcheckResult)
        if spellcheckResult and not spellcheckResult.isFinished() and self.currRange:
            word = spellcheckResult.getWord()
            # build partial sentence around word.
            left = u""  #$NON-NLS-1$ #
            right = u""  #$NON-NLS-1$
            count = 0 # word count
            try:
                rng1 = self.currRange.duplicate()
                while count < 6:
                    r = rng1.move(u"word", -1) #$NON-NLS-1$
                    if r == 0:
                        # moved 0 words. (start of text)
                        break
                    rng1.expand(u"word") #$NON-NLS-1$
                    left = rng1.text + left
                    count = count + 1
            except:
                pass
            count = 0
            try:
                rng2 = self.currRange.duplicate()
                while count < 8 :
                    r = rng2.move(u"word", +1) #$NON-NLS-1$
                    if r == 0:
                        # end of text
                        break
                    rng2.expand(u"word") #$NON-NLS-1$
                    right = right + rng2.text
                    count = count + 1
            except:
                pass
            sentence = left.strip()  + u" "   #$NON-NLS-1$
            # word start pos
            p1 = len(sentence)
            # append word and calc end post
            sentence = sentence +  word
            p2 = len(sentence)
            # append rest of sentence.
            sentence = sentence + u" " + right.strip() #$NON-NLS-1$
            spellcheckResult.setWordContext(sentence)
            spellcheckResult.setRangeInContext(p1, p2)
    # end _prepareResult

    def _getNextWord(self):
        word = None
        if self._hasMore():
            word = self._getIeWord()
        return word
    # end _getNextWord()

    def _replace(self, replaceWord, replaceAll=False): #@UnusedVariable
        origWord = self._getIeWord()
        self._replaceWord(self.currRange, origWord, replaceWord)
        if replaceAll and self.currRange:
            rng = self.currRange.duplicate()
            count = 0
            eod = rng.isEqual(self.endRange)
            while not eod and count < 10000:
                rng.moveStart(u"word")#$NON-NLS-1$
                rng.expand(u"word") #$NON-NLS-1$
                w = rng.text
                if len(w.strip()) > 0 and w == origWord:
                    self._replaceWord(rng, origWord, replaceWord)
                count = count + 1
                eod = rng.isEqual(self.endRange)
    # end _replace()

    def highlightWord(self, on): #@UnusedVariable
        self._higlightWord(on)
    # end highlightWord()

    def _setIeWord(self, word):
        u"""Sets the word (without modifications such as strip or lowercase) found in IE.""" #$NON-NLS-1$
        self.ieWord = word
    # end _setIeWord()

    def _getIeWord(self):
        return self.ieWord
    # end _getIeWord()

    def _setIeSentence(self, sentence):
        self.ieSentence = sentence
    # _setIeSentence()

    def _getIeSentence(self):
        return self.ieSentence
    # _getIeSentence()

    def _resetWordCount(self):
        self.wordCount = 0
    # end _resetWordCount()

    def _incWordCount(self):
        self.wordCount = self.wordCount + 1
    # end _incWordCount()

    def _getWordCount(self):
        return self.wordCount
    # end _getWordCount()

    def _hasMore(self):
        u"""Returns true if there are more words.""" #$NON-NLS-1$
        found = False
        self._setIeWord(None)
        self._setIeSentence(None)
        moveCount = 1 # number of words moved. If this is 0, then there is no 'next word'
        if self.currRange and self.endRange and self.startRange:
            # end of doc
            eod = True
            try:
                eod = self.currRange.isEqual(self.endRange)
            except:
                pass
            while not found and not eod and self._getWordCount() < 10000 and moveCount > 0:
                # move to next word location. (no need to do this for the first word since the range is already positioned at the 1st range)
                if not self.currRange.isEqual(self.startRange):
                    moveCount = self.currRange.moveStart(u"word")#$NON-NLS-1$

                # capture the full word.
                self.currRange.expand(u"word") #$NON-NLS-1$
                # get current word
                # The word found by IE may include the space (if any) following the word.
                w = self.currRange.text
                if moveCount > 0 and len(w.strip()) > 0 and not self._isAlphaNum(w.strip()):
                    self._incWordCount()
                    self._setIeWord(w)
                    found = True
                eod = self.currRange.isEqual(self.endRange)
        return found

    def _replaceWord(self, textRange, originalWord, replaceWord):
        if textRange and originalWord is not None and replaceWord is not None:
            # The text range where word found by IE may include the space (if any) following the word.
            if originalWord.endswith(u" "): #$NON-NLS-1$
                textRange.text = replaceWord + u" " #$NON-NLS-1$
            else:
                textRange.text = replaceWord
    # end  _replaceWord

    def _higlightWord(self, bOn=True):
        u"""Called when the current word needs to be highlighted and brought/scrolled into view.""" #$NON-NLS-1$
        if self.currRange:
            if bOn:
                self.currRange.scrollIntoView()
                self.currRange.select()
            else:
                self.mshtmlEditControl.selectNone()
    # end  _higlightWord()
# end ZMshtmlEditControlSpellCheckContext