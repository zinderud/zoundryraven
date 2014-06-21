from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.widgets.treemodel import IZTreeNodeModel
from zoundry.appframework.models.ui.widgets.treemodel import ZHiddenRootTreeNodeModel
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.base.util.types.list import ZSortedList
from zoundry.base.util.types.list import ZSortedSet
from zoundry.base.util.urlutil import decodeUri
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.index import IZLinkSearchFilter


# --------------------------------------------------------------------------------------
# Tree node impl for the link ido.
# --------------------------------------------------------------------------------------
class ZLinkIDONode(IZTreeNodeModel):

    def __init__(self, linkIDO):
        self.linkIDO = linkIDO
    # end __init__()

    def getLinkIDO(self):
        return self.linkIDO
    # end getLinkIDO()

    def getPath(self):
        return self.linkIDO.getPath()
    # end getPath()

    def getLabel(self):
        if not self.linkIDO.getHost():
            return decodeUri(self.linkIDO.getUrl())
        if not self.getPath():
            return u"/" #$NON-NLS-1$
        else:
            return self.getPath()
    # end getLabel()

    def getChildren(self):
        return []
    # end getChildren()

    def getImageLabel(self):
        return u"link" #$NON-NLS-1$
    # end getImageLabel()

    def getSelectedImageLabel(self):
        return u"link" #$NON-NLS-1$
    # end getSelectedImageLabel()

    def isBold(self):
        return False
    # end isBold()

    def isExpanded(self):
        return False
    # end isExpanded()

# end ZLinkIDONode


# --------------------------------------------------------------------------------------
# Compares two link IDO node objects.
# --------------------------------------------------------------------------------------
class ZLinkIDONodeComparator(ZDefaultListComparator):

    def compare(self, linkIDONode1, linkIDONode2):
        data1 = linkIDONode1.getPath()
        data2 = linkIDONode2.getPath()

        return ZDefaultListComparator.compare(self, data1, data2)
    # end compare()

    def equals(self, linkIDONode1, linkIDONode2):
        data1 = linkIDONode1.getPath()
        data2 = linkIDONode2.getPath()

        return ZDefaultListComparator.equals(self, data1, data2)
    # end equals()

# end ZLinkIDOComparator


# --------------------------------------------------------------------------------------
# A node that represent a single host in the "tree" view of links.
# --------------------------------------------------------------------------------------
class ZHostNode(IZTreeNodeModel):

    def __init__(self, host):
        self.host = host
        self.children = ZSortedSet(ZLinkIDONodeComparator())
    # end __init__()

    def addLinkIDO(self, linkIDO):
        return self.children.add(ZLinkIDONode(linkIDO))
    # end addLinkIDO()

    def removeLinkIDO(self, linkIDO):
        return self.children.remove(ZLinkIDONode(linkIDO))
    # end removeLinkIDO()

    def getHost(self):
        return self.host
    # end getHost()

    def getLabel(self):
        host = self.getHost()
        if host is None or host.strip() == u"": #$NON-NLS-1$
            host = u"(%s)" % _extstr(u"imgsviewmodel.local") #$NON-NLS-1$ #$NON-NLS-2$
        return host
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    def getImageLabel(self):
        return u"site" #$NON-NLS-1$
    # end getImageLabel()

    def getSelectedImageLabel(self):
        return u"site" #$NON-NLS-1$
    # end getSelectedImageLabel()

    def isBold(self):
        return True
    # end isBold()

    def isExpanded(self):
        # FIXME (EPW) it would be nice if this remembered its state, at least when refreshing
        return False
    # end isExpanded()

    def isEmpty(self):
        return self.children.isEmpty()
    # end isEmpty()

# end ZHostNode


# --------------------------------------------------------------------------------------
# Compares two host nodes using information in the filter.
# --------------------------------------------------------------------------------------
class ZHostNodeComparator(ZDefaultListComparator):

    def __init__(self, filter):
        self.filter = filter
    # end __init__()

    def compare(self, node1, node2):
        data1 = node1.getHost()
        data2 = node2.getHost()

        sortOrder = self.filter.getSortOrder()

        # Flip the sort if the order is DESC
        if sortOrder == IZLinkSearchFilter.SORT_ORDER_DESC:
            _temp = data1
            data1 = data2
            data2 = _temp

        return ZDefaultListComparator.compare(self, data1, data2)
    # end compare()

# end ZHostNodeComparator


