from zoundry.appframework.util.crypt import encryptPlainText
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY

# -----------------------------------------------------------------------------------------
# The interface that all media storage serializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZMediaStorageSerializer:

    def serialize(self, store):
        u"Called to serialize a media storage.  This should return a DOM." #$NON-NLS-1$
    # end serialize()

# end IZMediaStorageSerializer


# -----------------------------------------------------------------------------------------
# An implementation of a media storage serializer for version 1.0 (or 2006/07) of the Zoundry
# Raven media storage format.
# -----------------------------------------------------------------------------------------
class ZVer1MediaStorageSerializer(IZMediaStorageSerializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def serialize(self, store):
        storeDom = ZDom()
        storeDom.loadXML(u"<store xmlns='%s' />" % self.namespace) #$NON-NLS-1$

        storeElem = storeDom.documentElement
        storeElem.setAttribute(u"store-id", store.getId()) #$NON-NLS-1$
        storeElem.setAttribute(u"media-site-id", store.getMediaSiteId()) #$NON-NLS-1$
        storeElem.setAttribute(u"name", store.getName()) #$NON-NLS-1$
        self._serializeProperties(store.getProperties(), storeElem)

        return storeDom
    # end serialize()

    def _serializeProperties(self, storeProperties, parentElem):
        if storeProperties is None or len(storeProperties) == 0:
            return

        propertiesElem = parentElem.ownerDocument.createElement(u"properties", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(propertiesElem)

        for propKey in storeProperties:
            propVal = storeProperties[propKey]
            if propKey == u"password": #$NON-NLS-1$
                propVal = encryptPlainText(propVal, PASSWORD_ENCRYPTION_KEY)
            propertyElem = parentElem.ownerDocument.createElement(u"property", self.namespace) #$NON-NLS-1$
            propertiesElem.appendChild(propertyElem)
            propertyElem.setAttribute(u"name", propKey) #$NON-NLS-1$
            propertyElem.setText(propVal)
    # end _serializeProperties()

# end ZVer1MediaStorageDeserializer
