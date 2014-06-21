from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.util.xmlutil import ZXmlAttributes
from zoundry.base.zdom.dom import ZDom


# ----------------------------------------------------------------------------------------
# Loads resource store meta data entry
# ----------------------------------------------------------------------------------------
def loadStoreEntry(entry,  entryXmlPath):
    u"""loadStoreEntry(ZResourceStoreEntry , string) -> ZResourceStoreEntry
    """ #$NON-NLS-1$
    try:
        dom = ZDom()
        dom.load(entryXmlPath)
        return ZResourceStoreEntryDeserializer().deserialize(entry, dom)
    except Exception, e:
        raise e
# end loadStoreEntry()


# ----------------------------------------------------------------------------------------
# Saves a store entry meta data
# path.
# ----------------------------------------------------------------------------------------
def saveStoreEntry(entry, entryXmlPath):
    u"""saveStoreEntry(ZResourceStoreEntry, string) -> void
    """ #$NON-NLS-1$
    try:
        dom = ZResourceStoreEntrySerializer().serialize(entry)
        dom.save(entryXmlPath, True)
    except Exception, e:
        raise e
# end saveStoreEntry()

#-----------------------------------
# ZResourceStoreEntrySerializer
#-----------------------------------
class ZResourceStoreEntrySerializer:

    def __init__(self):
        self.namespace = IZAppNamespaces.RAVEN_RESOURCE_STORE_ENTRY_NAMESPACE
    # end __init__()

    def serialize(self, entry):
        dom = ZDom()
        dom.loadXML(u"<resource-entry  xmlns='%s' />" % self.namespace) #$NON-NLS-1$
        root = dom.documentElement
        root.setAttribute(u"id", entry.getId()) #$NON-NLS-1$
        self._serializeAttributes(entry,root)
        return dom
    # end serialize()

    # Generic serialization of an attribute-based model.
    def _serializeAttributes(self, attrModel, parentElem):
        allAttributes = attrModel.getAllAttributes()
        if allAttributes is None or len(allAttributes) == 0:
            return

        attributesElem = parentElem.ownerDocument.createElement(u"attributes", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(attributesElem)
        for (name, value, ns) in allAttributes:
            attributeElem = parentElem.ownerDocument.createElement(u"attribute", self.namespace) #$NON-NLS-1$
            attributesElem.appendChild(attributeElem)
            attributeElem.setAttribute(u"name", name) #$NON-NLS-1$
            attributeElem.setAttribute(u"namespace", ns) #$NON-NLS-1$
            attributeElem.setText(value)
    # end _serializeAttributes()
# end ZResourceStoreEntrySerializer


#-----------------------------------
# ZResourceStoreEntryDeserializer
#-----------------------------------
class ZResourceStoreEntryDeserializer:

    def __init__(self):
        self.namespace = IZAppNamespaces.RAVEN_RESOURCE_STORE_ENTRY_NAMESPACE
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, entry,  resourceDom):
        resourceDom.setNamespaceMap(self.nssMap)
        self._deserializeAttributes(resourceDom.documentElement, entry)
        return entry
    # end deserialize()

    def _deserializeAttributes(self, parentNode, model):
        attributesNode = parentNode.selectSingleNode(u"zns:attributes") #$NON-NLS-1$
        xmlAttributes = ZXmlAttributes(attributesNode, self.namespace)
        for (name, value, namespace) in xmlAttributes.getAllAttributes():
            model.setAttribute(name, value, namespace)
    # end _deserializeAttributes()

# end ZResourceStoreEntryDeserializer