import StringIO

# ----------------------------------------------------------------------------------------
# Converts a unicode string to utf8.  If the string is already in utf8, does nothing.
# ----------------------------------------------------------------------------------------
def convertToUtf8(text):
    u"Converts a unicode string to utf8." #$NON-NLS-1$
    if not text:
        return text
    if not isinstance(text, unicode):
        return text
    return text.encode(u"utf8") #$NON-NLS-1$
# end convertToUtf8()


# ----------------------------------------------------------------------------------------
# Removes the non-breaking space character 0xA0 from the string.  The 0xa0 character is
# pretty common in MS generated HTML.
# ----------------------------------------------------------------------------------------
def removeNBSP(text):
    try:
        if not text:
            return None
        buf = StringIO.StringIO()
        numReplaced = 0

        for ch in text:
            if ord(ch) == 0xa0:
                buf.write(str(u' ')) #$NON-NLS-1$
                numReplaced = numReplaced + 1
            else:
                buf.write(ch)
        # end for

        rval = buf.getvalue()
        return rval
    except:
        return text
# end removeNBSP()


# ----------------------------------------------------------------------------------------
# Converts a utf-8 string to unicode.  If the normal decode process fails for some reason,
# then we will strip away any characters > than 127 to "convert" the string to ascii.
# ----------------------------------------------------------------------------------------
def convertToUnicode(text, enc = u"utf8"): #$NON-NLS-1$
    if not text:
        return text
    if isinstance(text, unicode):
        return text
    if not enc:
        enc = u"utf8" #$NON-NLS-1$

    # First pass - simply decode using the given encoding. #$NON-NLS-1$
    try:
        return text.decode(enc)
    except:
        pass

    # Next, try utf8 if we haven't already tried it.
    if enc != u"utf8": #$NON-NLS-1$
        try:
            return text.decode(u"utf8") #$NON-NLS-1$
        except:
            pass

    # Remove any 0xa0 chars (very common) and then decode from utf-8 (AND simply replace 'bad' chars with '?')
    try:
        text = removeNBSP(text)
        return text.decode(u"utf8", u"replace") #$NON-NLS-1$ #$NON-NLS-2$
    except:
        pass

    return text
# end convertToUnicode()
