from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.blogeditorctrls.blogchooser import ZBlogInfoChooser
from zoundry.blogapp.ui.events.editors.blogeditorctrls.metadataevents import fireMetaDataTitleChangedEvent
from zoundry.blogapp.ui.events.editors.blogeditorevents import firePublishingChangeEvent
import wx


# ------------------------------------------------------------------------------
# A widget that shows the Blog Info, Title, and Tag Words for a single blog
# post.  This is the widget that appears at the top of the blog post editor.
# ------------------------------------------------------------------------------
class ZBlogPostMetaDataWidget(wx.Panel):

    def __init__(self, parent, zblogPostMetaDataModel):
        self.model = zblogPostMetaDataModel
        # title or tagwords have been modified.
        self.dirty = False
        self.initialTitle = None
        self.initialTagwords = None
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getModel(self):
        u"""getModel() -> ZBlogPostMetaDataModel
        Returns data model.""" #$NON-NLS-1$
        return self.model
    # end getModel()

    def _createWidgets(self):
        self.blogsLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"metadata.Blogs")) #$NON-NLS-1$
        self.blogsCtrl = ZBlogInfoChooser(self, self.model)
        self.titleLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"metadata.Title")) #$NON-NLS-1$
        self.titleText = wx.TextCtrl(self, wx.ID_ANY)
        self.tagwordsLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"metadata.Tagwords")) #$NON-NLS-1$
        self.tagwordsText = wx.TextCtrl(self, wx.ID_ANY)
        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createWidgets()

    def _layoutWidgets(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)

        flexGridSizer = wx.FlexGridSizer(3, 2, 2, 5)
        flexGridSizer.AddGrowableCol(1)
        flexGridSizer.AddGrowableRow(0)
        flexGridSizer.Add(self.blogsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP)
        flexGridSizer.Add(self.blogsCtrl, 0, wx.EXPAND)
        flexGridSizer.Add(self.titleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        flexGridSizer.Add(self.titleText, 0, wx.EXPAND)
        flexGridSizer.Add(self.tagwordsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        flexGridSizer.Add(self.tagwordsText, 0, wx.EXPAND)

        panelSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 3)
        panelSizer.Add(self.staticLine, 0, wx.EXPAND)

        self.SetSizer(panelSizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT, self.onTitleTextChange, self.titleText)
        self.Bind(wx.EVT_TEXT, self.onTagwordsTextChange, self.tagwordsText)
    # end _bindWidgetEvents()

    def getPubMetaDataList(self):
        return self.blogsCtrl.getPubMetaDataList()
    # end getPubMetaDataList()

    def getTitle(self):
        return self.titleText.GetValue()
    # end getTitle()

    def getTagwords(self):
        return self.tagwordsText.GetValue()
    # end getTagwords()

    def onTitleTextChange(self, event): #@UnusedVariable
        if not self.dirty and self.initialTitle is not None and self.initialTitle != self.titleText.GetValue().strip():
            self._setDirty(True)
        fireMetaDataTitleChangedEvent(self, self.getTitle())
    # end onTitleTextChange()

    def onTagwordsTextChange(self, event): #@UnusedVariable
        if not self.dirty and self.initialTagwords is not None and self.initialTagwords != self.tagwordsText.GetValue().strip():
            self._setDirty(True)
    # end onTagwordsTextChange()

    def refreshUI(self):
        # clear dirty flag since UI data will be same as model
        self._setDirty(False)
        # update UI for title and tags from model
        self.titleText.SetValue( self.getModel().getTitle() )
        self.tagwordsText.SetValue( self.getModel().getTagwords() )
        # save the initial data - used to compare to see if content has been modified.
        self.initialTitle = self.getModel().getTitle()
        self.initialTagwords = self.getModel().getTagwords()
        self.blogsCtrl.refreshUI()
    # end refreshUI()

    def updateModel(self):
        # Get the title and tags and set it in the model
        self.getModel().setTitle( self.titleText.GetValue().strip() )
        self.getModel().setTagwords( self.tagwordsText.GetValue().strip() )
        self.blogsCtrl.updateModel()
    # end updateModel()

    def _setDirty(self, dirty):
        if self.dirty != dirty:
            self.dirty = dirty
            if dirty:
                firePublishingChangeEvent(self)
            else:
                self.initialTitle = None
                self.initialTagwords = None
    # end _setDirty()

# end ZBlogPostMetaDataWidget
