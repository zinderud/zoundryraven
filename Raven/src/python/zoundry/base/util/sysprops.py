from zoundry.base.exceptions import ZException
from zoundry.base.messages import _extstr
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zdom.dom import ZElement
from zoundry.base.util.locking import ZMutex
from zoundry.base.util.fileutil import renameFile
from zoundry.base.util.fileutil import deleteFile
import re
import string


# --------------------------------------------------------
class IZSystemPropertiesListener:

    def onSystemPropertyChange(self, key, value):
        u"Called when a system property value changes." #$NON-NLS-1$
    # end onSystemPropertyChange()

# end IZSystemPropertiesListener


# --------------------------------------------------------
class ZSystemProperties:
    u"""Use this class to get and set System Properties.""" #$NON-NLS-1$

    def __init__(self, sysPropsFileName):
        # create a lock for thread synchronization
        self.lock = ZMutex(u"ZSystemProperties") #$NON-NLS-1$
        self.listeners = ZListenerSet()

        self.sysPropsFileName = sysPropsFileName
        self.sysPropsDoc = ZDom()

        self.reloadProperties()
    # end __init__()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener

    def _fireEvent(self, key, value):
        for listener in self.listeners:
            listener.onSystemPropertyChange(key, value)
    # end _fireEvent()

    def reloadProperties(self):
        self.lock.acquire()
        try:
            # Open and parse the system properties file
            self.sysPropsDoc.load(self.sysPropsFileName)
        finally:
            self.lock.release()
    # end reloadProperties()

    # Public method - call this to save the system properties.
    def save(self):
        u"Public method - call this to save the system properties." #$NON-NLS-1$
        self.lock.acquire()
        self.saveProperties()
        self.lock.release()
        self._fireEvent(None, None)
    # end save()

    # Note that locking is required prior to calling saveProperties()
    def saveProperties(self):
        try:
            tempSysPropsFileName = self.sysPropsFileName + u".t" #$NON-NLS-1$
            self.sysPropsDoc.save(tempSysPropsFileName, True)
            deleteFile(self.sysPropsFileName)
            renameFile(tempSysPropsFileName, self.sysPropsFileName)
        except Exception, e:
            raise ZException(_extstr(u"sysprops.ErrorSavingPropsFile") % self.sysPropsFileName, e) #$NON-NLS-1$
    # end saveProperties

    def getPropertyNodes(self, _xpath):
        u"""Returns a list of ZNodes given an xpath.""" #$NON-NLS-1$

        try:
            return self.sysPropsDoc.documentElement.selectNodes(_xpath)
        except:
            return None
    # end getPropertyNodes()

    def getPropertyNode(self, _xpath):
        u"""Returns a single ZNode given an xpath.""" #$NON-NLS-1$
        nodes = self.getPropertyNodes(_xpath)
        try:
            return nodes[0]
        except:
            return None
    # end getPropertyNode

    def getPropertyString(self, _xpath, _default = None):
        u"""Returns the specified system property as a string.""" #$NON-NLS-1$
        node = self.getPropertyNode(_xpath)
        if not node:
            return _default

        try:
            return node.getText()
        except:
            pass

        return _default
    # end getPropertyString()

    def getPropertyInt(self, _xpath, _default = None):
        u"""Returns the specified system property as an integer.""" #$NON-NLS-1$
        s = self.getPropertyString(_xpath, None)

        if not s:
            return _default

        try:
            return string.atoi(s)
        except:
            pass

        return _default
    # end getPropertyInt()

    def getPropertyFloat(self, _xpath, _default = None):
        u"""Returns the specified system property as a float.""" #$NON-NLS-1$
        s = self.getPropertyString(_xpath, None)

        if not s:
            return _default

        try:
            return string.atof(s)
        except:
            pass

        return _default
    # end getPropertyFloat()

    def getPropertyLong(self, _xpath, _default = None):
        u"""Returns the specified system property as a long.""" #$NON-NLS-1$
        s = self.getPropertyString(_xpath, None)

        if not s:
            return _default

        try:
            return string.atol(s)
        except:
            pass

        return _default
    # end getPropertyLong()

    def getPropertyBool(self, _xpath, _default = None):
        u"""Returns the specified system property as an integer.""" #$NON-NLS-1$
        s = self.getPropertyString(_xpath, None)

        if not s:
            return _default

        try:
            return s == u"true" or s == u"True" #$NON-NLS-1$ #$NON-NLS-2$
        except:
            pass

        return _default
    # end getPropertyInt()

    def setProperty(self, _xpath, value, autoCommit = True):
        u"""Sets a user or system property.  Takes an xpath, value, and optional boolean flag 'system' which
        indicates whether to change the user or system properties.  Raises a ValueError if the xpath is not
        a valid (already-existing) node or attribute.""" #$NON-NLS-1$
        self.lock.acquire()

        node = self.getPropertyNode(_xpath)
        if not node:
            node = self.createPropertyNode(_xpath)
        if not node:
            raise ValueError

        if isinstance(value, unicode) or isinstance(value, str):
            node.setText(value)
        elif isinstance(value, ZElement):
            node.removeAllChildren()
            value = node.ownerDocument.importNode(value, True)
            node.appendChild(value)
        else:
            raise ZException(u"Unsupported value type for setProperty: %s" % unicode(type(value))) #$NON-NLS-1$

        # Now save the files (pretty print)
        if autoCommit:
            self.saveProperties()
        self.lock.release()

        self._fireEvent(_xpath, value)
    # end setProperty()

    def removeProperty(self, _xpath, autoCommit = True):
        self.lock.acquire()

        node = self.getPropertyNode(_xpath)
        if node is not None:
            node.parentNode.removeChild(node)

        # Now save the files (pretty print)
        if autoCommit:
            self.saveProperties()
        self.lock.release()

        self._fireEvent(_xpath, None)
    # end removeProperty()

    # This method creates a node at the given xpath.  This will only work for simple xpath expressions.
    def createPropertyNode(self, _xpath):
        u"Creates a new node at the given xpath." #$NON-NLS-1$
        ownerDoc = self.sysPropsDoc
        xpathObj = ZXPathObject(_xpath)
        baseNode = None
        while not baseNode:
            if not xpathObj.popSegment():
                return None
            baseNode = ownerDoc.selectSingleNode(xpathObj.getCurrentPath())

        # Now we have identified the base node and xpathObj has a list of nodes that must
        # be created.
        node = baseNode
        while xpathObj.hasMoreSegments():
            segment = xpathObj.getNextSegment()
            newElem = ownerDoc.createElement(segment.getNodeName())
            attrs = segment.getAttributes()
            for attrName in attrs:
                attrValue = attrs[attrName]
                newElem.setAttribute(attrName, attrValue)
            node.appendChild(newElem)
            node = newElem

        return node
    # end createPropertyNode()

