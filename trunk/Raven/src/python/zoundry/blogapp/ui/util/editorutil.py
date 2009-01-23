# ------------------------------------------------------------------------------------
# Module containing utility method for the editor control.
# ------------------------------------------------------------------------------------
from zoundry.base.util.urlutil import getUriFromFilePath
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.dialogs.editimagemodel import ZEditImageModel
from zoundry.blogapp.models.ui.dialogs.editlinkmodel import ZEditLinkModel
from zoundry.blogapp.models.ui.dialogs.findreplacemodel import ZFindReplaceTextModel
from zoundry.blogapp.models.ui.dialogs.fontmodel import ZFontModel
from zoundry.blogapp.models.ui.dialogs.spellcheckmodel import ZSpellCheckModel
from zoundry.blogapp.models.ui.dialogs.tablemodel import ZHtmlTableModel
from zoundry.blogapp.ui.dialogs.findreplacedialog import ZFindReplaceDialog
from zoundry.blogapp.ui.dialogs.fontdialog import ZFontDialog
from zoundry.blogapp.ui.dialogs.imagedialog import ZImageDialog
from zoundry.blogapp.ui.dialogs.linkdialog import ZLinkDialog
from zoundry.blogapp.ui.dialogs.spellcheckdialog import ZSpellCheckDialog
from zoundry.blogapp.ui.dialogs.tabledialog import ZInsertTableDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.blogapp.ui.util.settingsutil import showRavenSettingsDialog
import wx


# ------------------------------------------------------------------------------------
# Editor link create/edit util
# ------------------------------------------------------------------------------------
class ZLinkUiUtil:

    def editLink(self, parentWindow, linkContext):
        u"""editLink(wxWindow, IZXHTMLEditControlLinkContext) -> void
        Shows the create and edit link dialog.
        """ #$NON-NLS-1$
        model = ZEditLinkModel(linkContext.getLinkAttributes())
        dialog = ZLinkDialog(parentWindow, model)
        dialog.CentreOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            attrs = model.getLinkAttributes()
            linkContext.setLinkAttributes(attrs)
        dialog.Destroy()
    # end editLink()
# end ZLinkUiUtil

# ------------------------------------------------------------------------------------
# Editor img create/edit util
# ------------------------------------------------------------------------------------
class ZImageUiUtil:

    def editImage(self, parentWindow, imageContext):
        u"""editImage(wxWindow, IZXHTMLImageControlLinkContext) -> void
        Shows the create and edit image dialog.
        """ #$NON-NLS-1$
        model = ZEditImageModel(imageContext.getImageAttributes())
        dialog = ZImageDialog(parentWindow, model)
        dialog.CentreOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            attrs = model.getImageAttributes()
            imageContext.setImageAttributes(attrs)
        dialog.Destroy()
    # end editImage()

    def insertImageFile(self, parentWindow, imageContext):
        u"""insertImageFile(wxWindow, IZXHTMLEditControlImageContext) -> void
        Shows the File open dialog to display an image.
        """ #$NON-NLS-1$
        file = None
        wildcard = u"Image files|*.gif;*.jpg;*.png;*.jpeg" #$NON-NLS-1$
        dialog = wx.FileDialog(parentWindow, u"Choose an image file.", u"", u"", wildcard, wx.OPEN) #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        if dialog.ShowModal() == wx.ID_OK:
            file = getNoneString(dialog.GetPath())
        dialog.Destroy()
        if file:
            (shortName, absPath, size, schemaDate) = getFileMetaData(file) #@UnusedVariable
            if shortName:
                shortName = convertToUnicode(shortName)
            else:
                shortName = u"" #$NON-NLS-1$
            url = getUriFromFilePath(absPath)                    
            attrs = { u"src" : url, u"alt" : shortName} #$NON-NLS-1$ #$NON-NLS-2$
            imageContext.insertImage(attrs)
    # end insertImageFile()

    def insertImageTag(self, parentWindow, imageContext):
        u"""insertImageTag(wxWindow, IZXHTMLEditControlImageContext) -> void
        Shows the Image dialog to allow user to enter img src attrs.
        """ #$NON-NLS-1$
        model = ZEditImageModel(None)
        dialog = ZImageDialog(parentWindow, model)
        dialog.CentreOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            attrs = model.getImageAttributes()
            imageContext.setImageAttributes(attrs)
        dialog.Destroy()
    # end insertImageTag()

