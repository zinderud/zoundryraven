from zoundry.appframework.util.osutilfactory import getOSUtil
from urlparse import urlsplit
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZIntegerSelectionValidator
from zoundry.base.net.http import ZHttpProxyConfiguration
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.appframework.util import crypt
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
import wx
from zoundry.appframework.messages import _extstr

# ------------------------------------------------------------------------------------
# A user preference page impl for the http proxy prefs section.
# ------------------------------------------------------------------------------------
class ZProxyPreferencePage(ZApplicationPreferencesPrefPage):
    
    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"prefpage.general.proxy.name")) #$NON-NLS-1$
        
        self.enableCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"prefpage.general.proxy.enable")) #$NON-NLS-1$
        self.controlsPanel = ZTransparentPanel(self, wx.ID_ANY)
        self.hostLabel = wx.StaticText(self.controlsPanel, wx.ID_ANY, _extstr(u"prefpage.general.proxy.host")) #$NON-NLS-1$
        self.hostTxt = wx.TextCtrl(self.controlsPanel, wx.ID_ANY)
        self.portLabel = wx.StaticText(self.controlsPanel, wx.ID_ANY, _extstr(u"prefpage.general.proxy.port")) #$NON-NLS-1$
        flags = ZIntegerSelectionValidator.ALLOW_EMPTY | ZIntegerSelectionValidator.POSITIVE_ONLY
        self.portTxt = ZValidatingTextCtrl(ZIntegerSelectionValidator(flags=flags), self.controlsPanel, wx.ID_ANY)
        
        self.usernameLabel = wx.StaticText(self.controlsPanel, wx.ID_ANY, _extstr(u"prefpage.general.proxy.username")) #$NON-NLS-1$
        self.usernameTxt = wx.TextCtrl(self.controlsPanel, wx.ID_ANY)
        self.passwordLabel = wx.StaticText(self.controlsPanel, wx.ID_ANY, _extstr(u"prefpage.general.proxy.password")) #$NON-NLS-1$
        self.passwordTxt = wx.TextCtrl(self.controlsPanel, wx.ID_ANY, style=wx.TE_PASSWORD)
    # end createWidgets()

    def populateWidgets(self):
        enable = self.session.getUserPreferenceBool(IZAppUserPrefsKeys.PROXY_ENABLE, False) #$NON-NLS-1$
        self.enableCB.SetValue(enable)
        self.controlsPanel.Enable(enable)
        
        host = self.session.getUserPreference(IZAppUserPrefsKeys.PROXY_HOST, u"") #$NON-NLS-1$
        port = self.session.getUserPreferenceInt(IZAppUserPrefsKeys.PROXY_PORT, 0) #$NON-NLS-1$
        if not host:
            # get data from os registry
            proxy = getOSUtil().getProxyConfig()
            if proxy and proxy.isConfigured():
                host = proxy.getHost()            
                port = proxy.getPortInt()
        self.hostTxt.SetValue(host)        
        if port > 0:
            self.portTxt.SetValue( unicode(port) )
        username = self.session.getUserPreference(IZAppUserPrefsKeys.PROXY_USERNAME, u"") #$NON-NLS-1$
        self.usernameTxt.SetValue(username)

        cyppass = self.session.getUserPreference(IZAppUserPrefsKeys.PROXY_PASSWORD, u"") #$NON-NLS-1$
        cyppass = getNoneString(cyppass)
        if cyppass:
            password = crypt.decryptCipherText(cyppass, PASSWORD_ENCRYPTION_KEY)
            self.passwordTxt.SetValue(password)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onEnableCB, self.enableCB)
        self.Bind(wx.EVT_TEXT, self.onDataChanged, self.hostTxt)
        self.Bind(wx.EVT_TEXT, self.onDataChanged, self.portTxt)
        self.Bind(wx.EVT_TEXT, self.onDataChanged, self.usernameTxt)
        self.Bind(wx.EVT_TEXT, self.onPasswordChanged, self.passwordTxt)
    # end bindWidgetEvents()

    def layoutWidgets(self):        
        flexGridSizer = wx.FlexGridSizer(4, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.hostLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.hostTxt, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.portLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.portTxt, 0, wx.RIGHT, 5)
        flexGridSizer.Add(self.usernameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.usernameTxt, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.passwordLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.passwordTxt, 0, wx.EXPAND | wx.RIGHT, 5)     
        self.controlsPanel.SetAutoLayout(True)
        self.controlsPanel.SetSizer(flexGridSizer)
                 
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.enableCB, 0, wx.EXPAND | wx.ALL, 2)
        staticBoxSizer.Add(self.controlsPanel, 1, wx.EXPAND | wx.ALL, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(staticBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()
    
    def onDataChanged(self, event):
        if self.enableCB.GetValue():
            (h, p) = self._getHostPortFromUI()
            self.session.setUserPreference(IZAppUserPrefsKeys.PROXY_HOST, h)
            self.session.setUserPreference(IZAppUserPrefsKeys.PROXY_PORT, p)
            self.session.setUserPreference(IZAppUserPrefsKeys.PROXY_USERNAME, getSafeString(self.usernameTxt.GetValue()))
            self.onSessionChange()            
        event.Skip()
    # end  onDataChanged
    
    def onPasswordChanged(self, event):
        if self.enableCB.GetValue():
            s = getSafeString(self.passwordTxt.GetValue())
            if s:
                s = crypt.encryptPlainText(s, PASSWORD_ENCRYPTION_KEY)
            self.session.setUserPreference(IZAppUserPrefsKeys.PROXY_PASSWORD, s)            
            self.onSessionChange()            
        event.Skip()
    # end  onPasswordChanged   
           
    def onEnableCB(self, event):
        self.session.setUserPreference(IZAppUserPrefsKeys.PROXY_ENABLE, event.IsChecked())
        self.controlsPanel.Enable(event.IsChecked())
        self.onSessionChange()
        event.Skip()
    # end onDebugCB() 
    
    def _getHostPortFromUI(self):        
        host = getSafeString( self.hostTxt.GetValue() )
        port = getSafeString( self.portTxt.GetValue() )
        if host.lower().startswith(u"http"): #$NON-NLS-1$
            (scheme, netloc, path, query, fragment) = urlsplit(host, u"http") #$NON-NLS-1$ @UnusedVariable
            desHostPort = netloc.split(u":") #$NON-NLS-1$
            h = desHostPort[0]
            p = u"80" #$NON-NLS-1$
            if len(desHostPort) == 2:
                p = desHostPort[1]
            if scheme == u"ssl" and p == u"80": #$NON-NLS-1$ #$NON-NLS-2$
                p = u"443" #$NON-NLS-1$
            if h:
                host = h
            if not port and p:
                port = p
        return (host, port)
    # end _getHostPortFromUI
    
    def apply(self):
        # also set changes to the global value
        (h, p) = self._getHostPortFromUI()
        proxy = ZHttpProxyConfiguration()
        proxy.setEnable( self.enableCB.GetValue() )
        proxy.setHost( h )
        port = 8080
        try:
            port  = int( p )
        except:
            pass
        proxy.setPort( port )
        proxy.setProxyAuthorization( getSafeString(self.usernameTxt.GetValue()), getSafeString(self.passwordTxt.GetValue()) )
        return ZApplicationPreferencesPrefPage.apply(self)
    # end apply()
       
# end ZProxyPreferencePage
