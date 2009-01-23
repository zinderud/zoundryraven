from zoundry.base.util.collections import isNotNoneAndEmpty
import wx

VIRTUAL_TREE_NODE = object()

# -------------------------------------------------------------------------------------------
# A visitor interface for visiting all of the nodes in a Tree.
# -------------------------------------------------------------------------------------------
class IZTreeViewVisitor:

    def visit(self, node, metaData):
        u"""visit(object, map) -> None
        Called when a node in the tree is visited.  The node is
        given, as well as a map of meta data about the UI state of
        the node.""" #$NON-NLS-1$
    # end visit()

# end IZTreeViewVisitor


# -------------------------------------------------------------------------------------------
# An interface that must be implemented in order for a class to function as a content
# provider for a Zoundry Tree View widget.  A content provider provides structured content
# information for the tree control.
# -------------------------------------------------------------------------------------------
class IZTreeViewContentProvider:

    def getImageList(self):
        u"Should return a ZMappedImageList instance." #$NON-NLS-1$
    # end getImageList()

    def getRootNode(self):
        u"Returns the root node of the tree.  This may or may not be displayed, depending on options." #$NON-NLS-1$
    # end getRootNode()

    def getChildren(self, node):
        u"Returns a list of children for the given node." #$NON-NLS-1$
    # end getChildren()

    def getLabel(self, node):
        u"Returns the label for the given node." #$NON-NLS-1$
    # end getLabel()

    def getImageIndex(self, node):
        u"Returns the image index for the given node." #$NON-NLS-1$
    # end getImageIndex()

    def getSelectedImageIndex(self, node):
        u"Returns the image index for the given node when the node is selected." #$NON-NLS-1$
    # end getSelectedImageIndex()

    def getBoldFlag(self, node):
        u"Returns true if the node's label should be bold." #$NON-NLS-1$
    # end getBoldFlag()

    def getExpandedFlag(self, node):
        u"Returns true if the given node is expended." #$NON-NLS-1$
    # end getExpandedFlag()

# end IZTreeViewContentProvider


# -------------------------------------------------------------------------------------------
# This visitor is used to collapse all nodes in the tree view.
# -------------------------------------------------------------------------------------------
class ZCollapseAllTreeViewVisitor(IZTreeViewVisitor):

    def __init__(self, treeView):
        self.treeView = treeView
    # end __init__()

    def visit(self, node, metaData): #@UnusedVariable
        treeId = metaData[u"id"] #$NON-NLS-1$
        self.treeView.CollapseAllChildren(treeId)
        self.treeView.Collapse(treeId)
    # end visit()

# end ZCollapseAllTreeViewVisitor


# -------------------------------------------------------------------------------------------
# This visitor is used to deselect all nodes in the tree view.
# -------------------------------------------------------------------------------------------
class ZDeselectAllTreeViewVisitor(IZTreeViewVisitor):

    def __init__(self, treeView):
        self.treeView = treeView
    # end __init__()

    def visit(self, node, metaData): #@UnusedVariable
        treeId = metaData[u"id"] #$NON-NLS-1$
        if self.treeView.IsSelected(treeId):
            self.treeView.SelectItem(treeId, False)
    # end visit()

# end ZDeselectAllTreeViewVisitor


# -------------------------------------------------------------------------------------------
# A visitor that gets the list of nodes that are selected.
# -------------------------------------------------------------------------------------------
class ZGetSelectedTreeNodesVisitor(IZTreeViewVisitor):

    def __init__(self, treeView):
        self.treeView = treeView
        self.nodes = []
    # end __init__()
    
    def getNodes(self):
        return self.nodes
    # end getNodes()

    def visit(self, node, metaData):
        treeId = metaData[u"id"] #$NON-NLS-1$
        if self.treeView.IsSelected(treeId):
            self.nodes.append(node)
    # end visit()

# end ZGetSelectedTreeNodesVisitor


