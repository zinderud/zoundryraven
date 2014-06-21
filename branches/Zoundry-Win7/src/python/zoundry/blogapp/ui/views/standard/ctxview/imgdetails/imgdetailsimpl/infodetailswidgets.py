from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.resources.registry import getImageType
from zoundry.appframework.services.imaging.imaging import ZThumbnailParams
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.base.exceptions import ZException
from zoundry.base.util.fileutil import deleteFile
from zoundry.blogapp.messages import _extstr
from zoundry.appframework.ui.widgets.controls.progress import ZProgressLabelCtrl
import PIL
import os
import wx

# ----------------------------------------------------------------------------------------
# A widget that displays a preview of the image.
# ----------------------------------------------------------------------------------------
class ZImagePreviewPanel(ZTransparentPanel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
    # end __init__()

    def _createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"infodetailswidgets.Preview")) #$NON-NLS-1$

        self.generatingMsg = ZProgressLabelCtrl(self, _extstr(u"infodetailswidgets.GeneratingPreview")) #$NON-NLS-1$
        self.previewUnavailableMsg = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.PreviewUnavailable")) #$NON-NLS-1$
        self.previewBmp = ZStaticBitmap(self, None)
    # end _createWidgets()

    def _layoutWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.HORIZONTAL)
        staticBoxSizer.Add(self.generatingMsg, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        staticBoxSizer.Add(self.previewUnavailableMsg, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        staticBoxSizer.Add(self.previewBmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)

        self.SetAutoLayout(True)
        self.SetSizer(staticBoxSizer)
    # end _layoutWidgets()

    def reset(self):
        self.generatingMsg.Show(True)
        self.generatingMsg.start()
        self.previewUnavailableMsg.Show(False)
        self.previewBmp.Show(False)
    # end reset()

    def updateFromError(self, error):
        # Log the error
        getLoggerService().exception(error)
        self.generatingMsg.Show(False)
        self.generatingMsg.stop()
        self.previewUnavailableMsg.Show(True)
        self.previewBmp.Show(False)
    # end updateFromError()

    def updateFromConnectionRespInfo(self, connectionRespInfo): #@UnusedVariable
        # Do nothing...
        pass
    # end updateFromConnectionRespInfo()

    def updateFromConnectionResp(self, connectionResp):
        imagingService = getApplicationModel().getService(IZAppServiceIDs.IMAGING_SERVICE_ID)
        bgColor = self.GetBackgroundColour()
        tnParams = ZThumbnailParams(backgroundColor = (bgColor.Red(), bgColor.Green(), bgColor.Blue()), dropShadow = True)
        tnFile = os.path.join(getApplicationModel().getUserProfile().getTempDirectory(), u"_ZImagePreviewPanel_tn.png") #$NON-NLS-1$
        try:
            imagingService.generateThumbnail(connectionResp.getContentFilename(), tnParams, tnFile)

            image = wx.Image(tnFile, getImageType(tnFile))
            if image is None:
                raise ZException()

            bitmap = image.ConvertToBitmap()
            self.previewBmp.setBitmap(bitmap)
            deleteFile(tnFile)
            self.generatingMsg.Show(False)
            self.generatingMsg.stop()
            self.previewUnavailableMsg.Show(False)
            self.previewBmp.Show(True)
        except Exception, e:
            getLoggerService().exception(e)
            self.updateFromError(e)
    # end updateFromConnectionResp()

# end ZImagePreviewPanel


# ----------------------------------------------------------------------------------------
# A widget that displays summary information about an image.
# ----------------------------------------------------------------------------------------
class ZImageSummaryPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
    # end __init__()

    def _createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"infodetailswidgets.Summary")) #$NON-NLS-1$

        boldFont = getDefaultFontBold()

        self.fileSizeLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.FileSize")) #$NON-NLS-1$
        self.fileSizeLabel.SetFont(boldFont)
        self.fileSize = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.imageWidthLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.ImageWidth")) #$NON-NLS-1$
        self.imageWidthLabel.SetFont(boldFont)
        self.imageWidth = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.imageHeightLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.ImageHeight")) #$NON-NLS-1$
        self.imageHeightLabel.SetFont(boldFont)
        self.imageHeight = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.imageTypeLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.ImageType")) #$NON-NLS-1$
        self.imageTypeLabel.SetFont(boldFont)
        self.imageType = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(4, 2, 2, 2)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.fileSizeLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.fileSize, 1, wx.EXPAND)
        flexGridSizer.Add(self.imageWidthLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.imageWidth, 1, wx.EXPAND)
        flexGridSizer.Add(self.imageHeightLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.imageHeight, 1, wx.EXPAND)
        flexGridSizer.Add(self.imageTypeLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.imageType, 1, wx.EXPAND)

        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(staticBoxSizer)
    # end _layoutWidgets()

    def reset(self):
        self.fileSize.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
        self.imageWidth.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
        self.imageHeight.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
        self.imageType.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
    # end reset()

    def updateFromError(self, error):
        # Log the error
        getLoggerService().exception(error)
        self.fileSize.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.imageWidth.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.imageHeight.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.imageType.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.Layout()
    # end updateFromError()

    def updateFromConnectionRespInfo(self, connectionRespInfo):
        # FIXME (EPW) pretty-format the file size (KB, MB, etc)
        if connectionRespInfo is not None and connectionRespInfo.getContentLength() is not None:
            try:
                self.fileSize.SetLabel(u"%d bytes" % connectionRespInfo.getContentLength()) #$NON-NLS-1$
                self.imageType.SetLabel(connectionRespInfo.getContentType())
            except Exception, e:
                getLoggerService().exception(e)
                getLoggerService().warning(u"Content length was of type '%s'." % unicode(type(connectionRespInfo.getContentLength()))) #$NON-NLS-1$
        self.Layout()
    # end updateFromConnectionRespInfo()

    def updateFromConnectionResp(self, connectionResp):
        filename = connectionResp.getContentFilename()
        try:
            # FIXME (EPW) Move this to a "get meta data" method on the IZImagingService interface
            image = PIL.Image.open(filename)
            (w, h) = image.size
            self.imageWidth.SetLabel(u"%d pixels" % w) #$NON-NLS-1$
            self.imageHeight.SetLabel(u"%d pixels" % h) #$NON-NLS-1$
            self.Layout()
        except Exception, e:
            self.updateFromError(e)
    # end updateFromConnectionResp()

# end ZImageSummaryPanel
