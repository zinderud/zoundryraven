from zoundry.blogpub.namespaces import IZBlogPubTagwordNamespaces
from zoundry.base.util.text.textutil import getNoneString

# ------------------------------------------------------------------------------
# Convenience function used to serialize a list of tag site urls to a string that
# can be saved in, for example, user prefs.
# ------------------------------------------------------------------------------
def serializeTagSiteList(siteUrlList):
    u"""serializeTagSiteList(string[]) -> string
    Serializes the list of tag sites to a string.""" #$NON-NLS-1$
    if siteUrlList is None:
        return None
    sitesStr = u",".join(siteUrlList) #$NON-NLS-1$
    return sitesStr
# end serializeTagSiteList()

# ------------------------------------------------------------------------------
# Convenience function used to deserialize a CSV string of tag site urls into a 
# list of tag site urls.
# ------------------------------------------------------------------------------
def deserializeTagSiteList(sitesCsvStr):
    u"""deserializeTagSiteList(string) -> string[]
    Deserializes the list of tag sites from a string.""" #$NON-NLS-1$
    if not getNoneString(sitesCsvStr):
        return []
    sites = sitesCsvStr.split(u",") #$NON-NLS-1$
    return sites
# end deserializeTagSiteList()

# ------------------------------------------------------------------------------
# Convenience function used to return a string[] from a IZTagwords[]
# ------------------------------------------------------------------------------
def getWordListFromZTagwords(tagwordsList):
    # returns string[] given IZTagwords[]
    rval = []
    iZTagwordsObj = _findTagwords(tagwordsList, IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI)
    if not iZTagwordsObj:
        # legacy, pre alpha build 132 support. check technorati ns. # FIXME (PJ) remove technorati tags NS for final release
        iZTagwordsObj = _findTagwords(tagwordsList, u"http://technorati.com/tag/") #$NON-NLS-1$
    if iZTagwordsObj and len(iZTagwordsObj.getTagwords()) > 0:
        rval.extend( iZTagwordsObj.getTagwords() ) 
    return rval
# end getWordListFromZTagwords()

def _findTagwords(tagwordsList, url):
    url = url.rstrip(u"/") #$NON-NLS-1$
    for ztagwords in tagwordsList:
        if ztagwords.getUrl().rstrip(u"/") == url: #$NON-NLS-1$
            return ztagwords
    return None
# end _findTagwords
