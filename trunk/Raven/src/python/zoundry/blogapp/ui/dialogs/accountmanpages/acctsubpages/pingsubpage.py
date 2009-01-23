from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.common.pubdatawidgets import ZPingListContentProvider
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.subpage import ZAccountPrefsSubPage
import wx

# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for ping sites options.
# ------------------------------------------------------------------------------
class ZPingSitesPrefSubPage(ZAccountPrefsSubPage):

    def __init__(self, parent, session):
        ZAccountPrefsSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self.overrideCB = wx.CheckBox(self, wx.ID_ANY, self._getOverridePingSitesLabel())
        self.panel = ZTransparentPanel(self, wx.ID_ANY)

        self.staticBox = wx.StaticBox(self.panel, wx.ID_ANY, _extstr(u"pingsubpage.PingSites")) #$NON-NLS-1$
        self.contentProvider = ZPingListContentProvider()
        self.pingSites = ZCheckBoxListViewWithButtons(self.contentProvider, self.panel, wx.ID_ANY)
    # end _createWidgets()

    def _getOverridePingSitesLabel(self):
        return _extstr(u"pingsubpage.OverrideGlobalPingSettings") #$NON-NLS-1$
    # end _getOverridePingSitesLabel()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onOverrideCB, self.overrideCB)
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onCheckListChange, self.pingSites)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        override = self._getSession().isOverridePingSites()
        self.overrideCB.SetValue(override)
        self.panel.Enable(override)
        self.contentProvider.setSelectedPingSites(self._getSession().getSelectedPingSites())
        self.pingSites.refresh()
    # end _populateWidgets()

    def _layoutWidgets(self):
        sbSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sbSizer.Add(self.pingSites, 1, wx.EXPAND | wx.ALL, 8)

        self.panel.SetSizer(sbSizer)
        self.panel.SetAutoLayout(True)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.overrideCB, 0, wx.ALL | wx.EXPAND, 5)
        box.Add(self.panel, 1, wx.ALL | wx.EXPAND, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end layoutWidgets()

    def onOverrideCB(self, event):
        override = event.IsChecked()
        self._getSession().setOverridePingSites(override)
        if override:
            sites = self.contentProvider.getSelectedPingSites()
            self._getSession().setSelectedPingSites(sites)
        self._populateWidgets()
        event.Skip()
    # end onOverrideCB()

    def onCheckListChange(self, event):
        if self.overrideCB.IsChecked():
            sites = self.contentProvider.getSelectedPingSites()
            self._getSession().setSelectedPingSites(sites)
        event.Skip()
    # end onCheckListChange()

# end ZPingSitesPrefSubPage
