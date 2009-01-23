from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingPasswordCtrl
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNonEmptySelectionValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZUrlSelectionValidator
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.subpage import ZAccountPrefsSubPage
from zoundry.base.util.text.textutil import getSafeString
import wx

# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for categories options.
# ------------------------------------------------------------------------------
class ZAccountSettingsPrefSubPage(ZAccountPrefsSubPage):

    def __init__(self, parent, session):
        ZAccountPrefsSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"settingssubpage.Credentials")) #$NON-NLS-1$
        self.usernameLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"settingssubpage.Username")) #$NON-NLS-1$
        self.username = ZValidatingTextCtrl(ZNonEmptySelectionValidator(_extstr(u"settingssubpage.InvalidUsernameError")), self) #$NON-NLS-1$
        self.passwordLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"settingssubpage.Password")) #$NON-NLS-1$
        self.password = ZValidatingPasswordCtrl(ZNonEmptySelectionValidator(_extstr(u"settingssubpage.InvalidPasswordError")), self) #$NON-NLS-1$

        # FIXME (EPW) add read-only widget for the API type
        self.staticBox2 = wx.StaticBox(self, wx.ID_ANY, _extstr(u"settingssubpage.APIInformation")) #$NON-NLS-1$
        self.endpointLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"settingssubpage.Endpoint")) #$NON-NLS-1$
        self.endpoint = ZValidatingTextCtrl(ZUrlSelectionValidator(_extstr(u"settingssubpage.InvalidEndpointError")), self) #$NON-NLS-1$
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.username)
        self._bindValidatingWidget(self.password)
        self._bindValidatingWidget(self.endpoint)

        self.Bind(wx.EVT_TEXT, self.onUsername, self.username)
        self.Bind(wx.EVT_TEXT, self.onPassword, self.password)
        self.Bind(wx.EVT_TEXT, self.onEndpoint, self.endpoint)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        username = self._getSession().getAccountUsername()
        password = self._getSession().getAccountPassword()
        endpoint = self._getSession().getAccountAPIUrl()
        self.username.SetValue(getSafeString(username))
        self.password.SetValue(getSafeString(password))
        self.endpoint.SetValue(getSafeString(endpoint))
    # end _populateWidgets()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)

        flexGridSizer = wx.FlexGridSizer(2, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        flexGridSizer.Add(self.usernameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.username, 0, wx.EXPAND | wx.ALL, 2)
        flexGridSizer.Add(self.passwordLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.password, 0, wx.EXPAND | wx.ALL, 2)

        # Static box sizer that has a label of "Credentials"
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 5)

        flexGridSizer = wx.FlexGridSizer(1, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.endpointLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        flexGridSizer.Add(self.endpoint, 0, wx.EXPAND | wx.ALL, 2)

        # Static box sizer that has a label of "API Information"
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox2, wx.VERTICAL)
        staticBoxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(staticBoxSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end layoutWidgets()

    def onUsername(self, event):
        self._getSession().setAccountUsername(self.username.GetValue())
        event.Skip()
    # end onUsername()

    def onPassword(self, event):
        self._getSession().setAccountPassword(self.password.GetValue())
        event.Skip()
    # end onPassword()

    def onEndpoint(self, event):
        self._getSession().setAccountAPIUrl(self.endpoint.GetValue())
        event.Skip()
    # end onEndpoint()

# end ZAccountSettingsPrefSubPage
