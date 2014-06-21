from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.accountstore.io.factory import getAccountDeserializerFactory
from zoundry.blogapp.services.accountstore.io.factory import getAccountSerializerFactory
import os

# ----------------------------------------------------------------------------------------
# This function takes a directory to a Raven Account and loads it into a ZAccount 
# instance, using the deserialization framework.
# ----------------------------------------------------------------------------------------
def loadAccount(accountDir):
    try:
        accountXmlPath = os.path.join(accountDir, u"account.xml") #$NON-NLS-1$
        dom = ZDom()
        dom.load(accountXmlPath)

        deserializer = getAccountDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(accountDir, dom)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"accountio.FailedToLoadAccount") % accountDir, e) #$NON-NLS-1$
# end loadAccount()


# ----------------------------------------------------------------------------------------
# This function takes a IZAccount instance and serializes it to disk into the given 
# account directory.
# ----------------------------------------------------------------------------------------
def saveAccount(account):
    try:
        serializer = getAccountSerializerFactory().getSerializer()
        serializer.serialize(account)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"accountio.FailedToSaveAccount") % account.getDirectoryPath(), e) #$NON-NLS-1$
# end saveAccount()
