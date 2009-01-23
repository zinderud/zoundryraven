from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.mediastorage.io.factory import getMediaStorageDeserializerFactory
from zoundry.blogapp.services.mediastorage.io.factory import getMediaStorageSerializerFactory

# ----------------------------------------------------------------------------------------
# This function takes a path to a Raven Media Storage and loads it into a 
# IZMediaStorage instance, using the deserialization framework.
# ----------------------------------------------------------------------------------------
def loadMediaStorage(mediaStoreXmlPath):
    try:
        dom = ZDom()
        dom.load(mediaStoreXmlPath)

        deserializer = getMediaStorageDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(dom)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"mediastorageio.FailedToLoadStore"), e) #$NON-NLS-1$
# end loadMediaStorage()


# ----------------------------------------------------------------------------------------
# This function takes a Media Storage instance and serializes it to disk at the given path
# ----------------------------------------------------------------------------------------
def saveMediaStorage(storage, storeXmlPath):
    try:
        serializer = getMediaStorageSerializerFactory().getSerializer()
        dom = serializer.serialize(storage)
        dom.save(storeXmlPath, True)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"mediastorageio.FailedToSaveStore") % storage.getId(), e) #$NON-NLS-1$
# end saveMediaStorage()
