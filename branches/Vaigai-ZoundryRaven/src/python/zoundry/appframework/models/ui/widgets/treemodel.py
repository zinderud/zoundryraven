from zoundry.appframework.ui.widgets.controls.tree import IZTreeViewContentProvider

# ---------------------------------------------------------------------------------------
# Provides an interface that can be implemented that will define a single node in a
# ZTreeView widget.  Users of the tree view widget must supply an
# IZTreeViewContentProvider in order for the tree to properly display data.  One way to
# create such a provider is for a given model to use the IZTreeNodeModel interface to
# create its tree hierarchy, then use the ZTreeNodeBasedContentProvider class as the
# tree view's provider.
# ---------------------------------------------------------------------------------------
class IZTreeNodeModel:

    def getLabel(self):
        u"Returns the label." #$NON-NLS-1$
    # end getLabel()

    def getChildren(self):
        u"Returns the list of children." #$NON-NLS-1$
    # end getChildren()

    def getImageLabel(self):
        u"Returns the image label." #$NON-NLS-1$
    # end getImageLabel()

    def getSelectedImageLabel(self):
        u"Returns the selected image label." #$NON-NLS-1$
    # end getSelectedImageLabel()

    def isBold(self):
        u"Returns the bold flag." #$NON-NLS-1$
    # end isBold()

    def isExpanded(self):
        u"Returns True if the node is expanded." #$NON-NLS-1$
    # end isExpanded()

    def compareTo(self, otherNode):
        u"Compares this node to some other node - should return 0 if equal, -1 if less than, +1 if greater than the given node." #$NON-NLS-1$
    # end compareTo()

# end IZTreeNodeModel


# ---------------------------------------------------------------------------------------
# This model can act as a root node when the root node is hidden.
# ---------------------------------------------------------------------------------------
class ZHiddenRootTreeNodeModel(IZTreeNodeModel):

    def __init__(self, children):
        self.children = children
    # end __init__()

    def getLabel(self):
        return u"[ROOT NODE]" #$NON-NLS-1$
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    # FIXME probably don't really need this
    def compareTo(self, otherNode): #@UnusedVariable
        return -1
    # end compareTo()

# end ZHiddenRootTreeNodeModel


# ---------------------------------------------------------------------------------------
# Implements a fully compatible TreeView content provider using the above tree node
# interface.  The provider must be given a root node which implements the IZTreeNodeModel
# interface and a mapped image list.
# ---------------------------------------------------------------------------------------
class ZTreeNodeBasedContentProvider(IZTreeViewContentProvider):

    def __init__(self, rootNode, imageList):
        self.rootNode = rootNode
        self.imageList = imageList
    # end __init__()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getRootNode(self):
        return self.rootNode
    # end getRootNode()

    def getChildren(self, node):
        return node.getChildren()
    # end getChildren()

    def getLabel(self, node):
        return node.getLabel()
    # end getLabel()

    def getImageIndex(self, node):
        return self.imageList[node.getImageLabel()]
    # end getImageIndex()

    def getSelectedImageIndex(self, node):
        return self.imageList[node.getSelectedImageLabel()]
    # end getSelectedImageIndex()

    def getBoldFlag(self, node):
        return node.isBold()
    # end getBoldFlag()

    def getExpandedFlag(self, node): #@UnusedVariable
        return node.isExpanded()
    # end getExpandedFlag()

# end ZTreeNodeBasedContentProvider
