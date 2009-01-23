from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.dialogs.prefpage import IZUserPreferencePageSession
from zoundry.appframework.ui.dialogs.prefpage import ZUserPreferencePage
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.tree import IZTreeViewVisitor
from zoundry.appframework.ui.widgets.controls.tree import ZTreeView
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx


# ------------------------------------------------------------------------------
# A simple tree view visitor that is used to locate the tree item id for a 
# given node id.
# ------------------------------------------------------------------------------
class ZTreeItemIdFinder(IZTreeViewVisitor):

    def __init__(self, nodeId, getNodeIdFunc):
        self.nodeId = nodeId
        self.getNodeIdFunc = getNodeIdFunc
        self.foundTreeItemId = None
    # end __init__()

    def visit(self, node, metaData):
        if self.getNodeIdFunc(node) == self.nodeId:
            self.foundTreeItemId = metaData[u"id"] #$NON-NLS-1$
    # end visit()

    def getTreeItemId(self):
        return self.foundTreeItemId
    # end getTreeItemId()

# end ZTreeItemIdFinder


# ---------------------------------------------------------------------------------------
# The default preference page to use when nothing is selected.
# ---------------------------------------------------------------------------------------
class ZDefaultPreferencePage(ZUserPreferencePage):

    def __init__(self, parent):
        ZUserPreferencePage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return IZUserPreferencePageSession()
    # end _createSession()

    def isDirty(self):
        return False
    # end isDirty()

    def isValid(self):
        return True
    # end isValid()

# end ZDefaultPreferencePage


