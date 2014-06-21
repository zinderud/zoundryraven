from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.prefs.appprefsdialog import ZUserPreferencesSession
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------------
# A session used by the blog publishing pref page.
# ------------------------------------------------------------------------------------
class ZBlogPublishingPrefPageSession(ZUserPreferencesSession):

    def __init__(self, prefPage, prefs):
        ZUserPreferencesSession.__init__(self, prefPage, prefs)
    # end __init__()

    def isAddPoweredByZoundry(self):
        return self.prefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY, False)
    # end isAddPoweredByZoundry()

    def setAddPoweredByZoundry(self, bValue):
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY, bValue)
    # end setAddPoweredByZoundry()

    def isRemoveNewLines(self):
        return self.prefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES, False)
    # end isRemoveNewLines()

    def setRemoveNewLines(self, bValue):
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES, bValue)
    # end setRemoveNewLines()
    
    def isUploadThumbnailsOnly(self):
        return self.prefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY, False)
    # end isUploadThumbnailsOnly()

    def setUploadThumbnailsOnly(self, bValue):
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY, bValue)
    # end setUploadThumbnailsOnly()

    def isForceReupload(self):
        return self.prefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD, False)
    # end isForceReupload()

    def setForceReupload(self, bValue):
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD, bValue)
    # end setForceReupload()

    def isAddLightbox(self):
        return self.prefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX, False)
    # end isAddLightbox()

    def setAddLightbox(self, bValue):
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX, bValue)
    # end setAddLightbox()

# end ZBlogPublishingPrefPageSession


# ------------------------------------------------------------------------------------
# A user preference page impl for the Blog Publishing user prefs section.
# ------------------------------------------------------------------------------------
class ZBlogPublishingPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZBlogPublishingPrefPageSession(self, getApplicationModel().getUserProfile().getPreferences())
    # end _createSession()

    def createWidgets(self):
        self.pubOptionsStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.Publishing_Options")) #$NON-NLS-1$
        self.poweredByCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.Add__Powered_By_Zoundry__to_the_post_footer")) #$NON-NLS-1$
        self.removeNewLinesCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.RemoveNewLines")) #$NON-NLS-1$

        self.imageUploadStaticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.Image_Upload")) #$NON-NLS-1$
        self.tnsOnlyCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.Upload_thumbnails_only")) #$NON-NLS-1$
        self.forceUploadCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.Re_Upload_images__even_if_not_dirty_")) #$NON-NLS-1$
        self.lightboxCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"blogpubprefpage.AddLightbox")) #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        self.poweredByCB.SetValue(self._getSession().isAddPoweredByZoundry())
        self.removeNewLinesCB.SetValue(self._getSession().isRemoveNewLines())
        self.tnsOnlyCB.SetValue(self._getSession().isUploadThumbnailsOnly())
        self.forceUploadCB.SetValue(self._getSession().isForceReupload())
        self.lightboxCB.SetValue(self._getSession().isAddLightbox())
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onPoweredByCB, self.poweredByCB)
        self.Bind(wx.EVT_CHECKBOX, self.onRemoveNewLinesCB, self.removeNewLinesCB)
        self.Bind(wx.EVT_CHECKBOX, self.onTnsOnlyCB, self.tnsOnlyCB)
        self.Bind(wx.EVT_CHECKBOX, self.onForceUploadCB, self.forceUploadCB)
        self.Bind(wx.EVT_CHECKBOX, self.onLightboxCB, self.lightboxCB)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)

        # pub options
        sbSizer = wx.StaticBoxSizer(self.pubOptionsStaticBox, wx.VERTICAL)
        internalBox = wx.BoxSizer(wx.VERTICAL)
        internalBox.Add(self.poweredByCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.removeNewLinesCB, 0, wx.EXPAND | wx.ALL, 2)
        sbSizer.AddSizer(internalBox, 0, wx.EXPAND | wx.ALL, 8)
        box.Add(sbSizer, 0, wx.ALL, 5)

        # image upload
        sbSizer = wx.StaticBoxSizer(self.imageUploadStaticBox, wx.VERTICAL)
        internalBox = wx.BoxSizer(wx.VERTICAL)
        internalBox.Add(self.tnsOnlyCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.forceUploadCB, 0, wx.EXPAND | wx.ALL, 2)
        internalBox.Add(self.lightboxCB, 0, wx.EXPAND | wx.ALL, 2)
        sbSizer.AddSizer(internalBox, 0, wx.EXPAND | wx.ALL, 8)
        box.Add(sbSizer, 0, wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end layoutWidgets()

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

# end ZBlogPublishingPreferencePage
