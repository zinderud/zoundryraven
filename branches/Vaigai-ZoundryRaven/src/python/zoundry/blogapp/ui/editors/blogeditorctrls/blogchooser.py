from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.colorutil import getDefaultControlBackgroundColor
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.blogeditorctrls.blogconfig import ZConfigureBlogCombo
from zoundry.blogapp.ui.editors.blogeditorctrls.blogselector import ZBlogSelectorCombo
from zoundry.blogapp.ui.editors.blogeditorctrls.blogselector import ZEVT_BLOG_SELECTOR_COMBO
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
from zoundry.blogapp.ui.util.blogutil import getBlogFromPubMetaData
import wx


ADDBLOGINFOWIDGETEVENT = wx.NewEventType()
DELBLOGINFOWIDGETEVENT = wx.NewEventType()
ZEVT_ADD_BLOGINFO_WIDGET = wx.PyEventBinder(ADDBLOGINFOWIDGETEVENT, 1)
ZEVT_DEL_BLOGINFO_WIDGET = wx.PyEventBinder(DELBLOGINFOWIDGETEVENT, 1)
# ----------------------------------------------------------------------------
# Custom event class.
# ----------------------------------------------------------------------------
class ZAddBlogInfoWidgetEvent(wx.PyCommandEvent):

    def __init__(self, windowID):
        self.eventType = ADDBLOGINFOWIDGETEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getInfoWidget(self):
        return self.infoWidget
    # end getInfoWidget()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZAddBlogInfoWidgetEvent

class ZRemoveBlogInfoWidgetEvent(wx.PyCommandEvent):

    def __init__(self, windowID, infoWidget):
        self.infoWidget = infoWidget
        self.eventType = DELBLOGINFOWIDGETEVENT
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getInfoWidget(self):
        return self.infoWidget
    # end getInfoWidget()

    def Clone(self):
        return self.__class__(self.GetId(), self.getInfoWidget())
    # end Clone()

# end ZRemoveBlogInfoWidgetEvent

class ZRemoveBlogInfoRunnable(IZRunnable):

    def __init__(self, infoChooser, index):
        self.infoChooser = infoChooser
        self.index = index
    # end __init__()

    def run(self):
        self.infoChooser._removeInfoWidget(self.index)
    # end run()

# end ZRemoveBlogInfoRunnable

