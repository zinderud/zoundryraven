from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromFile
from zoundry.blogapp import version
from zoundry.blogapp.messages import _extstr
import wx
import wx.lib.flatnotebook as fnb

# ------------------------------------------------------------------------------
# The Zoundry Raven About dialog.
# ------------------------------------------------------------------------------
class ZAboutDialog(ZBaseDialog):

    def __init__(self, parent):
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"aboutdialog.AboutRaven")) #$NON-NLS-1$

        size = self.GetBestSize()
        self.SetSize(size)
    # end __init__()

    def _createContentWidgets(self):
        self.notebook = fnb.FlatNotebook(self, wx.ID_ANY, style = fnb.FNB_BOTTOM | fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_NO_X_BUTTON | fnb.FNB_NODRAG)
        self.notebook.AddPage(self._createRavenInfoPage(), _extstr(u"aboutdialog.Info"), True, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createCreditsPage(), _extstr(u"aboutdialog.Credits"), False, -1) #$NON-NLS-1$

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createContentWidgets()

    def _createRavenInfoPage(self):
        self.infoPanel = wx.Panel(self.notebook, wx.ID_ANY)
        self.infoPanel.SetBackgroundColour(wx.WHITE)

        self.aboutBmp = getResourceRegistry().getBitmap(u"images/about/about.png") #$NON-NLS-1$
        self.aboutImage = ZStaticBitmap(self.infoPanel, self.aboutBmp)

        ver = version.ZVersion()
        verDate = ZSchemaDateTime(ver.getBuildDate())

        self.versionLabelLabel = wx.StaticText(self.infoPanel, wx.ID_ANY, u"%s: " % _extstr(u"splash.Version")) #$NON-NLS-1$ #$NON-NLS-2$
        self.versionLabelLabel.SetFont(getDefaultFontBold())
        self.versionLabel = wx.StaticText(self.infoPanel, wx.ID_ANY, ver.getFullVersionString())
        self.dateLabelLabel = wx.StaticText(self.infoPanel, wx.ID_ANY, u"%s: " % _extstr(u"splash.BuiltOn")) #$NON-NLS-1$ #$NON-NLS-2$
        self.dateLabelLabel.SetFont(getDefaultFontBold())
        self.dateLabel = wx.StaticText(self.infoPanel, wx.ID_ANY, verDate.toString(localTime = True))

        return self.infoPanel
    # end _createRavenInfoPage()

    def _createCreditsPage(self):
        self.creditsPanel = wx.Panel(self.notebook, wx.ID_ANY)
        self.creditsPanel.SetBackgroundColour(wx.WHITE)

        self.htmlWidget = ZHTMLViewControl(self.creditsPanel)

        return self.creditsPanel
    # end _createCreditsPage()

    def _populateContentWidgets(self):
        xhtmlDoc = loadXhtmlDocumentFromFile(getResourceRegistry().getResourcePath(u"html/about/credits.html")) #$NON-NLS-1$
        self.htmlWidget.setXhtmlDocument(xhtmlDoc)
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._layoutInfoPanel()
        self._layoutCreditsPanel()

        sizer.Add(self.notebook, 1, wx.EXPAND)
        sizer.Add(self.staticLine, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        return sizer
    # end _layoutContentWidgets()

    def _layoutInfoPanel(self):
        verAndDateSizer = wx.BoxSizer(wx.HORIZONTAL)
        verAndDateSizer.Add(self.versionLabelLabel, 0, wx.EXPAND | wx.RIGHT, 2)
        verAndDateSizer.Add(self.versionLabel, 0, wx.EXPAND | wx.RIGHT, 10)
        verAndDateSizer.Add(self.dateLabelLabel, 0, wx.EXPAND | wx.RIGHT, 2)
        verAndDateSizer.Add(self.dateLabel, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.aboutImage, 0, wx.EXPAND)
        sizer.AddSizer(verAndDateSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.infoPanel.SetSizer(sizer)
        self.infoPanel.SetAutoLayout(True)
    # end _layoutInfoPanel()

    def _layoutCreditsPanel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.htmlWidget, 1, wx.EXPAND)

        self.creditsPanel.SetSizer(sizer)
        self.creditsPanel.SetAutoLayout(True)
    # end _layoutCreditsPanel()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON
    # end _getButtonTypes()

# end ZAboutDialog
