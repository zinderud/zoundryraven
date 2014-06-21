from zoundry.blogapp.messages import _extstr
from zoundry.base.exceptions import ZException
from zoundry.base.net.contrib import urllib2_file #@UnusedImport
from zoundry.blogapp.services.mediastorage.mediastorageprovider import ZStreamBasedMediaStorageProvider
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
from zoundry.blogapp.ui.wizards.mediastoragewizard import ZNewMediaStorageWizardPage
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.dialogs.wizard import ZWizardPage
import wx
import os
import flickrapi

# To manage API keys, log in to Flickr as:
#  Username:  zoundry@yahoo.com
#  Password:  <kattare zoundry pwd>
FLICKR_API_KEY = u"8d9f5174f8e3c2f2ebf853e0d2d181b3" #$NON-NLS-1$
SECRET = u"bdeb67c4a9d04ae6" #$NON-NLS-1$
#TOKEN = u"72157604901646775-549ee853764ce52c" #$NON-NLS-1$

FLICKR_URL_FORMAT = u"http://farm%(farm-id)s.static.flickr.com/%(server-id)s/%(id)s_%(secret)s.jpg" #$NON-NLS-1$
FLICKR_URL_OFORMAT = u"http://farm%(farm-id)s.static.flickr.com/%(server-id)s/%(id)s_%(o-secret)s_o.%(o-format)s" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Behaves like the flickrapi module's TokenCache, but pulls/stores the info
# in the user's preferences.
# ------------------------------------------------------------------------------
class ZFlickrTokenCache(object):

    def __init__(self, properties):
        self.properties = properties
    # end __init__()

    def __get_cached_token(self):
        return self.properties[u"token"] #$NON-NLS-1$
    # end __get_cached_token()

    def __set_cached_token(self, token):
        self.properties[u"token"] = token #$NON-NLS-1$
    # end __set_cached_token()

    def forget(self):
        pass
    # end forget()

    token = property(__get_cached_token, __set_cached_token, forget, u"The cached token") #$NON-NLS-1$

# end ZFlickrTokenCache()


# ------------------------------------------------------------------------------
# An Flickr implementation of a media storage provider.
# ------------------------------------------------------------------------------
class ZFlickrMediaStorageProvider(ZStreamBasedMediaStorageProvider):

    def __init__(self, properties):
        ZStreamBasedMediaStorageProvider.__init__(self, properties)
    # end __init__()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        shortName = os.path.basename(fileName)
        flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, SECRET)
        flickr.token_cache = ZFlickrTokenCache(self.properties)
        tags = self._getTags()
        hidden = self._getHidden()
        uploadResult = flickr.upload(fileStream, title = shortName, tags = tags, hidden = hidden)
        photoIds = uploadResult.photoid
        photoId = photoIds[0].text
        photoInfo = flickr.photos_getInfo(photo_id = photoId)
        photo = photoInfo.photo[0]
        if u"originalsecret" in photo: #$NON-NLS-1$
            imageUrl = self._createOriginalUrl(photo)
        else:
            imageUrl = self._createUrl(photo)
        return ZUploadResponse(imageUrl)
    # end upload()

    def _createOriginalUrl(self, photo):
        args = {
            u"farm-id": photo[u"farm"], #$NON-NLS-2$ #$NON-NLS-1$
            u"server-id": photo[u"server"], #$NON-NLS-2$ #$NON-NLS-1$
            u"id": photo[u"id"], #$NON-NLS-2$ #$NON-NLS-1$
            u"o-secret": photo[u"originalsecret"], #$NON-NLS-2$ #$NON-NLS-1$
            u"o-format": photo[u"originalformat"] #$NON-NLS-2$ #$NON-NLS-1$
        }
        imageUrl = FLICKR_URL_OFORMAT % args
        return imageUrl
    # end _createOriginalUrl()

    def _createUrl(self, photo):
        args = {
            u"farm-id": photo[u"farm"], #$NON-NLS-2$ #$NON-NLS-1$
            u"server-id": photo[u"server"],  #$NON-NLS-2$ #$NON-NLS-1$
            u"id": photo[u"id"],  #$NON-NLS-2$ #$NON-NLS-1$
            u"secret": photo[u"secret"] #$NON-NLS-2$ #$NON-NLS-1$
        }
        imageUrl = FLICKR_URL_FORMAT % args
        return imageUrl
    # end _createUrl()

    def deleteFile(self, fileName, metaData): #@UnusedVariable
        raise ZException(u"Method deleteFile not supported") #$NON-NLS-1$
    # end deleteFile()

    def listFiles(self, relativePath = None): #$NON-NLS-2$ #$NON-NLS-1$
        raise ZException(u"Method listFiles not supported") #$NON-NLS-1$
    # end listFiles()

    def _getFileList(self, ftp):
        raise ZException(u"Method _getFileList not supported") #$NON-NLS-1$
    # end getFileList()

    def _getTags(self):
        if u"tags" in self.properties: #$NON-NLS-1$
            return self.properties[u"tags"] #$NON-NLS-1$
        return u"" #$NON-NLS-1$
    # end _getTags()

    def _getHidden(self):
        if u"hidden" in self.properties: #$NON-NLS-1$
            isHidden = self.properties[u"hidden"] #$NON-NLS-1$
            if isHidden:
                return u"1" #$NON-NLS-1$
        return u"0" #$NON-NLS-1$
    # end _getHidden()

