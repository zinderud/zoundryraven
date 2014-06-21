
# -----------------------------------------------------------------------------------------
# Implements a function that, given a string, will return either emptry string "" (when
# None or empty) or a stripped version of the value.
# -----------------------------------------------------------------------------------------
def getSafeString(value):
    if not value:
        return u"" #$NON-NLS-1$
    return unicode(value).strip()
# end getSafeString()


# -----------------------------------------------------------------------------------------
# Implements a function that, given a string, will return either None (when None or empty) 
# or a stripped version of the value.
# -----------------------------------------------------------------------------------------
def getNoneString(value):
    if not value:
        return None
    value = unicode(value).strip()
    if not value:
        return None
    return value
# end getNoneString()


# -----------------------------------------------------------------------------------------
# Returns true if the given path contains unicode characters.
# -----------------------------------------------------------------------------------------
def isUnicodePath(path):
    for ch in path:
        val = ord(ch)
        if val > 127:
            return True
    return False
# end isUnicodePath()


# -----------------------------------------------------------------------------------------
# Returns the name of a file sanitized to exclude troublesome characters such as
# /, $, unicode chars, spaces, etc.
# -----------------------------------------------------------------------------------------
def sanitizeFileName(fileName):
    lname = list(fileName)
    lrval = []
    for ch in lname:
        chVal = ord(ch)
        if chVal < 46 or chVal == 47 or (chVal > 122 and chVal < 128):
            ch = u"_" #$NON-NLS-1$
        lrval.append(ch)
    rval = u"".join(lrval) #$NON-NLS-1$
    if isUnicodePath(rval):
        rval = rval.encode(u"idna") #$NON-NLS-1$
    return rval
# end sanitizeFileName()
