from zoundry.base.util.fileutil import generateFilename
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.util.text.unicodeutil import convertToUnicode
import os
import wx

#--------------------------------------------------------
# Clipboard related utils.
#--------------------------------------------------------

def getUrlFromClipboard():
    u"""Returns the url found in the clipboard or None if not found. """#$NON-NLS-1$
    url =  None
    try :
        urlData = wx.URLDataObject();
        wx.TheClipboard.Open()
        success = wx.TheClipboard.GetData(urlData)
        wx.TheClipboard.Close()
        if success:
            s = urlData.GetURL()
            if s:
                s = s.strip()
                temp = s.lower()
                # FIXME (PJ) use reg-ex.
                if temp and ( temp.startswith(u"http://") or temp.startswith(u"https://") ): #$NON-NLS-1$ #$NON-NLS-2$
                    url = s
                # if temp
            #if s
        # if success
    except:
        pass
    return url
# getUrlFromClipboard()

def getTextFromClipboard():
    u"""Returns clipboard text if available or None otherwise.""" #$NON-NLS-1$
    text = None
    try:
        data = wx.TextDataObject()
        wx.TheClipboard.Open()
        ok = wx.TheClipboard.GetData(data)
        wx.TheClipboard.Close()
        if ok:
            text = data.GetText()
            if text:
                text = convertToUnicode(text)
    except:
        pass
    return text
# end getTextFromClipboard()

def setClipboardText(text = None):
    u"""Sets clipboard text if available.""" #$NON-NLS-1$
    if not text or text == u"": #$NON-NLS-1$
        return
    try:
        data = wx.TextDataObject()
        data.SetText(text)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(data)
        wx.TheClipboard.Close()
    except:
        pass
# setClipboardText()

def hasClipboardBitmap():
    u"""Returns true if clipboard has bitmap .""" #$NON-NLS-1$
    ok = False
    try:
        wx.TheClipboard.Open()
        ok = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)) or wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_DIB))
        wx.TheClipboard.Close()
    except:
        pass
    return ok
# end hasClipboardBitmap()

def getBitmapFromClipboard():
    u"""Returns clipboard bitmap if available or None otherwise.""" #$NON-NLS-1$
    bmp = None
    try:
        wx.TheClipboard.Open()
        ok = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)) or wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_DIB))
        if ok:
            bmpdata= wx.BitmapDataObject()
            if wx.TheClipboard.GetData(bmpdata):
                bmp = bmpdata.GetBitmap()
        wx.TheClipboard.Close()
    except Exception, e:
        getLoggerService().exception(e)
    return bmp
# end getTextFromClipboard()

def getPngFileFromClipboard(copyToResourceStore=False):
    u"""Returns the (temp) file path to png file representing the clipboard bitmap or None otherwise.
    If copyToResourceStore = true, then the tmp image file is copied to the resource store.
    """ #$NON-NLS-1$
    filepath = None
    bmp = getBitmapFromClipboard()
    if bmp:
        try:
            osutil = getOSUtil()
            tempDir = osutil.getSystemTempDirectory()
            name = generateFilename(u"zrclip", u".png") #$NON-NLS-1$ #$NON-NLS-2$
            filepath = os.path.abspath( os.path.join(tempDir, name) )
            bmp.SaveFile(filepath, wx.BITMAP_TYPE_PNG)
        except Exception, e:
            filepath = None
            getLoggerService().exception(e)
    if filepath and copyToResourceStore:
        try:
            # get resource store and add to it.
            resStore = getApplicationModel().getEngine().getService(IZAppServiceIDs.RESOURCE_STORE_SERVICE_ID)
            resEntry = resStore.addResource(filepath)
            if resEntry:
                # temp file was added to resource store, so, use the resource store path instead of temp file path.
                filepath = resEntry.getFilePath()
        except Exception, e:
            getLoggerService().exception(e)
    return filepath
# end getPngFileFromClipboard()