# --------------------------------------------------------------------------------------
# A wrapper around the list of link IDOs.  This class provides a two teired tree view
# of the link IDO data.  Each time an link IDO is added, it is added to a 'host'
# container based on the host information of the link IDO.  If the host container does
# not already exist, one is created for the IDO.  The wrapper keeps everything sorted
# and provides an easy way to add, remove, update IDOs.
# --------------------------------------------------------------------------------------
class ZLinkIDOHostsWrapper:

    def __init__(self, filter):
        self.hostNodes = ZSortedList(ZHostNodeComparator(filter))
        self.linkFilter = filter
    # end __init__()

    def addLinkIDO(self, linkIDO):
        if self.linkFilter.matches(linkIDO):
            hostNode = self._findHostNode(linkIDO.getHost())
            if not hostNode:
                hostNode = self._createHostNode(linkIDO.getHost())
            return hostNode.addLinkIDO(linkIDO)
        else:
            return False
    # end addLinkIDO()

    def removeLinkIDO(self, linkIDO):
        for hostNode in self.hostNodes:
            if hostNode.removeLinkIDO(linkIDO):
                if hostNode.isEmpty():
                    self.hostNodes.remove(hostNode)
                return True
        return False
    # end removeLinkIDO()

    def _findHostNode(self, host):
        for hostNode in self.hostNodes:
            if hostNode.getHost() == host:
                return hostNode
        return None
    # end _findHostNode()

    def _createHostNode(self, host):
        hostNode = ZHostNode(host)
        self.hostNodes.add(hostNode)
        return hostNode
    # end _createHostNode()

    def __len__(self):
        return len(self.hostNodes)
    # end __len__()

    def __contains__(self, key):
        return key in self.hostNodes
    # end __contains__()

    # Iterator over all of the attributes names (not in namespaces).
    def __iter__(self):
        return self.hostNodes.__iter__()
    # end __iter__()

    def __getitem__(self, key):
        return self.hostNodes[key]
    # end __getitem__()

# end ZLinkIDOHostsWrapper


# --------------------------------------------------------------------------------------
# The model associated with the context view for the Standard Perspective when a blog
# has been selected by the user.  This model provides access to all data that needs to
# be displayed by that view.
# --------------------------------------------------------------------------------------
class ZContextInfoLinksModel:

    def __init__(self, filter):
        self.currentFilter = filter
        self.hosts = None

        self.engine = getApplicationModel().getEngine()
        self.indexService = self.engine.getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
    # end __init__()

    def getCurrentFilter(self):
        return self.currentFilter
    # end getCurrentFilter()

    def setHostCriteria(self, hostCriteria):
        self.currentFilter.setHostCriteria(hostCriteria)
    # end setHostCriteria()

    def clearHostCriteria(self):
        self.currentFilter.setHostCriteria(None)
    # end clearHostCriteria()

    def getRootNode(self):
        return ZHiddenRootTreeNodeModel(self.getHosts())
    # end getRootNode()

    def getHosts(self):
        if self.hosts is None:
            indexResults = self.indexService.findLinks(self.currentFilter)
            self._processIndexResult(indexResults)
        return self.hosts
    # end getHosts()

    def getHost(self, index):
        return self.hosts[index]
    # end getHost()

    # Called by the view to re-query the index.  This is usually done when the search criteria
    # has changed (e.g. by typing a word in the search field).
    def refresh(self):
        # Force a re-query of the index.
        self.hosts = None
        self.getHosts()
    # end refresh()

    # Called by the view when it receives an event indicating that a new link IDO was
    # added to the index.  Returns True if the model's state was changed.
    def addLink(self, linkIDO):
        if self.hosts is not None:
            return self.hosts.addLinkIDO(linkIDO)
        return False
    # end addLink()

    # Called by the view when it receives an event indicating that a new link IDO was
    # removed from the index.  Returns True if the model's state was changed.
    def removeLink(self, linkIDO):
        if self.hosts is not None:
            return self.hosts.removeLinkIDO(linkIDO)
        return False
    # end removeLink()

    # Called by the view when it receives an event indicating that a new link IDO was
    # updated.  Returns True if the model's state was changed.
    def updateLink(self, linkIDO):
        if self.hosts is not None:
            self.hosts.removeLinkIDO(linkIDO)
            return self.hosts.addLinkIDO(linkIDO)
        return False
    # end updateLink()

    def _processIndexResult(self, indexResult):
        self.hosts = ZLinkIDOHostsWrapper(self.currentFilter)
        for ido in indexResult:
            self.hosts.addLinkIDO(ido)
    # end _processIndexResult()

# end ZContextInfoLinksModel
