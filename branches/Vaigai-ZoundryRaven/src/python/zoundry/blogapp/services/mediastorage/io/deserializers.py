from zoundry.appframework.util.crypt import decryptCipherText
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.blogapp.services.mediastorage.mediastorageimpl import ZMediaStorage


# -----------------------------------------------------------------------------------------
# The interface that all media storage deserializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZMediaStorageDeserializer:

    def deserialize(self, mediaStoreDom):
        u"Called to deserialize a media storage.  This should return an instance of IZMediaStorage." #$NON-NLS-1$
    # end deserialize()

# end IZMediaStorageDeserializer


# -----------------------------------------------------------------------------------------
# An implementation of a media storage deserializer for version 1.0 (or 2006/06) of the Zoundry
# Raven media storage format.
# -----------------------------------------------------------------------------------------
class ZVer1MediaStorageDeserializer(IZMediaStorageDeserializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, mediaStoreDom):
        mediaStoreDom.setNamespaceMap(self.nssMap)

        storeElem = mediaStoreDom.documentElement
        id = storeElem.getAttribute(u"store-id") #$NON-NLS-1$
        name = storeElem.getAttribute(u"name") #$NON-NLS-1$
        mediaSiteId = storeElem.getAttribute(u"media-site-id") #$NON-NLS-1$
        properties = self._deserializeProperties(storeElem)

        return ZMediaStorage(id, name, mediaSiteId, properties)
    # end deserialize()

    def _deserializeProperties(self, parentNode):
        properties = {}
        propertyNodes = parentNode.selectNodes(u"zns:properties/zns:property") #$NON-NLS-1$
        for propertyNode in propertyNodes:
            name = propertyNode.getAttribute(u"name") #$NON-NLS-1$
            value = propertyNode.getText()
            if name == u"password": #$NON-NLS-1$
                value = decryptCipherText(value, PASSWORD_ENCRYPTION_KEY)
            properties[name] = value
        return properties
    # end _deserializeProperties()

# end ZVer1MediaStorageDeserializer
