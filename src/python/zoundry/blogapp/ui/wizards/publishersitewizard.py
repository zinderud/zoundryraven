from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.registry import getImageType
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.appframework.ui.widgets.controls.progress import ZProgressLabelCtrl
from zoundry.appframework.ui.widgets.controls.validating.standard.combobox import ZValidatingBitmapComboBox
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNonEmptySelectionValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNullControlValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZUrlSelectionValidator
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowErrorMessage
from zoundry.appframework.ui.widgets.dialogs.wizard import ZAbstractPropertyBasedWizardPage
from zoundry.appframework.ui.widgets.dialogs.wizard import ZAbstractPropertyWizardSession
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizard
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizardBackroundTask
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizardPage
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.wizard.newpublishersitemodel import ZNewPublisherSiteWizardModel
from zoundry.blogapp.services.pubsystems.pubdefs import ZPublisherSiteDef
from zoundry.blogapp.ui.common.publisher import ZBlogCheckboxListContentProvider
from zoundry.blogapp.ui.util.mediastorageutil import ZMediaStorageUtil
import wx




# ------------------------------------------------------------------------------------------
# A wizard session object
# ------------------------------------------------------------------------------------------
class ZNewPublisherSiteWizardSession(ZAbstractPropertyWizardSession):

    def __init__(self):
        ZAbstractPropertyWizardSession.__init__(self)
    # end __init__()
# end ZNewPublisherSiteWizardSession


# ------------------------------------------------------------------------------------------
# The implementation of the New Publisher Site wizard.
# ------------------------------------------------------------------------------------------
class ZNewPublisherSiteWizard(ZWizard):

    def __init__(self, parent):
        self.model = ZNewPublisherSiteWizardModel()
        ZWizard.__init__(self, parent, ZNewPublisherSiteWizardSession(), wx.ID_ANY, _extstr(u"publishersitewizard.NewPublisherSiteWizard")) #$NON-NLS-1$
    # end __init__()

    def getAccountName(self):
        u"""getAccountName() -> string
        Returns account name
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"apiinfo-page.accname") #$NON-NLS-1$

    def getSiteId(self):
        u"""getSiteId() -> string
        Returns blog publisher site id or None
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"apiinfo-page.siteid") #$NON-NLS-1$

    def getUsername(self):
        u"""getUsername() -> string
        Returns username.
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"apiinfo-page.username") #$NON-NLS-1$

    def getPassword(self):
        u"""getPassword() -> string
        Returns password.
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"apiinfo-page.password") #$NON-NLS-1$

    def getApiUrl(self):
        u"""getApiUrl() -> string
        Returns api url
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"apiinfo-page.apiurl") #$NON-NLS-1$

    def getMediaUploadMethod(self):
        u""""getMediaUploadMethod() -> string
        Returns None, 'publisher' or 'mediastorage'. If mediastorage, then get store id from getMediaStorageId()
        """#$NON-NLS-1$
        return self.getSession().getProperty(u"confirm-page.file-upload-method") #$NON-NLS-1$

    def getMediaStorageId(self):
        u"""getMediaStorageId() -> string
        Returns media storage site id if upload method is 'mediastorage'.
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"confirm-page.file-upload-mediastorage-id") #$NON-NLS-1$

    def getSelectedBlogs(self):
        u"""getSelectedBlogs() -> list of izblog
        Returns list of selected blogs
        """ #$NON-NLS-1$
        return self.getSession().getProperty(u"confirm-page.selected-blogs") #$NON-NLS-1$

    def _createWizardPages(self):
        self.urlPage = ZNewPublisherSiteUrlPage(self.model, self)
        self.apiPage = ZNewPublisherSiteApiInfoPage(self.model, self)
        self.confirmPage = ZNewPublisherSiteConfirmPage(self.model, self)
        self.addPage(self.urlPage)
        self.addPage(self.apiPage)
        self.addPage(self.confirmPage)
    # end _createWizardPages()

    def _layoutWidgets(self):
        ZWizard._layoutWidgets(self)
        (w, h) = self.GetBestSizeTuple()
        w = max(w, 500)
        self.SetSize(wx.Size(w, h))
    # end _layoutWidgets()

    def _getDefaultImage(self):
        return getResourceRegistry().getImagePath(u"images/wizards/newpubsite.png") #$NON-NLS-1$
    # end _getDefaultImage()


