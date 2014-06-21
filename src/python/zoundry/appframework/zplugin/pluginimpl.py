from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import MESSAGES
from zoundry.appframework.messages import _extstr
from zoundry.appframework.resources.registry import ZAggregateResourceRegistry
from zoundry.appframework.resources.registry import ZResourceRegistry
from zoundry.appframework.zplugin.extpoint import ZExtensionPoint
from zoundry.appframework.zplugin.plugin import IZPlugin
from zoundry.base.exceptions import ZException
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.i18n import ZBundleCollection
from zoundry.base.util.zversion import ZVersion
from zoundry.base.util.zversion import ZVersionPattern
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zdom.domvisitor import ZDomVisitor
import os.path

PLUGIN_NSS_MAP = {
    u"plg" : IZAppNamespaces.RAVEN_PLUGIN_NAMESPACE #$NON-NLS-1$
}


# -----------------------------------------------------------------------------------
# Wraps the non-plugin resource registry in order to modify the requested path
# prior to attempting to resolve it.  For example, if the plugin is asked to resolve
# the path "images/menu/context/file.png", then this wrapper will change that to be
# "plugins/<pluginid>/images/menu/context/file.png".  This is basically to allow 
# some way for themes to also change the images for plugins (in addition to the 
# basic application images).
# -----------------------------------------------------------------------------------
class ZPluginResourceRegistryWrapper(ZResourceRegistry):

    def __init__(self, delegateRegistry, pluginId):
        self.delegateRegistry = delegateRegistry
        self.pluginId = pluginId
        
        ZResourceRegistry.__init__(self, None)
    # end __init__()

    def getResourcePath(self, path, dirOk = False):
        # Prepend the path with "plugins/<pluginid>"
        path = os.path.join(u"plugins", self.pluginId, path) #$NON-NLS-1$
        return self.delegateRegistry.getResourcePath(path, dirOk)
    # end getResourcePath()

# end ZPluginResourceRegistryWrapper


