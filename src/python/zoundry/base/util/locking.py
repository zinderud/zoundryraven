from threading import _RLock
#from threading import currentThread

DEBUG = False

# ------------------------------------------------------------------------------
# Simple mutex class.  This class is here mostly for explicitness of code - it
# should be used wherever synchronization/mutex/locking takes place in Raven.
# ------------------------------------------------------------------------------
class ZMutex(_RLock):

    def __init__(self, name = None):
        _RLock.__init__(self, DEBUG)

        self.name = name
        if self.name is None:
            self.name = u"ZMutex" #$NON-NLS-1$
    # end __init__()

    def __repr__(self):
        return _RLock.__repr__(self).replace(u"ZMutex", self.name) #$NON-NLS-1$
    # end __repr__()

#    def _note(self, format, *args):
#        format = format % args
#        format = u"[%s]: %s" % (currentThread().getName(), format) #$NON-NLS-1$
#        print format
#    # end _note()

# end ZMutex
