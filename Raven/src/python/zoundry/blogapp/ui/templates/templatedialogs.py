from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZNonEmptySelectionValidator
from zoundry.appframework.ui.widgets.dialogs.validating import ZValidatingHeaderDialog
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.blogeditorctrls.blogselector import IZBlogSelectorModel
from zoundry.blogapp.ui.editors.blogeditorctrls.validatingblogselector import ZValidatingBlogSelectorCombo
import wx

# ------------------------------------------------------------------------------
# Model used by the add template from blog dialog.
# ------------------------------------------------------------------------------
class ZAddTemplateFromBlogModel(IZBlogSelectorModel):

    def __init__(self):
        self.templateService = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
    # end __init__()

    def getTemplateByName(self, name):
        return self.templateService.getTemplateByName(name)
    # end getTemplateByName()

    def getAllBlogs(self):
        blogs = []
        for account in self.accountStore.getAccounts():
            for blog in account.getBlogs():
                blogs.append(blog)
        return blogs
    # end getAllBlogs()

    def getAllAccounts(self):
        return self.accountStore.getAccounts()
    # end getAllAccounts()

# end ZAddTemplateFromBlogModel


# ------------------------------------------------------------------------------
# Used to validate the value of the template name.
# ------------------------------------------------------------------------------
class ZTemplateNameValidator(ZBaseControlValidator):

    def __init__(self, model):
        self.model = model
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(_extstr(u"templatedialogs.PleaseEnterTemplateName")) #$NON-NLS-1$

        template = self.model.getTemplateByName(value)
        if template:
            return self._setReason(_extstr(u"templatedialogs.TemplateAlreadyExists")) #$NON-NLS-1$

        return True
    # end _isValid()

# end ZTemplateNameValidator


# ------------------------------------------------------------------------------
# The Add Template (from Blog) dialog.  This dialog prompts the user for
# information needed to create a new template by downloading information from
# a blog.
# ------------------------------------------------------------------------------
class ZAddTemplateFromBlogDialog(ZValidatingHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.model = ZAddTemplateFromBlogModel()

        ZValidatingHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"templatedialogs.AddTemplate")) #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.ADD_TEMPLATE_FROM_BLOG_DIALOG, True, True)
    # end __init__()

    def getSelectedBlog(self):
        return self.blogPicker.getBlog()
    # end getSelectedBlog()

    def getTemplateName(self):
        return self.templateNameText.GetValue()
    # end getTemplateName()

    def isMakeDefaultTemplate(self):
        return self.makeDefaultTemplateCB.IsChecked()
    # end isMakeDefaultTemplate()

    def selectBlog(self, blog):
        self.blogPicker.selectBlog(blog.getAccount().getId(), blog.getId())
        self.blogPicker.validate()
    # end selectBlog()

    def _createNonHeaderWidgets(self):
        self.blogLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"templatedialogs.FromBlog")) #$NON-NLS-1$ #$NON-NLS-2$
        self.blogPicker = ZValidatingBlogSelectorCombo(ZNonEmptySelectionValidator(_extstr(u"templatedialogs.ChooseABlog")), self.model, self) #$NON-NLS-1$
        self.templateNameLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"templatedialogs.TemplateName")) #$NON-NLS-1$ #$NON-NLS-2$
        self.templateNameText = ZValidatingTextCtrl(ZTemplateNameValidator(self.model), self, wx.ID_ANY)
        self.templateNameText.SetToolTipString(_extstr(u"templatedialogs.PickAFriendlyTemplateName")) #$NON-NLS-1$
        self.makeDefaultTemplateCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"templatedialogs.MakeThisTemplateTheDefault")) #$NON-NLS-1$

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self.makeDefaultTemplateCB.SetValue(True)
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        # Flexible grid sizer where all of the label->text ctrl pairs will live
        flexGridSizer = wx.FlexGridSizer(2, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        flexGridSizer.Add(self.blogLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.blogPicker, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.templateNameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.templateNameText, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(wx.StaticText(self, wx.ID_ANY, u""), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5) #$NON-NLS-1$
        flexGridSizer.Add(self.makeDefaultTemplateCB, 0, wx.EXPAND | wx.RIGHT, 5)

        # Static box sizer that has a label of "Profile Info"
        boxSizer = wx.BoxSizer(wx.VERTICAL)
        boxSizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 5)
        boxSizer.Add(self.staticLine, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 3)
        return boxSizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self._bindValidatingWidget(self.blogPicker)
        self._bindValidatingWidget(self.templateNameText)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self.blogPicker.SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return _extstr(u"templatedialogs.AddTemplateFromBlog") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"templatedialogs.DialogDescriptionMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/template/manager/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def setProfilePath(self, path):
        self.profilePathCtrl.setPath(path)
    # end setProfilePath()

    def setProfileName(self, name):
        self.profileNameText.SetValue(name)
    # end setProfileName()

# end ZAddTemplateFromBlogDialog
