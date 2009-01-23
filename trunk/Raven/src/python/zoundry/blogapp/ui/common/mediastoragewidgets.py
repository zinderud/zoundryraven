from zoundry.appframework.resources.registry import getImageType
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.listex import IZCheckBoxListViewContentProvider
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------------
# Content provider used to populate the list of media storages.
# ------------------------------------------------------------------------------------
class ZMediaStorageListContentProvider(IZListViewExContentProvider):

    def __init__(self, zmediaStorageManagerModel):
        self.model = zmediaStorageManagerModel
        self.imageList = ZMappedImageList()
        self._populateImageList()

        self.columns = [
                (_extstr(u"mediastoragedialog.Name"), None, wx.LIST_FORMAT_LEFT, ZListViewEx.COLUMN_RELATIVE,  65), #$NON-NLS-1$
                (_extstr(u"mediastoragedialog.Type"), None, wx.LIST_FORMAT_LEFT, ZListViewEx.COLUMN_RELATIVE, 35) #$NON-NLS-1$
        ]
    # end __init__()

    def _populateImageList(self):
        for site in self.model.getMediaSites():
            iconKey = site.getId()
            iconPath = site.getIconPath()
            icon = wx.Image(iconPath, getImageType(iconPath)).ConvertToBitmap()
            self.imageList.addImage(iconKey, icon)
    # end _populateImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 2
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getMediaStorages())
    # end getNumRows()

    # Return value format:  (label, imageKey, style, width)
    def getColumnInfo(self, columnIndex):
        return self.columns[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        store = self.model.getMediaStorages()[rowIndex]
        if columnIndex == 0:
            return store.getName()
        elif columnIndex == 1:
            return self.model.getMediaSite(store).getDisplayName()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex):
        if columnIndex == 0:
            store = self.model.getMediaStorages()[rowIndex]
            imageKey = self.model.getImageKey(store)
            return self.imageList[imageKey]
        return -1
    # end getRowImage()

# end ZMediaStorageListContentProvider

# ------------------------------------------------------------------------------------
# Single select checkbox version of content provider used to populate the list of media storages.
# ------------------------------------------------------------------------------------
class ZMediaStorageCheckBoxListContentProvider(ZMediaStorageListContentProvider, IZCheckBoxListViewContentProvider):

    def __init__(self, zmediaStorageManagerModel):
        ZMediaStorageListContentProvider.__init__(self, zmediaStorageManagerModel)
        self.selectedStoreId = None
    # end __init__()

    def setSelectedStoreId(self, storeId):
        self.selectedStoreId = storeId
    # end setSelectedStoreId

    def getSelectedStoreId(self):
        return self.selectedStoreId
    # end getSelectedStoreId

    def _getMediaStorageIndex(self, storeId):
        stores = self.model.getMediaStorages()
        for i in range(0, len(stores)):
            store = stores[i]
            if store.getId() == storeId:
                return i
        return -1
    # end getMediaStorageIndex()

    def _populateImageList(self):
        # skip - images not supported buy current checkbox view.
        pass
    # end _populateImageList()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

    def isChecked(self, rowIndex):
        mediaStore = self.model.getMediaStorages()[rowIndex]
        return self.selectedStoreId is not None and self.selectedStoreId == mediaStore.getId()
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        if checked:
            mediaStore = self.model.getMediaStorages()[rowIndex]
            self.selectedStoreId = mediaStore.getId()
    # end setChecked

# end ZMediaStorageCheckBoxListContentProvider