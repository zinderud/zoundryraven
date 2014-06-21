from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.zdom.dom import ZDom
import os

# ------------------------------------------------------------------------------
# The interface that all template serializer implementations must implement.
# ------------------------------------------------------------------------------
class IZTemplateSerializer:

    def serialize(self, template):
        u"Called to serialize a template.  This should write out the template to the template's directory." #$NON-NLS-1$
    # end serialize()

# end IZTemplateSerializer


# ------------------------------------------------------------------------------
# An implementation of an template serializer for the Zoundry Raven template
# format.
# ------------------------------------------------------------------------------
class ZBlogTemplateSerializer(IZTemplateSerializer):

    def __init__(self, namespace):
        self.namespace = namespace
    # end __init__()

    def serialize(self, template):
        templateDom = ZDom()
        templateDom.loadXML(u"<template xmlns='%s' />" % self.namespace) #$NON-NLS-1$
        templateElem = templateDom.documentElement
        templateElem.setAttribute(u"template-id", template.getId()) #$NON-NLS-1$

        self._serializeTemplate(templateElem, template)

        self._saveDom(templateDom, template.getTemplateDirectory())
    # end serialize()

    def _serializeTemplate(self, parentElem, template):
        rootFileNameElem = parentElem.ownerDocument.createElement(u"root", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(rootFileNameElem)
        if template.getRootFileName():
            rootFileNameElem.setText(template.getRootFileName())

        nameElem = parentElem.ownerDocument.createElement(u"name", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(nameElem)
        if template.getCreationTime():
            nameElem.setText(getSafeString(template.getName()))

        sourceElem = parentElem.ownerDocument.createElement(u"source", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(sourceElem)
        if template.getCreationTime():
            sourceElem.setText(getSafeString(template.getSource()))

        allFileElem = parentElem.ownerDocument.createElement(u"allFile", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(allFileElem)
        if template.getCreationTime():
            allFileElem.setText(getSafeString(template.getAllFileName()))

        bodyAndTitleFileElem = parentElem.ownerDocument.createElement(u"bodyAndTitleFile", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(bodyAndTitleFileElem)
        if template.getCreationTime():
            bodyAndTitleFileElem.setText(getSafeString(template.getTitleAndBodyFileName()))

        bodyOnlyFileElem = parentElem.ownerDocument.createElement(u"bodyOnlyFile", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(bodyOnlyFileElem)
        if template.getCreationTime():
            bodyOnlyFileElem.setText(getSafeString(template.getBodyOnlyFileName()))

        creationTimeElem = parentElem.ownerDocument.createElement(u"creationTime", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(creationTimeElem)
        if template.getCreationTime():
            creationTimeElem.setText(unicode(template.getCreationTime()))

        lastModifiedTimeElem = parentElem.ownerDocument.createElement(u"lastModifiedTime", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(lastModifiedTimeElem)
        if template.getLastModifiedTime():
            lastModifiedTimeElem.setText(unicode(template.getLastModifiedTime()))
    # end _serializeTemplate()

    def _saveDom(self, templateDom, templateDirectory):
        if not os.path.exists( templateDirectory ):
            os.makedirs( templateDirectory )
        domPath = os.path.join(templateDirectory, u"template.xml") #$NON-NLS-1$
        templateDom.save(domPath, True)
    # end _saveDom()

# end ZBlogTemplateSerializer
