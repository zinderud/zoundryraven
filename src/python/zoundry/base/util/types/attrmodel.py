from zoundry.base.util.schematypes import ZSchemaDateTime

# -----------------------------------------------------------------------------------------
# Base interface for models that contain attributes.
# -----------------------------------------------------------------------------------------
class IZAttributeModel:

    def setAttribute(self, name, value, namespace = None):
        u"Sets an attribute." #$NON-NLS-1$
    # end setAttribute()

    def getAttribute(self, name, namespace = None):
        u"Gets an attribute." #$NON-NLS-1$
    # end getAttribute()

    def hasAttribute(self, name, namespace = None):
        u"Returns true if attribute exists." #$NON-NLS-1$
    # end hasAttribute()

    # Returns all attributes in the given namespace as a list of tuples of the form (name, value).
    def getAttributes(self, namespace = None):
        u"Gets a list of all attributes in a namespace.  Format=(name, value)" #$NON-NLS-1$
    # end getAttributes()

    # Returns all attributes as a list of tuples of the form (name, value, namespace).
    def getAllAttributes(self):
        u"Gets a list of all attributes.  Format=(name, value, namespace)" #$NON-NLS-1$
    # end getAllAttributes()

    def removeAttribute(self, name, namespace = None):
        u"Removes an attribute." #$NON-NLS-1$
    # end removeAttribute()

# end IZAttributeModel

# -----------------------------------------------------------------------------------------
# Base class for models that have namespace-aware attributes.
# -----------------------------------------------------------------------------------------
class ZModelWithAttributes(IZAttributeModel):

    def __init__(self):
        self.attributesMap = {}
        self.attributesMap[None] = {}
    # end __init__()

    def removeAttribute(self, name, namespace = None):
        self.setAttribute(name, None, namespace)
    # end removeAttribute()

    def setAttribute(self, name, value, namespace = None):
        if not namespace in self.attributesMap:
            self.attributesMap[namespace] = {}

        attributes = self.attributesMap[namespace]
        if name in attributes and value is None:
            del attributes[name]
        elif value is not None:
            attributes[name] = value
    # end setAttribute()

    def setAttributeBool(self, name, value, namespace = None):
        if value:
            value = u"true" #$NON-NLS-1$
        else:
            value = u"false" #$NON-NLS-1$
        self.setAttribute(name, value, namespace)
    # end setAttributeBool()

    def getAttribute(self, name, namespace = None):
        if not namespace in self.attributesMap:
            return None

        attributes = self.attributesMap[namespace]
        if name in attributes:
            return attributes[name]
        return None
    # end getAttribute()

    def getAttributeBool(self, name, namespace = None, dflt = None):
        val = self.getAttribute(name, namespace)
        if val is None:
            return dflt

        return val == True or val == u"true" or val == u"True" #$NON-NLS-1$ #$NON-NLS-2$
    # end getAttributeBool()

    def getAttributeDate(self, name, namespace = None, dflt = None):
        val = self.getAttribute(name, namespace)
        if val is None:
            return dflt

        if isinstance(val, ZSchemaDateTime):
            return val
        else:
            return ZSchemaDateTime(val)
    # end getAttributeDate()

    def hasAttribute(self, name, namespace = None):
        return self.getAttribute(name, namespace) is not None

    # Returns all attributes in the given namespace as a list of tuples of the form (name, value).
    def getAttributes(self, namespace = None):
        if not namespace in self.attributesMap:
            return []

        rval = []
        attributes = self.attributesMap[namespace]
        for attributeName in attributes:
            rval.append( (attributeName, attributes[attributeName]) )
        return rval
    # end getAttributes()

    # Returns all attributes as a list of tuples of the form (name, value, namespace).
    def getAllAttributes(self):
        rval = []
        for namespace in self.attributesMap:
            attributes = self.attributesMap[namespace]
            for attributeName in attributes:
                rval.append( (attributeName, attributes[attributeName], namespace) )
        return rval
    # end getAllAttributes()

# end ZModelWithAttributes

# -----------------------------------------------------------------------------------------
# class for models that have namespace-aware attributes
# which also supports aattributes with a value of None.
# -----------------------------------------------------------------------------------------
class ZModelWithNoneValueAttributes(ZModelWithAttributes):

    def __init__(self):
        ZModelWithAttributes.__init__(self)

    def removeAttribute(self, name, namespace = None):
        # override to delete entry from map
        if not self.attributesMap.has_key(namespace):
            return
        attributes = self.attributesMap[namespace]
        if attributes.has_key(name):
            del attributes[name]
    # end removeAttribute()

    def setAttribute(self, name, value, namespace = None):
        # override to allow values to be None
        if not namespace in self.attributesMap:
            self.attributesMap[namespace] = {}

        attributes = self.attributesMap[namespace]
        attributes[name] = value
    # end setAttribute()

    def hasAttribute(self, name, namespace = None):
        if not self.attributesMap.has_key(namespace):
            return False
        attributes = self.attributesMap[namespace]
        return attributes.has_key(name)
    # end hasAttribute()
# ZModelWithNoneValueAttributes())