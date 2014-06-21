from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.models.ui.templates.templatesampledoc import ZTemplatePreviewDocument

# ------------------------------------------------------------------------------
# A model for the template manager window.
# ------------------------------------------------------------------------------
class ZTemplateManagerModel:

    def __init__(self):
        self.service = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        self.sampleDoc = ZTemplatePreviewDocument()
    # end __init__()

    def getService(self):
        return self.service
    # end getService()

    def getTemplates(self):
        return self.service.getTemplates()
    # end getTemplates()
    
    def getTemplateByName(self, name):
        return self.templateService.getTemplateByName(name)
    # end getTemplateByName()

    def getSampleDocument(self):
        return self.sampleDoc
    # end getSampleDocument()

    def removeTemplate(self, template):
        u"Removes a single template." #$NON-NLS-1$
        self.service.deleteTemplate(template.getId())
    # end removeTemplate()

# end ZTemplateManagerModel
