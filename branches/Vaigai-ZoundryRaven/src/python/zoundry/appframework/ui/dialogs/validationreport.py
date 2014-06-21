from zoundry.appframework.global_services import getResourceRegistry
from zoundry.base.util.validatables import ZValidationReportEntry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
import wx

# ------------------------------------------------------------------------------
# Generic dialog that displays validation messages
# ------------------------------------------------------------------------------
class ZValidationReportDialog(ZHeaderDialog):

    def __init__(self, parent, izConfigValidationReporter, title, description, imagePath):
        self.reporter = izConfigValidationReporter
        self.title = title
        self.description = description
        self.imagePath = imagePath
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, title)
        size = self.GetBestSize()
        if size.GetWidth() < 500:
            size.SetWidth(500)
        if size.GetHeight() < 300:
            size.SetHeight(300)            
        self.SetSize(size)
    # end __init__()

    def _createNonHeaderWidgets(self):
        self.provider = ZValidationReportListViewContentProvider(self.reporter)
        self.reportListView = ZListViewEx(self.provider, self)
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, u"Validation Messages") #$NON-NLS-1$
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        pass
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.reportListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(staticBoxSizer, 1, wx.EXPAND)
        #sizer.Add(self.reportListView, 1, wx.EXPAND)
        return sizer
    # end _layoutNonHeaderWidgets()

    def _getButtonTypes(self):
        if self.reporter.hasErrors():
            return ZBaseDialog.CLOSE_BUTTON
        else:
            return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def _getOKButtonLabel(self):
        return u"Continue..." #$NON-NLS-1$
    # end _getOKButtonLabel()

    def _setInitialFocus(self):
        if self.reporter.hasErrors():
            self.FindWindowById(wx.ID_CANCEL).SetFocus()
        else:
            self.FindWindowById(wx.ID_OK).SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return self.title
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return self.description
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return self.imagePath
    # end _getHeaderImagePath()

#ZValidationReportDialog())

# ----------------------------------------------------------------------------------------
# The content provider used for the list of images in the post.
# ----------------------------------------------------------------------------------------
class ZValidationReportListViewContentProvider(IZListViewExContentProvider):

    def __init__(self, izConfigValidationReporter):
        self.reporter = izConfigValidationReporter
        self.imageList = ZMappedImageList()
        registry = getResourceRegistry()
        self.imageList.addImage(u"%d" % ZValidationReportEntry.INFO, registry.getBitmap(u"images/common/check_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZValidationReportEntry.WARNING, registry.getBitmap(u"images/common/warning_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZValidationReportEntry.ERROR, registry.getBitmap(u"images/common/error_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len( self.reporter.listReports() )
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        columnName = None
        if columnIndex == 0:
            columnName = u"Message" #$NON-NLS-1$
        return (columnName, None, 0, ZListViewEx.COLUMN_RELATIVE, 100)
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        validationReportEntry = self.reporter.listReports()[rowIndex]
        return validationReportEntry.getMessage()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        validationReportEntry = self.reporter.listReports()[rowIndex]
        return self.imageList[u"%d" % validationReportEntry.getType() ] #$NON-NLS-1$
    # end getRowImage()

# end ZValidationReportListViewContentProvider