# ------------------------------------------------------------------------------
# A control that lets the user select and configure a single blog.  The widget
# is comprised of a drop-down blog selector (for selecting a blog to configure)
# and, once a blog has been selected, a popup window for configuring blog meta
# data (date/time, draft, categories, etc).
# ------------------------------------------------------------------------------
class ZBlogInfoWidget(wx.Panel):
    TYPE_NONE = 0
    TYPE_ADD = 1
    TYPE_DEL = 2

    def __init__(self, parent, model, widgetType = TYPE_NONE):
        self.model = model
        self.widgetType = widgetType
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.imgButton = None
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        if self.widgetType == ZBlogInfoWidget.TYPE_ADD:
            registry = getResourceRegistry()
            bitmap = registry.getBitmap(u"images/common/add.png") #$NON-NLS-1$
            self.imgButton = ZImageButton(self, bitmap, False, None, True)
            self.imgButton.SetToolTipString(_extstr(u"blogchooser.AddBlogTooltip")) #$NON-NLS-1$
            bitmap = registry.getBitmap(u"images/common/add_disabled.png") #$NON-NLS-1$
            self.imgButton.SetDisabledBitmap(bitmap)
        elif self.widgetType == ZBlogInfoWidget.TYPE_DEL:
            registry = getResourceRegistry()
            bitmap = registry.getBitmap(u"images/common/delete.png") #$NON-NLS-1$
            self.imgButton = ZImageButton(self, bitmap, False, None, True)
            self.imgButton.SetToolTipString(_extstr(u"blogchooser.RemoveBlogTooltip")) #$NON-NLS-1$

        self.blogSelectorCombo = ZBlogSelectorCombo(self, self.model)
        self.separator = wx.StaticLine(self, wx.VERTICAL)
        self.configureCombo = ZConfigureBlogCombo(self, None)
    # end _createWidgets()

    def _layoutWidgets(self):
        self.SetMinSize(wx.Size(-1, 20))

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.blogSelectorCombo, 1, wx.EXPAND)
        self.sizer.Add(self.separator, 0, wx.EXPAND)
        self.sizer.Add(self.configureCombo, 0, wx.EXPAND)
        if self.imgButton:
            self.sizer.Add(self.imgButton, 0, wx.ALIGN_RIGHT)

        self.separator.Show(False)
        self.configureCombo.Show(False)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_BLOG_SELECTOR_COMBO, self.onBlogSelection, self.blogSelectorCombo)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        if self.imgButton:
            self.Bind(wx.EVT_BUTTON, self.onImgButton, self.imgButton)
    # end _bindWidgetEvents()

    def onImgButton(self, event):
        if self.widgetType == ZBlogInfoWidget.TYPE_ADD:
            event = ZAddBlogInfoWidgetEvent(self.GetId())
            self.GetEventHandler().AddPendingEvent(event)
        elif self.widgetType == ZBlogInfoWidget.TYPE_DEL:
            event = ZRemoveBlogInfoWidgetEvent(self.GetId(), self )
            self.GetEventHandler().AddPendingEvent(event)
    # end onImgButton

    def showButton(self, show):
        if self.imgButton:
            self.imgButton.Enable(show)
    # end showButton()

    def _populateWidgets(self, pubMetaData):
        self.blogSelectorCombo.selectBlog(pubMetaData.getAccountId(), pubMetaData.getBlogId())
        self.configureCombo.setBlog(self.blogSelectorCombo.getBlog())
        self.configureCombo.setPubMetaData(pubMetaData)

        self.separator.Show(True)
        self.configureCombo.Show(True)
        self.Layout()
    # end _populateWidgets()

    def setPubMetaData(self, pubMetaData):
        if pubMetaData is not None:
            self._populateWidgets(pubMetaData)
    # end setPubMetaData()

    def getPubMetaData(self):
        blog = self.blogSelectorCombo.getBlog()
        if blog is None:
            return None
        pubMetaData = self.configureCombo.getPubMetaData()
        pubMetaData.setAccountId(blog.getAccount().getId())
        pubMetaData.setBlogId(blog.getId())

        return pubMetaData
    # end getPubMetaData()

    def onBlogSelection(self, event):
        blog = self.blogSelectorCombo.getBlog()
        if blog:
            self.configureCombo.setBlog(blog)
        self.separator.Show(True)
        self.configureCombo.Show(True)
        self.Layout()
        event.Skip()
    # end onBlogSelection()

    def onResize(self, event):
        self.Layout()
        event.Skip()
    # end onResize()

    def Layout(self):
        wx.Panel.Layout(self)
        self.blogSelectorCombo.setExtent(self.configureCombo.GetSizeTuple()[0])
        self.configureCombo.setExtent(self.blogSelectorCombo.GetSizeTuple()[0])
    # end Layout()

# end ZBlogInfoWidget


