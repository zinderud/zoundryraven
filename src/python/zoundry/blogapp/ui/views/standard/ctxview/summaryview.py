from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.sizers.cardsizer import ZCardSizer
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenu
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.appframework.ui.widgets.controls.common.togglebutton import ZNoFocusToggleButton
from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
import wx

# ------------------------------------------------------------------------------
# Action used to switch the detail panel.
# ------------------------------------------------------------------------------
class ZSummarySwitchDetailAction(ZMenuAction):

    def __init__(self, view, panelName):
        self.view = view
        self.panelName = panelName
    # end __init__()

    def isChecked(self, context): #@UnusedVariable
        return self.view.detailsContainer.selectedPanelName == self.panelName
    # end isChecked()

    def isEnabled(self, context): #@UnusedVariable
        return not self.isChecked(context)
    # end isEnabled()

    def runCheckAction(self, actionContext, checked): #@UnusedVariable
        if checked:
            self.view.detailsContainer.selectPanel(self.panelName)
    # end runCheckAction()

# end ZSummarySwitchDetailAction


# ------------------------------------------------------------------------------
# A view that shows summary information about something.
# ------------------------------------------------------------------------------
class ZSummaryView(ZBoxedView):

    def __init__(self, parent):
        ZBoxedView.__init__(self, parent)
    # end __init__()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/common_summary.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _createHeaderWidgets(self, parent, widgetList):
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/summary/panel_menu.png") #$NON-NLS-1$
        self.panelMenuButton = ZImageButton(parent, bitmap, True, None, True)
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/summary/use_template.png") #$NON-NLS-1$
        self.templateToggleButton = ZNoFocusToggleButton(parent, bitmap)

        widgetList.append(self.templateToggleButton)
        widgetList.append(self.panelMenuButton)

        appModel = getApplicationModel()
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        useTemplateInPreview = userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.POST_PREVIEW_VIEW_USE_TEMPLATE, True)
        self.templateToggleButton.Toggle(useTemplateInPreview)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        self.detailsContainer = self._createDetailsContainer(parent)
        self.invalidSelectionWidget = wx.Panel(parent, wx.ID_ANY)
        self.invalidSelectionWidget.SetBackgroundColour(wx.WHITE)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        if len(self.detailsContainer.getPanelNames()) <= 1:
            self.panelMenuButton.Show(False)

        cardSizer = ZCardSizer()
        cardSizer.Add(self.detailsContainer)
        cardSizer.Add(self.invalidSelectionWidget)
        return cardSizer
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelectionChanged)
        self.Bind(wx.EVT_BUTTON, self.onPanelMenuButton, self.panelMenuButton)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.onTemplateToggleButton, self.templateToggleButton)
    # end _bindWidgetEvents()

    def clearSelection(self):
        self.detailsContainer.Show(False)
        self.invalidSelectionWidget.Show(True)
    # end clearSelection()

    def enableSelection(self):
        self.detailsContainer.Show(True)
        self.invalidSelectionWidget.Show(False)
    # end enableSelection()

    def onTemplateToggleButton(self, event):
        appModel = getApplicationModel()
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        useTemplateInPreview = self.templateToggleButton.IsToggled()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.POST_PREVIEW_VIEW_USE_TEMPLATE, useTemplateInPreview)
        event.Skip()
    # end onTemplateToggleButton()

    def onPanelMenuButton(self, event):
        menuModel = ZMenuModel()
        for panelName in self.detailsContainer.getPanelNames():
            action = ZSummarySwitchDetailAction(self, panelName)
            menuId = menuModel.addMenuItemWithAction(panelName, 0, action)
            menuModel.setMenuItemCheckbox(menuId, True)
        menu = ZModelBasedMenu(menuModel, None, self)
        h = self.panelMenuButton.GetSizeTuple()[1]
        x = self.panelMenuButton.GetPositionTuple()[0]
        pos = wx.Point(x, h)
        self.PopupMenu(menu, pos)
        event.Skip()
    # end onPanelMenuButton()

    def _createDetailsContainer(self, parent):
        raise ZAbstractMethodCalledException(self.__class__, u"_createDetailsContainer") #$NON-NLS-1$
    # end _createDetailsContainer()

    def onViewSelectionChanged(self, event):
        raise ZAbstractMethodCalledException(self.__class__, u"onViewSelectionChanged") #$NON-NLS-1$
    # end onViewSelectionChanged()

    def destroy(self):
        self.detailsContainer.destroy()
    # end destroy()

# end ZSummaryView
