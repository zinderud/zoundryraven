
# ------------------------------------------------------------------------------
# Common interface for all 'parameter' classes.
# ------------------------------------------------------------------------------
class IZParameters:
    
    def getParameters(self):
        u"""getParameters() -> dictionary
        Returns the parameters dictionary object.""" #$NON-NLS-1$
    # end getParameters()

    def hasParameter(self, name):
        u"""hasParameter(name) -> string
        Returns true if the named parameter exists.""" #$NON-NLS-1$
    # end hasParameter()
        
    def getParameter(self, name, defaultValue = None):
        u"""getParameter(name, string) -> string
        Returns the named parameter.""" #$NON-NLS-1$
    # end getParameter()
         
    def getIntParameter(self, name, defaultValue = 0):
        u"""getIntParameter(name, int) -> int
        Convenience method that returns the parameter value as integer.""" #$NON-NLS-1$
    # end getIntParameter()

    def getBoolParameter(self, name, defaultValue = False):
        u"""getBoolParameter(name, bool) -> bool
        Convenience method that returns the parameter value as boolean.""" #$NON-NLS-1$        
    # end getBoolParameter()

    def override(self, otherParameters):
        u"""override(IZParameters) -> void
        Called to override the parameters with another set of parameters.""" #$NON-NLS-1$
    # end override()
    
    def clone(self):
        u"""clone() -> void
        Returns a copy.
        """ #$NON-NLS-1$  
    #end clone

# end IZParameters


# ------------------------------------------------------------------------------
# Concrete implementation of an IZParameters.
# ------------------------------------------------------------------------------
class ZParameters(IZParameters):
    
    def __init__(self, parameters = {}):
        self.parameters = parameters
    # end __init__()

    def _getParameterKey(self, name):
        if name:
            name = name.lower().strip()
        if name:
            return name
        else:
            return None
    # end _getParameterKey()

    def getParameters(self):
        return self.parameters
    # end getParameters()
    
    def hasParameter(self, name):
        key = self._getParameterKey(name)
        return key and self.parameters.has_key(key)

    def getParameter(self, name, defaultValue = None):
        key = self._getParameterKey(name)
        if key and self.parameters.has_key(key):
            return self.parameters[key]
        else:
            return defaultValue
    # end getParameter()
         
    def getIntParameter(self, name, defaultValue = 0):
        s = self.getParameter(name)
        if not s:
            return defaultValue
        try:
            return int(s)
        except:
            return defaultValue
    # end getIntParameter()

    def getBoolParameter(self, name, defaultValue = False):
        s = self.getParameter(name)
        if not s:
            return defaultValue
        try:
            s = s.strip().lower()
            if s == u"true" or s == u"yes": #$NON-NLS-1$ #$NON-NLS-2$
                return True
            else:
                return False
        except:
            return defaultValue
    # end getBoolParameter()
    
    def override(self, otherParameters):
        for (name, value) in otherParameters.getParameters().iteritems():
            self.parameters[name] = value
    # end override()
                
    def clone(self):
        zparams = ZParameters( self.parameters.copy() )
        return zparams
    # end clone()

# end ZParameters