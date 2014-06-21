from zoundry.base.css.csscolor import ZCssColor
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.dndsource import IZDnDSource
from zoundry.appframework.services.dnd.handlers.handler import ZBaseFileDnDHandler
from zoundry.appframework.services.imaging.imaging import ZThumbnailParams
from zoundry.base.util.urlutil import encodeUri
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.appframework.services.dnd.handlers.imagehandlerdialog import ZThumbnailImageDialog
import wx

SUPPORTED_TYPES = [
       u"image/jpeg", u"image/png", u"image/gif", u"image/bmp" #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
]


# ------------------------------------------------------------------------------
# Base class for the image file DnD Handlers.
# ------------------------------------------------------------------------------
class ZBaseImageFileDnDHandler(ZBaseFileDnDHandler):

    def __init__(self):
        ZBaseFileDnDHandler.__init__(self)
    # end __init__()

    def _getImagingService(self):
        return getApplicationModel().getService(IZAppServiceIDs.IMAGING_SERVICE_ID)
    # end _getImagingService()

    def _isSupportedImageType(self, fileName):
        mimeType = self._getMimeType(fileName)
        if mimeType is not None:
            type = mimeType.toString()
            return type in SUPPORTED_TYPES
        return False
    # end _isSupportedImageType()

# end ZBaseImageFileDnDHandler


# ------------------------------------------------------------------------------
# A handler that may get used when the user is dropping an image file.
# ------------------------------------------------------------------------------
class ZImageFileDnDHandler(ZBaseImageFileDnDHandler):

    def __init__(self):
        ZBaseImageFileDnDHandler.__init__(self)
    # end __init__()

    def getName(self):
        return _extstr(u"imagehandler.ImageFile") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"imagehandler.ImageFileDesc") #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        if not dndSource.hasType(IZDnDSource.TYPE_FILE):
            return False

        fileSource = dndSource.getSource(IZDnDSource.TYPE_FILE)
        fileName = fileSource.getData()
        return self._isSupportedImageType(fileName)
    # end canHandle()

    def handle(self, dndSource, dndContext):
        fileSource = self._getSource(dndSource)
        dialog = ZThumbnailImageDialog(dndContext.getWindow())
        rval = dialog.ShowModal()
        if rval == wx.ID_OK:
            model = dialog.getModel()
            if model.generateTNFlag:
                return self._handleWithThumbnail(fileSource, model)
            else:
                return self._handleNoThumbnail(fileSource)
        return None
    # end handle()

    def _getSource(self, dndSource):
        return dndSource.getSource(IZDnDSource.TYPE_FILE)
    # end _getSource()

    def _handleWithThumbnail(self, dndSource, model):
        srcFile = dndSource.getData()
        html = u"<html><body><p>" + self._createWithThumbnailHtmlFragString(srcFile, model) + u"</p></body></html>" #$NON-NLS-1$ #$NON-NLS-2$
        return loadXhtmlDocumentFromString(html)
    # end _handleWithThumbnail()

    def _handleNoThumbnail(self, dndSource):
        srcFile = dndSource.getData()
        html = self._createNoThumbnailHtmlFragString(srcFile)
        return loadXhtmlDocumentFromString(html)
    # end _handleNoThumbnail()

    def _createWithThumbnailHtmlFragString(self, srcFile, model):
        (url, shortName, absPath, size, schemaDate) = self._getFileMetaData(srcFile) #@UnusedVariable
        size = model.size
        tnParams = ZThumbnailParams(size, size)
        (tn_name, tn_width, tn_height) = self._getImagingService().generateThumbnail(srcFile, tnParams)
        srcFile = encodeUri(srcFile)
        tn_name = encodeUri(tn_name)
        style = self._createCSSStyle(model)
        html = u'<a xmlns:z="urn:zoundry:xhtml:ext,2007,08" z:rel="tn" href="%s" title="%s"><img xmlns:z="urn:zoundry:xhtml:ext,2007,08" z:rel="tn" border="0" src="%s" width="%d" height="%d" style="%s" alt="%s"/></a>' % (srcFile, shortName, tn_name, tn_width, tn_height, style, shortName) #$NON-NLS-1$
        return html
    # end _createWithThumbnailHtmlFragString()

    def _createCSSStyle(self, model):
        # Note: model is instanceof ZThumbnailImageDialogModel
        css = u"" #$NON-NLS-1$
        if model.alignment:
            if model.alignment == u"left" or model.alignment == u"right":  #$NON-NLS-1$  #$NON-NLS-2$
                css = u"display:inline; float:%s; " % model.alignment #$NON-NLS-1$
            elif model.alignment == u"center":  #$NON-NLS-1$
                css = u"display:block; text-align:center; margin-left:auto; margin-right:auto; " #$NON-NLS-1$
        else:
            css = u"display:inline; " #$NON-NLS-1$
        if model.borderStyle:
            (r,g,b) = (0,0,0)
            if model.borderColor:
                (r,g,b) = model.borderColor
            if not model.borderWidth:
                model.borderWidth = u"1" #$NON-NLS-1$
            cssColor = ZCssColor(red=r, blue=b, green=g)
            css = css +  u"border:%spx %s %s; " % (model.borderWidth, model.borderStyle, cssColor.getCssColor()) #$NON-NLS-1$
        if model.marginTop:
            css = css + u"margin-top:%spx; " % model.marginTop #$NON-NLS-1$
        if model.marginRight:
            css = css + u"margin-right:%spx; " % model.marginRight #$NON-NLS-1$
        if model.marginBottom:
            css = css + u"margin-bottom:%spx; " % model.marginBottom #$NON-NLS-1$
        if model.marginLeft:
            css = css + u"margin-left:%spx; " % model.marginLeft #$NON-NLS-1$
        return css.strip()
    # end _createCSSStyle()

    def _createNoThumbnailHtmlFragString(self, srcFile):
        (url, shortName, absPath, size, schemaDate) = self._getFileMetaData(srcFile) #@UnusedVariable
        srcFile = encodeUri(srcFile)
        html = u'<img xmlns:z="urn:zoundry:xhtml:ext,2007,08" z:rel="tn" src="%s" alt="%s"/>' % (srcFile, shortName) #$NON-NLS-1$
        return html
    # end _createNoThumbnailHtmlFragString()

