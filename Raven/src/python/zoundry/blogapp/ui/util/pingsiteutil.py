from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
import string

# ------------------------------------------------------------------------------
# Convenience function used to serialize a list of ping sites to a string that
# can be saved in, for example, user prefs.
# ------------------------------------------------------------------------------
def serializePingSiteList(sites):
    u"""_serializePingSiteList(IZWeblogPingSite[]) -> string
    Serializes the list of ping sites to a string.""" #$NON-NLS-1$
    if sites is None:
        return None
    siteIds = []
    for site in sites:
        siteIds.append(site.getAttribute(u"id")) #$NON-NLS-1$
    return string.join(siteIds)
# end serializePingSiteList()


# ------------------------------------------------------------------------------
# Convenience function used to deserialize a list of ping sites from a string
# to a list of ping site instances.
# ------------------------------------------------------------------------------
def deserializePingSiteList(sitesStr):
    u"""_serializePingSiteList(string) -> IZWeblogPingSite[]
    Deserializes the list of ping sites from a string.""" #$NON-NLS-1$
    if not getNoneString(sitesStr):
        return None
    publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)

    siteIds = sitesStr.split()
    return map(publisherService.findWeblogPingSiteById, siteIds)
# end deserializePingSiteList()
