from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.guid import generate
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.services.template.templateimpl import ZTemplate
from zoundry.blogapp.services.template.templateio import loadTemplate
from zoundry.blogapp.services.template.templateio import saveTemplate
from zoundry.blogapp.services.template.templatesvc import IZTemplateService
import os


# ------------------------------------------------------------------------------
# A filter function for use in the getDirectoryListing() method.  This will
# return true only for template directories.
# ------------------------------------------------------------------------------
def templateDirectoryFilter(path):
    templateXmlPath = os.path.join(path, u"template.xml") #$NON-NLS-1$
    return os.path.isdir(path) and os.path.isfile(templateXmlPath)
# end templateDirectoryFilter()


# ------------------------------------------------------------------------------
# Implementation of the template service.
# ------------------------------------------------------------------------------
class ZTemplateService(IZTemplateService):

    def __init__(self):
        self.templateDir = None
        self.templates = None
        self.listeners = ZListenerSet()
    # end __init__()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.applicationModel = applicationModel
        userProfile = self.applicationModel.getUserProfile()
        self.templateDir = userProfile.getDirectory(u"templates") #$NON-NLS-1$

        self.templates = self._loadTemplates()
        self.logger.debug(u"Template Service started [%d templates loaded]" % len(self.templates)) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.templateDir = None
        self.templates = None
    # end stop()

    def getTemplates(self):
        return self.templates
    # end getTemplates()

    def createTemplate(self):
        guid = generate()
        templateDir = self._getDirForNewTemplate(guid)
        template = ZTemplate(templateDir, guid)
        template.setCreationTime(ZSchemaDateTime())
        template.setLastModifiedTime(ZSchemaDateTime())
        return template
    # end createTemplate()

    def getTemplate(self, templateId):
        for template in self.templates:
            if template.getId() == templateId:
                return template
        return None
    # end getTemplate()

    def getTemplateByName(self, templateName):
        for template in self.templates:
            if template.getName() == templateName:
                return template
        return None
    # end getTemplateByName()

    def deleteTemplate(self, templateId):
        template = self.getTemplate(templateId)
        if template is not None:
            self.templates.remove(template)
            deleteDirectory(template.getTemplateDirectory(), True)
            self._fireDeletedTemplateEvent(template)
            return True
        return False
    # end deleteTemplate()

    def saveTemplate(self, template):
        if not (template in self.templates):
            self.templates.append(template)
            self._fireNewTemplateEvent(template)
        else:
            self._fireModifiedTemplateEvent(template)
        saveTemplate(template)
    # end saveTemplate()

    def _getDirForNewTemplate(self, guid):
        path = os.path.join(self.templateDir, guid)
        return path
    # end _getDirForNewTemplate()

    def _loadTemplates(self):
        templateDirs = getDirectoryListing(self.templateDir, templateDirectoryFilter)
        templates = []
        for template in map(self._loadTemplate, templateDirs):
            if template is not None:
                templates.append(template)
        return templates
    # end _loadTemplates()

    def _loadTemplate(self, templateDir):
        try:
            return loadTemplate(templateDir)
        except Exception, e:
            self.logger.exception(e)
            return None
    # end _loadTemplate()

    def _fireNewTemplateEvent(self, template):
        for listener in self.listeners:
            try:
                listener.onTemplateCreated(template)
            except Exception, e:
                self.logger.exception(e)
    # end _fireNewTemplateEvent()

    def _fireModifiedTemplateEvent(self, template):
        for listener in self.listeners:
            try:
                listener.onTemplateModified(template)
            except Exception, e:
                self.logger.exception(e)
    # end _fireModifiedTemplateEvent()

    def _fireDeletedTemplateEvent(self, template):
        for listener in self.listeners:
            try:
                listener.onTemplateDeleted(template)
            except Exception, e:
                self.logger.exception(e)
    # end _fireDeletedTemplateEvent()

# end ZTemplateService
