from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.dynamic.widgetfactory import ZWidgetFactory
from zoundry.appframework.ui.widgets.controls.validating.standard.combobox import ZValidatingBitmapComboBox
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNonEmptySelectionValidator
from zoundry.appframework.ui.widgets.dialogs.wizard import ZAbstractPropertyBasedWizardPage
from zoundry.appframework.ui.widgets.dialogs.wizard import ZAbstractPropertyWizardSession
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizard
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizardPage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.wizard.newmediastoragemodel import ZNewMediaStorageWizardModel
from zoundry.blogapp.services.mediastorage.mediastoragetype import IZMediaStorageCapabilities
from zoundry.blogapp.ui.menus.mediastoragemanager import ZMediaStorageMenuActionContext
from zoundry.blogapp.ui.menus.mediastoragemanager import ZTestMediaStorageMenuAction
import wx

# ------------------------------------------------------------------------------------------
# A wizard session object for use by the New Media Storage wizard.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizardSession(ZAbstractPropertyWizardSession):

    def __init__(self):
        ZAbstractPropertyWizardSession.__init__(self)
    # end __init__()

# end ZNewMediaStorageWizardSession


# ------------------------------------------------------------------------------------------
# The implementation of the New Media Storage wizard.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizard(ZWizard):

    def __init__(self, parent):
        self.model = ZNewMediaStorageWizardModel()
        ZWizard.__init__(self, parent, ZNewMediaStorageWizardSession(), wx.ID_ANY, _extstr(u"mediastoragewizard.NewMediaStorageWizard")) #$NON-NLS-1$
    # end __init__()

    def _createWizardPages(self):
        self.sitePage = ZNewMediaStorageWizardSitePage(self.model, self)
        self.paramsPage = ZNewMediaStorageWizardParamsPage(self.model, self)
        self.confirmPage = ZNewMediaStorageWizardConfirmPage(self.model, self)
        self.addPage(self.sitePage)
        self.addPage(self.paramsPage)
        self.addPage(self.confirmPage)
    # end _createWizardPages()

    def _layoutWidgets(self):
        ZWizard._layoutWidgets(self)

        (w, h) = self.GetBestSizeTuple()
        w = max(w, 450)
        self.SetSize(wx.Size(w, h))
    # end _layoutWidgets()

    def _getDefaultImage(self):
        return getResourceRegistry().getImagePath(u"images/wizards/newmediastorage.png") #$NON-NLS-1$
    # end _getDefaultImage()

    def getMediaStorageName(self):
        return self.session.getProperty(u"type-page.name") #$NON-NLS-1$
    # endgetMediaStorageName()

    def getMediaSiteId(self):
        return self.session.getProperty(u"type-page.site").getId() #$NON-NLS-1$
    # end getMediaSiteId()

    def getMediaStorageProperties(self):
        return self.session.getProperty(u"params-page.properties") #$NON-NLS-1$
    # end getMediaStorageProperties()

# end ZNewMediaStorageWizard


# ------------------------------------------------------------------------------------------
# The base class for all New Media Storage Wizard pages.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizardPage(ZAbstractPropertyBasedWizardPage):

    def __init__(self, model, parent):
        ZAbstractPropertyBasedWizardPage.__init__(self, model, parent)
    # end __init__()

    def getImage(self):
        return None
    # end getImage()

# end ZNewMediaStorageWizardPage


# -------------------------------------------------------------------------------------
# Validator for the value of the Media Storage Name field.
# -------------------------------------------------------------------------------------
class ZMediaStorageNameValidator(ZBaseControlValidator):

    def __init__(self, model):
        self.model = model
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"mediastoragewizard.EmptyStoreNameError")) #$NON-NLS-1$

        if self.model.mediaStoreExists(value):
            return self._setReason(_extstr(u"mediastoragewizard.StoreAlreadyExistsError") % value) #$NON-NLS-1$

        return True
    # end _isValid()

# end ZMediaStorageNameValidator