# end ZSystemProperties


# -----------------------------------------------------------------------------------
# A single segment of a simple xpath.  This class knows how to parse a simple segment
# and return its component parts.  This class can handle segments that just a simple
# node step (e.g. /root/path/to/node) and it can handle attribute tests within the
# step (e.g. /root/path[@attr1='value']).  Note: currently only handles multiple
# attributes if they are AND'd together.  If you have an xpath that uses OR, this
# will be meaningless.
# -----------------------------------------------------------------------------------
class ZXPathSegment:

    SEGMENT_PATTERN = re.compile(r"(.*?)\s*\[(.*?)\]") #$NON-NLS-1$
    ATTR_PATTERN = re.compile(r"\@(.*?)\s*=\s*['\"](.*?)['\"]") #$NON-NLS-1$

    def __init__(self, segmentStr):
        self.nodeName = None
        self.attributes = {}

        self._parseSegment(segmentStr)
    # end __init__()

    def getNodeName(self):
        return self.nodeName
    # end getNodeName()

    def getAttributes(self):
        return self.attributes
    # end getAttributes()

    def _parseSegment(self, segmentStr):
        if u'[' in segmentStr: #$NON-NLS-1$
            matcher = ZXPathSegment.SEGMENT_PATTERN.match(segmentStr)
            self.nodeName = matcher.group(1)
            qstr = matcher.group(2)
            if qstr:
                for (name, value) in ZXPathSegment.ATTR_PATTERN.findall(qstr):
                    self.attributes[name] = value
        else:
            self.nodeName = segmentStr
    # end _parseSegment()

# enc ZXPathSegment


# -----------------------------------------------------------------------------------
# Represents a parsed-out simple XPath.  This simple XPath is then iterated over
# in order to create the target DOM.
# -----------------------------------------------------------------------------------
class ZXPathObject:

    def __init__(self, _xpath):
        self.xpath = _xpath
        self.segments = []
        self.poppedSegments = []
        self._parseXpath()
    # end __init__()

    # Split the XPath based on / chars - ignore /'s if they are within a quoted string.
    def _splitXPath(self):
        indexes = []
        isInQuotedString = False
        for i in range(0, len(self.xpath)):
            ch = self.xpath[i]
            if ch == u"'" or ch == u"\"": #$NON-NLS-2$ #$NON-NLS-1$
                isInQuotedString = not isInQuotedString
            elif ch == u"/" and not isInQuotedString: #$NON-NLS-1$
                indexes.append(i)

        segments = []
        prevIndex = 0
        for index in indexes:
            segment = self.xpath[prevIndex + 1:index]
            segments.append(segment)
            prevIndex = index
        if not self.xpath.endswith(u"/"): #$NON-NLS-1$
            segments.append(self.xpath[prevIndex + 1:])

        return segments
    # end _splitXPath()

    def _parseXpath(self):
        self.segments = self._splitXPath()
    # end _parseXpath()

    def getCurrentPath(self):
        return string.joinfields(self.segments, u"/") #$NON-NLS-1$
    # end getCurrentPath()

    def popSegment(self):
        if len(self.segments) < 2:
            return False
        self.poppedSegments.append(self.segments.pop())
        return True
    # end popSegment()

    def getNextSegment(self):
        if len(self.poppedSegments) < 1:
            return None
        rval = self.poppedSegments.pop()
        self.segments.append(rval)
        return ZXPathSegment(rval)
    # end getNextSegment()

    def hasMoreSegments(self):
        return len(self.poppedSegments) > 0
    # end hasMoreSegments()

    def getNumSegments(self):
        return len(self.segments)
    # end getNumSegments()

# end ZXPathObject
