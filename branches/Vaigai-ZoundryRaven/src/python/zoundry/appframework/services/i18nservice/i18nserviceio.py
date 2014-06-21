from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.i18nservice.io.factory import getI18NDeserializerFactory
from zoundry.base.zdom.dom import ZDom

# ----------------------------------------------------------------------------------------
# This function takes a path to a Raven country codes file and loads it into a list of
# IZCountryCode objects.
# ----------------------------------------------------------------------------------------
def loadCountryCodes(xmlFilePath):
    try:
        dom = ZDom()
        dom.load(xmlFilePath)

        deserializer = getI18NDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(dom)
    except Exception, e:
        raise ZAppFrameworkException(_extstr(u"i18nserviceio.ErrorLoadingCountryCodes"), e) #$NON-NLS-1$
# end loadBackgroundTask()


# ----------------------------------------------------------------------------------------
# This function takes a path to a Raven language codes file and loads it into a list of
# IZLanguageCode objects.
# ----------------------------------------------------------------------------------------
def loadLanguageCodes(xmlFilePath):
    try:
        dom = ZDom()
        dom.load(xmlFilePath)

        deserializer = getI18NDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(dom)
    except Exception, e:
        raise ZAppFrameworkException(_extstr(u"i18nserviceio.ErrorLoadingLanguageCodes"), e) #$NON-NLS-1$
# end loadBackgroundTask()
