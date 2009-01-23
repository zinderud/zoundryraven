from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.fileutil import checkFile
import codecs

# ----------------------------------------------------------------------------------------
# Saves the given text content to file using utf8 encoding.
# ----------------------------------------------------------------------------------------
def saveUnicodeContent(fileName, text, enc=None):
    u"""Saves the given text to a file as a utf-8 stream.
    This method re-throws exceptions - so calling code should catch and handle them.""" #$NON-NLS-1$    
    file = None
    if not enc:
        enc = u"utf-8" #$NON-NLS-1$
    if not text:
        # TODO (PJ) throw here?
        text =  u"" #$NON-NLS-1$
    try:
        file = codecs.open(fileName, u"w", enc, u"replace") #$NON-NLS-1$ #$NON-NLS-2$
        # make sure the text is unicode before writing to file via codecs.
        text = convertToUnicode(text)
#        # write the utf-8 byte order marker for wintel platforms.
#        file.write(codecs.BOM_UTF8)
        file.write(text)
        file.close()
    except Exception, e:
        raise e
# end saveUnicodeContent()

# ----------------------------------------------------------------------------------------
# Loads and returns the text string the given utf-8 file
# ----------------------------------------------------------------------------------------
def loadUnicodeContent(fileName, enc=None):
    checkFile(fileName)
    if not enc:
        enc = u"utf-8" #$NON-NLS-1$

    file = None
    text = None
    try:
        file = codecs.open(fileName, u"r", enc, u"replace") #$NON-NLS-1$ #$NON-NLS-2$      
        text = file.read()
        file.close()        
        # if unicode string begins with the BOM (Py 2.3 bug?) remove the BOM character.
        if text and text[0] == unicode( codecs.BOM_UTF8, u"utf-8" ): #$NON-NLS-1$            
            text = text.lstrip( unicode( codecs.BOM_UTF8, u"utf-8" ) ) #$NON-NLS-1$        
    except:    
        # try loading without codecs
        try:
            file = open(fileName, u'r') #$NON-NLS-1$
            text = file.read()
            file.close()
            text = convertToUnicode(text)
        except:
            raise        
    return text
# end loadUnicodeContent()
