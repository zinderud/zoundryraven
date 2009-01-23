from zoundry.base.util.text.textutil import getNoneString

# -----------------------------------------------------------------------------------------
# This is a wrapper around the Zoundry Raven standard set of attributes.  The standard
# set of attributes is found in both the account.xml and xxxxxxx.rbe.xml files.  This
# class will wrap the <zns:attributes> element and provide easy access and modification
# of the attributes therein.
# -----------------------------------------------------------------------------------------
class ZXmlAttributes:

    def __init__(self, node, namespace = u""): #$NON-NLS-1$
        self.node = node
        self.namespace = namespace
        self.nssMap = { u"ans" : namespace } #$NON-NLS-1$
    # end __init__()

    # Gets an attribute in the given namespace.
    def getAttributeNS(self, name, namespace):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and @namespace = '%s']" % (name, namespace), self.nssMap) #$NON-NLS-1$
        if node:
            return getNoneString(node.getText())
        return None
    # end getAttributeNS()

    # Gets an attribute that does not exist in a namespace.
    def getAttribute(self, name):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and not(@namespace)]" % name, self.nssMap) #$NON-NLS-1$
        if node:
            return getNoneString(node.getText())
        return None
    # end getAttribute()

    # Returns all attributes in the given namespace as a list of (key, value) tuples.
    def getAttributesNS(self, namespace):
        nodes = self.node.selectNodes(u"ans:attribute[@namespace = '%s']" % namespace, self.nssMap) #$NON-NLS-1$
        rval = []
        for node in nodes:
            name = node.getAttribute(u"name") #$NON-NLS-1$
            value = getNoneString(node.getText())
            rval.append( (name, value) ) #$NON-NLS-1$
        return rval
    # end getAttributesNS()

    # Returns all attributes not in a namespace as a list of (key, value) tuples.
    def getAttributes(self):
        nodes = self.node.selectNodes(u"ans:attribute[not(@namespace)]", self.nssMap) #$NON-NLS-1$
        rval = []
        for node in nodes:
            name = node.getAttribute(u"name") #$NON-NLS-1$
            value = getNoneString(node.getText())
            rval.append( (name, value) ) #$NON-NLS-1$
        return rval
    # end getAttributes()
    
    # Returns all attributes as a list of (key, value, namespace) tuples.
    def getAllAttributes(self):
        nodes = self.node.selectNodes(u"ans:attribute", self.nssMap) #$NON-NLS-1$
        rval = []
        for node in nodes:
            name = node.getAttribute(u"name") #$NON-NLS-1$
            ns = node.getAttribute(u"namespace") #$NON-NLS-1$
            value = getNoneString(node.getText())
            if not ns:
                ns = None
            rval.append( (name, value, ns) )
        return rval
    # end getAllAttributes()

    # Sets the value of an attribute in a namespace.  Adds the attribute child if it does not exist.
    def setAttributeNS(self, name, value, namespace):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and @namespace = '%s']" % (name, namespace), self.nssMap) #$NON-NLS-1$
        if not node:
            node = self.node.ownerDocument.createElement(u"attribute", self.namespace) #$NON-NLS-1$
            self.node.appendChild(node)
            node.setAttribute(u"name", name) #$NON-NLS-1$
            node.setAttribute(u"namespace", namespace) #$NON-NLS-1$
        node.setText(value)
    # end setAttributeNS()

    # Sets the value of an attribute.  Adds the attribute child if it does not exist.
    def setAttribute(self, name, value):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and not(@namespace)]" % name, self.nssMap) #$NON-NLS-1$
        if not node:
            node = self.node.ownerDocument.createElement(u"attribute", self.namespace) #$NON-NLS-1$
            self.node.appendChild(node)
            node.setAttribute(u"name", name) #$NON-NLS-1$
        node.setText(value)
    # end setAttributeNS()

    def removeAttributeNS(self, name, namespace):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and @namespace = '%s']" % (name, namespace), self.nssMap) #$NON-NLS-1$
        if node:
            self.node.removeChild(node)
    # end removeAttribute()

    def removeAttribute(self, name):
        node = self.node.selectSingleNode(u"ans:attribute[@name = '%s' and not(@namespace)]" % name, self.nssMap) #$NON-NLS-1$
        if node:
            self.node.removeChild(node)
    # end removeAttribute()

    def has_key(self, key):
        return key in self
    # end has_key()

    def __len__(self):
        return len(self.node.selectNodes(u"ans:attribute[not(@namespace)]", self.nssMap)) #$NON-NLS-1$
    # end __len__()

    def __contains__(self, key):
        return self.getAttribute(key) is not None
    # end __contains__()

    # Iterator over all of the attributes names (not in namespaces).
    def __iter__(self):
        rval = []
        nodes = self.node.selectNodes(u"ans:attribute[not(@namespace)]", self.nssMap) #$NON-NLS-1$
        for node in nodes:
            rval.append(node.getAttribute(u"name")) #$NON-NLS-1$
        return rval.__iter__()
    # end __iter__()

    def __getitem__(self, key):
        return self.getAttribute(key)
    # end __getitem__()

    def __setitem__(self, key, value):
        self.setAttribute(key, value)
    # end __setitem__()

# end ZXmlAttributes
