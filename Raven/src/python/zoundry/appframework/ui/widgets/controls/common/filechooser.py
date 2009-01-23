from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
import wx

ZFCC_FILE_TYPE = 0
ZFCC_DIRECTORY_TYPE = 1

# -------------------------------------------------------------------------------------
# A simple file chooser control.  This is an aggregate control that combines a text box
# and a "Browse..." button.  The Browse button will pop up a standard file or
# directory chooser.  Note that this control does not validate that the value specified
# is a valid path.
# -------------------------------------------------------------------------------------
class ZFileChooserCtrl(ZTransparentPanel):

    def __init__(self, parent, type, dialogTitle):
        self.type = type
        self.dialogTitle = dialogTitle
        self.defaultDirectory = u"" #$NON-NLS-1$
        self.defaultFile = u"" #$NON-NLS-1$
        self.wildcard = u"*.*" #$NON-NLS-1$
        self.style = wx.OPEN

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def setDefaultDirectory(self, defaultDirectory):
        self.defaultDirectory = defaultDirectory
    # end setDefaultDirectory()

    def setDefaultFile(self, defaultFile):
        self.defaultFile = defaultFile
    # end setDefaultFile()

    def setWildcard(self, wildcard):
        self.wildcard = wildcard
    # end setWildcard()

    def setStyle(self, style):
        self.style = style
    # end setStyle()

    def getPath(self):
        return self.fileText.GetValue()
    # end getPath()

    def setPath(self, path):
        self.fileText.SetValue(path)
    # end setPath()

    def _createWidgets(self):
        self.fileText = wx.TextCtrl(self, wx.ID_ANY)
        self.browseButton = wx.Button(self, wx.ID_ANY, _extstr(u"Browse")) #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.fileText, 1, wx.EXPAND | wx.RIGHT, 5)
        boxSizer.Add(self.browseButton, 0)
        self.SetAutoLayout(True)
        self.SetSizer(boxSizer)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT, self.onText, self.fileText)
        self.Bind(wx.EVT_BUTTON, self.onBrowse, self.browseButton)
    # end _bindWidgetEvents()

    def SetToolTipString(self, tooltip):
        self.fileText.SetToolTipString(tooltip)
    # end SetToolTipString()

    def onText(self, event):
        # Propagate the EVT_TEXT event
        event = event.Clone()
        event.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
        event.Skip()
    # end onText()

    def onBrowse(self, event): #@UnusedVariable
        if self.type == ZFCC_DIRECTORY_TYPE:
            dialog = wx.DirDialog(self, self.dialogTitle, self.defaultDirectory, wx.DD_NEW_DIR_BUTTON)
        elif self.type == ZFCC_FILE_TYPE:
            dialog = wx.FileDialog(self, self.dialogTitle, self.defaultDirectory, self.defaultFile, self.wildcard, self.style)
        rval = dialog.ShowModal()
        if rval == wx.ID_OK:
            self.fileText.SetValue(dialog.GetPath())
        dialog.Destroy()
        event.Skip()
    # end onBrowse()

# end ZFileChooserCtrl