# end ZImageFileDnDHandler


# ------------------------------------------------------------------------------
# A handler that may get used when the user is dropping multiple image files.
# ------------------------------------------------------------------------------
class ZMultiImageFileDnDHandler(ZImageFileDnDHandler):

    def __init__(self):
        ZImageFileDnDHandler.__init__(self)
    # end __init__()

    def getName(self):
        return _extstr(u"imagehandler.MultipleImageFiles") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"imagehandler.MultipleImageFilesDesc") #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        if not dndSource.hasType(IZDnDSource.TYPE_MULTI_FILE):
            return False

        multiFileSource = dndSource.getSource(IZDnDSource.TYPE_MULTI_FILE)
        fileNames = multiFileSource.getData()
        for fileName in fileNames:
            if not self._isSupportedImageType(fileName):
                return False
        return True
    # end canHandle()

    def _getSource(self, dndSource):
        return dndSource.getSource(IZDnDSource.TYPE_MULTI_FILE)
    # end _getSource()

    def _handleWithThumbnail(self, dndSource, model):
        html = u"<p>"; #$NON-NLS-1$
        fileNames = dndSource.getData()
        for fileName in fileNames:
            frag = self._createWithThumbnailHtmlFragString(fileName, model)
            html = html + frag + u"<br/>" #$NON-NLS-1$
        html = html + u"</p>" #$NON-NLS-1$
        return loadXhtmlDocumentFromString(html)
    # end _handleWithThumbnail()

    def _handleNoThumbnail(self, dndSource):
        html = u"<p>"; #$NON-NLS-1$
        fileNames = dndSource.getData()
        for fileName in fileNames:
            frag = self._createNoThumbnailHtmlFragString(fileName)
            html = html + frag + u"<br/>" #$NON-NLS-1$
        html = html + u"</p>" #$NON-NLS-1$
        return loadXhtmlDocumentFromString(html)
    # end _handleNoThumbnail()

# end ZMultiImageFileDnDHandler