# -------------------------------------------------------------------------------------------
# A simple visitor that is used to update nodes in the tree.  Any given node will only be
# updated if it is found in the list of dirty nodes (passed to the visitor when the visitor
# is created).
# -------------------------------------------------------------------------------------------
class ZSimpleTreeNodeUpdateVisitor(IZTreeViewVisitor):

    def __init__(self, treeView, dirtyNodes):
        self.treeView = treeView
        self.dirtyNodes = dirtyNodes
    # end __init__()

    def visit(self, node, metaData):
        treeId = metaData[u"id"] #$NON-NLS-1$
        if self._nodeListContainsNode(self.dirtyNodes, node):
            (nodeText, nodeImgIdx, nodeSelImgIdx, nodeBoldFlag) = self.treeView._getTreeItemParams(node)
            nodeExpandedFlag = self.treeView.contentProvider.getExpandedFlag(node)
            self.treeView.SetItemText(treeId, nodeText)
            self.treeView.SetItemImage(treeId, nodeImgIdx)
            if nodeSelImgIdx >= 0:
                self.treeView.SetItemImage(treeId, nodeSelImgIdx, wx.TreeItemIcon_Selected)
            self.treeView.SetItemBold(treeId, nodeBoldFlag)
            if nodeExpandedFlag:
                self.treeView.Expand(treeId)
            else:
                self.treeView.Collapse(treeId)
    # end visit()

    # Returns True if the given node is in the nodeList.  If nodeList is None, then this method
    # always returns True.
    def _nodeListContainsNode(self, nodeList, node):
        if nodeList is None:
            return True

        # Always test for reference equality.
        for n in nodeList:
            if n is node:
                return True

        return False
    # end _nodeListContainsNode()

# end ZSimpleTreeNodeUpdateVisitor


