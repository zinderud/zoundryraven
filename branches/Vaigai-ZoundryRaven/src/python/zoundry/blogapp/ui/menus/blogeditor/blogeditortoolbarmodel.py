from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostXhtmlClearValidationMessagesAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostXhtmlTidyAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostXhtmlValidationAction
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostFormatHtmlDropDownAction
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostFormatHtmlAction
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZPluginToolBarModel
from zoundry.blogapp.constants import IZBlogAppToolBarIds
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostCreateThumbnailImageDropDownAction
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostImageAlignDropDownAction
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostImageBorderDropDownAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostFontSettingsAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertExtEntryMarkerContextMenuAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertTableAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSpellCheckAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostToolbarImagesAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostToolbarLinksAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogRichTextFormatAction
from zoundry.blogapp.ui.menus.blogeditor.imagemenumodel import ZImageAlignMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.imagemenumodel import ZImageBorderMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.imagemenumodel import ZImageMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.imagemenumodel import ZImageThumbnailMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.linkmenumodel import ZLinkMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.tablemenumodel import ZTableModelBuilder

#--------------------------------------------------------------------
# Edit control toolbar model.
#--------------------------------------------------------------------
class ZBlogContentEditorToolbarModel(ZPluginToolBarModel):

    def __init__(self, wysiwyg = True):
        ZPluginToolBarModel.__init__(self, IZBlogAppToolBarIds.ZID_BLOG_EDITOR_DESIGNER_TOOLBAR)
        self.wysiwyg = wysiwyg 
        self.setDefaultToolSize(16)
        self.buildModel()
    # end __init__()

    def buildModel(self):
        resourceReg = getResourceRegistry()

        # Font
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.Font"), 10, ZBlogPostFontSettingsAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Font_Settings")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_font.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_font_disabled.png")) #$NON-NLS-1$
        self.addSeparator(15)

        # Bold, Italic, Underline, Strike
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Bold"), 20, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_BOLD) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Bold")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_bold.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_bold_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Italic"), 25, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ITALIC) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Italic")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_italic.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_italic_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Underline"), 30, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_UNDERLINE) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Underline")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_underline.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_underline_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Strikethrough"), 35, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_STRIKETHRU) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Strikethrough")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_strikethrough.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_strikethrough_disabled.png")) #$NON-NLS-1$
        self.addSeparator(40)        
                
        if self.wysiwyg:
            self._buildWysiwygEditorModel(resourceReg)
        else:
            self._buildXhtmlEditorModel(resourceReg)

    # end buildModel()
    
    def _buildWysiwygEditorModel(self, resourceReg):
        # text ustification
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Align_Left"), 45, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ALIGN_LEFT) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Align_Left")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_left.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_left_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Center"), 50, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ALIGN_CENTER) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Center")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_center.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_center_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Align_Right"), 55, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ALIGN_RIGHT) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Align_Right")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_right.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_right_disabled.png")) #$NON-NLS-1$ #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Justify"), 60, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_JUSTIFY) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Justify")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_justify.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_align_justify_disabled.png")) #$NON-NLS-1$
        self.addSeparator(70)        
        
        # Indent
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.Indent"), 75, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_INDENT) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Indent")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_indent.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_indent_disabled.png")) #$NON-NLS-1$
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.De_Indent"), 80, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_OUTDENT) ) #$NON-NLS-1$
        self.setToolDescription(toolId,_extstr(u"blogeditortoolbarmodel.Remove_Indent")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_indent_remove.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_indent_remove_disabled.png")) #$NON-NLS-1$

        self.addSeparator(82)
        # Block quote
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.Blockquote"), 83, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_INDENT) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Blockquote")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_blockquote.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_blockquote_disabled.png")) #$NON-NLS-1$
        self.addSeparator(85)

        # Lists
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Bullet_List"), 90, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_UNORDERED_LIST) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Bulleted_List")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_list_bullets.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_list_bullets_disabled.png")) #$NON-NLS-1$
        toolId = self.addToggleItemWithAction(_extstr(u"blogeditortoolbarmodel.Number_List"), 95, ZBlogRichTextFormatAction(IZRichTextEditControl.ZCAPABILITY_ORDERED_LIST) ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Numbered_List")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_list_numbers.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_list_numbers_disabled.png")) #$NON-NLS-1$

        self.addSeparator(100)

        # Inserts (image, link, etc...)
        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Insert_Image"), 105, ZBlogPostToolbarImagesAction( ZImageMenuModelBuilder().createImageMenuModel() )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Insert_Image")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_image.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_image_disabled.png")) #$NON-NLS-1$\

        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Insert_Link"), 110, ZBlogPostToolbarLinksAction( ZLinkMenuModelBuilder().createToolbarLinkMenuModel() )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Insert_Link")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link_disabled.png")) #$NON-NLS-1$

        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Insert_Table"), 115, ZBlogPostInsertTableAction( ZTableModelBuilder().createToolbarTableMenuModel() )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Insert_Table")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/table.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/table_disabled.png")) #$NON-NLS-1$

        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.Extended_Entry"), 125, ZBlogPostInsertExtEntryMarkerContextMenuAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Insert_Extended_Entry_marker")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_extentry.png")) #$NON-NLS-1$

        # Spell Check
        self.addSeparator(130)
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.Spell_Check"), 135, ZBlogPostSpellCheckAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Check_Spelling")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_spellcheck.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_spellcheck_disabled.png")) #$NON-NLS-1$

    # end _buildWysiwygEditorModel
    
    def _buildXhtmlEditorModel(self, resourceReg):
        # Validate
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.XhtmlValidate"), 137, ZBlogPostXhtmlValidationAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.XhtmlValidateDescription")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/xhtml_valid.png")) #$NON-NLS-1$
        #self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_spellcheck_disabled.png")) #$NON-NLS-1$
        
        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.XhtmlTidy"), 138, ZBlogPostXhtmlTidyAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.XhtmlTidyDescription")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/xhtml_tidy.png")) #$NON-NLS-1$
        #self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_spellcheck_disabled.png")) #$NON-NLS-1$

        toolId = self.addItemWithAction(_extstr(u"blogeditortoolbarmodel.XhtmlClearMessages"), 139, ZBlogPostXhtmlClearValidationMessagesAction()) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.XhtmlClearMessagesDescription")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/xhtml_delete.png")) #$NON-NLS-1$
        #self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_spellcheck_disabled.png")) #$NON-NLS-1$
        
    # end _buildXhtmlEditorModel    
        
