from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesDialog

# ------------------------------------------------------------------------------
# Displays the application preferences dialog, optionally jumping to a specific
# page id.
# ------------------------------------------------------------------------------
def showRavenSettingsDialog(parent, jumpToPageId = None):
    prefsDialog = ZApplicationPreferencesDialog(parent, jumpToPageId)
    prefsDialog.ShowModal()
    prefsDialog.Destroy()
# end showRavenSettingsDialog()