# -------------------------------------------------------------------------------------------
# A Zoundry Tree View widget.  This widget extends the standard WX widget in order to
# implement a content provider model.
#
# FIXME (EPW) TEST implement a collapseAll/expandAll feature
# -------------------------------------------------------------------------------------------
class ZTreeView(wx.TreeCtrl):

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TR_HAS_BUTTONS):
        self.contentProvider = contentProvider
        self.hasData = False
        self.rootHidden = (style & wx.TR_HIDE_ROOT) != 0

        wx.TreeCtrl.__init__(self, parent, id, pos, size, style, name = u"ZTreeView") #$NON-NLS-1$
        imageList = self.contentProvider.getImageList()
        if imageList is not None:
            self.AssignImageList(imageList)
        self._bindWidgetEvents()
    # end __init__()

    def deselectAll(self):
        visitor = ZDeselectAllTreeViewVisitor(self)
        self.accept(visitor)
    # end deselectAll()

    def setContentProvider(self, contentProvider):
        self.contentProvider = contentProvider
        self.clear()
    # end setContentProvider()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onNodeExpanding, self)
    # end _bindWidgetEvents()

    def onNodeExpanding(self, event):
        treeItemId = event.GetItem()
        node = self.GetPyData(treeItemId)
        (childItemId, cookie) = self.GetFirstChild(treeItemId) #@UnusedVariable
        childNode = self.GetPyData(childItemId)
        if childNode == VIRTUAL_TREE_NODE:
            self.DeleteChildren(treeItemId)
            self._populateChildren(node, treeItemId)
        event.Skip()
    # end onNodeExpanding()

    # Call this to refresh the tree (when the content provider has changed).  Optionally, a list
    # of nodes to update can be passed.  In that case, only those items in the tree that represent
    # the nodes in the list will be updated.
    def refresh(self, nodeList = None):
        if not self.hasData:
            self._populateTree()
        else:
            self._updateTree(nodeList)
    # end refresh()

    def clear(self):
        self.DeleteAllItems()
        self.hasData = False
    # end clear()

    def collapseAll(self):
        visitor = ZCollapseAllTreeViewVisitor(self)
        self.accept(visitor)
    # end collapseAll()

    def _getTreeItemParams(self, dataNode):
        nodeText = self.contentProvider.getLabel(dataNode)
        nodeImgIdx = self.contentProvider.getImageIndex(dataNode)
        nodeSelImgIdx = self.contentProvider.getSelectedImageIndex(dataNode)
        nodeBoldFlag = self.contentProvider.getBoldFlag(dataNode)
        return (nodeText, nodeImgIdx, nodeSelImgIdx, nodeBoldFlag)
    # end _getTreeItemParams()

    def _updateTree(self, nodeList = None):
        # If you don't want to refresh anything, then just bail.
        if isNotNoneAndEmpty(nodeList):
            return

        # This visitor will update the contents of any nodes
        visitor = ZSimpleTreeNodeUpdateVisitor(self, nodeList)
        self.accept(visitor)

        # Now update the structure of the tree
        self._synchTreeNode()
    # end _updateTree()

    # Called by a tree visitor when it wants to visit all of the nodes in the tree.
    def accept(self, visitor):
        u"""accept(IZTreeViewVisitor) -> None
        Allows a tree view visitor to visit all of the nodes in the
        tree.""" #$NON-NLS-1$

        self._traverse(visitor, None)
    # end accept()
    
    def getSelectedNodes(self):
        visitor = ZGetSelectedTreeNodesVisitor(self)
        self.accept(visitor)
        return visitor.getNodes()
    # end getSelectedNodes()

    def _traverse(self, visitor, treeId = None):
        isRoot = False
        if treeId is None:
            treeId = self.GetRootItem()
            isRoot = True

        if not isRoot or not self.rootHidden:
            node = self.GetPyData(treeId)
            metaData = self._createMetaData(treeId)
            visitor.visit(node, metaData)

        if isRoot or self.IsExpanded(treeId):
            (childId, cookie) = self.GetFirstChild(treeId)
            while childId.IsOk():
                self._traverse(visitor, childId)
                (childId, cookie) = self.GetNextChild(treeId, cookie)
    # end _traverse()

    def _createMetaData(self, treeId):
        metaData = {}
        metaData[u"id"] = treeId #$NON-NLS-1$
        metaData[u"bold"] = self.IsBold(treeId) #$NON-NLS-1$
        metaData[u"selected"] = self.IsSelected(treeId) #$NON-NLS-1$
        metaData[u"expanded"] = self.IsExpanded(treeId) #$NON-NLS-1$
        metaData[u"visible"] = self.IsVisible(treeId) #$NON-NLS-1$
        return metaData
    # end _createMetaData()

    def _populateTree(self):
        dataNode = self.contentProvider.getRootNode()
        (nodeText, nodeImgIdx, nodeSelImgIdx, nodeBoldFlag) = self._getTreeItemParams(dataNode)
        treeItemId = self.AddRoot(nodeText, nodeImgIdx, nodeSelImgIdx, wx.TreeItemData(dataNode))
        if nodeBoldFlag:
            self.SetItemBold(treeItemId, True)

        self._populateChildren(dataNode, treeItemId)
        self.hasData = True
    # end _populateTree()

    def _populateChildren(self, dataNode, parentTreeItemId):
        childDataNodes = self.contentProvider.getChildren(dataNode)
        if childDataNodes:
            for childDataNode in childDataNodes:
                (nodeText, nodeImgIdx, nodeSelImgIdx, nodeBoldFlag) = self._getTreeItemParams(childDataNode)
                expandedFlag = self.contentProvider.getExpandedFlag(childDataNode)
                childItemId = self.AppendItem(parentTreeItemId, nodeText, nodeImgIdx, nodeSelImgIdx, wx.TreeItemData(childDataNode))
                if nodeBoldFlag:
                    self.SetItemBold(childItemId)
                if self.contentProvider.getChildren(childDataNode) and not expandedFlag:
                    self._populateVirtualChild(childItemId)
                else:
                    self._populateChildren(childDataNode, childItemId)
                    self.Expand(childItemId)
    # end _populateChildren()

    def _populateVirtualChild(self, treeItemId):
        self.AppendItem(treeItemId, u"PLACEHOLDER CHILD", -1, -1, wx.TreeItemData(VIRTUAL_TREE_NODE)) #$NON-NLS-1$
    # end _populateVirtualChild()

    def _synchTreeNode(self, treeItemId = None):
        isRoot = False
        if treeItemId is None:
            treeItemId = self.GetRootItem()
            isRoot = True

        modelNode = self.GetPyData(treeItemId)
        modelNodes = self.contentProvider.getChildren(modelNode)
        if isRoot or self.IsExpanded(treeItemId):
            widgetNodes = self._getChildren(treeItemId)
            self._synchNodeLists(treeItemId, widgetNodes, modelNodes)
            for (childWidgetNode, childMetaData) in widgetNodes: #@UnusedVariable
                self._synchTreeNode(childMetaData[u"id"]) #$NON-NLS-1$
        if len(modelNodes) > 0 and self.GetChildrenCount(treeItemId) == 0 and not self.IsExpanded(treeItemId):
            self._populateVirtualChild(treeItemId)
    # end _synchTreeNode()

    # Given two lists of nodes (one list from the widget, one list from the
    # model), synch them up.  The model node list is obviously the definitive
    # value, and we are trying to make the widget contain the same values.
    # To do this, iterate through both lists at the same time.  At each position,
    # compare what's in the widget list to what's in the model list.  If they
    # are different, then one of the following is true:
    #  1) The model node is new
    #  2) The widget node was deleted from the model
    def _synchNodeLists(self, parentTreeItemId, widgetNodes, modelNodes):
        end = max(len(widgetNodes), len(modelNodes))
        for idx in range(0, end):
            (childWidgetNode, widgetNodeMetaData) = self._safeWidgetListGet(widgetNodes, idx)
            modelNode = self._safeModelListGet(modelNodes, idx)
            # If the nodes are different...
            if childWidgetNode != modelNode:
                # If the model node is None, it means that the widget node list 
                # is longer than the model node list, and we should obviously
                # remove the widget node from the widget.
                if modelNode is None:
                    self._removeWidgetChild(childWidgetNode, widgetNodeMetaData, widgetNodes)
                # If the widget node list contains the model node, then it
                # means that there was some re-ordering of the lists, so just
                # remove it now and assume that it will get added back in later
                elif self._widgetNodeListContains(widgetNodes, modelNode): # widgetNode was removed from model
                    self._removeWidgetChild(childWidgetNode, widgetNodeMetaData, widgetNodes)
                else: # model node is a new node in the model
                    self._insertModelChild(parentTreeItemId, modelNode, widgetNodes, idx)
        # Anything left in the list of widget nodes must be deleted (this is 
        # the case where, at the end of the above loop, the widget nodes list
        # is larger than the model nodes list).
        for idx2 in range(len(widgetNodes) - 1, end - 1, -1):
            (childWidgetNode, widgetNodeMetaData) = self._safeWidgetListGet(widgetNodes, idx2)
            self._removeWidgetChild(childWidgetNode, widgetNodeMetaData, widgetNodes)
    # end _synchNodeLists()

    def _getChildren(self, treeItemId):
        rval = []
        (childId, cookie) = self.GetFirstChild(treeItemId)
        while childId.IsOk():
            node = self.GetPyData(childId)
            metaData = self._createMetaData(childId)
            rval.append( (node, metaData) )
            (childId, cookie) = self.GetNextChild(treeItemId, cookie)
        return rval
    # end _getChildren()

    def _widgetNodeListContains(self, widgetNodes, modelNode):
        for (node, metaData) in widgetNodes: #@UnusedVariable
            if node == modelNode:
                return True
        return False
    # end _widgetNodeListContains()

    def _removeWidgetChild(self, childWidgetNode, widgetNodeMetaData, widgetNodes):
        item = (childWidgetNode, widgetNodeMetaData)
        if item in widgetNodes:
            widgetNodes.remove( item )
            self.Delete(widgetNodeMetaData[u"id"]) #$NON-NLS-1$
    # end _removeWidgetChild()

    def _insertModelChild(self, parentTreeItemId, modelNode, widgetNodes, insertionIndex):
        (nodeText, nodeImgIdx, nodeSelImgIdx, nodeBoldFlag) = self._getTreeItemParams(modelNode)
        expandedFlag = self.contentProvider.getExpandedFlag(modelNode)
        childItemId = self.InsertItemBefore(parentTreeItemId, insertionIndex, nodeText, nodeImgIdx, nodeSelImgIdx, wx.TreeItemData(modelNode))
        if nodeBoldFlag:
            self.SetItemBold(childItemId)
        if self.contentProvider.getChildren(modelNode) and not expandedFlag:
            self._populateVirtualChild(childItemId)
        else:
            self._populateChildren(modelNode, childItemId)
            self.Expand(childItemId)
        widgetNodes.insert(insertionIndex, (modelNode, self._createMetaData(childItemId)))
    # end _insertModelChild()

    def _safeWidgetListGet(self, aList, index):
        if index < len(aList):
            return aList[index]
        return (None, None)
    # end _safeWidgetListGet()

    def _safeModelListGet(self, aList, index):
        if index < len(aList):
            return aList[index]
        return None
    # end _safeModelListGet()

# end ZTreeView