# end ZBlogContentEditorToolbarModel()

#--------------------------------------------------------------------
# Wysiwyg editor context tool bar. Eg. Image align.
#--------------------------------------------------------------------
class ZBlogWysiwygEditorContextToolbarModel(ZPluginToolBarModel):

    def __init__(self):
        ZPluginToolBarModel.__init__(self, IZBlogAppToolBarIds.ZID_BLOG_EDITOR_DESIGNER_CONTEXT_TOOLBAR)
        self.setDefaultToolSize(16)
        self.buildModel()
    # end __init__()

    def buildModel(self):
        resourceReg = getResourceRegistry()
        # Image align
        imageAlignMenuModel = ZImageAlignMenuModelBuilder().createImageAlignMenuModel()
        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Align"), 10, ZBlogPostImageAlignDropDownAction(imageAlignMenuModel)) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Align_Image")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_left.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_left_disabled.png")) #$NON-NLS-1$
        # Image border
        imageBorderMenuModel = ZImageBorderMenuModelBuilder().createImageBorderMenuModel()
        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Border"), 20, ZBlogPostImageBorderDropDownAction(imageBorderMenuModel)) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Image_border")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_border.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_border_disabled.png")) #$NON-NLS-1$
        # Image thumbnail options
        tnMenuModel = ZImageThumbnailMenuModelBuilder().createImageThumbnailMenuModel()
        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.Thumbnail"), 30, ZBlogPostCreateThumbnailImageDropDownAction( tnMenuModel )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.Create_Thumbnail")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_thumbnail.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_thumbnail_disabled.png")) #$NON-NLS-1$
        self.addSeparator(35)

        # Format Html
        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.HtmlBlockTags"), 41, ZBlogPostFormatHtmlDropDownAction( ZFormatHtmlMenuModelBuilder(), True )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.HtmlBlockTagsDescription")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/text_heading_1.png")) #$NON-NLS-1$
        #self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_html_disabled.png")) #$NON-NLS-1$

        toolId = self.addDropDownItemWithAction(_extstr(u"blogeditortoolbarmodel.HtmlTags"), 42, ZBlogPostFormatHtmlDropDownAction( ZFormatHtmlMenuModelBuilder(), False )) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditortoolbarmodel.HtmlTagsDescription")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_html.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_html_disabled.png")) #$NON-NLS-1$
        self.addSeparator(45)


    # end buildModel()

# end ZBlogWysiwygEditorContextToolbarModel


#-------------------------------------------
# Menu model used list html tags
#-------------------------------------------
class ZFormatHtmlMenuModelBuilder:

    def createHtmlTagMenuModel(self, tagNames):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_HTML_FORMAT_MENU)
        parentId = None
        gravity = 10
        for tag in tagNames:
            mid = menuModel.addMenuItemWithAction(tag,  gravity, ZBlogPostFormatHtmlAction(tag), parentId ) #$NON-NLS-1$ @UnusedVariable
        return menuModel
    # end createHtmlTagMenuModel()
# end ZFormatHtmlMenuModelBuilder