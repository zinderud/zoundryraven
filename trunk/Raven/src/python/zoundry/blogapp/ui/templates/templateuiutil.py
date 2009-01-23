from zoundry.base.xhtml.xhtmldocutil import removeJavaScript
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.dialogs.bgtaskprogressdialog import ZBackgroundTaskProgressDialog
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.template.templategrabber import ZBlogTemplateGrabberBGTask
from zoundry.blogapp.ui.templates.templatedialogs import ZAddTemplateFromBlogDialog
import wx

# ------------------------------------------------------------------------------
# Convenience function that lets the user download a template from a blog.
# ------------------------------------------------------------------------------
def doTemplateDownload(parentWindow, blog = None):
    dialog = ZAddTemplateFromBlogDialog(parentWindow)
    if blog is not None:
        dialog.selectBlog(blog)
    if dialog.ShowModal() == wx.ID_OK:
        blog = dialog.getSelectedBlog()
        templateName = dialog.getTemplateName()
        makeDefaultTemplate = dialog.isMakeDefaultTemplate()

        task = ZBlogTemplateGrabberBGTask()
        task.initialize(blog, templateName, makeDefaultTemplate)
        taskService = getApplicationModel().getService(IZBlogAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        taskService.addTask(task)
        
        title = task.getName()
        description = _extstr(u"templateuiutil.DownloadingBlogTemplate") % blog.getName() #$NON-NLS-1$
        imagePath = u"images/dialogs/bgtask/header_image.png" #$NON-NLS-1$
        taskDialog = ZBackgroundTaskProgressDialog(parentWindow, task, title, description, imagePath)
        taskDialog.ShowModal()
        taskDialog.Destroy()

    dialog.Destroy()
# end doTemplateDownload()

# ------------------------------------------------------------------------------
# Disables javascript by removing script references from the xhtml document.
# ------------------------------------------------------------------------------
def disableTemplatePreviewJavaScript(xhtmlDoc):
    removeJavaScript(xhtmlDoc)
# end disableTemplatePreviewJavaScript        
    
