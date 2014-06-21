from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.storesubpage import ZMediaStoragePrefSubPage
import wx


# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for media storage options.
# ------------------------------------------------------------------------------
class ZBlogMediaStoragePrefSubPage(ZMediaStoragePrefSubPage):

    def __init__(self, parent, session):
        ZMediaStoragePrefSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self.overrideCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"storesubpage.OverrideAccountMediaStorageSetting")) #$NON-NLS-1$

        self.panel = ZTransparentPanel(self, wx.ID_ANY)
        self._createStoreWidgets(self.panel)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        ZMediaStoragePrefSubPage._bindWidgetEvents(self)
        self.Bind(wx.EVT_CHECKBOX, self.onOverrideCB, self.overrideCB)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        override = self._getSession().isOverrideMediaStorage()
        self.overrideCB.SetValue(override)
        self.panel.Enable(override)

        ZMediaStoragePrefSubPage._populateWidgets(self)
    # end _populateWidgets()

    def _layoutWidgets(self):
        panelBox = self._createStoreLayout()
        self.panel.SetSizer(panelBox)
        self.panel.SetAutoLayout(True)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.overrideCB, 0, wx.TOP | wx.LEFT, 5)
        box.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end layoutWidgets()

    def onOverrideCB(self, event):
        override = event.IsChecked()
        self.panel.Enable(override)
        self._getSession().setOverrideMediaStorage(override)
        event.Skip()
    # end onOverrideCB()

# end ZBlogMediaStoragePrefSubPage