# ------------------------------------------------------------------------------
# A control that lets the user select and configure blogs.  This control is
# used by the blog post editor - it allows the user to select which blogs to
# publish an entry to.  In addition, it lets the user configure the publishing
# parameters for each blog (date/time, draft, categories, etc).
#
# This control will return a list of IZPubMetaData objects at any given time,
# which represent the information found in each of the configured blogs.  If
# no blogs are configured, then an empty list is returned.
#
# Whenever anything in the control is changed, an event is fired so that the
# editor's dirty flag can be set.
# ------------------------------------------------------------------------------
class ZBlogInfoChooser(wx.Panel):
    # Max amount of info widgets that can be displayed.
    MAX_WIDGETS = 3

    def __init__(self, parent, zblogPostMetaDataModel):
        self.model = zblogPostMetaDataModel
        self.infoWidgets = []
        self.defaultInfoWidget = None
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.defaultInfoWidget = ZBlogInfoWidget(self, self.model, ZBlogInfoWidget.TYPE_ADD)
        self.infoWidgets.append(self.defaultInfoWidget)
    # end _createWidgets()

    def _layoutWidgets(self):
        self.SetMinSize( wx.Size( -1, 20 * len(self.infoWidgets) ) )
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for infoWidget in self.infoWidgets:
            self.sizer.Add(infoWidget, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_ADD_BLOGINFO_WIDGET, self.onAddNewInfoWidget, self.defaultInfoWidget)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
    # end _bindWidgetEvents()

    def _enableAddOption(self):
        self.defaultInfoWidget.showButton( self._canAddMore() )
    # end _enableAddOption()

    def _canAddMore(self):
        return len(self.infoWidgets) < ZBlogInfoChooser.MAX_WIDGETS
    # end _canAddMore()

    def onAddNewInfoWidget(self, event): #@UnusedVariable
        self._addNewInfoWidget(None)
    # end addNewInfoWidget()

    def _addNewInfoWidget(self, pubMetaData):
        if not self._canAddMore():
            return
        infoWidget = ZBlogInfoWidget(self, self.model, ZBlogInfoWidget.TYPE_DEL)
        self.Bind(ZEVT_DEL_BLOGINFO_WIDGET, self.onRemoveInfoWidget, infoWidget)
        self.infoWidgets.append( infoWidget )
        self._enableAddOption()
        self._layoutWidgets()
        # do layout at 2 levels - one for the container in the editor, and other to work around layout in pubish dialog container.
        self.GetParent().Layout()
        self.GetParent().GetParent().Layout()
        self.GetParent().Refresh()
        if pubMetaData is not None:
            infoWidget.setPubMetaData(pubMetaData)
    # end _addNewInfoWidget

    def onRemoveInfoWidget(self, event):
        widget = event.getInfoWidget()
        try:
            index = self.infoWidgets.index(widget)
            self.Unbind(ZEVT_DEL_BLOGINFO_WIDGET, widget)
            widget.Show(False)
            self.RemoveChild(widget)
            runnable = ZRemoveBlogInfoRunnable(self, index)
            fireUIExecEvent(runnable, self)
        except:
            pass
    # end removeNewInfoWidget

    def _removeInfoWidget(self, index):
        if index > 0 and index < len(self.infoWidgets):
            try:
                infoWidget = self.infoWidgets[index]
                del self.infoWidgets[index]
                self._enableAddOption()
                self._layoutWidgets()
                self.GetParent().Layout()
                self.GetParent().GetParent().Layout()
                self.GetParent().Refresh()
                infoWidget.Destroy()
            except:
                pass
    # end _removeInfoWidget()

    def refreshUI(self):
        # update UI from model
        pubMetaDataList = self.model.getPubMetaDataList()
        if pubMetaDataList and len(pubMetaDataList) > 0:
            for index in range( len(pubMetaDataList) ):
                pubMetaData = pubMetaDataList[index]
                if index < len(self.infoWidgets):
                    # update existing info widget
                    blog = getBlogFromIds(pubMetaData.getAccountId(), pubMetaData.getBlogId())
                    if blog is not None:
                        widget = self.infoWidgets[index]
                        widget.setPubMetaData(pubMetaData)
                else:
                    # add new widget and populate it.
                    self._addNewInfoWidget(pubMetaData)
    # end refreshUI()

    def updateModel(self):
        # Flush UI data to model (document)
        pubMetaDataList = []
        # tmp list to keep track of duplicate pubmeta data pointing  the same blog
        tmpBlogs = []
        for infoWidget in self.infoWidgets:
            pubMetaData = infoWidget.getPubMetaData()
            if pubMetaData is not None:
                blog = getBlogFromPubMetaData(pubMetaData)
                if blog is not None and blog.getId() not in tmpBlogs:
                    pubMetaDataList.append(pubMetaData)
                    tmpBlogs.append( blog.getId() )
        self.model.setPubMetaDataList(pubMetaDataList)
    # end updateModel()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(getDefaultControlBackgroundColor(), wx.SOLID))
        paintDC.Clear()

        brush = wx.TRANSPARENT_BRUSH
        pen = wx.Pen(getDefaultControlBorderColor())
        paintDC.SetBrush(brush)
        paintDC.SetPen(pen)

        paintDC.DrawRectangle(0, 0, w, h)

        del paintDC

        event.Skip()
    # end onPaint()

# end ZBlogInfoChooser
