from zoundry.appframework.ui.widgets.controls.common.panel import ZSmartTransparentPanel
import wx
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.services.validation.xhtmlvalidation import ZXhtmlValidationMessage
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider



# ----------------------------------------------------------------------------------------
# The content provider used for the list of images in the post.
# ----------------------------------------------------------------------------------------
class ZXhtmlValidationReportListViewContentProvider(IZListViewExContentProvider):

    def __init__(self):
        self.columnInfo = [(u"Line",10), (u"Column", 10), (u"Message", 80)] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.validationMessageList = []
        self.imageList = ZMappedImageList()
        registry = getResourceRegistry()
        self.imageList.addImage(u"%d" % ZXhtmlValidationMessage.SUCCESS, registry.getBitmap(u"images/common/check2_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZXhtmlValidationMessage.INFO, registry.getBitmap(u"images/common/information_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZXhtmlValidationMessage.WARNING, registry.getBitmap(u"images/common/warning_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZXhtmlValidationMessage.ERROR, registry.getBitmap(u"images/common/error_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
        self.imageList.addImage(u"%d" % ZXhtmlValidationMessage.FATAL, registry.getBitmap(u"images/common/error_whitebg.png")) #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()
    
    def setValidationMessages(self, validationMessageList):
        # list of ZXhtmlValidationMessage
        self.clearValidationMessages()
        if validationMessageList:
            self.validationMessageList = validationMessageList
    # end setValidationMessages
    
    def addValidationMessage(self, zxhtmlValidationMessage):
        if zxhtmlValidationMessage:
            self.validationMessageList.append(zxhtmlValidationMessage)
    # end addValidationMessages()    
    
    def getValidationMessage(self, index):
        if index >= 0 and index < len(self.validationMessageList):
            return self.validationMessageList[index]
        else:
            return None
    # end getValidationMessage()
    
    def getValidationMessages(self):
        return self.validationMessageList
    # end getValidationMessages()        
    
    def clearValidationMessages(self):
        self.validationMessageList = []
    # end clearValidationMessages()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return len(self.columnInfo)
    # end getNumColumns()

    def getNumRows(self):
        return len( self.validationMessageList )
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        (columnName, widthPercent) = self.columnInfo[columnIndex] 
        return (columnName, None, 0, ZListViewEx.COLUMN_RELATIVE, widthPercent)
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        zxhtmlValidationMessage = self.validationMessageList[rowIndex]
        if columnIndex == 0: 
            if zxhtmlValidationMessage.getLine() >= 0:
                return u"%3d" % zxhtmlValidationMessage.getLine() #$NON-NLS-1$
            else:
                return u"" #$NON-NLS-1$
        elif columnIndex == 1:
            if zxhtmlValidationMessage.getColumn() >= 0:
                return u"%3d" % zxhtmlValidationMessage.getColumn() #$NON-NLS-1$
            else:
                return u"" #$NON-NLS-1$ 
        else:
            return zxhtmlValidationMessage.getMessage()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        if columnIndex == 0:
            zxhtmlValidationMessage = self.validationMessageList[rowIndex]
            return self.imageList[u"%d" % zxhtmlValidationMessage.getSeverity() ] #$NON-NLS-1$
        else:
            return -1
    # end getRowImage()

# end ZXhtmlValidationReportListViewContentProvider

# ------------------------------------------------------------------------------
# Validation List view pabel
# ------------------------------------------------------------------------------
class ZXhtmlValidationReportView(ZSmartTransparentPanel):

    def __init__(self, parent, provider):
        ZSmartTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.listView = None
        # provider is ZXhtmlValidationReportListViewContentProvider
        self.provider = provider
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgets()
    # end __init__()

    def _createWidgets(self):
        self.listView = ZListViewEx(self.provider, self)
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, u"Validation Messages") #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.listView, 1, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(staticBoxSizer, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets

    def _bindWidgets(self):
        pass
    # end _bindWidgets()
    
    def getListControl(self):
        return self.listView
    # end getListControl(
    
# end ZXhtmlValidationReportView()    

