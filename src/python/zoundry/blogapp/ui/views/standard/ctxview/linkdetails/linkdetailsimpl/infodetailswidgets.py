from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.blogapp.messages import _extstr
import wx


# ----------------------------------------------------------------------------------------
# A widget that displays summary information about an link.
# ----------------------------------------------------------------------------------------
class ZLinkSummaryPanel(wx.Panel):
    
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
        self.linkTypeLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"infodetailswidgets.LinkType")) #$NON-NLS-1$
        self.linkTypeLabel.SetFont(boldFont)
        self.linkType = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
    # end _createWidgets()
    
    def _layoutWidgets(self):
        flexGridSizer = wx.FlexGridSizer(4, 2, 2, 2)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.Add(self.fileSizeLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.fileSize, 1, wx.EXPAND)
        flexGridSizer.Add(self.linkTypeLabel, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.linkType, 1, wx.EXPAND)

        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(flexGridSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(staticBoxSizer)
    # end _layoutWidgets()
    
    def reset(self):
        self.fileSize.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
        self.linkType.SetLabel(_extstr(u"infodetailswidgets.Retrieving")) #$NON-NLS-1$
    # end reset()

    def updateFromError(self, error):
        # Log the error
        getLoggerService().exception(error)
        self.fileSize.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.linkType.SetLabel(_extstr(u"infodetailswidgets.Unavailable")) #$NON-NLS-1$
        self.Layout()
    # end updateFromError()
    
    def updateFromConnectionRespInfo(self, connectionRespInfo):
        # FIXME pretty-format the file size (KB, MB, etc)
        cl = connectionRespInfo.getContentLength()
        if cl is None:
            cl = 0
        self.fileSize.SetLabel(u"%d bytes" % cl) #$NON-NLS-1$
        self.linkType.SetLabel(connectionRespInfo.getContentType())
        self.Layout()
    # end updateFromConnectionRespInfo()
    
    def updateFromConnectionResp(self, connectionResp): #@UnusedVariable
        pass
    # end updateFromConnectionResp()

# end ZLinkSummaryPanel
