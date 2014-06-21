from zoundry.base.exceptions import ZClassNotFoundException
import string

# -------------------------------------------------------------------------------------
# A classloader that is capable of loading a Python class given its fully qualified
# class name.  This classloader impl is not thread safe.  In order to provide a thread
# safe classloader, this class should be extended.
# -------------------------------------------------------------------------------------
class ZClassLoader:

    def __init__(self):
        self.cache = {}
    # end __init__()

    # Loads the fully qualified class given by 'className'.  This method will throw an exception
    # if it cannot find the class.
    def loadClass(self, qualifiedClassName):
        if self.cache.has_key(qualifiedClassName):
            return self.cache[qualifiedClassName]

        (moduleName, className) = self._splitClassName(qualifiedClassName)
        try:
            module = __import__(moduleName)
            if not module:
                raise ZClassNotFoundException(qualifiedClassName)
            parts = moduleName.split(u".")[1:] #$NON-NLS-1$
            for part in parts:
                module = getattr(module, part)
                if not module:
                    raise ZClassNotFoundException(qualifiedClassName)
            
            theClass = getattr(module, className)
            if not theClass:
                raise ZClassNotFoundException(qualifiedClassName)
            
            self.cache[qualifiedClassName] = theClass
            return theClass
        except Exception, e:
            raise ZClassNotFoundException(qualifiedClassName, e)
    # end loadClass()

    def _splitClassName(self, qualifiedClassName):
        components = qualifiedClassName.split(u".") #$NON-NLS-1$
        moduleName = string.join(components[0:len(components) - 1], u".") #$NON-NLS-1$
        className = components[len(components) - 1]
        return (moduleName, className)
    # end _splitClassName()

# end ZClassLoader