# end ZImageUiUtil

# ------------------------------------------------------------------------------------
# Editor spellcheck util
# ------------------------------------------------------------------------------------
class ZSpellCheckUiUtil:

    def runSpellCheck(self, parentWindow, spellcheckContext):
        if spellcheckContext is None:
            ZShowInfoMessage(parentWindow, _extstr(u"spellcheckuiutil.SpellcheckNotSupported"), _extstr(u"spellcheckdialog.DialogTitle") ) #$NON-NLS-1$ #$NON-NLS-2$
            return
        model = ZSpellCheckModel(spellcheckContext)
        if not model.isSpellcheckEnabled():
            message = _extstr(u"spellcheckuiutil.SpellcheckNotEnabledQuestion") #$NON-NLS-1$
            title = _extstr(u"spellcheckdialog.DialogTitle") #$NON-NLS-1$
            if ZShowYesNoMessage(parentWindow, message, title ):
                showRavenSettingsDialog(parentWindow, u"zoundry.appframework.ui.preferences.prefpage.spelling") #$NON-NLS-1$
                if not model.isSpellcheckEnabled():
                    return
            else:
                return

        # Init model
        model.initializeSpellcheckContext()
        # check first mispelled word\
        spellcheckResult = model.checkNextWord()
        if spellcheckResult and not spellcheckResult.isFinished():
            dialog = ZSpellCheckDialog(parentWindow, model)
            dialog.ShowModal()
            dialog.Destroy()
            spellcheckResult = model.checkNextWord()
        model.cleanupSpellcheckContext()
        if spellcheckResult and spellcheckResult.isFinished():
            ZShowInfoMessage(parentWindow, _extstr(u"spellcheckuiutil.SpellcheckCompleted"), _extstr(u"spellcheckdialog.DialogTitle") ) #$NON-NLS-1$ #$NON-NLS-2$
    # end runSpellCheck()
# end ZSpellCheckUiUtil

# ------------------------------------------------------------------------------------
# Editor find and find/replace util
# ------------------------------------------------------------------------------------
class ZFindReplaceUiUtil:

    def runFindReplace(self, parentWindow, findReplaceContext):
        model = ZFindReplaceTextModel(findReplaceContext)
        model.initializeFindReplaceContext()
        dialog = ZFindReplaceDialog(parentWindow, model)
        dialog.ShowModal()
        dialog.Destroy()
        model.cleanupFindReplaceContext()
    # end runFindReplace()
# end ZFindReplaceUiUtil

# ------------------------------------------------------------------------------------
# Editor CSS property util
# ------------------------------------------------------------------------------------
class ZCssStyleUiUtil:

    def setFontSettings(self, parentWindow, izXHTMLEditControlStyleContext):
        model = ZFontModel(izXHTMLEditControlStyleContext)
        dialog = ZFontDialog(parentWindow, model)
        if dialog.ShowModal()  == wx.ID_OK:
            izXHTMLEditControlStyleContext.applyStyle(model.getFontInfo(), model.getColor(), model.getBackground() )
        dialog.Destroy()
    # end setFontSettings()
# end ZCssStyleUiUtil

# ------------------------------------------------------------------------------------
# Html table create/edit util
# ------------------------------------------------------------------------------------
class ZTableUiUtil:

    def insertTable(self, parentWindow, tableContext):
        u"""insertTable(wxWindow, IZXHTMLEditControlTableContext) -> void
        Shows the create and edit table dialog.
        """ #$NON-NLS-1$
        model = ZHtmlTableModel(None)
        dialog = ZInsertTableDialog(parentWindow, model)
        dialog.CentreOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            attrs = model.getTableAttributes()
            tableContext.insertTable(attrs)
        dialog.Destroy()
    # end insertTable()

    def editTable(self, parentWindow, tableContext):
        u"""editTable(wxWindow, IZXHTMLEditControlTableContext) -> void
        Shows the create and edit table dialog.
        """ #$NON-NLS-1$
        model = ZHtmlTableModel( tableContext.getTableAttributes() )
        dialog = ZInsertTableDialog(parentWindow, model)
        dialog.CentreOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            attrs = model.getTableAttributes()
            tableContext.setTableAttributes(attrs)
        dialog.Destroy()
    # end editTable()
# end ZTableUiUtil

