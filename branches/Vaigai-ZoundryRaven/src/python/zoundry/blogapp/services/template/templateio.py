from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.services.template.io.factory import getTemplateDeserializerFactory
from zoundry.blogapp.services.template.io.factory import getTemplateSerializerFactory
from zoundry.appframework.global_services import getLoggerService
import os

# ----------------------------------------------------------------------------------------
# This function takes a directory to a Raven Template and loads it into a ZTemplate 
# instance, using the deserialization framework.
# ----------------------------------------------------------------------------------------
def loadTemplate(templateDir):
    try:
        templateXmlPath = os.path.join(templateDir, u"template.xml") #$NON-NLS-1$
        dom = ZDom()
        dom.load(templateXmlPath)

        deserializer = getTemplateDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(templateDir, dom)
    except Exception, e:
        raise ZBlogAppException(u"Failed to load template: %s" % templateDir, e) #$NON-NLS-1$
# end loadTemplate()


# ----------------------------------------------------------------------------------------
# This function takes a IZTemplate instance and serializes it to disk into the given 
# template directory.
# ----------------------------------------------------------------------------------------
def saveTemplate(template):
    try:
        serializer = getTemplateSerializerFactory().getSerializer()
        serializer.serialize(template)
    except Exception, e:
        getLoggerService().exception(e)
        raise ZBlogAppException(u"Failed to save template: %s" % template.getDirectoryPath(), e) #$NON-NLS-1$
# end saveTemplate()
