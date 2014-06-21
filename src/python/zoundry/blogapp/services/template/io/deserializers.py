from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.services.template.templateimpl import ZTemplate

# -----------------------------------------------------------------------------------------
# The interface that all template deserializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZTemplateDeserializer:

    def deserialize(self, templateDirectory, templateDom):
        u"Called to deserialize a template.  This should return an instance of IZTemplate." #$NON-NLS-1$
    # end deserialize()

# end IZTemplateDeserializer


# -----------------------------------------------------------------------------------------
# An implementation of an template deserializer for version 1.0 (or 2006/06) of the Zoundry
# Raven template format.
# -----------------------------------------------------------------------------------------
class ZBlogTemplateDeserializer(IZTemplateDeserializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, templateDirectory, templateDom):
        templateDom.setNamespaceMap(self.nssMap)
        template = ZTemplate(templateDirectory, templateDom.documentElement.getAttribute(u"template-id")) #$NON-NLS-1$

        self._deserializeTemplate(template, templateDom)

        return template
    # end deserialize()

    def _deserializeTemplate(self, template, templateDom):
        rootNode = templateDom.selectSingleNode(u"/zns:template/zns:root") #$NON-NLS-1$
        nameNode = templateDom.selectSingleNode(u"/zns:template/zns:name") #$NON-NLS-1$
        sourceNode = templateDom.selectSingleNode(u"/zns:template/zns:source") #$NON-NLS-1$
        allFileNode = templateDom.selectSingleNode(u"/zns:template/zns:allFile") #$NON-NLS-1$
        titleAndBodyFileNode = templateDom.selectSingleNode(u"/zns:template/zns:bodyAndTitleFile") #$NON-NLS-1$
        bodyOnlyFileNode = templateDom.selectSingleNode(u"/zns:template/zns:bodyOnlyFile") #$NON-NLS-1$
        creationTimeNode = templateDom.selectSingleNode(u"/zns:template/zns:creationTime") #$NON-NLS-1$
        lastModifiedTimeNode = templateDom.selectSingleNode(u"/zns:template/zns:lastModifiedTime") #$NON-NLS-1$
        
        root = rootNode.getText()
        if nameNode:
            name = nameNode.getText()
        else:
            name = u"Unnamed Template" #$NON-NLS-1$

        if sourceNode:
            source = sourceNode.getText()
        else:
            source = u"Zoundry Raven Alpha" #$NON-NLS-1$
        allFile = allFileNode.getText()
        titleAndBodyFile = titleAndBodyFileNode.getText()
        bodyOnlyFile = bodyOnlyFileNode.getText()
        creationTime = creationTimeNode.getText()
        lastModifiedTime = lastModifiedTimeNode.getText()
        
        template.setRootFileName(root)
        template.setName(name)
        template.setSource(source)
        template.setAllFileName(allFile)
        template.setTitleAndBodyFileName(titleAndBodyFile)
        template.setBodyOnlyFileName(bodyOnlyFile)
        template.setCreationTime(ZSchemaDateTime(creationTime))
        template.setLastModifiedTime(ZSchemaDateTime(lastModifiedTime))
    # end _deserializeTemplate()

# end ZBlogTemplateDeserializer