# -----------------------------------------------------------------------------------
# Wraps a single plugin found by the plugin registry.  This plugin object will load
# the plugin meta information from the zplugin.xml file.
# -----------------------------------------------------------------------------------
class ZPlugin(IZPlugin):

    # Creates a ZPlugin given a plugin directory.  This may throw an exception if there
    # is something structurally wrong with the plugin.
    def __init__(self, pluginDirectory):
        self.pluginDirectory = pluginDirectory
        self.pluginSpecDom = self._loadPluginSpec()
        self.pluginSpecDom.setNamespaceMap(PLUGIN_NSS_MAP)
        self.pluginStringBundle = self._loadStringBundle()
        self.pluginResourceRegistry = None

        self.classloader = ZClassLoader()
        
        self._resolveExternalizedStrings()
    # end __init__()

    def getPluginDirectory(self):
        return self.pluginDirectory
    # end getPluginDirectory()

    def getId(self):
        return self.pluginSpecDom.selectSingleNode(u"/plg:zoundry-plugin").getAttribute(u"id") #$NON-NLS-1$ #$NON-NLS-2$
    # end getId()

    def getName(self):
        return self.pluginSpecDom.selectSingleNode(u"/plg:zoundry-plugin").getAttribute(u"name") #$NON-NLS-1$ #$NON-NLS-2$
    # end getName()

    # Returns a ZVersion object representing the version of this plugin.
    def getVersion(self):
        verStr = self.pluginSpecDom.selectSingleNode(u"/plg:zoundry-plugin").getAttribute(u"version") #$NON-NLS-1$ #$NON-NLS-2$
        return ZVersion(verStr)
    # end getVersion()

    def getString(self, key):
        return self.pluginStringBundle.getString(key)
    # end getString()

    def getClassloader(self):
        return self.classloader
    # end getClassloader()

    # Validates the plugin.  This method will raise an Exception if the plugin is invalid for
    # any reason (not schema-valid, missing a dependency, etc...).  In order to check for
    # dependencies, the list of loaded plugins is passed in.
    def validate(self, schemaXML, plugins, extensionDefs):
        self._schemaValidate(schemaXML)
        self._validateExtensionPoints(extensionDefs)
        for (pluginId, pluginVersion) in self.getDependencies():
            self._validateDependency(pluginId, pluginVersion, plugins)
        self._duplicatePluginIdCheck(plugins)
    # end validate()
    
    # Quick validation of the plugin.  Skips the parts of validation that could
    # not have changed without the plugin.xml file being modified.
    def quickValidate(self, plugins):
        for (pluginId, pluginVersion) in self.getDependencies():
            self._validateDependency(pluginId, pluginVersion, plugins)
        self._duplicatePluginIdCheck(plugins)
    # end quickValidate()

    # Returns a list of tuples that are the plugins that this plugin depends on.  Each item in
    # the list is a tuple like:  (pluginId, pluginVersion)  where the pluginId is a string and
    # the pluginVersion is a ZVersionPattern.
    def getDependencies(self):
        dependencies = []

        nodes = self.pluginSpecDom.selectNodes(u"/plg:zoundry-plugin/plg:dependencies/plg:depends") #$NON-NLS-1$
        if nodes:
            for node in nodes:
                pid = node.getAttribute(u"on") #$NON-NLS-1$
                ver = node.getAttribute(u"version") #$NON-NLS-1$
                dependencies.append( (pid, ZVersionPattern(ver)) )

        return dependencies
    # end getDependencies()

    # Returns a list of extension points defined in this plugin.
    def getExtensionPoints(self, type = None):
        xpath = u"/plg:zoundry-plugin/plg:zoundry-extension" #$NON-NLS-1$
        if type:
            xpath = u"/plg:zoundry-plugin/plg:zoundry-extension[@point = '%s']" % type #$NON-NLS-1$
        nodes = self.pluginSpecDom.selectNodes(xpath)
        extensionPoints = []
        if nodes:
            for node in nodes:
                extensionPoints.append(ZExtensionPoint(self, node, self.classloader))
        return extensionPoints
    # end getExtensionPoints()

    # Loads the zplugin.xml file.
    def _loadPluginSpec(self):
        try:
            self.pluginSpecFile = os.path.join(self.pluginDirectory, u"zplugin.xml") #$NON-NLS-1$
            dom = ZDom()
            dom.load(self.pluginSpecFile)
            return dom
        except Exception, e:
            raise ZAppFrameworkException(_extstr(u"plugin.FailedToLoadPluginSpec") % self.pluginSpecFile, e) #$NON-NLS-1$
    # end _loadPluginSpec()

    # Loads the plugin's string bundle.
    def _loadStringBundle(self):
        rootBundleFile = os.path.join(self.pluginDirectory, u"zstringbundle.xml") #$NON-NLS-1$
        return ZBundleCollection(rootBundleFile)
    # end _loadPluginSpec()

    def _resolveExternalizedStrings(self):
        visitor = ZPluginStringResolverVisitor(self.pluginStringBundle)
        visitor.visit(self.pluginSpecDom)
    # end _resolveExternalizedStrings()

    # Validates this plugin against the zplugin.rng Relax NG schema.
    def _schemaValidate(self, schemaXML):
        try:
            self.pluginSpecDom.validate(schemaXML)
        except ZException, ze:
            raise ZAppFrameworkException(_extstr(u"plugin.PluginSpecNotSchemaValid") % ze.getMessage(), ze) #$NON-NLS-1$
    # end _schemaValidate()

    def _validateExtensionPoints(self, extensionDefs):
        # Get a list of all extension points.
        extensionPoints = self.getExtensionPoints()
        for extensionPoint in extensionPoints:
            extensionPointId = extensionPoint.getType()
            # If there is no extension declaration, throw
            if not extensionDefs.has_key(extensionPointId):
                raise ZAppFrameworkException(_extstr(u"pluginimpl.UndeclaredExtensionPointError") % (extensionPoint.getId(), extensionPointId)) #$NON-NLS-1$
            extensionDef = extensionDefs[extensionPointId]
            
            iface = None
            epointClass = None
            try:
                iface = extensionDef.getInterface()
            except Exception, e:
                raise ZAppFrameworkException(_extstr(u"pluginimpl.ErrorLoadingExtPointInterface") % extensionPointId, e) #$NON-NLS-1$
            # If there is an interface, then make sure the contributed class extends that interface.
            if iface:
                className = extensionPoint.getClass()
                if not className and not extensionDef.isInterfaceOptional():
                    raise ZAppFrameworkException(_extstr(u"pluginimpl.MissingClassForExtensionPoint") % (extensionPoint.getId(), extensionPointId, unicode(iface))) #$NON-NLS-1$
                try:
                    if className:
                        epointClass = self.classloader.loadClass(className)
                except Exception, e:
                    raise ZAppFrameworkException(_extstr(u"pluginimpl.ErrorLoadingContributedClass") % (className, extensionPointId), e) #$NON-NLS-1$
                if epointClass and not issubclass(epointClass, iface):
                    raise ZAppFrameworkException(_extstr(u"pluginimpl.ClassDoesNotImplementCorrectInterfaceError") % (className, extensionPoint.getId(), unicode(iface))) #$NON-NLS-1$

            schemaLocation = extensionDef.getSchemaLocation()
            # If there is a schema location, do schema validation against the extension point data.
            if schemaLocation:
                extensionDataNode = extensionPoint.getExtensionDataNode()
                if not extensionDataNode:
                    raise ZAppFrameworkException(_extstr(u"plugin.MissingExtensionPoint") % extensionPointId) #$NON-NLS-1$
                node = extensionDataNode.selectSingleNode(u"*") #$NON-NLS-1$
                if not node:
                    raise ZAppFrameworkException(_extstr(u"plugin.MissingExtensionPoint") % extensionPointId) #$NON-NLS-1$
                schemaXML = self._loadExtensionSchema(schemaLocation)
                try:
                    node.validate(schemaXML)
                except ZException, ze:
                    raise ZAppFrameworkException(_extstr(u"plugin.ExtensionFailedToValidate") % ze.getMessage()) #$NON-NLS-1$
                except Exception, e:
                    raise ZAppFrameworkException(_extstr(u"plugin.ExtensionFailedToValidate") % unicode(e)) #$NON-NLS-1$
    # end _validateExtensionPoints()

    def _loadExtensionSchema(self, schemaLocation):
        try:
            f = open(schemaLocation, u"r") #$NON-NLS-1$
            xml = f.read()
            f.close()
            return xml
        except Exception, e:
            raise ZAppFrameworkException(_extstr(u"plugin.CouldNotFindExtensionSchema") % schemaLocation, e) #$NON-NLS-1$
    # end _loadExtensionSchema()

    # Validates that the given plugin id exists in the list of plugins.
    def _validateDependency(self, pluginId, pluginVersion, plugins):
        for plugin in plugins:
            if pluginId == plugin.getId():
                version = plugin.getVersion()
                if pluginVersion == version:
                    return True
        raise ZAppFrameworkException(_extstr(u"plugin.DependencyCheckFailed") % (self.getId(), unicode(pluginVersion), pluginId )) #$NON-NLS-1$
    # end _validateDependency()

    def _duplicatePluginIdCheck(self, plugins):
        # FIXME remove this method and any code that references this method since duplicate-id check is now down in ZPluginRegistry::loadPlugins()        
        for plugin in plugins:
            myId = self.getId()
            if myId == plugin.getId() and not self == plugin:
                raise ZAppFrameworkException(_extstr(u"plugin.DuplicatePluginId") % myId) #$NON-NLS-1$
    # end _duplicatePluginIdCheck()

    def getResourceRegistry(self):
        if self.pluginResourceRegistry is None:
            resourceRegistryPath = os.path.join(self.pluginDirectory, u"resources") #$NON-NLS-1$
            registries = [
                  ZPluginResourceRegistryWrapper(getResourceRegistry(), self.getId()),
                  ZResourceRegistry(resourceRegistryPath)
            ]
            self.pluginResourceRegistry = ZAggregateResourceRegistry(registries)
        
        return self.pluginResourceRegistry
    # end getResourceRegistry()

# end ZPlugin


# -----------------------------------------------------------------------------------
# A visitor that visits the plugin spec dom and replaces all %key.name% formatted 
# strings with their respective values (looked up from the string bundle).
# -----------------------------------------------------------------------------------
class ZPluginStringResolverVisitor(ZDomVisitor):

    def __init__(self, stringBundle):
        self.stringBundle = stringBundle
    # end __init__()

    def visitElement(self, element):
        text = element.getText()
        if text and text.startswith(u"%") and text.endswith(u"%"): #$NON-NLS-1$ #$NON-NLS-2$
            key = text[1:len(text)-1]
            newValue = self.stringBundle.getString(key)
            # If the string is not found in the Plugin's bundle, then look in the "appframework"'s 
            # bundle.  The string will only exist there if the plugin is a 1st party Zoundry plugin.
            if newValue is None:
                newValue = MESSAGES.getString(key)
            # Only change the text of the element if we found a value for the key.
            if newValue is not None:
                element.setText(newValue)
    # end visitElement()

# end ZPluginStringResolverVisitor
