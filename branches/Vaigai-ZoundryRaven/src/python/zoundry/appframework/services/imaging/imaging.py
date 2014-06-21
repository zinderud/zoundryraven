from zoundry.base.util.fileutil import generateFilename
from PIL import Image
from PIL import ImageFilter
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
import os

# ----------------------------------------------------------------------------------------
# Set of parameters to use when the imaging service generates a thumbnail.
# ----------------------------------------------------------------------------------------
class ZThumbnailParams:

    def __init__(self, width = 200, height = 200, borderWidth = 0, borderColor = None, backgroundColor = None, dropShadow = False):
        self.width = width
        self.height = height
        self.borderWidth = borderWidth
        self.borderColor = borderColor
        self.backgroundColor = backgroundColor
        self.dropShadow = dropShadow

        if self.borderColor is None:
            self.borderColor = (0, 0, 0)
        if self.backgroundColor is None:
            self.backgroundColor = (255, 255, 255)
    # end __init__()

    def setWidth(self, width):
        self.width = width
    # end setWidth()

    def setHeight(self, height):
        self.height = height
    # end setHeight()

    def setBorderWidth(self, borderWidth):
        self.borderWidth = borderWidth
    # end setBorderWidth()

    def setBorderColor(self, red, green, blue):
        self.borderColor = (red, green, blue)
    # end setBorderColor()

    def setBackgroundColor(self, red, green, blue):
        self.backgroundColor = (red, green, blue)
    # end setBackgroundColor()

    def setDropShadow(self, dropShadow):
        self.dropShadow = dropShadow
    # end setDropShadow()

# end ZThumbnailParams


# ----------------------------------------------------------------------------------------
# The interface to the imaging service.
# ----------------------------------------------------------------------------------------
class IZImagingService(IZService):

    def generateThumbnail(self, sourceFile, tnParams, destFile = None):
        u"""generateThumbnail(string, ZThumbnailParams, string?) -> (string, int, int)
        Generates a thumbnail for the given image file.
        sourceFile: file path to the source image file
        params: options that the thumbnail service will use (width, height, etc).
        destFile: (optional) where to copy the thumbnail file
        Return Value: a tuple:  (tn_name, tn_width, tn_height)""" #$NON-NLS-1$
    # end generateThumbnail()

    def getImageSize(self, imageFile):
        u"""getImageSize(string) -> (int, int)
        Returns image size as a tuple (width, height) or (-1, -1) if not available.
        """ #$NON-NLS-1$
    # end getImageSize()

    # FIXME (EPW) add some or all of the following to the imaging interface:
    #  - createDropShadow()
    #  - rotateImage()
    #  - lightenImage()
    #  - darkenImage()
    #  - scaleImage()
    #  - addImageBorder()

# end IZImagingService()


# ----------------------------------------------------------------------------------------
# The implementation of the imaging service.
#
# FIXME (EPW) create a unit test for this service
# ----------------------------------------------------------------------------------------
class ZImagingService(IZImagingService):

    def __init__(self):
        self.logger = None
        self.thumbnailDir = None
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"Imaging Service started.") #$NON-NLS-1$

        self.thumbnailDir = self.applicationModel.getUserProfile().getDirectory(u"thumbnails") #$NON-NLS-1$
    # end start()

    def stop(self):
        pass
    # end stop()

    def generateThumbnail(self, sourceFile, tnParams, destFile = None):
        if destFile is None:
            destFile = self._createDestFile()
        if os.path.exists(destFile):
            os.remove(destFile)
        if not os.path.isfile(sourceFile):
            raise ZAppFrameworkException(_extstr(u"imaging.PathDoesNotExistError") % sourceFile) #$NON-NLS-1$

        width = tnParams.width
        height = tnParams.height

        inputFilePath = sourceFile
        outputFilePath = destFile
        try:
            image = Image.open(inputFilePath)
            image = image.convert(u"RGB") #$NON-NLS-1$
            image.thumbnail((width, height), Image.ANTIALIAS)
            if tnParams.dropShadow:
                bgcolor = (tnParams.backgroundColor[2] << 16) + (tnParams.backgroundColor[1] << 8) + tnParams.backgroundColor[0]
                image = self._addDropShadow(image, background = bgcolor)
            image.save(outputFilePath)
            (rWidth, rHeight) = image.size
            return (outputFilePath, rWidth, rHeight)
        except Exception, e:
            raise ZAppFrameworkException(_extstr(u"imaging.ErrorCreatingThumbnailError") % sourceFile, e) #$NON-NLS-1$
    # end generateThumbnail()

    def getImageSize(self, imageFile):
        width = -1
        height = -1
        if imageFile and os.path.isfile(imageFile):
            try:
                image = Image.open(imageFile)
                (width, height) = image.size
            except:
                pass
        return (width, height)
    # end getImageSize()

    def _createDestFile(self):
        name = generateFilename(u"zrtn", u"_tn.jpg") #$NON-NLS-1$ #$NON-NLS-2$
        return os.path.join(self.thumbnailDir, name) #$NON-NLS-1$
    # end _createDestFile()

    def _addDropShadow(self, image, offset=(5,5), background=0xffffff, shadow=0x444444, border=8, iterations=3):
        u"""
          Add a gaussian blur drop shadow to an image.

          image       - The image to overlay on top of the shadow.
          offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                        positive or negative.
          background  - Background colour behind the image.
          shadow      - Shadow colour (darkness).
          border      - Width of the border around the image.  This must be wide
                        enough to account for the blurring of the shadow.
          iterations  - Number of times to apply the filter.  More iterations
                        produce a more blurred shadow, but increase processing time.
        """ #$NON-NLS-1$

        # Create the backdrop image -- a box in the background colour with a #$NON-NLS-1$
        # shadow on it.
        totalWidth = image.size[0] + abs(offset[0]) + 2*border
        totalHeight = image.size[1] + abs(offset[1]) + 2*border
        back = Image.new(image.mode, (totalWidth, totalHeight), background)

        # Place the shadow, taking into account the offset from the image
        shadowLeft = border + max(offset[0], 0)
        shadowTop = border + max(offset[1], 0)
        back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0],
                            shadowTop + image.size[1]] )

        # Apply the filter to blur the edges of the shadow.  Since a small kernel
        # is used, the filter must be applied repeatedly to get a decent blur.
        n = 0
        while n < iterations:
            back = back.filter(ImageFilter.BLUR)
            n += 1

        # Paste the input image onto the shadow backdrop
        imageLeft = border - min(offset[0], 0)
        imageTop = border - min(offset[1], 0)
        back.paste(image, (imageLeft, imageTop))

        return back
    # end _addDropShadow()


# end ZImagingService
