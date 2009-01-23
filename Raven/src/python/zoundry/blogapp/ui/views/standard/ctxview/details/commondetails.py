from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.sizers.cardsizer import ZCardSizer
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx

# -----------------------------------------------------------------------------------------
# Factory interface for creating details panels.
# -----------------------------------------------------------------------------------------
class IZDetailsPanelFactory:

    def createDetailsPanel(self, parent):
        u"""createDetailsPanel(wx.Window) -> IZDetailsPanel
        Creates an instance of IZDetailsPanel.""" #$NON-NLS-1$
    # end createDetailsPanel()

# end IZDetailsPanelFactory


# -----------------------------------------------------------------------------------------
# An interface that all details panel impls must implement.
# -----------------------------------------------------------------------------------------
class IZDetailsPanel:

    def onSelectionChanged(self, selection):
        u"""onSelectionChanged(object) -> None
        Called when the user selects something.""" #$NON-NLS-1$
    # end onSelectionChanged()

    def destroy(self):
        u"""destroy() -> None
        Called when the panel is being destroyed.""" #$NON-NLS-1$
    # end destroy()

# end IZDetailsPanel


# -----------------------------------------------------------------------------------------
# The blog post details panel base class.  This class must be the base class for all
# blog post detail panels.
# -----------------------------------------------------------------------------------------
class ZAbstractDetailsPanel(wx.Panel, IZDetailsPanel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()

    def _createWidgets(self):
        pass
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        pass
    # end _layoutWidgets()

    def onSelectionChanged(self, selection):
        raise ZAbstractMethodCalledException(self.__class__, u"onSelectionChanged") #$NON-NLS-1$
    # end onSelectionChanged()

    def destroy(self):
        pass
    # end destroy()

# end ZAbstractDetailsPanel


# -----------------------------------------------------------------------------------------
# This container class contains one or more instances of a ZBlogPostDetailsPanel.  Each
# blog post details container is shown in a separate tab (if there are multiple).
# -----------------------------------------------------------------------------------------
class ZAbstractDetailsPanelContainer(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.selectedPanelName = None

        self.detailsPanelDefs = []
        self.detailsPanels = []

        self._loadDetailsPanelDefs()

        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()

    def _loadDetailsPanelDefs(self):
        pluginRegistry = getApplicationModel().getPluginRegistry()
        extensions = pluginRegistry.getExtensions(self._getExtensionPoint())
        self.detailsPanelDefs = map(self._getExtensionDefClass(), extensions)
    # end _loadDetailsPanelDefs()

    def _createDetailsPanels(self, parent):
        for panelDef in self.detailsPanelDefs:
            factoryClass = panelDef.getClass()
            factory = factoryClass()
            panel = factory.createDetailsPanel(parent)
            self.detailsPanels.append( (panelDef.getName(), panel) )
    # end _createDetailsPanels()

    def _createWidgets(self):
        self._createDetailsPanels(self)
    # end _createWidgets()

    def getPanelNames(self):
        names = []
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            names.append(panelName)
        return names
    # end getPanelNames()

    def selectPanel(self, name):
        for (panelName, panel) in self.detailsPanels:
            panel.Show(panelName == name)
        self.selectedPanelName = name
    # end selectPanel()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        cardSizer = ZCardSizer()
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            cardSizer.Add(panel)
            panel.Show(False)

        # Show the first panel
        # FIXME (EPW) remember the one that was last shown (userprops) and show that one here
        self.detailsPanels[0][1].Show(True)
        self.selectedPanelName = self.detailsPanels[0][0]

        self.SetAutoLayout(True)
        self.SetSizer(cardSizer)
    # end _layoutWidgets()

    def destroy(self):
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            panel.destroy()

        # FIXME (EPW) save the name of the panel that was shown
    # end destroy()

    def _getExtensionPoint(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getExtensionPoint") #$NON-NLS-1$
    # end _getExtensionPoint()

    def _getExtensionDefClass(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getExtensionDefClass") #$NON-NLS-1$
    # end _getExtensionDefClass()

# end ZAbstractDetailsPanelContainer
