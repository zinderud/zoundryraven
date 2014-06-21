#@PydevCodeAnalysisIgnore
u'''Exceptions used by the FlickrAPI module.''' #$NON-NLS-1$

class IllegalArgumentException(ValueError):
    u'''Raised when a method is passed an illegal argument.
    
    More specific details will be included in the exception message
    when thrown.
    ''' #$NON-NLS-1$

class FlickrError(Exception):
    u'''Raised when a Flickr method fails.
    
    More specific details will be included in the exception message
    when thrown.
    ''' #$NON-NLS-1$
