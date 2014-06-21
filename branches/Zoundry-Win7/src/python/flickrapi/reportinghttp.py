# -*- encoding: utf-8 -*-
#@PydevCodeAnalysisIgnore

u'''HTTPHandler that supports a callback method for progress reports.
''' #$NON-NLS-1$

import urllib2
import httplib
import logging

__all__ = [u'urlopen'] #$NON-NLS-1$

logging.basicConfig()
LOG = logging.getLogger(__name__)

progress_callback = None

class ReportingSocket(object):
    u'''Wrapper around a socket. Gives progress report through a
    callback function.
    ''' #$NON-NLS-1$

    min_chunksize = 10240

    def __init__(self, socket):
        self.socket = socket

    def sendall(self, bits):
        u'''Sends all data, calling the callback function for every
        sent chunk.
        ''' #$NON-NLS-1$

        LOG.debug(u"SENDING: %s..." % bits[0:30]) #$NON-NLS-1$
        total = len(bits)
        sent = 0
        chunksize = max(self.min_chunksize, total / 100)

        while len(bits) > 0:
            send = bits[0:chunksize]
            self.socket.sendall(send)
            sent += len(send)
            if progress_callback:
                progress = float(sent) / total * 100
                progress_callback(progress, sent == total)

            bits = bits[chunksize:]

    def makefile(self, mode, bufsize):
        u'''Returns a file-like object for the socket.''' #$NON-NLS-1$

        return self.socket.makefile(mode, bufsize)

    def close(self):
        u'''Closes the socket.''' #$NON-NLS-1$

        return self.socket.close()

class ProgressHTTPConnection(httplib.HTTPConnection):
    u'''HTTPConnection that gives regular progress reports during
    sending of data.
    ''' #$NON-NLS-1$

    def connect(self):
        u'''Connects to a HTTP server.''' #$NON-NLS-1$

        httplib.HTTPConnection.connect(self)
        self.sock = ReportingSocket(self.sock)

class ProgressHTTPHandler(urllib2.HTTPHandler):
    u'''HTTPHandler that gives regular progress reports during sending
    of data.
    ''' #$NON-NLS-1$
    def http_open(self, req):
        return self.do_open(ProgressHTTPConnection, req)

def set_callback(method):
    u'''Sets the callback function to use for progress reports.''' #$NON-NLS-1$

    global progress_callback # IGNORE:W0603

    if not callable(method):
        raise ValueError(u'Callback method must be callable') #$NON-NLS-1$

    progress_callback = method

def urlopen(url_or_request, callback, body=None):
    u'''Opens an URL using the ProgressHTTPHandler.''' #$NON-NLS-1$

    set_callback(callback)
    opener = urllib2.build_opener(ProgressHTTPHandler)
    return opener.open(url_or_request, body)

if __name__ == u'__main__': #$NON-NLS-1$
    def upload(progress, finished):
        u'''Upload progress demo''' #$NON-NLS-1$

        LOG.info(u"%3.0f - %s" % (progress, finished)) #$NON-NLS-1$

    conn = urlopen(u"http://www.flickr.com/", u'x' * 10245, upload) #$NON-NLS-2$ #$NON-NLS-1$
    data = conn.read()
    LOG.info(u"Read data") #$NON-NLS-1$
    print data[:100].split(u'\n')[0] #$NON-NLS-1$