# end ZFlickrMediaStorageProvider


# ------------------------------------------------------------------------------
# A custom wizard page to handle flickr authorization.
# ------------------------------------------------------------------------------
class ZFlickrAuthorizationWizardPage(ZNewMediaStorageWizardPage):

    def __init__(self, model, parent):
        ZNewMediaStorageWizardPage.__init__(self, model, parent)
        self.flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, SECRET)
        self.frob = None
        self.token = None
        self.authorized = False
    # end __init__()

    def _createWidgets(self):
        self.descriptionLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"flickrprovider.FlickrAuthDescription")) #$NON-NLS-1$
        self.stepOneLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"flickrprovider.BeginAuthLabel")) #$NON-NLS-1$
        self.stepOneButton = wx.Button(self, wx.ID_ANY, _extstr(u"flickrprovider.Begin")) #$NON-NLS-1$
        self.stepTwoLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"flickrprovider.ClickHereLabel")) #$NON-NLS-1$
        self.stepTwoButton = wx.Button(self, wx.ID_ANY, _extstr(u"flickrprovider.Authorized")) #$NON-NLS-1$

        self.resultLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"flickrprovider.NotYetAuthorized")) #$NON-NLS-1$
        self.completeBitmap = getResourceRegistry().getBitmap(u"images/common/check.png") #$NON-NLS-1$
        self.completeImage = ZStaticBitmap(self, self.completeBitmap)
        self.warningBitmap = getResourceRegistry().getBitmap(u"images/common/warning.png") #$NON-NLS-1$
        self.warningImage = ZStaticBitmap(self, self.warningBitmap)
    # end _createWidgets()

    def _populateWidgets(self):
        self.stepOneButton.Enable(True)
        self.stepTwoButton.Enable(False)
        self.warningImage.Show(True)
        self.completeImage.Show(False)
        self._fireInvalidEvent()
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onStepOneButton, self.stepOneButton)
        self.Bind(wx.EVT_BUTTON, self.onStepTwoButton, self.stepTwoButton)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(2, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.stepOneLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.stepOneButton, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.stepTwoLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.stepTwoButton, 0, wx.EXPAND | wx.RIGHT, 5)

        resultSizer = wx.BoxSizer(wx.HORIZONTAL)
        resultSizer.Add(self.warningImage, 0, wx.EXPAND | wx.ALL, 2)
        resultSizer.Add(self.completeImage, 0, wx.EXPAND | wx.ALL, 2)
        resultSizer.Add(self.resultLabel, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.descriptionLabel, 1, wx.EXPAND | wx.ALL, 10)
        box.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)
        box.AddSizer(resultSizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def onStepOneButton(self, event):
        bc = wx.BusyCursor()
        try:
            flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, SECRET)
            (token, frob) = flickr.get_token_part_one(perms=u"delete") #$NON-NLS-1$
            self.token = token
            self.frob = frob
            if token:
                self._onAuthorized()
            else:
                self.stepOneButton.Enable(False)
                self.stepTwoButton.Enable(True)
        finally:
            del bc
        event.Skip()
    # end onStepOneButton()

    def onStepTwoButton(self, event):
        token = None
        try:
            token = self.flickr.get_token_part_two( (None, self.frob) )
        except:
            pass
        if token:
            self.token = token
            self._onAuthorized()
        else:
            self.resultLabel.SetLabel(_extstr(u"flickrprovider.StillNotAuthorized")) #$NON-NLS-1$
            self._populateWidgets()
        event.Skip()
    # end onStepTwoButton()

    def onEnter(self, session, eventDirection): #@UnusedVariable
        self.paramsPageProps = session.getProperty(u"params-page.properties") #$NON-NLS-1$
        if not self.authorized:
            self._fireInvalidEvent()
    # end onEnter()

    def onExit(self, session, eventDirection): #@UnusedVariable
        if eventDirection == ZWizardPage.NEXT:
            params = session.getProperty(u"params-page.properties") #$NON-NLS-1$
            params[u"token"] = self.token #$NON-NLS-1$
        return True
    # end onExit()

    def _onAuthorized(self):
        self.resultLabel.SetLabel(_extstr(u"flickrprovider.RavenIsAuthorized")) #$NON-NLS-1$
        self.warningImage.Show(False)
        self.completeImage.Show(True)
        self.Layout()
        self.stepOneButton.Enable(False)
        self.stepTwoButton.Enable(False)
        self._fireValidEvent()
    # end _onAuthorized()

    def getDataProperties(self):
        rval = {}
        if self.token:
            self.paramsPageProps[u"token"] = self.token #$NON-NLS-1$
            rval[u"params-page.properties"] = self.paramsPageProps #$NON-NLS-1$
        return rval
    # end getDataProperties()

# end ZNewMediaStorageWizardParamsPage

