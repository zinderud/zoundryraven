# -*- encoding: utf-8 -*-
#@PydevCodeAnalysisIgnore
from zoundry.base.util.text.unicodeutil import convertToUnicode

u'''Module for encoding data as form-data/multipart''' #$NON-NLS-1$

import os
import base64

class Part(object):
    u'''A single part of the multipart data.

    >>> Part({'name': 'headline'}, 'Nice Photo')
    ... # doctest: +ELLIPSIS
    <flickrapi.multipart.Part object at 0x...>

    >>> image = file('tests/photo.jpg')
    >>> Part({'name': 'photo', 'filename': image}, image.read(), 'image/jpeg')
    ... # doctest: +ELLIPSIS
    <flickrapi.multipart.Part object at 0x...>
    ''' #$NON-NLS-1$

    def __init__(self, parameters, payload, content_type=None):
        self.content_type = content_type
        self.parameters = parameters
        self.payload = payload

    def render(self):
        u'''Renders this part -> List of Strings''' #$NON-NLS-1$

        parameters = [u'%s="%s"' % (k, v) #$NON-NLS-1$
                      for k, v in self.parameters.iteritems()]

        lines = [u'Content-Disposition: form-data; %s' % u'; '.join(parameters)] #$NON-NLS-2$ #$NON-NLS-1$

        if self.content_type:
            lines.append(u"Content-Type: %s" % self.content_type) #$NON-NLS-1$

        lines.append(u'') #$NON-NLS-1$

        if isinstance(self.payload, unicode):
            lines.append(self.payload.encode(u'utf-8')) #$NON-NLS-1$
        else:
            lines.append(self.payload)

        return lines

class FilePart(Part):
    u'''A single part with a file as the payload

    This example has the same semantics as the second Part example:

    >>> FilePart({'name': 'photo'}, 'tests/photo.jpg', 'image/jpeg')
    ... #doctest: +ELLIPSIS
    <flickrapi.multipart.FilePart object at 0x...>
    ''' #$NON-NLS-1$

    def __init__(self, parameters, filename, content_type):
        parameters[u'filename'] = filename #$NON-NLS-1$

        imagefile = open(filename, u'rb') #$NON-NLS-1$
        payload = imagefile.read()
        imagefile.close()

        Part.__init__(self, parameters, payload, content_type)

def boundary():
    u"""Generate a random boundary, a bit like Python 2.5's uuid module.""" #$NON-NLS-1$

    bytes = os.urandom(16)
    b64str = base64.b64encode(bytes, str(u'ab')) #$NON-NLS-1$
    b64stru = convertToUnicode(b64str)
    return b64stru.strip(u'=') #$NON-NLS-1$

class Multipart(object):
    u'''Container for multipart data''' #$NON-NLS-1$

    def __init__(self):
        u'''Creates a new Multipart.''' #$NON-NLS-1$

        self.parts = []
        self.content_type = u'form-data/multipart' #$NON-NLS-1$
        self.boundary = boundary()

    def attach(self, part):
        u'''Attaches a part''' #$NON-NLS-1$

        self.parts.append(part)

    def __str__(self):
        u'''Renders the Multipart''' #$NON-NLS-1$

        lines = []
        for part in self.parts:
            lines += [u'--' + self.boundary] #$NON-NLS-1$
            lines += part.render()
        lines += [u'--' + self.boundary + u"--"] #$NON-NLS-2$ #$NON-NLS-1$

        for i in range(0, len(lines)):
            line = lines[i]
            if isinstance(line, unicode):
                lines[i] = line.encode(u'utf-8') #$NON-NLS-1$

        return u'\r\n'.join(lines) #$NON-NLS-1$

    def header(self):
        u'''Returns the top-level HTTP header of this multipart''' #$NON-NLS-1$

        return (u"Content-Type", #$NON-NLS-1$
                u"multipart/form-data; boundary=%s" % self.boundary) #$NON-NLS-1$
