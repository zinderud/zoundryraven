import wx

# ------------------------------------------------------------------------------
# The interface that must be implemented in order to supply a content provider
# for a status bar.
# ------------------------------------------------------------------------------
class IZStatusBarContentProvider:

    def getNumPanes(self):
        u"""getNumPanes() -> int
        Returns the number of panes in the status bar.""" #$NON-NLS-1$
    # end getNumPanes()

    def getPaneWidth(self, paneIdx):
        u"""getPaneWidth(int) -> int
        Returns the width of the pane at the given index.""" #$NON-NLS-1$
    # end getPaneWidth()

    def getPaneStyle(self, paneIdx):
        u"""getPaneStyle(int) -> int
        Returns the style that should be used for the pane
        at the given index.  Valid values are:
        wx.SB_NORMAL
        wx.SB_FLAT
        wx.SB_RAISED""" #$NON-NLS-1$
    # end getPaneStyle()

    def getPaneText(self, paneIdx):
        u"""getPaneText(int) -> string
        Gets the text for the pane at the given index.""" #$NON-NLS-1$
    # end getPaneText()

# end IZStatusBarContentProvider


# ------------------------------------------------------------------------------
# A model that can be used to model the information in the status bar.
# ------------------------------------------------------------------------------
class ZStatusBarModel:

    # --------------------------------------------------------------------------
    # An inner class - holds the information about a pane.
    # --------------------------------------------------------------------------
    class ZStatusBarPane:

        def __init__(self, name):
            self.name = name
            self.text = None
            self.style = wx.SB_NORMAL
            self.width = -1
        # end __init__()

    # end ZStatusBarPane

    def __init__(self):
        self.panes = []
    # end __init__()

    def getPanes(self):
        return self.panes
    # end getPanes()

    def addPane(self, paneName):
        u"""addPane(string) -> ZStatusBarModel.ZStatusBarPane
        Adds a pane to the model.  A new pane object is
        created and returned.""" #$NON-NLS-1$
        pane = ZStatusBarModel.ZStatusBarPane(paneName)
        self.panes.append(pane)
        return pane
    # end addPane()

    def getPane(self, paneName):
        u"""getPane(string) -> ZStatusBarModel.ZStatusBarPane
        Returns the pane with the given name.""" #$NON-NLS-1$
        for pane in self.panes:
            if pane.name == paneName:
                return pane
        return None
    # end getPane()

    def removePane(self, paneName):
        u"""removePane(string) -> boolean
        Removes the pane with the given name from the model.""" #$NON-NLS-1$
        pane = self.getPane(paneName)
        if pane is not None:
            self.panes.remove(pane)
            return True
        return False
    # end removePane()

    def setPaneWidth(self, paneName, width):
        pane = self.getPane(paneName)
        if pane is not None:
            pane.width = width
    # end setPaneWidth()

    def setPaneText(self, paneName, text):
        pane = self.getPane(paneName)
        if pane is not None:
            pane.text = text
    # end setPaneText()

    def setPaneStyle(self, paneName, style):
        pane = self.getPane(paneName)
        if pane is not None:
            pane.style = style
    # end setPaneStyle()

# end ZStatusBarModel


# ------------------------------------------------------------------------------
# A content provider implementation that is based on a status bar model object.
# ------------------------------------------------------------------------------
class ZStatusBarModelBasedContentProvider(IZStatusBarContentProvider):

    def __init__(self, model):
        self.model = model
    # end __init__()

    def getNumPanes(self):
        return len(self.model.getPanes())
    # end getNumPanes()

    def getPaneWidth(self, paneIdx):
        return self.model.getPanes()[paneIdx].width
    # end getPaneWidth()

    def getPaneStyle(self, paneIdx):
        return self.model.getPanes()[paneIdx].style
    # end getPaneStyle()

    def getPaneText(self, paneIdx):
        return self.model.getPanes()[paneIdx].text
    # end getPaneText()

# end ZStatusBarModelBasedContentProvider


# ------------------------------------------------------------------------------
# Extends the wx status bar in order to implement a provider-based version of
# a status bar.
# ------------------------------------------------------------------------------
class ZStatusBar(wx.StatusBar):

    def __init__(self, parent, contentProvider):
        self.contentProvider = contentProvider
        self.sizeChanged = False

        wx.StatusBar.__init__(self, parent, wx.ID_ANY)

        self._createCustomWidgets()
        
        self._bindCustomWidgets()
        self.Bind(wx.EVT_SIZE, self._onZStatusBarSize)
        self.Bind(wx.EVT_IDLE, self._onZStatusBarIdle)

        self.refresh()
        self.reposition()
    # end __init__()

    def _createCustomWidgets(self):
        pass
    # end _createCustomWidgets()

    def _bindCustomWidgets(self):
        pass
    # end _bindCustomWidgets()

    def _refreshPane(self, paneIdx): #@UnusedVariable
        pass
    # end _refreshPane()

    def _repositionPane(self, paneIdx, rect): #@UnusedVariable
        pass
    # end _repositionPane()

    def setContentProvider(self, contentProvider):
        self.contentProvider = contentProvider
    # end setContentProvider()

    def refresh(self):
        numPanes = self.contentProvider.getNumPanes()
        if self.GetFieldsCount() != numPanes:
            self.SetFieldsCount(numPanes)
        widths = []
        styles = []
        for idx in range(0, numPanes):
            widths.append(self.contentProvider.getPaneWidth(idx))
            styles.append(self.contentProvider.getPaneStyle(idx))
        self.SetStatusWidths(widths)
        self.SetStatusStyles(styles)
        for idx in range(0, numPanes):
            paneText = self.contentProvider.getPaneText(idx)
            if paneText is not None:
                self.SetStatusText(paneText, idx)
            else:
                self._refreshPane(idx)
    # end refresh()

    def reposition(self):
        numPanes = self.contentProvider.getNumPanes()
        for idx in range(0, numPanes):
            paneText = self.contentProvider.getPaneText(idx)
            if paneText is None:
                rect = self.GetFieldRect(idx)
                self._repositionPane(idx, rect)
        self.sizeChanged = False
    # end reposition()

    def _onZStatusBarSize(self, event):
        self.reposition()  # for normal size events
        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True
        event.Skip()
    # end _onZStatusBarSize()

    def _onZStatusBarIdle(self, event):
        if self.sizeChanged:
            self.reposition()
        event.Skip()
    # end _onZStatusBarIdle()

# end ZStatusBar
