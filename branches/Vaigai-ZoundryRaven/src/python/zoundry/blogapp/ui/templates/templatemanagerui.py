from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.controls.listex import IZCheckBoxListViewContentProvider
import wx

# ------------------------------------------------------------------------------
# Provider used to populate the list of templates.
# ------------------------------------------------------------------------------
class ZTemplateListProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model

        self.imageMap = self._createImageMap()
        self.columnInfo = self._createColumnInfo()
    # end __init__()

    def _createColumnInfo(self):
        cstyle = wx.LIST_FORMAT_LEFT
        columnInfo = [
            (u"Template", None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30), #$NON-NLS-1$
            (u"Template Source", None, cstyle, ZListViewEx.COLUMN_RELATIVE, 40), #$NON-NLS-1$
            (u"Added", None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30), #$NON-NLS-1$
        ]
        return columnInfo
    # end _createColumnInfo()

    def _createImageMap(self):
        imageList = ZMappedImageList()
        imageList.addImage(u"template", getResourceRegistry().getBitmap(u"images/dialogs/template/manager/template.png")) #$NON-NLS-1$ #$NON-NLS-2$
        return imageList
    # end _createImageMap()

    def getImageList(self):
        return self.imageMap
    # end getImageList()

    def getNumColumns(self):
        return 3
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getTemplates())
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columnInfo[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        try:
            template = self.model.getTemplates()[rowIndex]
            if columnIndex == 0:
                return template.getName()
            if columnIndex == 1:
                return template.getSource()
            if columnIndex == 2:
                return unicode(template.getCreationTime())
        except IndexError, ie: #@UnusedVariable
            return u"" #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        if columnIndex == 0:
            return self.imageMap[u"template"] #$NON-NLS-1$
        else:
            return -1
    # end getRowImage()

# end ZTemplateListProvider


# ------------------------------------------------------------------------------
# Provider used to populate the list of templates.
# ------------------------------------------------------------------------------
class ZTemplateCheckBoxListProvider(ZTemplateListProvider, IZCheckBoxListViewContentProvider):

    def __init__(self, model):
        ZTemplateListProvider.__init__(self, model)

        self.selectedIds = []
    # end __init__()

    def getSelectedTemplateId(self):
        if self.selectedIds:
            return self.selectedIds[0]
        else:
            return None
    # end getSelectedTemplateId()

    def setSelectedTemplateId(self, templateId):
        if templateId is not None:
            self.selectedIds = [ templateId ]
        else:
            self.selectedIds = []
    # end setSelectedTemplateId()

    def isChecked(self, rowIndex):
        template = self.model.getTemplates()[rowIndex]
        return template.getId() in self.selectedIds
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        template = self.model.getTemplates()[rowIndex]
        templateId = template.getId()
        if checked and not templateId in self.selectedIds:
            self.selectedIds.append(templateId)
        elif not checked and templateId in self.selectedIds:
            self.selectedIds.remove(templateId)
    # end setChecked

# end ZTemplateCheckBoxListProvider
