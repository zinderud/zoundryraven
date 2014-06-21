from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.subpage import ZAccountPrefsSubPage
import wx


# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for publishing options.
# ------------------------------------------------------------------------------
class ZPublishingPrefSubPage(ZAccountPrefsSubPage):

    def __init__(self, parent, session):
        ZAccountPrefsSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self.overrideCB = wx.CheckBox(self, wx.ID_ANY, self._getOverrideLabel())

        self.panel = ZTransparentPanel(self, wx.ID_ANY)

        self.pubOptionsStaticBox = wx.StaticBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.PublishingOptions")) #$NON-NLS-1$
        self.poweredByCB = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.AddPoweredByZoundry")) #$NON-NLS-1$
        self.removeNewLinesCB = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.RemoveNewLines")) #$NON-NLS-1$

        self.imageUploadStaticBox = wx.StaticBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.ImageUpload")) #$NON-NLS-1$
        self.tnsOnlyCB = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.UploadTNsOnly")) #$NON-NLS-1$
        self.forceUploadCB = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.ReUploadImages")) #$NON-NLS-1$
        self.lightboxCB = wx.CheckBox(self.panel, wx.ID_ANY, _extstr(u"pubsubpage.AddLightbox")) #$NON-NLS-1$
    # end _createWidgets()

    def _getOverrideLabel(self):
        return _extstr(u"pubsubpage.OverridePublishingSettings") #$NON-NLS-1$
    # end _getOverrideLabel()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onOverrideCB, self.overrideCB)

        self.Bind(wx.EVT_CHECKBOX, self.onPoweredByCB, self.poweredByCB)
        self.Bind(wx.EVT_CHECKBOX, self.onRemoveNewLinesCB, self.removeNewLinesCB)
        self.Bind(wx.EVT_CHECKBOX, self.onTnsOnlyCB, self.tnsOnlyCB)
        self.Bind(wx.EVT_CHECKBOX, self.onForceUploadCB, self.forceUploadCB)
        self.Bind(wx.EVT_CHECKBOX, self.onLightboxCB, self.lightboxCB)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        override = self._getSession().isOverridePublishingSettings()
        self.overrideCB.SetValue(override)
        self.panel.Enable(override)

        self.poweredByCB.SetValue(self._getSession().isAddPoweredByZoundry())
        self.removeNewLinesCB.SetValue(self._getSession().isRemoveNewLines())
        self.tnsOnlyCB.SetValue(self._getSession().isUploadThumbnailsOnly())
        self.forceUploadCB.SetValue(self._getSession().isForceReupload())
        self.lightboxCB.SetValue(self._getSession().isAddLightbox())
    # end _populateWidgets()

    def _layoutWidgets(self):
        panelBox = wx.BoxSizer(wx.VERTICAL)

        # pub options
        sbSizer = wx.StaticBoxSizer(self.pubOptionsStaticBox, wx.VERTICAL)
        internalBox = wx.BoxSizer(wx.VERTICAL)
        internalBox.Add(self.poweredByCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.removeNewLinesCB, 0, wx.EXPAND | wx.ALL, 2)
        sbSizer.AddSizer(internalBox, 0, wx.EXPAND | wx.ALL, 8)
        panelBox.Add(sbSizer, 0)

        # image upload
        sbSizer = wx.StaticBoxSizer(self.imageUploadStaticBox, wx.VERTICAL)
        internalBox = wx.BoxSizer(wx.VERTICAL)
        internalBox.Add(self.tnsOnlyCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.forceUploadCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.lightboxCB, 0, wx.EXPAND | wx.ALL, 2)
        sbSizer.AddSizer(internalBox, 0, wx.EXPAND | wx.ALL, 8)
        panelBox.Add(sbSizer, 0, wx.TOP, 8)

        self.panel.SetSizer(panelBox)
        self.panel.SetAutoLayout(True)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.overrideCB, 0, wx.ALL, 5)
        box.Add(self.panel, 0, wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end layoutWidgets()

    def onOverrideCB(self, event):
        override = event.IsChecked()
        self._getSession().setOverridePublishingSettings(override)
        if override:
            self._getSession().setAddPoweredByZoundry(self.poweredByCB.IsChecked())
            self._getSession().setRemoveNewLines(self.removeNewLinesCB.IsChecked())
            self._getSession().setUploadThumbnailsOnly(self.tnsOnlyCB.IsChecked())
            self._getSession().setForceReupload(self.forceUploadCB.IsChecked())
            self._getSession().setAddLightbox(self.lightboxCB.IsChecked())
        self._populateWidgets()
        event.Skip()
    # end onOverrideCB()

    def onPoweredByCB(self, event):
        self._getSession().setAddPoweredByZoundry(event.IsChecked())
        event.Skip()
    # end onPoweredByCB()

    def onRemoveNewLinesCB(self, event):
        self._getSession().setRemoveNewLines(event.IsChecked())
        event.Skip()
    # end onRemoveNewLinesCB()
    
    def onTnsOnlyCB(self, event):
        self._getSession().setUploadThumbnailsOnly(event.IsChecked())
        event.Skip()
    # end onTnsOnlyCB()

    def onForceUploadCB(self, event):
        self._getSession().setForceReupload(event.IsChecked())
        event.Skip()
    # end onForceUploadCB()

    def onLightboxCB(self, event):
        self._getSession().setAddLightbox(event.IsChecked())
        event.Skip()
    # end onLightboxCB()


# end ZPublishingPrefSubPage
