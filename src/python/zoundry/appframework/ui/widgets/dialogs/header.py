from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx


# --------------------------------------------------------------------------------------
# A simple extension of the Zoundry Base Dialog that provides a standard header at the
# top of the dialog.
# --------------------------------------------------------------------------------------
class ZHeaderDialog(ZBaseDialog):

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE, name = u"ZHeaderDialog"): #$NON-NLS-1$):
        ZBaseDialog.__init__(self, parent, id, title, pos, size, style, name)
    # end __init__()

    def _createContentWidgets(self):
        u"Creates a control for the dialog header and a static line below it." #$NON-NLS-1$
        self.headerPanel = self._createHeaderPanel()
        self.headerStaticLine = wx.StaticLine(self)

        self._createNonHeaderWidgets()
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        u"Populates the header with data." #$NON-NLS-1$
        self._populateNonHeaderWidgets()
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        sizer = self._layoutNonHeaderWidgets()

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.headerPanel, 0, wx.EXPAND)
        box.Add(self.headerStaticLine, 0, wx.EXPAND)
        box.AddSizer(sizer, 1, wx.EXPAND | wx.ALL, self._getNonHeaderContentBorder())

        return box
    # end _layoutContentWidgets()

    def _createHeaderPanel(self):
        panel = wx.Panel(self, wx.ID_ANY)
        panel.SetBackgroundColour(wx.WHITE)

        self.headerLink = wx.HyperlinkCtrl(panel, wx.ID_ANY, self._getHeaderTitle(), self._getHeaderHelpURL())
        self.headerLink.SetFont(getDefaultFontBold())
        self.headerMessage = wx.StaticText(panel, wx.ID_ANY, self._getHeaderMessage())
        headerImagePath = self._getHeaderImagePath()
        if not headerImagePath:
            headerImagePath = u"images/dialogs/image/header_image.png" #$NON-NLS-1$
        self.headerIcon = ZStaticBitmap(panel, getResourceRegistry().getBitmap(headerImagePath))

        linkAndMsgSizer = wx.BoxSizer(wx.VERTICAL)
        linkAndMsgSizer.Add(self.headerLink, 0, wx.ALL, 2)
        linkAndMsgSizer.Add(self.headerMessage, 1, wx.EXPAND | wx.ALL, 2)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSizer(linkAndMsgSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.headerIcon, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetAutoLayout(True)
        panel.SetSizer(sizer)

        return panel
    # end _createHeaderPanel()

    def _updateHeader(self):
        self.headerLink.SetLabel(self._getHeaderTitle())
        self.headerLink.SetURL(self._getHeaderHelpURL())
        self.headerMessage.SetLabel(self._getHeaderMessage())
        self.headerIcon.setBitmap( getResourceRegistry().getBitmap (self._getHeaderImagePath() ) )
        self.headerPanel.Layout()
        self.headerPanel.Refresh()
    # end _updateHeader()

    def _getNonHeaderContentBorder(self):
        return 5
    # end _getNonHeaderContentBorder()

    def _createNonHeaderWidgets(self):
        u"Called to create the non header related widgets.  (abstract)" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_createNonHeaderWidgets") #$NON-NLS-1$
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        u"Called to populate the non header related widgets." #$NON-NLS-1$
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        u"Called to layout the non header related widgets.  Should return a sizer.  (abstract)" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_layoutNonHeaderWidgets") #$NON-NLS-1$
    # end _layoutNonHeaderWidgets()

    def _getHeaderTitle(self):
        u"Returns the header title. (abstract)" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_getHeaderTitle") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        u"Returns the header message. (abstract)" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_getHeaderMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        u"Returns the path to an image that will be shown in the header. (abstract)" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_getHeaderImagePath") #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        u"Returns a http URL to the specific Online User Guide section for this dialog." #$NON-NLS-1$
        # FIXME (EPW) Create a context-sensitive Online Help URL here.
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

# end ZHeaderDialog