# ------------------------------------------------------------------------------
# Base class for preferences dialogs.  This is a base class and is meant to be
# extended to be used properly.  The appropriate methods from ZHeaderDialog
# should be implemented, as well as some additional 'abstract' methods defined
# here.  A preferences dialog is basically a dialog with a splitter window.  The
# left side of the splitter is a tree control, while the right side is an 
# instance of ZUserPreferencePage.
# ------------------------------------------------------------------------------
class ZPreferencesDialog(ZHeaderDialog):

    def __init__(self, parent, jumpToPageId = None):
        self.currentSelection = None
        self.currentPage = None
        self.currentPageId = None
        self.pageCache = {}
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        title = self._getDialogTitle()
        size = self._getInitialSize()
        
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, title, name = u"PrefsDialog", style = style, size = size) #$NON-NLS-1$

        self._enableButtons(False)
        self.jumpToPage(jumpToPageId)
        self.prefsTreeView.SetFocus()
    # end __init__()
    
    def _getNonHeaderContentBorder(self):
        return 0
    # end _getNonHeaderContentBorder()

    def _createNonHeaderWidgets(self):
        self.splitterWindow = ZSplitterWindow(self)
        self.splitterWindow.SetMinimumPaneSize(100)
        self.splitterWindow.SetSashSize(3)

        self.leftPanel = self._createLeftTreePanel()
        self.currentPage = self._createDefaultPage()
        self.currentPageId = None

        self.splitterWindow.SplitVertically(self.leftPanel, self.currentPage, 175)

        self.lowerStaticLine = wx.StaticLine(self)
    # end _createNonHeaderWidgets()

    def _createLeftTreePanel(self):
        panel = ZTransparentPanel(self.splitterWindow, wx.ID_ANY, style = wx.NO_BORDER)

        # Create the prefs tree view.
        provider = self._createTreeProvider()
        treeStyle = wx.NO_BORDER | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_HAS_BUTTONS
        self.prefsTreeView = ZTreeView(provider, panel, style = treeStyle)
        self.prefsTreeView.refresh()
        
        self.treeButtons = self._createTreeButtons(panel)

        # Create a little static vertical line (aesthetic only)
        self.middleStaticLine = wx.StaticLine(panel, style = wx.LI_VERTICAL)

        return panel
    # end _createLeftTreePanel()
    
    def _createTreeButtons(self, parent): #@UnusedVariable
        return []
    # end _createTreeButtons()

    # This is the page created when no pref page is selected.
    def _createDefaultPage(self):
        defaultPrefPage = ZDefaultPreferencePage(self.splitterWindow)
        return defaultPrefPage
    # end _createDefaultPage()

    def _populateNonHeaderWidgets(self):
        self._enableApplyButton(False)
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        treeSizer = wx.BoxSizer(wx.VERTICAL)
        treeSizer.Add(self.prefsTreeView, 1, wx.EXPAND)
        for button in self.treeButtons:
            treeSizer.Add(button, 0, wx.EXPAND | wx.ALL, 2)
        
        leftPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftPanelSizer.Add(treeSizer, 1, wx.EXPAND)
        leftPanelSizer.Add(self.middleStaticLine, 0, wx.EXPAND)
        self.leftPanel.SetAutoLayout(True)
        self.leftPanel.SetSizer(leftPanelSizer)
        self.leftPanel.Layout()

        verticalSizer = wx.BoxSizer(wx.VERTICAL)
        verticalSizer.Add(self.splitterWindow, 1, wx.EXPAND)
        verticalSizer.Add(self.lowerStaticLine, 0, wx.EXPAND)
        return verticalSizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeItemSelected, self.prefsTreeView)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.onTreeItemChanging, self.prefsTreeView)

        self._bindOkButton(self.onOK)
        self._bindCancelButton(self.onCancel)
        self._bindApplyButton(self.onApply)
    # end _bindWidgetEvents()

    def onTreeItemChanging(self, event):
        if self.currentPage is not None:
            if self.currentPage.isDirty():
                # FIXME (EPW) provide override for this message and title
                if not ZShowYesNoMessage(self, _extstr(u"prefsdialog.PrefPageSwitchMessage"), _extstr(u"prefsdialog.DiscardChanges")): #$NON-NLS-2$ #$NON-NLS-1$
                    event.Veto()
                    return
                else:
                    self.currentPage.rollback()
        event.Skip()
    # end onTreeItemChanging()

    def onTreeItemSelected(self, event):
        node = self.prefsTreeView.GetPyData(event.GetItem())
        self.currentSelection = node
        self._updateHeader()
        self._changePreferencePage()

        event.Skip()
    # end onTreeItemSelected()

    # This method is called when the user is changing to a new preference page.
    def _changePreferencePage(self):
        oldPage = self.currentPage
        oldPage.Show(False)

        if self.currentSelection is None:
            self.currentPage = self._createDefaultPage()
            self.currentPage.Show(True)
        elif self.currentSelection in self.pageCache:
            self.currentPage = self.pageCache[self.currentSelection]
            self.currentPage.Show(True)
        else:
            # Construct the preference page.
            self.currentPage = self._createPrefPage(self.splitterWindow, self.currentSelection)
            self.currentPage.setPrefsDialog(self)

            # Create, populate, layout the page.
            self.currentPage.createWidgets()
            self.currentPage.bindWidgetEvents()
            self.currentPage.populateWidgets()
            self.currentPage.layoutWidgets()
            self.pageCache[self.currentSelection] = self.currentPage
        # Call rollback here, which should clear out the page's session
        # and force it to update its visual state (this is useful when one
        # pref page's initial visual state depends on another page's data, 
        # which may have changed since this page was created).
        self.currentPage.rollback()

        self.currentPageId = self._resolveNodeId(self.currentSelection)
        
        self.splitterWindow.ReplaceWindow(oldPage, self.currentPage)
        self.splitterWindow.Layout()
        self.currentPage.Layout()
    # end _changePreferencePage()

    def _getButtonTypes(self):
        return ZBaseDialog.OK_BUTTON | ZBaseDialog.CANCEL_BUTTON | ZBaseDialog.APPLY_BUTTON
    # end _getButtonTypes()

    # Called by the active pref page when the user changes something.
    def onPrefPageChange(self):
        if self.currentPage is not None:
            if self.currentPage.isDirty() and self.currentPage.isValid():
                self._enableButtons(True)
            else:
                self._enableButtons(False)
    # end onPrefPageChange()

    def _enableButtons(self, enabled = True):
        self._enableOkButton(enabled)
        self._enableApplyButton(enabled)
        cancelButton = self.FindWindowById(wx.ID_CANCEL)
        if enabled:
            cancelButton.SetLabel(_extstr(u"Cancel")) #$NON-NLS-1$
        else:
            cancelButton.SetLabel(_extstr(u"Close")) #$NON-NLS-1$
    # end _enableButtons()

    def onOK(self, event):
        try:
            self.currentPage.apply()
            self._destroyPages()
        except Exception, e:
            ZShowExceptionMessage(self, e)
        event.Skip()
    # end OnOk()

    def onApply(self, event):
        if self.currentPage.apply():
            self._enableButtons(False)
        event.Skip()
    # end OnApply()

    def onCancel(self, event):
        try:
            if self.currentPage:
                self.currentPage.rollback()
            self._destroyPages()
        except Exception, e:
            ZShowExceptionMessage(self, e)
        self._destroy()
        event.Skip()
    # end onCancel()

    def _destroyPages(self):
        for key in self.pageCache:
            page = self.pageCache[key]
            page.destroy()
    # end _destroyPages()
    
    def _destroy(self):
        pass
    # end _destroy()

    def jumpToPage(self, jumpToPageId):
        if jumpToPageId is None:
            jumpToPageId = self._getDefaultPageId()
        if jumpToPageId is not None:
            treeItemId = self._findTreeItemByNodeId(jumpToPageId)
            if treeItemId is not None:
                self.prefsTreeView.SelectItem(treeItemId)
    # end jumpToPage()
    
    def _findTreeItemByNodeId(self, nodeId):
        finder = ZTreeItemIdFinder(nodeId, self._resolveNodeId)
        self.prefsTreeView.accept(finder)
        return finder.getTreeItemId()
    # end _findTreeItemByNodeId()
    
    def _resolveNodeId(self, treeNode):
        raise ZAbstractMethodCalledException(self.__class__, u"_resolveNodeId") #$NON-NLS-1$
    # end _resolveNodeId()

    def _getDefaultPageId(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getDefaultPageId") #$NON-NLS-1$
    # end _getDefaultPageId()

    def _getDialogTitle(self):
        return self._getHeaderTitle()
    # end _getDialogTitle()
    
    def _createTreeProvider(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_createTreeProvider") #$NON-NLS-1$
    # end _createTreeProvider()

    def _createPrefPage(self, parent, currentSelection):
        raise ZAbstractMethodCalledException(self.__class__, u"_createPrefPage") #$NON-NLS-1$
    # end _createPrefPage()
    
    def _getInitialSize(self):
        return wx.Size(550, 450)
    # end _getInitialSize()
    
# end ZPreferencesDialog
