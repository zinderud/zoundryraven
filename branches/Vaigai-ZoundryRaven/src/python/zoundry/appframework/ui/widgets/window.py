from zoundry.appframework.ui.events.commonevents import ZEVT_UIEXEC
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx

# ----------------------------------------------------------------------------------------
# A base class for top level windows.
# ----------------------------------------------------------------------------------------
class ZBaseWindow(wx.Frame):

    def __init__(self, parent, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN, name = u"ZBaseWindow"): #$NON-NLS-1$
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, pos, size, style, name)
        
        self._initWindow()
    # end __init__()

    def _initWindow(self):
        self._createWidgets()
        self._populateWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        self._setInitialFocus()
        
        self.Bind(ZEVT_UIEXEC, self.onUIExec)
    # end _initWindow()

    def _createWidgets(self):
        self.windowPanel = wx.Panel(self, wx.ID_ANY)
        self._createWindowWidgets(self.windowPanel)
    # end _createWidgets()

    def _populateWidgets(self):
        self._populateWindowWidgets()
    # end _populateWidgets()

    def _layoutWidgets(self):
        # Subclass should layout its content into a sizer
        sizer = self._layoutWindowWidgets()
        
        self.windowPanel.SetAutoLayout(True)
        self.windowPanel.SetSizer(sizer)
        self.windowPanel.Layout()

        windowSizer = wx.BoxSizer(wx.VERTICAL)
        windowSizer.Add(self.windowPanel, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(windowSizer)
        self.Layout()
    # end _layoutWidgets()
    
    def _createWindowWidgets(self, parent):
        u"Creates the widgets for this window." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_createWindowWidgets") #$NON-NLS-1$
    # end _createWindowWidgets()

    def _populateWindowWidgets(self):
        pass
    # end _populateWindowWidgets()

    def _layoutWindowWidgets(self):
        u"Lays out the window's widgets and returns a sizer (should be implemented by subclasses)." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_layoutWindowWidgets") #$NON-NLS-1$
    # end _layoutWindowWidgets()
    
    def _bindWidgetEvents(self):
        u"Binds widget events for this window." #$NON-NLS-1$
    # end _bindWidgetEvents()
    
    def _setInitialFocus(self):
        u"Sets the initial user focus for the window." #$NON-NLS-1$
    # end _setInitialFocus()

    def onUIExec(self, event):
        event.getRunnable().run()
    # end onUIExec()

# end ZBaseWindow
