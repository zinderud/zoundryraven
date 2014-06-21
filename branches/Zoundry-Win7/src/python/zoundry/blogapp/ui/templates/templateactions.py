from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarAction
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.templates.templateuiutil import doTemplateDownload

# ------------------------------------------------------------------------------
# Action to add a template from a blog.
# ------------------------------------------------------------------------------
class ZAddTemplateFromBlogAction(ZMenuAction):

    def runAction(self, actionContext):
        doTemplateDownload(actionContext.getParentWindow())
    # end runAction()

# end ZAddTemplateFromBlogAction


# ------------------------------------------------------------------------------
# Action to remove a template.
# ------------------------------------------------------------------------------
class ZRemoveTemplateAction(ZToolBarAction):

    def isEnabled(self, context): #@UnusedVariable
        return context.getTemplate() is not None
    # end isEnabled()

    def runAction(self, actionContext):
        template = actionContext.getTemplate()
        window = actionContext.getParentWindow()
        if template is not None and self._confirmDelete(window, template):
            service = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
            service.deleteTemplate(template.getId())
    # end runAction()

    def _confirmDelete(self, parent, template):
        title = _extstr(u"templateactions.DeleteTemplateTitle") #$NON-NLS-1$
        message = _extstr(u"templateactions.DeleteTemplateMsg") % template.getName() #$NON-NLS-1$
        return ZShowYesNoMessage(parent, message, title)
    # end _confirmDelete()

# end ZRemoveTemplateAction
