from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.widgets.treemodel import IZTreeNodeModel
from zoundry.appframework.models.ui.widgets.treemodel import ZHiddenRootTreeNodeModel
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.base.util.types.list import ZSortedList
from zoundry.base.util.types.list import ZSortedSet
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.index import IZImageSearchFilter
from zoundry.base.util.urlutil import decodeUri


# --------------------------------------------------------------------------------------
# Tree node impl for the image ido.
# --------------------------------------------------------------------------------------
class ZImageIDONode(IZTreeNodeModel):

    def __init__(self, imageIDO):
        self.imageIDO = imageIDO
    # end __init__()
    
    def getImageIDO(self):
        return self.imageIDO
    # end getImageIDO()

    def getPath(self):
        return self.imageIDO.getPath()
    # end getPath()

    def getLabel(self):
        if not self.imageIDO.getHost():
            return decodeUri(self.imageIDO.getUrl())
        if not self.getPath():
            return u"/" #$NON-NLS-1$
        else:
            return self.getPath()
    # end getLabel()

    def getChildren(self):
        return []
    # end getChildren()

    def getImageLabel(self):
        return u"image" #$NON-NLS-1$
    # end getImageLabel()

    def getSelectedImageLabel(self):
        return u"image" #$NON-NLS-1$
    # end getSelectedImageLabel()

    def isBold(self):
        return False
    # end isBold()

    def isExpanded(self):
        return False
    # end isExpanded()

# end ZImageIDONode


# --------------------------------------------------------------------------------------
# Compares two image IDO node objects.
# --------------------------------------------------------------------------------------
class ZImageIDONodeComparator(ZDefaultListComparator):
    
    def compare(self, imageIDONode1, imageIDONode2):
        data1 = imageIDONode1.getPath()
        data2 = imageIDONode2.getPath()

        return ZDefaultListComparator.compare(self, data1, data2)
    # end compare()

    def equals(self, imageIDONode1, imageIDONode2):
        data1 = imageIDONode1.getPath()
        data2 = imageIDONode2.getPath()

        return ZDefaultListComparator.equals(self, data1, data2)
    # end equals()

# end ZImageIDOComparator


# --------------------------------------------------------------------------------------
# A node that represent a single host in the "tree" view of images.
# --------------------------------------------------------------------------------------
class ZHostNode(IZTreeNodeModel):

    def __init__(self, host):
        self.host = host
        self.children = ZSortedSet(ZImageIDONodeComparator())
    # end __init__()

    def addImageIDO(self, imageIDO):
        return self.children.add(ZImageIDONode(imageIDO))
    # end addImageIDO()

    def removeImageIDO(self, imageIDO):
        return self.children.remove(ZImageIDONode(imageIDO))
    # end removeImageIDO()

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
        if sortOrder == IZImageSearchFilter.SORT_ORDER_DESC:
            _temp = data1
            data1 = data2
            data2 = _temp

        return ZDefaultListComparator.compare(self, data1, data2)
    # end compare()

# end ZHostNodeComparator


# --------------------------------------------------------------------------------------
# A wrapper around the list of image IDOs.  This class provides a two teired tree view
# of the image IDO data.  Each time an image IDO is added, it is added to a 'host' 
# container based on the host information of the image IDO.  If the host container does
# not already exist, one is created for the IDO.  The wrapper keeps everything sorted
# and provides an easy way to add, remove, update IDOs.
# --------------------------------------------------------------------------------------
class ZImageIDOHostsWrapper:

    def __init__(self, filter):
        self.hostNodes = ZSortedList(ZHostNodeComparator(filter))
        self.imageFilter = filter
    # end __init__()

    def addImageIDO(self, imageIDO):
        if self.imageFilter.matches(imageIDO):
            hostNode = self._findHostNode(imageIDO.getHost())
            if not hostNode:
                hostNode = self._createHostNode(imageIDO.getHost())
            if hostNode.addImageIDO(imageIDO):
                return True
        else:
            return False
    # end addImageIDO()

    def removeImageIDO(self, imageIDO):
        for hostNode in self.hostNodes:
            if hostNode.removeImageIDO(imageIDO):
                if hostNode.isEmpty():
                    self.hostNodes.remove(hostNode)
                return True
        return False
    # end removeImageIDO()

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

# end ZImageIDOHostsWrapper


# --------------------------------------------------------------------------------------
# The model associated with the context view for the Standard Perspective when a blog
# has been selected by the user.  This model provides access to all data that needs to
# be displayed by that view.
# --------------------------------------------------------------------------------------
class ZContextInfoImagesModel:

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
            indexResults = self.indexService.findImages(self.currentFilter)
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

    # Called by the view when it receives an event indicating that a new image IDO was
    # added to the index.  Returns True if the model's state was changed.
    def addImage(self, imageIDO):
        if self.hosts is not None:
            return self.hosts.addImageIDO(imageIDO)
        return False
    # end addImage()

    # Called by the view when it receives an event indicating that a new image IDO was
    # removed from the index.  Returns True if the model's state was changed.
    def removeImage(self, imageIDO):
        if self.hosts is not None:
            return self.hosts.removeImageIDO(imageIDO)
        return False
    # end removeImage()

    # Called by the view when it receives an event indicating that a new image IDO was
    # updated.  Returns True if the model's state was changed.
    def updateImage(self, imageIDO):
        if self.hosts is not None:
            self.hosts.removeImageIDO(imageIDO)
            return self.hosts.addImageIDO(imageIDO)
        return False
    # end updateImage()
    
    def _processIndexResult(self, indexResult):
        self.hosts = ZImageIDOHostsWrapper(self.currentFilter)
        for ido in indexResult:
            self.hosts.addImageIDO(ido)
    # end _processIndexResult()

# end ZContextInfoImagesModel
