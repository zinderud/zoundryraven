from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.blogapp.models.ui.editors.blogeditormodel import ZBlogPostMetaDataModel
from zoundry.blogapp.ui.editors.blogeditorctrls.blogchooser import ZBlogInfoChooser
import wx

# ------------------------------------------------------------------------------
# The Blog Publishing dialog.  This dialog allows the user to publish a blog
# entry.
# ------------------------------------------------------------------------------
class ZBlogPublishingDialog(ZHeaderDialog):

    def __init__(self, parent, document, blog):
        self.blog = blog
        self.document = document
        self.blogInfoModel = ZBlogPostMetaDataModel()
        self.blogInfoModel.setInitDocument(document)
        self.pubMetaDataCtrl = None
        #FIXME (PJ) extern this and rest of string in this class/module
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, u"Publish Blog Entry", style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZBlogPublishingDialog") #$NON-NLS-2$ #$NON-NLS-1$
        self.Layout()
    # end __init__()

    def getPubMetaDataList(self):
        metaDataList = []
        if self.pubMetaDataCtrl is not None:
            self.pubMetaDataCtrl.updateModel()
            metaDataList = self.blogInfoModel.getPubMetaDataList()
        return  metaDataList
    # end getPubMetaDataList

    def getPubMetaData(self):
        # Return selected pubmeta data
        rval = None
        metaDataList = self.getPubMetaDataList()
        if metaDataList and len(metaDataList) > 0:
            rval = metaDataList[0]
        return rval
    # end getPubMetaData

    def _createNonHeaderWidgets(self):
        # FIXME (PJ) extern this
        self.publishToStaticBox = wx.StaticBox(self, wx.ID_ANY, u"Publish To Blog(s)") #$NON-NLS-1$
        self.pubMetaDataCtrl = ZBlogInfoChooser(self, self.blogInfoModel)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self.pubMetaDataCtrl.refreshUI()
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        staticBox = wx.StaticBoxSizer(self.publishToStaticBox, wx.VERTICAL)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.pubMetaDataCtrl, 0, wx.EXPAND | wx.ALL)
        staticBox.AddSizer(box, 1, wx.EXPAND | wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(staticBox, 1, wx.EXPAND | wx.ALL, 5)
        return box
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self._getOkButton().SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return u"Publish Blog Entry"  #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return u"Use this dialog to configure publishing settings and then publish your blog entry." #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/blogpub/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def _getOKButtonLabel(self):
        return u"Publish" #$NON-NLS-1$
    # end _getOKButtonLabel()

# end ZBlogPublishingDialog
