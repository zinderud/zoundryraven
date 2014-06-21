from zoundry.appframework.ui.widgets.controls.dynamic.widgetfactory import ZWidgetFactory
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.dialogs.editstoremodel import ZEditMediaStorageModel
import wx

# ------------------------------------------------------------------------------------------
# This dialog is used to edit the settings of an existing media storage.  
#
# FIXME (EPW) share code with ZNewMediaStorageWizardParamsPage
# ------------------------------------------------------------------------------------------
class ZEditMediaStorageSettingsDialog(ZValidatingHeaderDialog):

    def __init__(self, store, parent):
        self.model = ZEditMediaStorageModel(store)
        self.title = _extstr(u"editstoredialog.EditSettings") % store.getName() #$NON-NLS-1$
        self.widgetFactory = ZWidgetFactory(self, True)
        self.widgets = []

        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, self.title)
        
        self.SetSize(self.GetBestSize())
    # end __init__()

    def _createNonHeaderWidgets(self):
        self._createSiteWidgets()
    # end _createNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)

        flexGridSizer = wx.FlexGridSizer(len(self.widgets), 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        for (name, label, widget) in self.widgets: #@UnusedVariable
            flexGridSizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
            flexGridSizer.Add(widget, 0, wx.EXPAND | wx.RIGHT, 5)
        
        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 10)
        
        return box
    # end _layoutNonHeaderWidgets()
    
    def _bindWidgetEvents(self):
        self._bindOkButton(self.onOK)
    # end _bindWidgetEvents()

    def _getHeaderTitle(self):
        return _extstr(u"editstoredialog.EditMediaStorageSettings") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"editstoredialog.EditMediaStorageDialogMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/mediastorage/edit/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _createSiteWidgets(self):
        site = self.model.getMediaSite()
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"editstoredialog._Settings") % site.getDisplayName()) #$NON-NLS-1$
        siteProps = site.getProperties()
        for siteProp in siteProps:
            if siteProp.getType() == u"hidden": #$NON-NLS-1$
                continue
            label = self._createLabelFromProperty(siteProp)
            name = siteProp.getName()
            control = self._createControlFromProperty(siteProp)
            self.widgets.append( (name, label, control) )
    # end _createSiteWidgets()

    def _createLabelFromProperty(self, siteProp):
        label = getSafeString(siteProp.getDisplayName())
        if siteProp.getType() == u"checkbox": #$NON-NLS-1$
            label = u"" #$NON-NLS-1$
        else:
            label = label + u":" #$NON-NLS-1$
        return wx.StaticText(self, wx.ID_ANY, label)
    # end _createLabelFromProperty()

    def _createControlFromProperty(self, siteProp):
        widgetFactoryProps = {}
        name = siteProp.getName()
        value = self.model.getMediaStorage().getProperties()[name]

        widgetFactoryProps[u"type"] = siteProp.getType() #$NON-NLS-1$
        widgetFactoryProps[u"name"] = name #$NON-NLS-1$
        widgetFactoryProps[u"value"] = value #$NON-NLS-1$
        widgetFactoryProps[u"label"] = siteProp.getDisplayName() #$NON-NLS-1$
        widgetFactoryProps[u"tooltip"] = siteProp.getTooltip() #$NON-NLS-1$
        widgetFactoryProps[u"validation-regexp"] = siteProp.getValidationRegexp() #$NON-NLS-1$
        widgetFactoryProps[u"validation-error-message"] = siteProp.getValidationErrorMessage() #$NON-NLS-1$
        
        return self.widgetFactory.createWidget(widgetFactoryProps)
    # end _createControlFromProperty()

    def _getDataProperties(self):
        storeProperties = {}
        for (name, label, widget) in self.widgets: #@UnusedVariable
            storeProperties[name] = unicode(widget.GetValue())
        return storeProperties
    # end _getDataProperties()

    def onOK(self, event):
        properties = self._getDataProperties()
        self.model.updateStore(properties)
        event.Skip()
    # end onOK()

# end ZEditMediaStorageSettingsDialog
