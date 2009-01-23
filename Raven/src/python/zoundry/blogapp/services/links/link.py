from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.urlutil import quote
from zoundry.base.util.urlutil import quote_plus

#----------------------------------------------------
# Defines a basic hyper link
#----------------------------------------------------
class IZLink:

    def getName(self):
        u"""getTitle() -> string
        Returns link name.""" #$NON-NLS-1$
    # end getName()

    def getUrl(self):
        u"""getUrl() -> string
        Returns link href.""" #$NON-NLS-1$
    # end getUrl()

    def getRel(self):
        u"""getRel() -> string
        Returns optional link rel attribute or None if not given.""" #$NON-NLS-1$
    # end getRel()

    def getIconAsBitmap(self):
        u"""getIconAsBitmap() -> wxBitmap or None if not found.
        Returns icon bitmap or None if not found."""  #$NON-NLS-1$
    # getIconAsBitmap

#end IZLink

#----------------------------------------------------
# Link format types.
#----------------------------------------------------
class IZLinkFormatType:
    TAG = u"tag" #$NON-NLS-1$
    SEARCH = u"search" #$NON-NLS-1$
    REFERENCE = u"reference" #$NON-NLS-1$
    AFFILIATE = u"affiliate" #$NON-NLS-1$
# end IZLinkFormatType

#----------------------------------------------------
# Link formatter is repsonsible for creating link urls
# given some context data. For example, if the  context
# data is Zoundry Raven, then a Technorati link formatter
# would create the link http://technoratir.com/tags/Zoundry+Raven.
# A Google search link formatter would return http://www.google.com/q=Zoundry%20Raven.
#----------------------------------------------------
class IZLinkFormatter(IZLink):


    def getType(self):
        u"""getType() -> string
        Returns the type (IZLinkFormatType) value."""  #$NON-NLS-1$
    # end getType()

    def formatUrl(self, text):
        u"""formatUrl(string) -> string
        Returns formatted url given context data.""" #$NON-NLS-1$
    # end formatUrl()
# end IZLinkFormatter

#----------------------------------------------------
# Implementation of a link
#----------------------------------------------------
class ZLink(IZLink):

    def __init__(self, linkDef):
        self.linkDef = linkDef
    #end __init()__

    def getDef(self):
        return self.linkDef
    # end getDef()

    def getName(self):
        return self.getDef().getName()
    # end getName()

    def getUrl(self):
        return self.getDef().getUrl()
    # end getUrl()

    def getRel(self):
        return self.getDef().getRel()
    # end getRel()

    def getIconAsBitmap(self):
        return self.getDef().getIconAsBitmap()
    # getIconAsBitmap()
#end ZLink

#----------------------------------------------------
# Basic link formatter implementation.
#----------------------------------------------------
class ZBasicLinkFormatter(ZLink, IZLinkFormatter):

    def __init__(self, linkFormatDef):
        ZLink.__init__(self, linkFormatDef)
    # end __init__()

    def getType(self):
        return self.getDef().getType()
    # end getType()

    def getFormat(self):
        return self.getDef().getFormat()
    # end getFormat()

    def formatUrl(self, text):
        text = getSafeString(text)
        if not self.getFormat() or not text:
            return self.getUrl()
        return self._internalFormatUrl(self.getFormat(), self.getUrl(), text)
    # end formatUrl()

    def _internalFormatUrl(self, urlFormat, srcUrl,  text): #@UnusedVariable
        # FIXME (PJ) covert text 2 utf8 first?
        enc = getNoneString( self.getDef().getEncoding() )
        replaceText = None
        if enc and u"+" == enc: #$NON-NLS-1$
            replaceText = quote_plus(text)
        elif enc: #$NON-NLS-1$
            replaceText = quote_plus(text)
            replaceText = replaceText.replace(u"+", enc[0]) #$NON-NLS-1$
        else:
            replaceText = quote(text)
        rval = urlFormat.replace(u"{0}", replaceText) #$NON-NLS-1$
        return rval
    # end _internalFormatUrl()
# end ZBasicLinkFormatter

#----------------------------------------------------
# Zoundry product affiliate link formatter implementation.
#----------------------------------------------------
class ZAffiliateLinkFormatter(ZBasicLinkFormatter):

    def __init__(self, linkFormatDef):
        ZBasicLinkFormatter.__init__(self, linkFormatDef)
    # end __init__()
# ZAffiliateLinkFormatter
