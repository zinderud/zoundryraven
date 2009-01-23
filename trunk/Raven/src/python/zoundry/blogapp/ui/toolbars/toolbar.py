from zoundry.appframework.global_services import getResourceRegistry
import wx


# -----------------------------------------------------------------------------------------
# Gets a toolbar bitmap with a given name.
# -----------------------------------------------------------------------------------------
def getToolbarBitmap(name):
    return getResourceRegistry().getBitmap(u"images/mainapp/toolbar/%s.png" % name) #$NON-NLS-1$
# end getToolbarBitmap()


# -----------------------------------------------------------------------------------------
# Creates the main toolbar for the application.
# -----------------------------------------------------------------------------------------
def createMainToolBar(app):
    toolbar = app.CreateToolBar(wx.TB_TEXT | wx.NO_BORDER | wx.TB_FLAT)
    toolbar.SetToolBitmapSize(wx.Size(24, 24))
    toolbar.AddLabelTool(wx.ID_ANY, u"New", getToolbarBitmap(u"new"), wx.NullBitmap) #$NON-NLS-2$ #$NON-NLS-1$
    toolbar.AddLabelTool(wx.ID_ANY, u"Cut", getToolbarBitmap(u"cut"), wx.NullBitmap) #$NON-NLS-2$ #$NON-NLS-1$
    toolbar.AddLabelTool(wx.ID_ANY, u"Copy", getToolbarBitmap(u"copy"), wx.NullBitmap) #$NON-NLS-2$ #$NON-NLS-1$
    toolbar.AddLabelTool(wx.ID_ANY, u"Paste", getToolbarBitmap(u"paste"), wx.NullBitmap) #$NON-NLS-2$ #$NON-NLS-1$
    
    return toolbar
# end createMainToolBar()