# -------------------------------------------------------------------------------------
# Validator for the value of the Publisher site account Name field.
# -------------------------------------------------------------------------------------
class ZPublisherAccountNameValidator(ZBaseControlValidator):

    def __init__(self, model):
        self.model = model
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"publishersitewizard.EmptyAccountNameError")) #$NON-NLS-1$
        if self.model.accountNameExists(value):
            return self._setReason(_extstr(u"publishersitewizard.AccountAlreadyExistsError") % value) #$NON-NLS-1$
        return True
    # end _isValid()
# end ZPublisherAccountNameValidator


# ------------------------------------------------------------------------------------------
# The base class for all new publisher site wizard pages.
# ------------------------------------------------------------------------------------------
class ZNewPublisherSiteWizardPageBase(ZAbstractPropertyBasedWizardPage):

    def __init__(self, model, parent):
        ZAbstractPropertyBasedWizardPage.__init__(self, model, parent)
    # end __init__()

    def getImage(self):
        return None
    # end getImage()
# end ZNewPublisherSiteWizardPageBase


# ------------------------------------------------------------------------------------------
# Page 1: show text box for the user to enter the blog site url.
# ------------------------------------------------------------------------------------------
class ZNewPublisherSiteUrlPage(ZNewPublisherSiteWizardPageBase):

    def __init__(self, model, parent):
        ZNewPublisherSiteWizardPageBase.__init__(self, model, parent)
    # end __init__()

    def _createWidgets(self):
        self.description1 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.WelcomeMessage")) #$NON-NLS-1$
        self.description1.SetFont(getDefaultFontBold())
        self.description2 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.WizardDescription"), size = wx.Size(-1, 80)) #$NON-NLS-1$
        self.urlLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.BlogUrlLabel")) #$NON-NLS-1$
        urlValidator = ZUrlSelectionValidator(_extstr(u"publishersitewizard.BlogUrlInvalid"), nonEmpty=False) #$NON-NLS-1$
        self.urlText = ZValidatingTextCtrl(urlValidator, self, wx.ID_ANY)
        self.urlText.SetToolTipString(_extstr(u"publishersitewizard.BlogUrlTooltip")) #$NON-NLS-1$
        self.animateControl = ZProgressLabelCtrl(self)
        self.clickHereHyperlink = wx.HyperlinkCtrl(self, wx.ID_ANY, _extstr(u"publishersitewizard.NoBlogYet"), u"http://www.blogger.com/?ref=ZoundryRaven") #$NON-NLS-2$ #$NON-NLS-1$
    # end _createWidgets()

    def _populateWidgets(self):
        self._showBusy(False)
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.urlText)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(1, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.urlLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.urlText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.animateControl, 0,  wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.clickHereHyperlink, 0, wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.description1, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(self.description2, 0, wx.EXPAND | wx.ALL, 10)
        box.AddSizer(flexGridSizer, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def _showBusy(self, enable, text = u""): #$NON-NLS-1$
        if getNoneString(text):
            self.animateControl.setLabel(text)
        self.animateControl.Show(enable)
    # end _showBusy()

    def _getSiteUrl(self):
        return self.urlText.GetValue().strip()
    # end _getSiteUrl()

    def getDataProperties(self):
        rval = {}
        rval[u"siteurl-page.url"] = self._getSiteUrl() #$NON-NLS-1$
        return rval
    # end getDataProperties()

    def _refresh(self, eventType, eventData):
        if eventType == u"begin-autodiscover": #$NON-NLS-1$
            self.urlText.Enable(False)
            self._showBusy(True, u"Checking... %s" % self._getSiteUrl()) #$NON-NLS-1$
        elif eventType == u"end-autodiscover":  #$NON-NLS-1$
            self.urlText.Enable(True)
            self._showBusy(False)
        elif eventType == u"error-autodiscover": #$NON-NLS-1$
            (errMsg, errDetails, err) = eventData #@UnusedVariable
            ZShowErrorMessage(self, errMsg, errDetails)
    # end _refresh()

    def onEnter(self, session, eventDirection): #@UnusedVariable
        self.urlText.SetFocus()
    # end onEnter()

    def onExit(self, session, eventDirection):
        if eventDirection == ZWizardPage.NEXT:
            oldValue = session.getProperty(u"siteurl-page.url") #$NON-NLS-1$
            newValue = self._getSiteUrl()
            # auto discover if there is a new value and it not empty
            if newValue and newValue != oldValue:
                # check for cached discover data
                cacheMap = session.getProperty(u"siteurl-page.discover-info-cache") #$NON-NLS-1$
                if cacheMap and cacheMap.has_key(newValue):
                    discoverInfo = cacheMap[newValue]
                    session.setProperty(u"siteurl-page.discover-info", discoverInfo) #$NON-NLS-1$
                else:
                    task = ZAutodiscoverTask(self, session)
                    self._fireBeginBackgroundTaskEvent(task)
                    return False
            elif oldValue and not newValue:
                # new value does not exist. reset auto-disc.
                session.setProperty(u"siteurl-page.discover-info", None) #$NON-NLS-1$
        return True
    # end onExit()

# end ZNewPublisherSiteUrlPage


# ------------------------------------------------------------------------------------------
# Page 1 Wizard bg task to perform auto-discover
# ------------------------------------------------------------------------------------------
class ZAutodiscoverTask(ZWizardBackroundTask):

    def __init__(self, page, session):
        ZWizardBackroundTask.__init__(self, page, session)

    def _runTask(self):
        newValue = self.getPage()._getSiteUrl()
        # fire evt to start busy animation
        self.refreshPage(u"begin-autodiscover",newValue) #$NON-NLS-1$
        rval = False
        try:
            # reset previous value
            self.getSession().setProperty(u"siteurl-page.discover-info", None) #$NON-NLS-1$
            discoverInfo = self.getPage()._getModel().autodiscover(newValue)
            #print u"ZAutodiscoverTask info",discoverInfo #$NON-NLS-1$ FIXME (PJ) remove this debug line
            self.getSession().setProperty(u"siteurl-page.discover-info", discoverInfo) #$NON-NLS-1$
            # cache successful results
            if discoverInfo and discoverInfo.siteId:
                cacheMap = self.getSession().getProperty(u"siteurl-page.discover-info-cache") #$NON-NLS-1$
                if cacheMap is None:
                    cacheMap = {}
                    self.getSession().setProperty(u"siteurl-page.discover-info-cache", cacheMap) #$NON-NLS-1$
                cacheMap[newValue] = discoverInfo
            rval = True
        except Exception, e:
            # FIXME (PJ) show friendly error messages
            # fire evt to show error message to user.
            zex = ZException(rootCause = e)
            data = (u"Auto discovery error", zex.getStackTrace(), zex) #$NON-NLS-1$
            self.refreshPage(u"error-autodiscover", data) #$NON-NLS-1$
        # finally fire evt to hide busy animate control
        self.refreshPage(u"end-autodiscover") #$NON-NLS-1$
        return rval

# ------------------------------------------------------------------------------------------
# Page 2: show api information
# ------------------------------------------------------------------------------------------
class ZNewPublisherSiteApiInfoPage(ZNewPublisherSiteWizardPageBase):

    def __init__(self, model, parent):
        ZNewPublisherSiteWizardPageBase.__init__(self, model, parent)
    # end __init__()

    def _createWidgets(self):
        self.description1 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.ApiInfo")) #$NON-NLS-1$
        self.description1.SetFont(getDefaultFontBold())
        self.description2 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.ApiInfoDescription"), size = wx.Size(-1, 40)) #$NON-NLS-1$

        self.accLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.AccountNameLabel")) #$NON-NLS-1$
        accNameValidator = ZPublisherAccountNameValidator( self._getModel() )
        self.accText = ZValidatingTextCtrl(accNameValidator, self, wx.ID_ANY)
        self.accText.SetToolTipString(_extstr(u"publishersitewizard.AccountNameTooltip")) #$NON-NLS-1$

        self.siteLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.SiteTypeLabel")) #$NON-NLS-1$
        comboValidator = ZNonEmptySelectionValidator(_extstr(u"publishersitewizard.EmptySiteTypeSelectionError")) #$NON-NLS-1$
        self.siteCombo = ZValidatingBitmapComboBox(comboValidator, self, wx.ID_ANY, style = wx.CB_READONLY)
        self.siteCombo.SetToolTipString(_extstr(u"publishersitewizard.SiteTypeTooltip")) #$NON-NLS-1$
        self.Bind(wx.EVT_COMBOBOX, self.onComboEvent, self.siteCombo.widget)

        self.autodiscoveryHint = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$

        self.usernameLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.UsernameLabel")) #$NON-NLS-1$
        usernameValidator = ZNonEmptySelectionValidator(_extstr(u"publishersitewizard.EmptyUsername")) #$NON-NLS-1$
        self.usernameText = ZValidatingTextCtrl(usernameValidator, self, wx.ID_ANY)
        self.usernameText.SetToolTipString(_extstr(u"publishersitewizard.UsernameTooltip")) #$NON-NLS-1$

        self.passwordLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.PasswordLabel")) #$NON-NLS-1$
        passwordValidator = ZNonEmptySelectionValidator(_extstr(u"publishersitewizard.EmptyPassword")) #$NON-NLS-1$
        self.passwordText = ZValidatingTextCtrl(passwordValidator, self, wx.ID_ANY, style=wx.TE_PASSWORD )
        self.passwordText.SetToolTipString(_extstr(u"publishersitewizard.PasswordTooltip")) #$NON-NLS-1$

        self.apiUrlLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.ApiUrlLabel")) #$NON-NLS-1$
        apiUrlValidator = ZUrlSelectionValidator(_extstr(u"publishersitewizard.ApiUrlInvalid")) #$NON-NLS-1$
        self.apiUrlText = ZValidatingTextCtrl(apiUrlValidator, self, wx.ID_ANY)
        self.apiUrlText.SetToolTipString(_extstr(u"publishersitewizard.ApiUrlTooltip")) #$NON-NLS-1$
        self.apiUrlHint = wx.StaticText(self, wx.ID_ANY, u"Api Url hints") #$NON-NLS-1$
        self.animateControl = ZProgressLabelCtrl(self)
    # end _createWidgets()

    def _populateWidgets(self):
        self._showBusy(False)
        siteDefList = []
        siteDefList.extend( self._getModel().listPublisherSites() )
        siteDefList.sort( lambda x, y: cmp( x.getName().lower(), y.getName().lower() ) )
        for siteDef in siteDefList:
            bitmap = siteDef.getIconAsBitmap()
            self.siteCombo.Append(siteDef.getName(), siteDef, bitmap)
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.accText)
        self._bindValidatingWidget(self.siteCombo)
        self._bindValidatingWidget(self.usernameText)
        self._bindValidatingWidget(self.passwordText)
        self._bindValidatingWidget(self.apiUrlText)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(7, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.accLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.accText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.siteLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.siteCombo, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.autodiscoveryHint, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.usernameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.usernameText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.passwordLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.passwordText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.apiUrlLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.apiUrlText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.apiUrlHint, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.animateControl, 0,  wx.EXPAND | wx.ALIGN_LEFT |wx.RIGHT, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.description1, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(self.description2, 0, wx.EXPAND | wx.ALL, 10)
        box.AddSizer(flexGridSizer, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def getDataProperties(self):
        rval = {}
        rval[u"apiinfo-page.accname"] = self.accText.GetValue().strip() #$NON-NLS-1$
        site = self._getSelectedSite()
        id = None
        if site:
            id = site.getId()
        rval[u"apiinfo-page.siteid"] = id#$NON-NLS-1$
        rval[u"apiinfo-page.username"] = self.usernameText.GetValue().strip() #$NON-NLS-1$
        rval[u"apiinfo-page.password"] = self.passwordText.GetValue().strip() #$NON-NLS-1$
        rval[u"apiinfo-page.apiurl"] = self.apiUrlText.GetValue().strip() #$NON-NLS-1$
        return rval
    # end getDataProperties()

    def _enableControls(self, enable):
        self.accText.Enable(enable)
        self.siteCombo.Enable(enable)
        self.usernameText.Enable(enable)
        self.passwordText.Enable(enable)
        self.apiUrlText.Enable(enable)

    def _showBusy(self, enable, text = u""): #$NON-NLS-1$
        if getNoneString(text):
            self.animateControl.setLabel(text)
        self.animateControl.Show(enable)

    def _updateDiscoverInfo(self, discoverInfo ):
        hint = u"" #$NON-NLS-1$
        if discoverInfo:
            if discoverInfo.engineName:
                hint = u"Autodiscovered %s" % discoverInfo.engineName #$NON-NLS-1$
            else:
                hint = u"Autodiscover information not available." #$NON-NLS-1$
            if discoverInfo.username and not self.usernameText.GetValue():
                self.usernameText.SetValue(discoverInfo.username)
            if discoverInfo.siteId:
                self._selectSiteId(discoverInfo.siteId)

            apiUrl = None
            if getNoneString(discoverInfo.apiUrl):
                apiUrl = discoverInfo.apiUrl
            else:
                # find api url from site def
                apiUrl = self._getDefaultUrlForSelectedSite()
            if apiUrl:
                self.apiUrlText.SetValue(apiUrl)

        self.autodiscoveryHint.SetLabel(hint)

    def _refresh(self, eventType, eventData):
        if eventType == u"begin-listblogs": #$NON-NLS-1$
            self._enableControls(False)
            self._showBusy(True, u"Getting blog list...") #$NON-NLS-1$
        elif eventType == u"end-listblogs":  #$NON-NLS-1$
            self._enableControls(True)
            self._showBusy(False)
        elif eventType == u"error-listblogs": #$NON-NLS-1$
            (errMsg, errDetails, err) = eventData #@UnusedVariable
            ZShowErrorMessage(self, errMsg, errDetails)

    def onEnter(self, session, eventDirection):
        self.accText.SetFocus()
        if eventDirection == ZWizardPage.NEXT:
            discoverInfo = session.getProperty(u"siteurl-page.discover-info") #$NON-NLS-1$
            #print u"ApiInfoPageinfo-Enter discinfo=", discoverInfo # FIXME (PJ) delete this #$NON-NLS-1$
            self._updateDiscoverInfo(discoverInfo)

    def onExit(self, session, eventDirection):
        # look up blog list if data has changed
        if eventDirection == ZWizardPage.NEXT:
            siteId   = self._getSelectedSite().getId()
            username = self.usernameText.GetValue().strip()
            password = self.passwordText.GetValue().strip()
            apiUrl = self.apiUrlText.GetValue().strip()
            key = siteId + username + password + apiUrl
            oldKey = session.getProperty(u"apiinfo-page.modifykey") #$NON-NLS-1$
            if not oldKey or oldKey != key:
                task = ZListBlogsTask(self, session, siteId, username, password, apiUrl,key)
                self._fireBeginBackgroundTaskEvent(task)
                return False
        return True

    def onComboEvent(self, event): #@UnusedVariable
        defUrl = self._getDefaultUrlForSelectedSite()
        if defUrl:
            self.apiUrlText.SetValue(defUrl)

    def _getDefaultUrlForSelectedSite(self):
        # Attempts to get the default or predefined url for the currenly selected site.
        siteDef = self._getSelectedSite()
        defUrl = self._getModel().getDefaultApiUrl(siteDef)
        return defUrl

    def _selectSiteId(self, siteId):
        n = self.siteCombo.GetCount()
        for idx in range(n):
            data = self.siteCombo.GetClientData(idx)
            if data and data.getId() == siteId:
                self.siteCombo.SetSelection(idx)
                self.siteCombo.validate()
                break

    def _getSelectedSite(self):
        data = None
        idx = self.siteCombo.GetSelection()
        if idx != -1:
            data = self.siteCombo.GetClientData(idx)
            # print "SELSITE %s %s" % (data.getName(),data.getId())
        return data
    # end _getSelectedSite()

# ------------------------------------------------------------------------------------------
# Page 2 bg task to list bogs using publisher api
# ------------------------------------------------------------------------------------------
class ZListBlogsTask(ZWizardBackroundTask):

    def __init__(self, page, session, siteId, username, password, apiUrl, key):
        ZWizardBackroundTask.__init__(self, page, session)
        self.siteId = siteId
        self.username = username
        self.password = password
        self.apiUrl = apiUrl
        self.key = key

    def _runTask(self):
        # fire evt to start busy animation
        self.refreshPage(u"begin-listblogs") #$NON-NLS-1$
        rval = False
        try:
            blogs = self.getPage()._getModel().listBlogs(self.siteId, self.username, self.password, self.apiUrl)
            idx = 0
            idBlogList = []
            for blog in blogs:
                idBlogList.append( (idx, blog) )
                idx = idx + 1
            self.getSession().setProperty(u"apiinfo-page.modifykey", self.key) #$NON-NLS-1$
            self.getSession().setProperty(u"apiinfo-page.id-bloglist", idBlogList) #$NON-NLS-1$
            rval = True
        except Exception, e:
            # FIXME (PJ) show friendly error messages
            zex = ZException(rootCause = e)
            data = (u"Error fetching list of blogs", zex.getStackTrace(), zex) #$NON-NLS-1$
            # fire evt to show error message to user.
            self.refreshPage(u"error-listblogs", data) #$NON-NLS-1$
        # finally fire evt to hide busy animate control
        self.refreshPage(u"end-listblogs") #$NON-NLS-1$
        return rval

#-----------------------------------------------------------------------
# Page 3 - confirm blog list and choose media storage site.
#-----------------------------------------------------------------------
class ZNewPublisherSiteConfirmPage(ZNewPublisherSiteWizardPageBase):

    def __init__(self, model, parent):
        self.blogSiteId = None
        self.blogListProvider = ZBlogCheckboxListContentProvider()
        ZNewPublisherSiteWizardPageBase.__init__(self, model, parent)
    # end __init__()

    def _createWidgets(self):
        self.description1 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.Confirm")) #$NON-NLS-1$
        self.description1.SetFont(getDefaultFontBold())
        self.description2 = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.ConfirmDescription"), size = wx.Size(-1, 40)) #$NON-NLS-1$
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"accountblogs.BlogList")) #$NON-NLS-1$
        self.blogListControl = ZCheckBoxListViewWithButtons(self.blogListProvider, self)
        self.mediaUploadLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"publishersitewizard.MediaUploadMethodLabel")) #$NON-NLS-1$
        comboValidator = ZNullControlValidator()
        self.mediaUploadCombo = ZValidatingBitmapComboBox(comboValidator, self, wx.ID_ANY, style = wx.CB_READONLY)
        self.mediaUploadCombo.SetToolTipString(_extstr(u"publishersitewizard.MediaUploadMethodTooltip")) #$NON-NLS-1$
        self.mediaWizardButton = wx.Button(self, wx.ID_ANY, _extstr(u"publishersitewizard.CreateNewMediaStorage")) #$NON-NLS-1$

    def _populateMediaSitesList(self, selectedMediaStorageId = None):
        self.mediaUploadCombo.Clear()
        # FIXME (PJ) create a new 're-usable' model which lists given blog site id + available media storages  => maybe as a new control
        if self.blogSiteId:
            siteDef = self._getModel().getPublisherSite(self.blogSiteId)
            if siteDef.getCapabilities().supportsUploadMedia():
                bitmap = siteDef.getIconAsBitmap()
                name = u"Blog Fileupload (via %s)"  % siteDef.getName()  #$NON-NLS-1$
                self.mediaUploadCombo.Append(name, siteDef, bitmap)

        mediaStores = []
        mediaStores.extend( self._getModel().getMediaStorages() )
        mediaStores.sort( lambda x, y: cmp( x.getName().lower(), y.getName().lower() ) )
        for mediaStore in mediaStores:
            mediaSite = self._getModel().getMediaSite(mediaStore)
            if mediaSite.isInternal():
                continue
            name = mediaStore.getName() + u" (" + mediaSite.getDisplayName() + u")" #$NON-NLS-1$ #$NON-NLS-2$
            iconPath = mediaSite.getIconPath()
            bitmap = wx.Image(iconPath, getImageType(iconPath)).ConvertToBitmap()
            self.mediaUploadCombo.Append(name, mediaStore, bitmap)
        # select first item
        if  self.mediaUploadCombo.GetCount() > 0:
            if selectedMediaStorageId:
                self._selectMediaSite(selectedMediaStorageId)
            else:
                self.mediaUploadCombo.SetSelection(0)
                self.mediaUploadCombo.validate()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onMediaWizardButton, self.mediaWizardButton)
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onBlogCheckedEvent, self.blogListControl)

    def _layoutWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(self.blogListControl , 1, wx.EXPAND | wx.ALL, 5)

        flexGridSizer = wx.FlexGridSizer(1, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.mediaUploadLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.mediaUploadCombo, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.mediaWizardButton, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.description1, 0, wx.EXPAND | wx.ALL, 10)
        box.Add(self.description2, 0, wx.EXPAND | wx.ALL, 10)
        box.AddSizer(staticBoxSizer, 1, wx.EXPAND| wx.ALL,5)
        box.AddSizer(flexGridSizer, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)

    def getDataProperties(self):
        rval = {}
        return rval
    # end getDataProperties()

    def onMediaWizardButton(self, event): #@UnusedVariable
        storeId = ZMediaStorageUtil().createNewMediaStorage(self)
        if storeId:
            self._populateMediaSitesList(storeId)

    def onEnter(self, session, eventDirection):
        if eventDirection == ZWizardPage.NEXT:
            oldKey = session.getProperty(u"confirm-page.modifykey") #$NON-NLS-1$
            newKey = session.getProperty(u"apiinfo-page.modifykey") #$NON-NLS-1$
            modified = not oldKey or newKey != oldKey
            idBlogList = session.getProperty(u"apiinfo-page.id-bloglist")#$NON-NLS-1$
            if modified and idBlogList:
                self.blogSiteId = session.getProperty(u"apiinfo-page.siteid") #$NON-NLS-1$
                self._populateMediaSitesList()
                session.setProperty(u"confirm-page.modifykey", newKey) #$NON-NLS-1$
                blogs = []
                for (dataId, blog) in idBlogList: #@UnusedVariable
                    blogs.append(blog)
                self.blogListProvider.setBlogList(blogs)
                self.blogListControl.checkBoxListView.refreshItems()
                # pre-select all
                self.blogListControl.checkBoxListView.checkAll()

    def onExit(self, session, eventDirection): #@UnusedVariable
        if eventDirection == ZWizardPage.NEXT:
            blogs = self._getSelectedBlogList()
            session.setProperty(u"confirm-page.selected-blogs", blogs) #$NON-NLS-1$
            obj = self._getSelectedMediaSite()
            uploadmethod = None
            mediastorageid = None
            if obj is not None and isinstance(obj, ZPublisherSiteDef):
                uploadmethod = u"publisher" #$NON-NLS-1$
            elif obj is not None:
                uploadmethod = u"mediastorage" #$NON-NLS-1$
                mediastorageid = obj.getId()
            session.setProperty(u"confirm-page.file-upload-method", uploadmethod) #$NON-NLS-1$
            session.setProperty(u"confirm-page.file-upload-mediastorage-id", mediastorageid) #$NON-NLS-1$
        return True

    def _getSelectedMediaSite(self):
        data = None
        idx = self.mediaUploadCombo.GetSelection()
        if idx != -1:
            data =  self.mediaUploadCombo.GetClientData(idx)
        return data
    # end _getSelectedMediaSite()

    def _selectMediaSite(self, storeId):
        n = self.mediaUploadCombo.GetCount()
        for idx in range(n):
            data = self.mediaUploadCombo.GetClientData(idx)
            if data and data.getId() == storeId:
                self.mediaUploadCombo.SetSelection(idx)
                self.mediaUploadCombo.validate()
                break

    def _getSelectedBlogList(self):
        rval = self.blogListProvider.getSelectedBlogList()
        return rval
    # end _getSelectedBlogList

    def onBlogCheckedEvent(self, event): #@UnusedVariable
        if len( self.blogListControl.checkBoxListView.getCheckedItems() ) > 0:
            self._fireValidEvent()
        else:
            self._fireInvalidEvent()
    # end onBlogCheckedEvent
