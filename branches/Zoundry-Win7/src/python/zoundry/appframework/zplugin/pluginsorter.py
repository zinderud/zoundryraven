from zoundry.base.exceptions import ZException

# ------------------------------------------------------------------------------------
# Note:  this module exists for the sole purpose of sorting the list of loaded plugins
# by their dependency hierarchy.  This is achieved by creating a tree from the 
# dependencies listed in the zplugin.xml file.  Nodes are created for each plugin, and
# each node is added to the tree as a child of some other node.  An artificial root
# node (The Omega Node) is created so that multiple 0-dependency plugins can have a
# common parent.  If a plugin has multiple dependencies, the dependency that is 
# deepest in the tree is the one that will be used as the parent.  At the end, each
# plugin will have a depth in the tree, and the plugins will then be sorted by that
# depth value (ensuring that plugins will appear later in the list than all of their
# dependents.
# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
# Class that wraps a plugin object in a simple Node structure.  This lets us create
# a pseudo-tree from the plugins (based on dependencies) for later traversing.
# ------------------------------------------------------------------------------------
class ZPluginNode:

    def __init__(self, plugin):
        self.plugin = plugin
        self.depth = -1
        self.parent = None
        self.children = []
        self.treed = False   # True when the node has been added to the tree
        self.treeing = False # True when we begin treeing the node, False when done (prevents infinite loop)
    # end __init__()

    def hasParent(self):
        return self.parent is not None
    # end hasParent()

    def addChild(self, node):
        self.children.append(node)
    # end addChild()

    # Overload __repr__ for debugging purposes.
    def __repr__(self):
        try:
            rval = u"Omega Node\n" #$NON-NLS-1$
            if self.plugin:
                id = self.plugin.getId()
                rval = u"\n" + id.rjust(len(id) + self.depth * 3) #$NON-NLS-1$
            for child in self.children:
                rval = rval + child.__repr__()
            
            return rval
        except Exception, e:
            return ZException(rootCause = e).getStackTrace()
    # End __repr__()

# end ZPluginNode


# ------------------------------------------------------------------------------------
# Iterates through a list of plugin nodes and returns the one with the given plugin 
# id.
# ------------------------------------------------------------------------------------
def _findPluginNode(pluginId, pluginNodes):
    for node in pluginNodes:
        if node.plugin.getId() == pluginId:
            return node
    return None
# end _findPluginNode()


# ------------------------------------------------------------------------------------
# Adds the given node to the tree (represented by rootNode).  The list of plugin nodes
# is provided as well for lookups.
# ------------------------------------------------------------------------------------
def _addNodeToTree(node, rootNode, pluginNodes):
    # Skip if already done.
    if node.treed:
        return

    dependencies = node.plugin.getDependencies()
    node.treeing = True

    # Figure out which dependency is deepest in the tree and add myself as a child to THAT parent.
    parent = None
    for (pid, _ver) in dependencies:
        pnode = _findPluginNode(pid, pluginNodes)
        # Skip nodes that can't be found or are in the process of 'treeing'.
        if not pnode or pnode.treeing:
            continue
        # Add to the tree (if not already).
        _addNodeToTree(pnode, rootNode, pluginNodes)
        # If this potential parent is deeper than any other parent...
        if parent is None or pnode.depth > parent.depth:
            parent = pnode
    if not parent:
        parent = rootNode

    # Now add myself to the parent, thus becoming "treed". :)
    if not parent == node.parent: # don't add to the same parent twice
        node.parent = parent
        parent.addChild(node)
        node.depth = parent.depth + 1
        node.treed = True
    
    node.treeing = False
# end _addNodeToTree()


# ------------------------------------------------------------------------------------
# A simple 'cmp' type function that compares two plugin nodes.
# ------------------------------------------------------------------------------------
def _cmpPluginNodes(node1, node2):
    return cmp(node1.depth, node2.depth)
# end _cmpPluginNodes()


# ------------------------------------------------------------------------------------
# Unwraps a plugin from its wrapper node.
# ------------------------------------------------------------------------------------
def _unwrapPluginNode(node):
    return node.plugin
# end _unwrapPluginNode()


# ------------------------------------------------------------------------------------
# Sorts the list of ZPlugins and returns the sorted list.  Sorts them by dependencies.
# If the resulting sorted list is iterated in order, the order of the plugins 
# guarantees that plugins are always visited after their dependencies.
# ------------------------------------------------------------------------------------
def sortPlugins(plugins):
    # Step 1 - create the plugin tree.
    omegaNode = ZPluginNode(None)
    omegaNode.depth = 0
    omegaNode.treed = True
    
    pluginNodes = map(ZPluginNode, plugins)
    for node in pluginNodes:
        _addNodeToTree(node, omegaNode, pluginNodes)

    pluginNodes.sort(_cmpPluginNodes)
    return map(_unwrapPluginNode, pluginNodes)
# end sortPlugins()

