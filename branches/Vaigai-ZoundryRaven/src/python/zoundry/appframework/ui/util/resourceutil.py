from zoundry.appframework.global_services import getResourceRegistry
from zoundry.base.util.i18n import ZLocale
from zoundry.base.util.fileutil import getDirectoryListing
import os
import string

# -------------------------------------------------------------------------------------
# Gets the flag bitmap path for the given locale.
# -------------------------------------------------------------------------------------
def getFlagPathForLocale(localeStr):
    u"""getFlagPathForLocale(string) -> string
    Gets the flag bitmap path for the given locale.""" #$NON-NLS-1$

    locale = ZLocale(localeStr)
    bitmapPath = None
    if locale.hasCountryCode():
        bitmapPath = getResourceRegistry().getImagePath(u"images/common/flags/%s.png" % string.lower(locale.getCountryCode())) #$NON-NLS-1$
    if bitmapPath is None or not os.path.isfile(bitmapPath):
        bitmapPath = getResourceRegistry().getImagePath(u"images/common/flags/%s.png" % locale.getLanguageCode()) #$NON-NLS-1$
    if bitmapPath is None or not os.path.isfile(bitmapPath):
        bitmapPath = None
    return bitmapPath
# end getFlagPathForLocale()


# -------------------------------------------------------------------------------------
# Gets the flag bitmap for the given locale.
# -------------------------------------------------------------------------------------
def getFlagBitmapForLocale(locale):
    u"""getFlagBitmapForLocale(string|ZLocale) -> wx.Bitmap
    Gets the flag bitmap for the given ZLocale or locale string.""" #$NON-NLS-1$

    if not isinstance(locale, ZLocale):
        locale = ZLocale(locale)
    bitmap = None
    if locale.hasCountryCode():
        bitmap = getResourceRegistry().getBitmap(u"images/common/flags/%s.png" % string.lower(locale.getCountryCode())) #$NON-NLS-1$
    if bitmap is None:
        bitmap = getResourceRegistry().getBitmap(u"images/common/flags/%s.png" % locale.getLanguageCode()) #$NON-NLS-1$
    return bitmap
# end getFlagBitmapForLocale()


# -------------------------------------------------------------------------------------
# Gets an empty bitmap.
# -------------------------------------------------------------------------------------
def getEmptyFlagBitmap():
    return getResourceRegistry().getBitmap(u"images/common/flags/empty.png") #$NON-NLS-1$
# end getEmptyFlagBitmap()


# -------------------------------------------------------------------------------------
# Gets all of the flag bitmaps:  returns a list of (langCode, bitmap) tuples
# -------------------------------------------------------------------------------------
def getAllFlagBitmaps():
    u"returns a list of (countryCode, bitmap) tuples" #$NON-NLS-1$
    rval = []
    flagPath = getResourceRegistry().getResourcePath(u"images/common/flags", True) #$NON-NLS-1$
    for filePath in getDirectoryListing(flagPath):
        baseFileName = os.path.basename(filePath)
        countryCode = os.path.splitext(baseFileName)[0]
        bitmap = getResourceRegistry().getBitmap(u"images/common/flags/%s" % baseFileName) #$NON-NLS-1$
        if countryCode and bitmap is not None and len(countryCode) == 2:
            rval.append( (countryCode, bitmap) )
    return rval
# end getAllFlagBitmaps()
