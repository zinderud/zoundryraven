from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.zplugin import pluginsorter
from zoundry.appframework.zplugin.extpointdef import IZExtensionDef
from zoundry.appframework.zplugin.extpointdef import ZExtensionDef
from zoundry.appframework.zplugin.pluginimpl import ZPlugin
from zoundry.appframework.zplugin.registry import IZPluginRegistry
from zoundry.appframework.zplugin.registry import IZPluginRegistryListener
from zoundry.base.exceptions import ZException
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.zdom.dom import ZDom
import os

PLUGIN_SCHEMA_PATH = u"2006/03/zplugin.rng" #$NON-NLS-1$
ZEXTENSION_SCHEMA_PATH = u"2006/03/zoundry.extension.rng" #$NON-NLS-1$

# -------------------------------------------------------------------------------------
# A filter function for the getDirectoryListing() function.
# -------------------------------------------------------------------------------------
def PLUGIN_DIRECTORY_FILTER(path):
    if os.path.isdir(path):
        specFile = os.path.join(path, u"zplugin.xml") #$NON-NLS-1$
        return os.path.isfile(specFile)
    return False
# end PLUGIN_DIRECTORY_FILTER()


# -------------------------------------------------------------------------------------
# This is an implementation of an extension def which is used to bootstrap the plugin
# registry.  Plugins can only contribute to extension points that have been declared.
# And you declare an extension point by contributing to the 'zoundry.extension' 
# extension point.  :)  Hence a chicken and the egg dilemma.  This class provides a
# "hard coded" extension point declaration.  All other extension point declarations 
# will appear in plugins.
# -------------------------------------------------------------------------------------
class ZBootstrapExtensionDef(IZExtensionDef):
    
    def __init__(self, systemProfile):
        self.systemProfile = systemProfile
    # end __init__()

    def getExtensionId(self):
        return IZAppExtensionPoints.ZEP_ZOUNDRY_EXTENSION
    # end getName()

    def getSchemaLocation(self):
        return self.systemProfile.getSchema(ZEXTENSION_SCHEMA_PATH)
    # end getSchemaLocation()
    
    def getInterface(self):
        return None
    # end getInterface()

# end IZExtensionDef


# -------------------------------------------------------------------------------------
# This is an implementation of a plugin registry listener that takes a list of other
# IZPluginRegistryListener instances and routes the events to all of them.
# -------------------------------------------------------------------------------------
class ZAggregatePluginRegistryListener(IZPluginRegistryListener):

    def __init__(self, listenerList = []):
        self.listeners = listenerList
    # end __init__()
    
    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def pluginsLoading(self, numPlugins):
        for listener in self.listeners:
            listener.pluginsLoading(numPlugins)
    # end pluginsLoading()

    def pluginLoading(self, pluginId):
        for listener in self.listeners:
            listener.pluginLoading(pluginId)
    # end pluginLoading()

    def pluginLoaded(self, pluginId):
        for listener in self.listeners:
            listener.pluginLoaded(pluginId)
    # end pluginLoaded()

    def pluginFailed(self, pluginId, failureMessage):
        for listener in self.listeners:
            listener.pluginFailed(pluginId, failureMessage)
    # end pluginFailed()

    def pluginsLoaded(self, numLoaded, numFailed):
        for listener in self.listeners:
            listener.pluginsLoaded(numLoaded, numFailed)
    # end pluginsLoaded()

    def pluginsValidating(self, numPlugins):
        for listener in self.listeners:
            listener.pluginsValidating(numPlugins)
    # end pluginsValidating()

    def pluginValidating(self, pluginId):
        for listener in self.listeners:
            listener.pluginValidating(pluginId)
    # end pluginValidating()
    
    def pluginValidated(self, pluginId):
        for listener in self.listeners:
            listener.pluginValidated(pluginId)
    # end pluginValidate()
    
    def pluginValidationFailed(self, pluginId, failureMessage):
        for listener in self.listeners:
            listener.pluginValidationFailed(pluginId, failureMessage)
    # end pluginValidationFailed()

    def pluginsValidated(self, numValidPlugins, numInvalidPlugins):
        for listener in self.listeners:
            listener.pluginsValidated(numValidPlugins, numInvalidPlugins)
    # end pluginsValidated()

# end ZAggregatePluginRegistryListener


