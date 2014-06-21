from Queue import Queue
from zoundry.appframework.engine.service import IZService
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.guid import generate
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.util.zthread import ZThread
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.accountstore.account import IZBlogAccount
from zoundry.blogapp.services.accountstore.accountstore import IZAccountStoreListener
from zoundry.blogapp.services.datastore.datastore import IZDataStoreListener
from zoundry.blogapp.services.mediastorage.mediastoragesrvc import IZMediaStorageServiceListener
from zoundry.blogapp.services.usage.usageio import ZUsagePacketSerializer
from zoundry.blogapp.version import ZVersion
import os

# ------------------------------------------------------------------------------
# Some constants for packet types.
# ------------------------------------------------------------------------------
class IZUsagePacketTypes:

    EXIT_SERVICE = u"zoundry.usage.internal.exit" #$NON-NLS-1$

    NEW_ACCOUNT = u"zoundry.usage.new-account" #$NON-NLS-1$
    CHANGE_ACCOUNT = u"zoundry.usage.change-account" #$NON-NLS-1$
    DELETE_ACCOUNT = u"zoundry.usage.delete-account" #$NON-NLS-1$

    NEW_MEDIA_STORE = u"zoundry.usage.new-media-storage" #$NON-NLS-1$
    DELETE_MEDIA_STORE = u"zoundry.usage.delete-media-storage" #$NON-NLS-1$

# end IZUsagePacketTypes


# ------------------------------------------------------------------------------
# Simple container class that holds information about a particular bit of
# usage.  Always has a type and a timestamp.
# ------------------------------------------------------------------------------
class ZUsagePacket:

    def __init__(self, type):
        self.attributes = {}
        self.id = generate()
        
        self.addAttribute(u"packet.packet-type", type) #$NON-NLS-1$
        self.addAttribute(u"packet.timestamp", unicode(ZSchemaDateTime())) #$NON-NLS-1$
    # end __init__()
    
    def getType(self):
        return self.attributes[u"packet.packet-type"] #$NON-NLS-1$
    # end getType()
    
    def getId(self):
        return self.id
    # end getId()

    def addAttribute(self, name, value):
        self.attributes[name] = unicode(value)
    # end addAttribute()

    def getAttributes(self):
        return self.attributes
    # end getAttributes()

# end ZUsagePacket


# ------------------------------------------------------------------------------
# Implementation of a service for doing anonymous usage statistics gathering.
#
# FIXME (EPW) need an anonymous usage statistics preference page
# ------------------------------------------------------------------------------
class ZUsageStatisticsService(IZService, IZDataStoreListener, IZMediaStorageServiceListener, IZAccountStoreListener, IZRunnable):

    def __init__(self):
        self.serializer = ZUsagePacketSerializer()
        self.logger = None
        self.running = False
        self.version = ZVersion()
        self.profileGuid = getApplicationModel().getUserProfile().getGuid()
        self.usageDir = None
    # end __init__()

    def start(self, applicationModel):
        self.queue = Queue(0)
        userProfile = applicationModel.getUserProfile()
        self.usageDir = userProfile.getDirectory(u"usage") #$NON-NLS-1$

        engine = applicationModel.getEngine()
        self.logger = engine.getService(IZBlogAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"Anonymous Usage Statistics Service started.") #$NON-NLS-1$

        accountStore = engine.getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        dataStore = engine.getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        mediaStoreService = engine.getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)

        accountStore.addListener(self)
        dataStore.addListener(self)
        mediaStoreService.addListener(self)

        self.done = False
        self.running = True
        thread = ZThread(self, u"ZUsageStatisticsService", True) #$NON-NLS-1$
        thread.start()
    # end start()

    def stop(self):
        self.logger = None
        packet = self._createPacket(IZUsagePacketTypes.EXIT_SERVICE)
        self.queue.put_nowait(packet)
        while self.running:
            pass
    # end stop()

    def run(self):
        done = False
        while not done:
            packet = self.queue.get()
            if packet.getType() == IZUsagePacketTypes.EXIT_SERVICE:
                done = True
            else:
                self._savePacket(packet)
        self.running = False
    # end run()

    def _savePacket(self, packet):
        packetDom = self.serializer.serialize(packet)
        fname = os.path.join(self.usageDir, packet.getId() + u".xml") #$NON-NLS-1$
        packetDom.save(fname, True)
    # end _savePacket()
#
#    def onDocumentAdded(self, document):
#        self.logger.debug(u"Document added.")
#    # end onDocumentAdded()
#
#    def onDocumentChanged(self, document, metaDataOnly):
#        self.logger.debug(u"Document changed.")
#    # end onDocumentChange()
#
#    def onDocumentDeleted(self, document):
#        self.logger.debug(u"Document deleted.")
#    # end onDocumentDeleted()

    def onMediaStorageAdded(self, mediaStore):
        packet = self._createPacket(IZUsagePacketTypes.NEW_MEDIA_STORE)
        packet.addAttribute(u"mediastorage.site-id", mediaStore.getMediaSiteId()) #$NON-NLS-1$
        packet.addAttribute(u"mediastorage.id-hash", hash(mediaStore.getId())) #$NON-NLS-1$
        self.queue.put_nowait(packet)
    # end onMediaStorageAdded()

    def onMediaStorageRemoved(self, mediaStore):
        packet = self._createPacket(IZUsagePacketTypes.DELETE_MEDIA_STORE)
        packet.addAttribute(u"mediastorage.site-id", mediaStore.getMediaSiteId()) #$NON-NLS-1$
        packet.addAttribute(u"mediastorage.id-hash", hash(mediaStore.getId())) #$NON-NLS-1$
        self.queue.put_nowait(packet)
    # end onMediaStorageRemoved() #$NON-NLS-1$

    def onAccountAdded(self, account):
        packet = self._createPacket(IZUsagePacketTypes.NEW_ACCOUNT)
        if isinstance(account, IZBlogAccount):
            apiInfo = account.getAPIInfo()
            packet.addAttribute(u"account.type", apiInfo.getType()) #$NON-NLS-1$
            packet.addAttribute(u"account.id-hash", unicode(hash(account.getId()))) #$NON-NLS-1$
        self.queue.put_nowait(packet)
    # end onAccountAdded()

    def onAccountChanged(self, account): #@UnusedVariable
        pass
    # end onAccountChange()

    def onAccountDeleted(self, account):
        packet = self._createPacket(IZUsagePacketTypes.NEW_ACCOUNT)
        if isinstance(account, IZBlogAccount):
            apiInfo = account.getAPIInfo()
            packet.addAttribute(u"account.type", apiInfo.getType()) #$NON-NLS-1$
            packet.addAttribute(u"account.id-hash", unicode(hash(account.getId()))) #$NON-NLS-1$
        self.queue.put_nowait(packet)
    # end onAccountDeleted()

    def _createPacket(self, type):
        packet = ZUsagePacket(type)
        packet.addAttribute(u"global.app-version", self.version.getFullVersionString()) #$NON-NLS-1$
        packet.addAttribute(u"global.profile-guid", self.profileGuid) #$NON-NLS-1$
        return packet
    # end _createPacket()

# end ZUsageStatisticsService
