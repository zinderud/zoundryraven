from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.services.extpointdef import ZBlogAppBaseDef
from zoundry.blogapp.services.links.link import ZBasicLinkFormatter
from zoundry.blogapp.services.links.link import ZLink
from zoundry.blogapp.services.links.linkdefs import ZLinkDef
from zoundry.blogapp.services.links.linkdefs import ZLinkFormatterDef
from zoundry.blogapp.services.links.linkprovider import ZLinkProviderBase


# ---------------------------------------------------------------------------------------
# Definition representing the plug-in config.
# ---------------------------------------------------------------------------------------
class ZSimpleLinkProviderEntriesDef(ZBlogAppBaseDef):

    def __init__(self, extensionPoint):
        # See base class for getName(), getIcon(), getCapabilities() etc.
        ZBlogAppBaseDef.__init__(self, extensionPoint)
        self.linkDefs = None
        self.formatterDefs = None
    # end __init__()

    def _getExtensionDefNodeName(self):
        return u"plg:link-entries"  #$NON-NLS-1$
    # end _getExtensionDefNodeName()

    def getLinkDefs(self):
        u"""getLinks() -> ZLinkDef[]
        Returns the list of links configured in this entry.""" #$NON-NLS-1$
        if self.linkDefs is None:
            resouceReg = self.extensionPoint.getPlugin().getResourceRegistry()
            self.linkDefs = []
            linkElems = self._getExtensionDefChildNodes(u"plg:links/plg:link") #$NON-NLS-1$
            for linkElem in linkElems:
                linkDef = ZLinkDef(linkElem, resouceReg)
                self.linkDefs.append(linkDef)
        return self.linkDefs
    # end getLinkDefs()

    def getFormatterDefs(self):
        u"""getFormatters() -> IZLinkFormatterDef[]
        Returns the list of formatters configured in this entry.""" #$NON-NLS-1$
        if self.formatterDefs is None:
            resouceReg = self.extensionPoint.getPlugin().getResourceRegistry()
            self.formatterDefs = []
            formatElems = self._getExtensionDefChildNodes(u"plg:link-formatters/plg:link-formatter") #$NON-NLS-1$
            for formatterElem in formatElems:
                formatterDef = ZLinkFormatterDef(formatterElem, resouceReg)
                self.formatterDefs.append(formatterDef)
        return self.formatterDefs
    # end getFormatterDefs()
# end ZSimpleLinkProviderEntriesDef

#-----------------------------------------------
# Simple config file based provider.
#-----------------------------------------------
class ZSimpleLinkProvider(ZLinkProviderBase):

    def __init__(self):
        ZLinkProviderBase.__init__(self)
        self.links = []
        self.formatters = []
        self.formattersTypeMap = {}
    # end __init__()

    def _initialize(self):
        entryDefs = self._loadEntriesDefs()
        for entry in entryDefs:
            self._addLinks( entry.getLinkDefs() )
            self._addFormatters( entry.getFormatterDefs() )
    # end _initialize()

    def _addLinks(self, linkDefs):
        for linkDef in linkDefs:
            if not linkDef.getName():
                self._getLogger().warning(u"Ignoring LinkDef - name is None.") #$NON-NLS-1$
                continue
            if not linkDef.getUrl():
                self._getLogger().warning(u"Ignoring LinkDef - url is None for link %s" % linkDef.getName()) #$NON-NLS-1$
                continue
            link = ZLink(linkDef)
            self.links.append(link)
    # end _addLinks()

    def _addFormatters(self, formatDefs):
        for formatDef in formatDefs:
            if not formatDef.getName():
                self._getLogger().warning(u"Ignoring LinkFormatterDef - name is None.") #$NON-NLS-1$
                continue
            if not formatDef.getUrl():
                self._getLogger().warning(u"Ignoring LinkFormatterDef - url is None for link %s" % formatDef.getName()) #$NON-NLS-1$
                continue
            if not formatDef.getType():
                self._getLogger().warning(u"Ignoring LinkFormatterDef - type is None for link %s" % formatDef.getName()) #$NON-NLS-1$
                continue
            if not formatDef.getFormat():
                self._getLogger().warning(u"Ignoring LinkFormatterDef - format is None for link %s" % formatDef.getName()) #$NON-NLS-1$
                continue
            formatter = ZBasicLinkFormatter(formatDef)
            self.formatters.append(formatter)
            typeList = None
            if self.formattersTypeMap.has_key( formatDef.getFormat() ):
                typeList = self.formattersTypeMap[ formatDef.getFormat() ]
            else:
                typeList = []
                self.formattersTypeMap[ formatDef.getFormat() ] = typeList
            typeList.append( formatter)
    # end _addFormatters()

    def _listLinks(self, maxNumLinks):
        if maxNumLinks > 0 and maxNumLinks < len(self.links):
            return self.links[0:maxNumLinks]
        else:
            return self.links
    # end _listLinks()

    def _listFormatters(self):
        return self.formatters
    # end _listFormatters()

    def _loadEntriesDefs(self):
        pluginRegistry = self._getApplicationModel().getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_SIMPLELINKS_PROVIDER_ENTRIES)
        entryDefs = map(ZSimpleLinkProviderEntriesDef, extensions)
        rval = []
        idList = []
        for entrydef in entryDefs:
            entryId = entrydef.getId()
            if getNoneString(entryId) is None:
                self.logger.error(u"SimpleLinkProvider config entry id is None.") #$NON-NLS-1$
                continue
            if entryId in idList:
                self.logger.warning(u"Ignoring - duplicate SimpleLinkProvider config entry id %s" % entryId) #$NON-NLS-1$
                continue
            idList.append(entryId)
            rval.append(entrydef)
        return rval
    # end _loadEntriesDefs()

# end ZSimpleProviderBase