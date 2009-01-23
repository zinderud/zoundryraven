from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs

#=================================================
# Util methods related to links and link formatters
#=================================================

def getLinkFormatterByUrl(linkType, linkUrl):
    u"""getLinkFormatterByUrl(string, string) -> IZLinkFormatter
    returns IZLinkFormatter given type (e.g. tag) and id/url (e.g. www.techonorati.com).
    Returns empty of not found.
    """ #$NON-NLS-1$

    formatter = None
    linkService = getApplicationModel().getService(IZBlogAppServiceIDs.LINKS_SERVICE_ID)
    formatterList = linkService.listFormattersByType(linkType)
    if formatterList:
        for formatter in formatterList:
            if formatter.getUrl() == linkUrl:
                return formatter
    return None
# end getLinkFormatterByUrl

def getLinkFormattersByUrls(linkType, linkUrls):
    u"""getLinkFormattersByUrls(string, string[]) -> IZLinkFormatter[]
    returns IZLinkFormatter[] given type (e.g. tag) and list of id/url (e.g. www.techonorati.com).
    """ #$NON-NLS-1$
    
    rval = []
    for url in linkUrls:
        formatter = getLinkFormatterByUrl(linkType, url)
        if formatter:
            rval.append( formatter )
    return rval
# end getLinkFormattersByUrls())