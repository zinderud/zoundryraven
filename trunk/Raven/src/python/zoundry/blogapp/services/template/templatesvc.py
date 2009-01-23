from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Interface for the template service listener.
# ------------------------------------------------------------------------------
class IZTemplateServiceListener:

    def onTemplateCreated(self, template):
        u"""onTemplateCreated(IZTemplate) -> None""" #$NON-NLS-1$
    # end onTemplateCreated()

    def onTemplateDeleted(self, template):
        u"""onTemplateDeleted(IZTemplate) -> None""" #$NON-NLS-1$
    # end onTemplateDeleted()

    def onTemplateModified(self, template):
        u"""onTemplateModified(IZTemplate) -> None""" #$NON-NLS-1$
    # end onTemplateModified()

# end IZTemplateServiceListener


# ------------------------------------------------------------------------------
# Interface for the template service.
# ------------------------------------------------------------------------------
class IZTemplateService(IZService):

    def addListener(self, listener):
        u"""addListener(IZTemplateServiceListener) -> None""" #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"""removeListener(IZTemplateServiceListener) -> None""" #$NON-NLS-1$
    # end removeListener()

    def createTemplate(self):
        u"""createTemplate() -> IZTemplate
        Creates a new empty template (must be saved).""" #$NON-NLS-1$
    # end createTemplate()

    def getTemplates(self):
        u"""getTemplates() -> IZTemplate[]
        Returns a list of all templates.""" #$NON-NLS-1$
    # end getTemplates()

    def getTemplate(self, templateId):
        u"""getTemplate(id) -> IZTemplate
        Gets the template with the given ID.""" #$NON-NLS-1$
    # end getTemplate()

    def getTemplateByName(self, templateName):
        u"""getTemplateByName(string) -> IZTemplate
        Gets the template with the given name.""" #$NON-NLS-1$
    # end getTemplateByName()

    def deleteTemplate(self, templateId):
        u"""deleteTemplate(id) -> boolean
        Deletes a template.""" #$NON-NLS-1$
    # end deleteTemplate()

    def saveTemplate(self, template):
        u"""saveTemplate(IZTemplate) -> None
        Saves the template to disk.""" #$NON-NLS-1$
    # end saveTemplate()

# end IZTemplateService