# ------------------------------------------------------------------------------------------
# The first page of the new media storage wizard.  This page displays a list of sites that
# the user can choose from.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizardSitePage(ZNewMediaStorageWizardPage):

    def __init__(self, model, parent):
        ZNewMediaStorageWizardPage.__init__(self, model, parent)
        self.customPages = None
        self.site = None
    # end __init__()

    def _createWidgets(self):
        self.description1 = wx.StaticText(self, wx.ID_ANY, _extstr(u"mediastoragewizard.WelcomeMessage")) #$NON-NLS-1$
        self.description1.SetFont(getDefaultFontBold())
        self.description2 = wx.StaticText(self, wx.ID_ANY, _extstr(u"mediastoragewizard.WizardDescription"), size = wx.Size(-1, 80)) #$NON-NLS-1$
        self.siteLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"mediastoragewizard.MediaStorageType")) #$NON-NLS-1$
        comboValidator = ZNonEmptySelectionValidator(_extstr(u"mediastoragewizard.EmptyStoreTypeSelectionError")) #$NON-NLS-1$
        self.siteCombo = ZValidatingBitmapComboBox(comboValidator, self, wx.ID_ANY, style = wx.CB_READONLY)
        self.siteCombo.SetToolTipString(_extstr(u"mediastoragewizard.StoreTypeComboTooltip")) #$NON-NLS-1$
        self.nameLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"mediastoragewizard.MediaStorageName")) #$NON-NLS-1$
        nameValidator = ZMediaStorageNameValidator(self._getModel())
        self.nameText = ZValidatingTextCtrl(nameValidator, self, wx.ID_ANY)
        self.nameText.SetToolTipString(_extstr(u"mediastoragewizard.MediaStorageNameTooltip")) #$NON-NLS-1$
        self.clickHereHyperlink = wx.HyperlinkCtrl(self, wx.ID_ANY, _extstr(u"mediastoragewizard.NoStorageLink"), u"http://picasaweb.google.com/?ref=ZoundryRaven") #$NON-NLS-2$ #$NON-NLS-1$
    # end _createWidgets()

    def _populateWidgets(self):
        mediaSites = self._getModel().getMediaSites()
        for site in mediaSites:
            iconPath = site.getIconPath()
            bitmap = getResourceRegistry().getBitmap(iconPath)
            self.siteCombo.Append(site.getDisplayName(), None, bitmap)
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.siteCombo)
        self._bindValidatingWidget(self.nameText)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(2, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.siteLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.siteCombo, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.nameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.nameText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY, u""), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5) #$NON-NLS-1$
        flexGridSizer.Add(self.clickHereHyperlink, 0, wx.EXPAND | wx.RIGHT, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.description1, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(self.description2, 0, wx.EXPAND | wx.ALL, 10)
        box.AddSizer(flexGridSizer, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def getDataProperties(self):
        rval = {}
        rval[u"type-page.site"] = self._getSelectedSite() #$NON-NLS-1$
        rval[u"type-page.name"] = self.nameText.GetValue() #$NON-NLS-1$
        return rval
    # end getDataProperties()

    def onEnter(self, session, eventDirection): #@UnusedVariable
        if eventDirection == ZWizardPage.NEXT:
            mediaSites = self._getModel().getMediaSites()
            idx = 0
            for site in mediaSites:
                if site.getId() == u"zoundry.blogapp.mediastorage.site.picasa": #$NON-NLS-1$
                    self.siteCombo.Select(idx)
                    self.siteCombo.validate()
                    self.nameText.SetFocus()
                    return
                idx = idx + 1

        self.siteCombo.SetFocus()
    # end onEnter()

    def onExit(self, session, eventDirection): #@UnusedVariable
        if eventDirection == ZWizardPage.NEXT:
            site = self._getSelectedSite()
            if site != self.site:
                self.site = site
                # Remove any old custom pages we may have had
                if self.customPages:
                    for page in self.customPages:
                        # magic number - the position of the first custom 
                        # page and the position of all custom pages as they 
                        # are removed
                        self.wizard.removePage(2)
                    self.customPages = None
                # Now add in new pages
                pages = []
                wizardPageClasses = self.site.createContributedWizardPages()
                insertionPoint = 2
                for wizardPageClass in wizardPageClasses:
                    page = wizardPageClass(self.model, self.wizard)
                    pages.append(page)
                    self.wizard.addPage(page, insertionPoint)
                    insertionPoint = insertionPoint + 1
                self.customPages = pages
        return True
    # end onExit()

    def _getSelectedSite(self):
        idx = self.siteCombo.GetSelection()
        return self._getModel().getMediaSites()[idx]
    # end _getSelectedSite()

# end ZNewMediaStorageTypePage


# ------------------------------------------------------------------------------------------
# The first page of the new media storage wizard.  This page displays a list of sites that
# the user can choose from.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizardParamsPage(ZNewMediaStorageWizardPage):

    def __init__(self, model, parent):
        self.mediaSite = None
        self.widgetFactory = ZWidgetFactory(self, True)
        self.widgets = []

        ZNewMediaStorageWizardPage.__init__(self, model, parent)
    # end __init__()

    def onEnter(self, session, eventDirection): #@UnusedVariable
        self.storeName = session.getProperty(u"type-page.name") #$NON-NLS-1$
        selectedMediaSite = session.getProperty(u"type-page.site") #$NON-NLS-1$
        if self.mediaSite != selectedMediaSite:
            self.mediaSite = selectedMediaSite
            self.DestroyChildren()
            self.widgets = []
            self._createSiteWidgets()
            self._layoutSiteWidgets()
            self._validate()
            # Commented out because SetFocus() was causing some strange behavior...
#            (name, label, widget) = self.widgets[0] #@UnusedVariable
#            widget.SetFocus()
    # end onEnter()

    def _createSiteWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"mediastoragewizard._Settings") % self.mediaSite.getDisplayName()) #$NON-NLS-1$
        siteProps = self.mediaSite.getProperties()
        for siteProp in siteProps:
            if siteProp.getType() == u"hidden": #$NON-NLS-1$
                continue
            label = self._createLabelFromProperty(siteProp)
            name = siteProp.getName()
            control = self._createControlFromProperty(siteProp)
            self.widgets.append( (name, label, control) )
    # end _createSiteWidgets()

    def _createLabelFromProperty(self, siteProp):
        label = siteProp.getDisplayName()
        if siteProp.getType() == u"checkbox": #$NON-NLS-1$
            label = u"" #$NON-NLS-1$
        else:
            label = label + u":" #$NON-NLS-1$
        return wx.StaticText(self, wx.ID_ANY, label)
    # end _createLabelFromProperty()

    def _createControlFromProperty(self, siteProp):
        widgetFactoryProps = {}
        widgetFactoryProps[u"type"] = siteProp.getType() #$NON-NLS-1$
        widgetFactoryProps[u"name"] = siteProp.getName() #$NON-NLS-1$
        widgetFactoryProps[u"value"] = siteProp.getDefaultValue() #$NON-NLS-1$
        widgetFactoryProps[u"label"] = siteProp.getDisplayName() #$NON-NLS-1$
        widgetFactoryProps[u"tooltip"] = siteProp.getTooltip() #$NON-NLS-1$
        widgetFactoryProps[u"validation-regexp"] = siteProp.getValidationRegexp() #$NON-NLS-1$
        widgetFactoryProps[u"validation-error-message"] = siteProp.getValidationErrorMessage() #$NON-NLS-1$

        return self.widgetFactory.createWidget(widgetFactoryProps)
    # end _createControlFromProperty()

    def _layoutSiteWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)

        flexGridSizer = wx.FlexGridSizer(len(self.widgets), 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        for (name, label, widget) in self.widgets: #@UnusedVariable
            flexGridSizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
            flexGridSizer.Add(widget, 0, wx.EXPAND | wx.RIGHT, 5)

        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutSiteWidgets()

    def getDataProperties(self):
        rval = {}

        storeProperties = {}
        for (name, label, widget) in self.widgets: #@UnusedVariable
            storeProperties[name] = unicode(widget.GetValue())

        rval[u"params-page.properties"] = storeProperties #$NON-NLS-1$
        return rval
    # end getDataProperties()

# end ZNewMediaStorageWizardParamsPage


# ------------------------------------------------------------------------------------------
# The first page of the new media storage wizard.  This page displays a list of sites that
# the user can choose from.
# ------------------------------------------------------------------------------------------
class ZNewMediaStorageWizardConfirmPage(ZNewMediaStorageWizardPage):

    def __init__(self, model, parent):
        ZNewMediaStorageWizardPage.__init__(self, model, parent)
        self.mediaSite = None
        self.propertyValues = {}
        self.session = None
    # end __init__()

    def onEnter(self, session, eventDirection): #@UnusedVariable
        self.session = session
        self.mediaSite = session.getProperty(u"type-page.site") #$NON-NLS-1$
        self.propertyValues = session.getProperty(u"params-page.properties") #$NON-NLS-1$
        self.DestroyChildren()
        self.widgets = []
        self._createConfirmWidgets()
        self._layoutConfirmWidgets()
        self._bindConfirmWidgetEvents()
    # end onEnter()

    def _createConfirmWidgets(self):
        self.confirmText = wx.StaticText(self, wx.ID_ANY, _extstr(u"mediastoragewizard.ConfirmSettingsText")) #$NON-NLS-1$
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"mediastoragewizard.Settings")) #$NON-NLS-1$
        siteProps = self.mediaSite.getProperties()
        for siteProp in siteProps:
            label = self._createLabelFromProperty(siteProp)
            valueLabel = self._createLabelFromPropertyValue(siteProp)
            self.widgets.append( (label, valueLabel) )

        self.testButton = wx.Button(self, wx.ID_ANY, _extstr(u"mediastoragewizard.TestSettings")) #$NON-NLS-1$
        storage = self._createMediaStorageForTesting()
        if not storage.getCapabilities().hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_DELETE):
            self.testButton.Show(False)
    # end _createConfirmWidgets()

    def _createLabelFromProperty(self, siteProp):
        label = siteProp.getDisplayName()
        label = label + u":" #$NON-NLS-1$
        textCtrl = wx.StaticText(self, wx.ID_ANY, label)
        textCtrl.SetFont(getDefaultFontBold())
        return textCtrl
    # end _createLabelFromProperty()

    def _createLabelFromPropertyValue(self, siteProp):
        name = siteProp.getName()
        label = self.propertyValues[name]
        if name == u"password": #$NON-NLS-1$
            label = u"******" #$NON-NLS-1$
        text = wx.StaticText(self, wx.ID_ANY, label)
        text.SetToolTipString(label)
        return text
    # end _createLabelFromPropertyValue()

    def _layoutConfirmWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)

        flexGridSizer = wx.FlexGridSizer(len(self.widgets), 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        for (label, widget) in self.widgets: #@UnusedVariable
            flexGridSizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
            flexGridSizer.Add(widget, 0, wx.EXPAND | wx.RIGHT, 5)

        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.Add(self.confirmText, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        box.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(self.testButton, 0, wx.LEFT, 10)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutConfirmWidgets()

    def _bindConfirmWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onTest, self.testButton)
    # end _bindConfirmWidgetEvents()

    def onTest(self, event):
        storage = self._createMediaStorageForTesting()
        context = ZMediaStorageMenuActionContext(self, storage, None)
        action = ZTestMediaStorageMenuAction()
        action.runAction(context)
        event.Skip()
    # end onTest()

    def getMediaStorageName(self):
        return self.session.getProperty(u"type-page.name") #$NON-NLS-1$
    # endgetMediaStorageName()

    def getMediaSiteId(self):
        return self.session.getProperty(u"type-page.site").getId() #$NON-NLS-1$
    # end getMediaSiteId()

    def getMediaStorageProperties(self):
        return self.session.getProperty(u"params-page.properties") #$NON-NLS-1$
    # end getMediaStorageProperties()

    def _createMediaStorageForTesting(self):
        storageService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        name = self.getMediaStorageName()
        mediaSiteId = self.getMediaSiteId()
        properties = self.getMediaStorageProperties()
        persist = False
        storage = storageService.createMediaStorage(name, mediaSiteId, properties, persist)
        return storage
    # end _createMediaStorageForTesting()

# end ZNewMediaStorageWizardConfirmPage