# -------------------------------------------------------------------------------------
# The plugin registry handles loading all of the plugins found in the system.  The
# registry gets the plugin install location from the given System Profile.  It then
# scans the plugin install location for plugins.  The plugins are loaded (taking into
# account dependencies) and organized.  The registry can then be used by other parts
# of the application.
# -------------------------------------------------------------------------------------
class ZPluginRegistry(IZPluginRegistry):

    def __init__(self, systemProfile, userProfile):
        self.systemProfile = systemProfile
        self.userProfile = userProfile
        self.listener = None
        self.plugins = None
        self.extensionsCache = {}
    # end __init__()
    
    def loadPlugins(self, listener = None):
        if not listener:
            listener = IZPluginRegistryListener()
        self.listener = listener
        pluginDirectories = self._getPluginDirectories()
        self.listener.pluginsLoading(len(pluginDirectories))

        # Go through all of the plugin directories and load each plugin.  The end result is a 
        # list of ZPlugin objects.
        totalFailed = 0        
        pluginMap = {}
        for pluginDirectory in pluginDirectories:
            self.listener.pluginLoading(os.path.basename(pluginDirectory))
            try:
                plugin = ZPlugin(pluginDirectory)
                if pluginMap.has_key( plugin.getId() ):
                    # plugin already exists.
                    # Check for new versions of plug-ins as well as duplicate versions
                    prevPlugin = pluginMap[ plugin.getId() ]
                    v1 = plugin.getVersion()
                    v2 = prevPlugin.getVersion()
                    if v1 > v2:
                        #  new plugin is the latest version
                        pluginMap[ plugin.getId() ] = plugin
                    elif v1 == v2:
                        # new plugin and old plug have same version id -> duplicate plugin id error  
                        raise ZAppFrameworkException(_extstr(u"plugin.DuplicatePluginId") % plugin.getId()) #$NON-NLS-1$
                    elif v1 < v2:
                        # prevPlugin version number is newer. Do nothing (to keep the prevPlugin)
                        pass 
                else:
                    pluginMap[ plugin.getId() ] = plugin
                    self.listener.pluginLoaded(plugin.getId())
            except ZException, ze:
                self.listener.pluginFailed(os.path.basename(pluginDirectory), ze.getStackTrace())
                totalFailed += 1
            except Exception, e:
                self.listener.pluginFailed(os.path.basename(pluginDirectory), ZException(rootCause = e).getStackTrace())
                totalFailed += 1
        self.listener.pluginsLoaded(len(pluginMap), totalFailed)
        # get plugins as a list
        plugins = pluginMap.values()
        # Sort the plugins by dependencies.
        plugins = pluginsorter.sortPlugins(plugins)

        # Load all of the extension point extensions.
        self.extensionDefs = self._loadExtensionDefs(plugins)

        # Now validate each plugin.
        self.listener.pluginsValidating(len(plugins))
        validPlugins = []
        invalidPlugins = []
        for plugin in plugins:
            pluginId = plugin.getId()
            self.listener.pluginValidating(pluginId)
            try:
                self._validatePlugin(plugin, validPlugins)
                validPlugins.append(plugin)
                self.listener.pluginValidated(pluginId)
            except ZException, ze:
                self.listener.pluginValidationFailed(pluginId, ze.getStackTrace())
                invalidPlugins.append(plugin)
            except Exception, e:
                self.listener.pluginValidationFailed(pluginId, ZException(rootCause = e).getStackTrace())
                invalidPlugins.append(plugin)
        self.listener.pluginsValidated(len(validPlugins), len(invalidPlugins))

        self.plugins = validPlugins
    # end loadPlugins()

    def _validatePlugin(self, plugin, validPlugins):
        doQuickValidation = False
        userPluginsDir = self.userProfile.getDirectory(u"plugins") #$NON-NLS-1$
        pluginValidatedFilePath = os.path.join(userPluginsDir, plugin.getId() + u".xml") #$NON-NLS-1$
        pluginXMLFilePath = os.path.join(plugin.getPluginDirectory(), u"zplugin.xml") #$NON-NLS-1$
        if os.path.isfile(pluginValidatedFilePath):
            pluginValidatedTimestamp = getFileMetaData(pluginValidatedFilePath)[3]
            pluginXMLTimestamp = getFileMetaData(pluginXMLFilePath)[3]
            doQuickValidation = pluginXMLTimestamp < pluginValidatedTimestamp

        if doQuickValidation:
            plugin.quickValidate(validPlugins)
        else:
            schemaXML = self._loadPluginSchemaXML()
            plugin.validate(schemaXML, validPlugins, self.extensionDefs)
            ZDom(u"""<validated timestamp="%s" />""" % unicode(ZSchemaDateTime())).save(pluginValidatedFilePath) #$NON-NLS-1$
    # end _validatePlugin()

    def _loadPluginSchemaXML(self):
        schemaPath = self._getPluginSchemaPath()
        try:
            f = open(schemaPath, u"r") #$NON-NLS-1$
            xml = f.read()
            f.close()
            return xml
        except Exception, e:
            raise ZAppFrameworkException(_extstr(u"plugin.FailedToLoadSchema"), e) #$NON-NLS-1$
    # end _loadSchemaXML()

    def _getPluginSchemaPath(self):
        return self.systemProfile.getSchema(PLUGIN_SCHEMA_PATH)
    # end _getPluginSchemaPath()

    def _loadExtensionDefs(self, plugins):
        extensions = {}
        # Seed the list of declared extensions with the bootstrap one.
        extensions[IZAppExtensionPoints.ZEP_ZOUNDRY_EXTENSION] = ZBootstrapExtensionDef(self.systemProfile)
        for plugin in plugins:
            for epoint in plugin.getExtensionPoints(IZAppExtensionPoints.ZEP_ZOUNDRY_EXTENSION):
                extDef = ZExtensionDef(epoint, plugin.getPluginDirectory())
                extensions[extDef.getExtensionId()] = extDef
        return extensions
    # end _loadExtensionDefs()

    def _getPluginDirectories(self):
        pluginsDir = self.systemProfile.getPluginDirectory()
        return getDirectoryListing(pluginsDir, PLUGIN_DIRECTORY_FILTER)
    # end _getPluginDirectories()

    def getExtensions(self, extensionPointTypeId):
        if self.extensionsCache.has_key(extensionPointTypeId):
            return self.extensionsCache[extensionPointTypeId]

        extensions = []
        for plugin in self.plugins:
            for epoint in plugin.getExtensionPoints(extensionPointTypeId):
                extensions.append(epoint)
        
        self.extensionsCache[extensionPointTypeId] = extensions
        return extensions
    # end getExtensions()
    
    def getExtension(self, extensionPointTypeId, extensionPointId):
        extensions = self.getExtensions(extensionPointTypeId)
        for ext in extensions:
            if ext.getId() == extensionPointId:
                return ext
        return None
    # end getExtension()
    
    def getPlugin(self, pluginId):
        for plugin in self.plugins:
            if plugin.getId() == pluginId:
                return plugin
        return None
    # end getPlugin()

# end ZPluginRegistry

