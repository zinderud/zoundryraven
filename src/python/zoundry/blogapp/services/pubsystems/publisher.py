from zoundry.blogapp.exceptions import ZBlogAppException
#from zoundry.blogapp.services.capabilities import IZCapabilities
#from zoundry.blogapp.services.parameters import IZParameters
#from zoundry.blogapp.services.extpointdef import IZBlogAppDef
# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZPublisherException(ZBlogAppException):

    def __init__(self, message, rootCause = None):
        ZBlogAppException.__init__(self, message, rootCause)


# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
#class IZPublisherConstants:
#    
#    API_URL          = u"zoundry.blogapp.pubsystems.publisher.api.url"  #$NON-NLS-1$
#    API_USERNAME     = u"zoundry.blogapp.pubsystems.publisher.api.username"  #$NON-NLS-1$
#    API_PASSWORD     = u"zoundry.blogapp.pubsystems.publisher.api.password"  #$NON-NLS-1$
#    API_AUTH_SCHEME  = u"zoundry.blogapp.pubsystems.publisher.api.authscheme"  #$NON-NLS-1$
    
    
# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class IZPublisher:
    
    def initialize(self, capabilities, parameters, logger):
        u"""initialize(IZCapabilities, IZParameters, IZLoggerService) -> void
        Initializes the publisher with optional (override) capabilities and parameters.""" #$NON-NLS-1$
    
    def setTypeDef(self, typedef):    
        u"""setTypeDef(IZBlogAppDef) -> void
        Sets the associated publisher-type def.""" #$NON-NLS-1$
        
    def getTypeDef(self):
        u"""getTypeDef() -> IZBlogAppDef
        Returns the publisher-type def.""" #$NON-NLS-1$
                
    def getCapabilities(self):
        u"""getCapabilities() -> IZCapabilities
        Returns IZCapabilities object.""" #$NON-NLS-1$

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns IZParameters object.""" #$NON-NLS-1$

# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class IZPublisherRequest:    
    pass

# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class IZPublisherResponse:
    
    def isOK(self):
        u"""isOK() -> bool
        Returns true if the response was successful.""" #$NON-NLS-1$
        
    def getMessage(self):
        u"""getMessage() -> string
        Returns optional response message.""" #$NON-NLS-1$


# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZPublisherBase(IZPublisher):
    u""""Base impl. of publisher""" #$NON-NLS-1$
    def __init__(self):
        self.typedef = None
        self.parameters = None
        self.capabilities = None
        self.logger = None
    
    def _getLogger(self):
        return self.logger
       
    def initialize(self, capabilities, parameters, logger):
        self.logger = logger
        if capabilities:
            self.getCapabilities().override(capabilities)
        if parameters:
            self.getParameters().override(parameters)
    
    def setTypeDef(self, typedef):
        self.typedef = typedef
        self.parameters = self.typedef.getParameters().clone()
        self.capabilities = self.typedef.getCapabilities().clone()
                
    def getTypeDef(self):
        return self.typedef        
        
    def getCapabilities(self):
        return self.capabilities
    
    def _getCapabilitesAsMap(self):
        map = {}
        for key in self.getCapabilities().getCapabilityKeys():
            map[key] = self.getCapabilities().hasCapability(key)
        return map

    def getParameters(self):
        return self.parameters

    def _getParametersAsMap(self):
        return self.getParameters().getParameters()    

# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZPublisherRequest(IZPublisherRequest):
    u""""Base impl. of publisher request""" #$NON-NLS-1$
    def __init__(self):
        pass

# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZPublisherResponse(IZPublisherResponse):
    u""""Base impl. of publisher response""" #$NON-NLS-1$
    
    def __init__(self, ok = False, message = None):
        self.ok = ok
        self.message = message
    
    def isOK(self):
        return self.ok
        
    def getMessage(self):
        return self.message
    
# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZQualifiedPublisherId:
    u"""ZQualifiedPublisherId provides way to separate server ids by using a
    namespace. Most servers (except for Atom) return either interger or string
    values for blog and entry ids. This means, two blogs (or posts) from two different
    servers may have the same id. e.g. 1.
    
    The current solution for this is to refer to blog or entry id in Raven using
    a qualified string form: 
         
            {localId} serverId
            
   For example, the local id could be the account or blog id in Raven.
      
             {urn:acc,acc_id:blog,blog_id} post_id
             """ #$NON-NLS-1$
    
    def __init__(self, id = None, localId = None, serverId = None):
        self.id = None
        self.localId = None
        self.serverId = None        
        if id is not None:
            # format is {localId} serverId
            id = id.strip()
            self.id = id
            j = id.find(u"}")  #$NON-NLS-1$
            if j!= -1:
                self.localId  = id[1 : j].strip()
                self.serverId  = id[j+1:].strip()
                # recreate id after stripping white spaces
                self.id = u"{%s}%s" % (self.localId, self.serverId) #$NON-NLS-1$
                
        elif localId and serverId:            
            self.localId  = localId.strip()
            self.serverId = serverId.strip()
            self.id = u"{%s}%s" % (self.localId, self.serverId) #$NON-NLS-1$

    def getId(self):
        return self.id
    
    def getLocalId(self):
        return self.localId
    
    def getServerId(self):
        return self.serverId
    
    def __str__(self):
        return  self.getId()

