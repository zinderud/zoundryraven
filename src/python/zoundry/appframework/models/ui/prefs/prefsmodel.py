from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.prefs.prefsdef import ZPreferencePageDef
from zoundry.appframework.models.ui.widgets.treemodel import IZTreeNodeModel
from zoundry.appframework.models.ui.widgets.treemodel import ZHiddenRootTreeNodeModel
from zoundry.appframework.resources.resourceutils import ZMappedImageList


# ---------------------------------------------------------------------------------------
# Base class for modelling a single node in the User Preferences dialog's tree view.
# ---------------------------------------------------------------------------------------
class ZPrefPageModel(IZTreeNodeModel):

    def __init__(self, prefDef):
        self.prefDef = prefDef
        self.children = []
    # end __init__()

    def setChildren(self, children):
        self.children = children
    # end setChildren()

    def getLabel(self):
        return self.prefDef.getName()
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    def getImageLabel(self):
        return self.prefDef.getIconKey()
    # end getImageLabel()

    def getSelectedImageLabel(self):
        return self.prefDef.getIcon()
    # end getSelectedImageLabel()

    def isBold(self):
        return self.children is not None and len(self.children) > 0
    # end isBold()

    def isExpanded(self):
        return True
    # end isExpanded()

    def compareTo(self, otherNode):
        myPriority = self.prefDef.getPriority()
        otherPriority = otherNode.prefDef.getPriority()
        if myPriority < otherPriority:
            return -1
        elif myPriority > otherPriority:
            return 1
        else:
            return 0
    # end compareTo()

    def getId(self):
        return self.prefDef.getId()
    # end getId()

    def getName(self):
        return self.getLabel()
    # end getName()
    
    def getDescription(self):
        return self.prefDef.getDescription()
    # end getDescription()

    def getHeaderImagePath(self):
        return self.prefDef.resolveHeaderImage()
    # end getHeaderImagePath()
    
    def getPreferencePageClass(self):
        return self.prefDef.getClass()
    # end getPreferencePageClass()

# end ZPrefPageModel


# ---------------------------------------------------------------------------------------
# The model used by the Settings Dialog (User Preferences Dialog).  This model uses the
# prefpage extension point as its source of data.
# ---------------------------------------------------------------------------------------
class ZPreferencesModel:

    def __init__(self):
        self.prefsDefs = self._loadAllPrefDefs()
        self.rootNode = self._buildPrefsTree()
        self.imageList = self._createImageList()
    # end __init__()

    def getRootNode(self):
        return self.rootNode
    # end getRootNode()
    
    def getImageList(self):
        return self.imageList
    # end getImageList()

    def _createImageList(self):
        imageList = ZMappedImageList()
        for prefDef in self.prefsDefs:
            imageList.addImage(prefDef.getIconKey(), prefDef.loadIcon())
        return imageList
    # end _createImageList()

    def _buildPrefsTree(self):
        topLevelPrefDefs = self._getChildDefs(None)
        topLevelNodes = map(self._createModel, topLevelPrefDefs)

        return ZHiddenRootTreeNodeModel(topLevelNodes)
    # end _buildPrefsTree()

    def _createModel(self, prefDef):
        model = ZPrefPageModel(prefDef)
        childDefs = self._getChildDefs(prefDef.getId())
        childNodes = map(self._createModel, childDefs)
        model.setChildren(childNodes)
        return model
    # end _createModel()

    def _getChildDefs(self, parent):
        rval = []
        for prefDef in self.prefsDefs:
            if prefDef.getParent() == parent:
                rval.append(prefDef)
        return rval
    # end _getChildDefs()

    def _loadAllPrefDefs(self):
        pluginRegistry = getApplicationModel().getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZAppExtensionPoints.ZEP_PREFERENCE_PAGE)
        return map(ZPreferencePageDef, extensions)
    # end _loadAllPrefDefs()

# end ZPreferencesModel
