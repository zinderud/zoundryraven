
# -----------------------------------------------------------------------------------
# This class represents a single extension point def found in the zplugin.xml file.
# -----------------------------------------------------------------------------------
class ZExtensionPoint:

    def __init__(self, plugin, node, classloader):
        self.plugin = plugin
        self.epNode = node
        self.classloader = classloader
    # end __init__()

    def getId(self):
        return self.epNode.selectSingleNodeText(u"plg:id") #$NON-NLS-1$
    # end getId()

    def getClass(self):
        return self.epNode.selectSingleNodeText(u"plg:class") #$NON-NLS-1$
    # end getClass()

    def getType(self):
        return self.epNode.getAttribute(u"point") #$NON-NLS-1$
    # end getType()
    
    def getPlugin(self):
        return self.plugin
    # end getPlugin()

    def getExtensionDataNode(self):
        return self.epNode.selectSingleNode(u"plg:extension-data") #$NON-NLS-1$
    # end getExtensionDataText()

    def loadClass(self):
        return self.classloader.loadClass(self.getClass())
    # end loadClass()

# end ZExtensionPoint

