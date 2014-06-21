from zoundry.base.exceptions import ZException
from zoundry.base.util.locking import ZMutex

# -----------------------------------------------------------------------------------
# Returns true if Python sequence, dictionary, set or list is not none and empty
# -----------------------------------------------------------------------------------
def isNotNoneAndEmpty( pyCollection):
    if pyCollection is not None and len(pyCollection) == 0:
        return True
    else:
        return False
# end isNotNoneAndEmpty()


# -----------------------------------------------------------------------------------
# A node in the listener linked list.
# -----------------------------------------------------------------------------------
class ZListenerSetNode:

    def __init__(self, listener):
        self.listener = listener
        self.prevNode = None
        self.nextNode = None
    # end __init__()

    def getListener(self):
        return self.listener
    # end getListener()

    def getNext(self):
        return self.nextNode
    # end getNext()

    def setNext(self, node):
        self.nextNode = node
    # end setNext()

    def getPrevious(self):
        return self.prevNode
    # end getPrevious()

    def setPrevious(self, node):
        self.prevNode = node
    # end setPrevious()

# end ZListenerSetNode


# -----------------------------------------------------------------------------------
# Iterates over the items in the listener list.
# -----------------------------------------------------------------------------------
class ZListenerSetIterator:

    def __init__(self, listenerList, node):
        self.listenerList = listenerList
        self.node = node
    # end __init__()

    def __iter__(self):
        return self
    # end __iter__()

    def next(self):
        self.listenerList._acquireMutex()
        try:
            if self.node is None:
                raise StopIteration()
            rval = self.node
            self.node = self.node.getNext()
            return rval.getListener()
        finally:
            self.listenerList._releaseMutex()
    # end next()

# end ZListenerSetIterator


# -----------------------------------------------------------------------------------
# Implements a python list that is safe to modify at any time (even while someone
# else is iterating it).  This is accomplished simply by using some rudimentary
# mutex locking and using a linked list data structure.  There is probably still a
# race condition:  if a listener is removed !immediately! after being returned from
# an iterator, then there could be problems.  The only solution to that would be to
# synchronize around an entire iteration.  We could easily support this by exposing
# the acquire() and release() methods publicly.
# -----------------------------------------------------------------------------------
class ZListenerSet:

    def __init__(self):
        self.mutex = ZMutex(u"ZListenerSetMTX") #$NON-NLS-1$
        self.head = None
    # end __init__()

    def append(self, listener):
        self.addListener(listener)
    # end append()

    def remove(self, listener):
        self.removeListener(listener)
    # end remove()

    def clear(self):
        self._acquireMutex()
        self.head = None
        self._releaseMutex()
    # end clear()

    def addListener(self, listener):
        self._acquireMutex()
        try:
            if listener in self:
                return
            newNode = ZListenerSetNode(listener)
            if self.head is None:
                self.head = newNode
            else:
                lastNode = self._getLastNode()
                newNode.setPrevious(lastNode)
                lastNode.setNext(newNode)
        finally:
            self._releaseMutex()
    # end addListener()

    def removeListener(self, listener):
        self._acquireMutex()
        try:
            node = self._findNode(listener)
            if node is not None:
                prevNode = node.getPrevious()
                nextNode = node.getNext()
                if prevNode is not None:
                    prevNode.setNext(nextNode)
                else:
                    self.head = nextNode
                if nextNode is not None:
                    nextNode.setPrevious(prevNode)
        finally:
            self._releaseMutex()
    # end removeListener()

    # Convenience method to execute a callback method on each
    # of the listeners in the set within a synchronized block.
    def doCallback(self, callbackMethodName, argumentSequence = None):
        self._acquireMutex()
        try:
            if argumentSequence is None:
                argumentSequence = []

            for listener in self:
                try:
                    method = getattr(listener, callbackMethodName)
                    method(*argumentSequence)
                except ZException, ze:
                    raise ze
                except Exception, e:
                    raise ZException(e)
        finally:
            self._releaseMutex()
    # end doCallback()

    def _findNode(self, listener):
        if self.head is not None:
            if self.head.getListener() == listener:
                return self.head
            currentNode = self.head
            while currentNode is not None and not currentNode.getListener() == listener:
                currentNode = currentNode.getNext()
            return currentNode
        return None
    # end _findNode()

    def _getLastNode(self):
        if self.head is not None:
            currentNode = self.head
            while currentNode.getNext() is not None:
                currentNode = currentNode.getNext()

            return currentNode
        return None
    # end _getLastNode()

    def _acquireMutex(self):
        self.mutex.acquire()
    # end _acquireMutex()

    def _releaseMutex(self):
        self.mutex.release()
    # end _releaseMutex()

    def __contains__(self, listener):
        return self._findNode(listener) is not None
    # end __contains__()

    def __iter__(self):
        return ZListenerSetIterator(self, self.head)
    # end __iter__()

# end ZListenerSet
