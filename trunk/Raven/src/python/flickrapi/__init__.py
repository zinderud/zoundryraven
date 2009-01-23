#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore
from zoundry.base.net.http import ZSimpleTextHTTPRequest

u'''A FlickrAPI interface.

See `the FlickrAPI homepage`_ for more info.

.. _`the FlickrAPI homepage`: http://flickrapi.sf.net/
''' #$NON-NLS-1$

__version__ = u'1.1' #$NON-NLS-1$
__all__ = (u'FlickrAPI', u'IllegalArgumentException', u'FlickrError', #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        u'XMLNode', u'set_log_level', u'__version__') #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
__author__ = u'Sybren St\u00fcvel'.encode(u'utf-8') #$NON-NLS-2$ #$NON-NLS-1$

# Copyright (c) 2007 by the respective coders, see
# http://flickrapi.sf.net/
#
# This code is subject to the Python licence, as can be read on
# http://www.python.org/download/releases/2.5.2/license/
#
# For those without an internet connection, here is a summary. When this
# summary clashes with the Python licence, the latter will be applied.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import md5
import urllib
import urllib2
import mimetools
import os.path
import logging
import copy
import webbrowser

from flickrapi.tokencache import TokenCache, SimpleTokenCache
from flickrapi.xmlnode import XMLNode
from flickrapi.multipart import Part, Multipart, FilePart
from flickrapi.exceptions import IllegalArgumentException, FlickrError
from flickrapi.cache import SimpleCache
from flickrapi import reportinghttp

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def make_utf8(dictionary):
    u'''Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.
    
    Returns a copy of the dictionary, doesn't touch the original.
    ''' #$NON-NLS-1$
    
    result = {}

    for (key, value) in dictionary.iteritems():
        if isinstance(key, unicode):
            key = key.encode(u'utf-8') #$NON-NLS-1$
        if isinstance(value, unicode):
            value = value.encode(u'utf-8') #$NON-NLS-1$
        else:
            value = str(value)
        result[key] = value
    
    return result
        
def debug(method):
    u'''Method decorator for debugging method calls.

    Using this automatically sets the log level to DEBUG.
    ''' #$NON-NLS-1$

    LOG.setLevel(logging.DEBUG)

    def debugged(*args, **kwargs):
        LOG.debug(u"Call: %s(%s, %s)" % (method.__name__, args, #$NON-NLS-1$
            kwargs))
        result = method(*args, **kwargs)
        LOG.debug(u"\tResult: %s" % result) #$NON-NLS-1$
        return result

    return debugged

# REST parsers, {format: parser_method, ...}. Fill by using the
# @rest_parser(format) function decorator
rest_parsers = {}

def rest_parser(format):
    u'''Function decorator, use this to mark a function as the parser for REST as
    returned by Flickr.
    ''' #$NON-NLS-1$

    def decorate_parser(method):
        rest_parsers[format] = method
        return method

    return decorate_parser

class FlickrAPI:
    u"""Encapsulates Flickr functionality.
    
    Example usage::
      
      flickr = flickrapi.FlickrAPI(api_key)
      photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
      sets = flickr.photosets_getList(user_id='73509078@N00')
    """ #$NON-NLS-1$
    
    flickr_host = u"api.flickr.com" #$NON-NLS-1$
    flickr_rest_form = u"/services/rest/" #$NON-NLS-1$
    flickr_auth_form = u"/services/auth/" #$NON-NLS-1$
    flickr_upload_form = u"/services/upload/" #$NON-NLS-1$
    flickr_replace_form = u"/services/replace/" #$NON-NLS-1$

    def __init__(self, api_key, secret=None, fail_on_error=None, username=None,
            token=None, format=u'xmlnode', store_token=True, cache=False): #$NON-NLS-1$
        u"""Construct a new FlickrAPI instance for a given API key
        and secret.
        
        api_key
            The API key as obtained from Flickr.
        
        secret
            The secret belonging to the API key.
        
        fail_on_error
            If False, errors won't be checked by the FlickrAPI module.
            Deprecated, don't use this parameter, just handle the FlickrError
            exceptions.
        
        username
            Used to identify the appropriate authentication token for a
            certain user.
        
        token
            If you already have an authentication token, you can give
            it here. It won't be stored on disk by the FlickrAPI instance.

        format
            The response format. Use either "xmlnode" or "etree" to get a parsed
            response, or use any response format supported by Flickr to get an
            unparsed response from method calls. It's also possible to pass the
            ``format`` parameter on individual calls.

        store_token
            Disables the on-disk token cache if set to False (default is True).
            Use this to ensure that tokens aren't read nor written to disk, for
            example in web applications that store tokens in cookies.

        cache
            Enables in-memory caching of FlickrAPI calls - set to ``True`` to
            use. If you don't want to use the default settings, you can
            instantiate a cache yourself too:

            >>> f = FlickrAPI(api_key='123')
            >>> f.cache = SimpleCache(timeout=5, max_entries=100)
        """ #$NON-NLS-1$
        
        if fail_on_error is not None:
            LOG.warn(u"fail_on_error has been deprecated. Remove this " #$NON-NLS-1$
                     u"parameter and just handle the FlickrError exceptions.") #$NON-NLS-1$
        else:
            fail_on_error = True

        self.api_key = api_key
        self.secret = secret
        self.fail_on_error = fail_on_error
        self.default_format = format
        
        self.__handler_cache = {}

        if token:
            # Use a memory-only token cache
            self.token_cache = SimpleTokenCache()
            self.token_cache.token = token
        elif not store_token:
            # Use an empty memory-only token cache
            self.token_cache = SimpleTokenCache()
        else:
            # Use a real token cache
            self.token_cache = TokenCache(api_key, username)

        if cache:
            self.cache = SimpleCache()
        else:
            self.cache = None

    def __repr__(self):
        u'''Returns a string representation of this object.''' #$NON-NLS-1$


        return u'[FlickrAPI for key "%s"]' % self.api_key #$NON-NLS-1$
    __str__ = __repr__

    def trait_names(self):
        u'''Returns a list of method names as supported by the Flickr
        API. Used for tab completion in IPython.
        ''' #$NON-NLS-1$

        rsp = self.reflection_getMethods(format=u'etree') #$NON-NLS-1$

        def tr(name):
            u'''Translates Flickr names to something that can be called
            here.

            >>> tr(u'flickr.photos.getInfo')
            u'photos_getInfo'
            ''' #$NON-NLS-1$
            
            return name[7:].replace(u'.', u'_') #$NON-NLS-2$ #$NON-NLS-1$

        return [tr(m.text) for m in rsp.getiterator(u'method')] #$NON-NLS-1$

    @rest_parser(u'xmlnode') #$NON-NLS-1$
    def parse_xmlnode(self, rest_xml):
        u'''Parses a REST XML response from Flickr into an XMLNode object.''' #$NON-NLS-1$

        rsp = XMLNode.parse(rest_xml, store_xml=True)
        if rsp[u'stat'] == u'ok' or not self.fail_on_error: #$NON-NLS-2$ #$NON-NLS-1$
            return rsp
        
        err = rsp.err[0]
        raise FlickrError(u'Error: %(code)s: %(msg)s' % err) #$NON-NLS-1$

    @rest_parser(u'etree') #$NON-NLS-1$
    def parse_etree(self, rest_xml):
        u'''Parses a REST XML response from Flickr into an ElementTree object.''' #$NON-NLS-1$

        # Only import it here, to maintain Python 2.4 compatibility
        import xml.etree.ElementTree

        rsp = xml.etree.ElementTree.fromstring(rest_xml)
        if rsp.attrib[u'stat'] == u'ok' or not self.fail_on_error: #$NON-NLS-2$ #$NON-NLS-1$
            return rsp
        
        err = rsp.find(u'err') #$NON-NLS-1$
        raise FlickrError(u'Error: %s: %s' % ( #$NON-NLS-1$
            err.attrib[u'code'], err.attrib[u'msg'])) #$NON-NLS-2$ #$NON-NLS-1$

    def sign(self, dictionary):
        u"""Calculate the flickr signature for a set of params.
        
        data
            a hash of all the params and values to be hashed, e.g.
            ``{"api_key":"AAAA", "auth_token":"TTTT", "key":
            u"value".encode('utf-8')}``

        """ #$NON-NLS-1$

        data = [self.secret]
        for key in sorted(dictionary.keys()):
            data.append(key)
            datum = dictionary[key]
            if isinstance(datum, unicode):
                raise IllegalArgumentException(u"No Unicode allowed, " #$NON-NLS-1$
                        u"argument %s (%r) should have been UTF-8 by now" #$NON-NLS-1$
                        % (key, datum))
            data.append(datum)
        
        md5_hash = md5.new()
        md5_hash.update(u''.join(data)) #$NON-NLS-1$
        return md5_hash.hexdigest()

    def encode_and_sign(self, dictionary):
        u'''URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.
        ''' #$NON-NLS-1$
        
        dictionary = make_utf8(dictionary)
        if self.secret:
            dictionary[u'api_sig'] = self.sign(dictionary) #$NON-NLS-1$
        return urllib.urlencode(dictionary)
        
    def __getattr__(self, attrib):
        u"""Handle all the regular Flickr API calls.
        
        Example::

            flickr.auth_getFrob(api_key="AAAAAA")
            xmlnode = flickr.photos_getInfo(photo_id='1234')
            xmlnode = flickr.photos_getInfo(photo_id='1234', format='xmlnode')
            json = flickr.photos_getInfo(photo_id='1234', format='json')
            etree = flickr.photos_getInfo(photo_id='1234', format='etree')
        """ #$NON-NLS-1$

        # Refuse to act as a proxy for unimplemented special methods
        if attrib.startswith(u'_'): #$NON-NLS-1$
            raise AttributeError(u"No such attribute '%s'" % attrib) #$NON-NLS-1$

        # Construct the method name and see if it's cached
        method = u"flickr." + attrib.replace(u"_", u".") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        if method in self.__handler_cache:
            return self.__handler_cache[method]
        
        def handler(**args):
            u'''Dynamically created handler for a Flickr API call''' #$NON-NLS-1$

            if self.token_cache.token and not self.secret:
                raise ValueError(u"Auth tokens cannot be used without " #$NON-NLS-1$
                                 u"API secret") #$NON-NLS-1$

            # Set some defaults
            defaults = {u'method': method, #$NON-NLS-1$
                        u'auth_token': self.token_cache.token, #$NON-NLS-1$
                        u'api_key': self.api_key, #$NON-NLS-1$
                        u'format': self.default_format} #$NON-NLS-1$

            args = self.__supply_defaults(args, defaults)
            args = make_utf8(args)

            return self.__wrap_in_parser(self.__flickr_call,
                    parse_format=args[u'format'], **args) #$NON-NLS-1$

        handler.method = method
        self.__handler_cache[method] = handler
        return handler
    
    def __supply_defaults(self, args, defaults):
        u'''Returns a new dictionary containing ``args``, augmented with defaults
        from ``defaults``.

        Defaults can be overridden, or completely removed by setting the
        appropriate value in ``args`` to ``None``.

        >>> f = FlickrAPI('123')
        >>> f._FlickrAPI__supply_defaults(
        ...  {'foo': 'bar', 'baz': None, 'token': None},
        ...  {'baz': 'foobar', 'room': 'door'})
        {'foo': 'bar', 'room': 'door'}
        ''' #$NON-NLS-1$

        result = args.copy()
        for key, default_value in defaults.iteritems():
            # Set the default if the parameter wasn't passed
            if key not in args:
                result[key] = default_value

        for key, value in result.copy().iteritems():
            # You are able to remove a default by assigning None, and we can't
            # pass None to Flickr anyway.
            if result[key] is None:
                del result[key]
        
        return result

    def __flickr_call(self, **kwargs):
        u'''Performs a Flickr API call with the given arguments. The method name
        itself should be passed as the 'method' parameter.
        
        Returns the unparsed data from Flickr::

            data = self.__flickr_call(method='flickr.photos.getInfo',
                photo_id='123', format='rest')
        ''' #$NON-NLS-1$

        LOG.debug(u"Calling %s" % kwargs) #$NON-NLS-1$

        post_data = self.encode_and_sign(kwargs)

        # Return value from cache if available
        if self.cache and self.cache.get(post_data):
            return self.cache.get(post_data)

        url = u"http://" + FlickrAPI.flickr_host + FlickrAPI.flickr_rest_form #$NON-NLS-1$
        flicksocket = urllib.urlopen(url, post_data)
        reply = flicksocket.read()
        flicksocket.close()

        # Store in cache, if we have one
        if self.cache is not None:
            self.cache.set(post_data, reply)

        return reply
    
    def __wrap_in_parser(self, wrapped_method, parse_format, *args, **kwargs):
        u'''Wraps a method call in a parser.

        The parser will be looked up by the ``parse_format`` specifier. If there
        is a parser and ``kwargs['format']`` is set, it's set to ``rest``, and
        the response of the method is parsed before it's returned.
        ''' #$NON-NLS-1$

        # Find the parser, and set the format to rest if we're supposed to
        # parse it.
        if parse_format in rest_parsers and u'format' in kwargs: #$NON-NLS-1$
            kwargs[u'format'] = u'rest' #$NON-NLS-2$ #$NON-NLS-1$

        LOG.debug(u'Wrapping call %s(self, %s, %s)' % (wrapped_method, args, #$NON-NLS-1$
            kwargs))
        data = wrapped_method(*args, **kwargs)

        # Just return if we have no parser
        if parse_format not in rest_parsers:
            return data

        # Return the parsed data
        parser = rest_parsers[parse_format]
        return parser(self, data)

    def auth_url(self, perms, frob):
        u"""Return the authorization URL to get a token.

        This is the URL the app will launch a browser toward if it
        needs a new token.
            
        perms
            "read", "write", or "delete"
        frob
            picked up from an earlier call to FlickrAPI.auth_getFrob()

        """ #$NON-NLS-1$

        encoded = self.encode_and_sign({
                    u"api_key": self.api_key, #$NON-NLS-1$
                    u"frob": frob, #$NON-NLS-1$
                    u"perms": perms}) #$NON-NLS-1$

        return u"http://%s%s?%s" % (FlickrAPI.flickr_host, FlickrAPI.flickr_auth_form, encoded) #$NON-NLS-1$

    def web_login_url(self, perms):
        u'''Returns the web login URL to forward web users to.

        perms
            "read", "write", or "delete"
        ''' #$NON-NLS-1$
        
        encoded = self.encode_and_sign({
                    u"api_key": self.api_key, #$NON-NLS-1$
                    u"perms": perms}) #$NON-NLS-1$

        return u"http://%s%s?%s" % (FlickrAPI.flickr_host, FlickrAPI.flickr_auth_form, encoded) #$NON-NLS-1$

    def upload(self, fileStream, callback=None, **arg):
        u"""Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        fileStream
            file to upload
        callback
            method that gets progress reports
        title
            title of the photo
        description
            description a.k.a. caption of the photo
        tags
            space-delimited list of tags, ``'''tag1 tag2 "long
            tag"'''``
        is_public
            "1" or "0" for a public resp. private photo
        is_friend
            "1" or "0" whether friends can see the photo while it's
            marked as private
        is_family
            "1" or "0" whether family can see the photo while it's
            marked as private

        The callback method should take two parameters:
        def callback(progress, done)
        
        Progress is a number between 0 and 100, and done is a boolean
        that's true only when the upload is done.
        
        For now, the callback gets a 'done' twice, once for the HTTP
        headers, once for the body.
        """ #$NON-NLS-1$

        if not fileStream:
            raise IllegalArgumentException(u"fileStream must be specified") #$NON-NLS-1$
        
        # verify key names
        required_params = (u'api_key', u'auth_token', u'api_sig') #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        optional_params = (u'title', u'description', u'tags', u'is_public',  #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
                           u'is_friend', u'is_family', u'hidden') #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
        possible_args = required_params + optional_params
        
        for a in arg.keys():
            if a not in possible_args:
                raise IllegalArgumentException(u"Unknown parameter " #$NON-NLS-1$
                        u"'%s' sent to FlickrAPI.upload" % a) #$NON-NLS-1$

        arguments = {u'auth_token': self.token_cache.token, #$NON-NLS-1$
                     u'api_key': self.api_key} #$NON-NLS-1$
        arguments.update(arg)

        # Convert to UTF-8 if an argument is an Unicode string
        arg = make_utf8(arguments)
        
        if self.secret:
            arg[u"api_sig"] = self.sign(arg) #$NON-NLS-1$
        url = u"http://" + FlickrAPI.flickr_host + FlickrAPI.flickr_upload_form #$NON-NLS-1$

        return self._sendFile(url, arg, fileStream)
#
#        # construct POST data
#        body = Multipart()
#
#        for a in required_params + optional_params:
#            if a not in arg:
#                continue
#            
#            part = Part({u'name': a}, arg[a]) #$NON-NLS-1$
#            body.attach(part)
#
#        filepart = FilePart({u'name': u'photo'}, filename, u'image/jpeg') #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
#        body.attach(filepart)
#
#        return self.__send_multipart(url, body, callback)
    
    def replace(self, filename, fileStream, photo_id):
        u"""Replace an existing photo.

        Supported parameters:

        filename
            name of a file to upload
        fileStream
            file to upload
        photo_id
            the ID of the photo to replace
        """ #$NON-NLS-1$
        
        if not fileStream:
            raise IllegalArgumentException(u"fileStream must be specified") #$NON-NLS-1$
        if not photo_id:
            raise IllegalArgumentException(u"photo_id must be specified") #$NON-NLS-1$

        args = {u'filename': filename, #$NON-NLS-1$
                u'photo_id': photo_id, #$NON-NLS-1$
                u'auth_token': self.token_cache.token, #$NON-NLS-1$
                u'api_key': self.api_key} #$NON-NLS-1$

        args = make_utf8(args)
        
        if self.secret:
            args[u"api_sig"] = self.sign(args) #$NON-NLS-1$
        url = u"http://" + FlickrAPI.flickr_host + FlickrAPI.flickr_replace_form #$NON-NLS-1$

        del args[u"filename"] #$NON-NLS-1$

        return self._sendFile(url, args, fileStream)

#        # construct POST data
#        body = Multipart()
#
#        for arg, value in args.iteritems():
#            # No part for the filename
#            if value == u'filename': #$NON-NLS-1$
#                continue
#            
#            part = Part({u'name': arg}, value) #$NON-NLS-1$
#            body.attach(part)
#
#        filepart = FilePart({u'name': u'photo'}, filename, u'image/jpeg') #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
#        body.attach(filepart)
#
#        return self.__send_multipart(url, body)

    def _sendFile(self, url, params, fileStream):
        params[u"photo"] = fileStream #$NON-NLS-1$
        request = ZSimpleTextHTTPRequest(url)
        request.send(params)
        rspXML = request.getResponse()
        return self.parse_xmlnode(rspXML)
    # end sendFile()

    def __send_multipart(self, url, body, progress_callback=None):
        u'''Sends a Multipart object to an URL.
        
        Returns the resulting XML from Flickr.
        ''' #$NON-NLS-1$

        LOG.debug(u"Uploading to %s" % url) #$NON-NLS-1$
        request = urllib2.Request(url)
        request.add_data(str(body))
        
        (header, value) = body.header()
        request.add_header(header, value)
        
        if progress_callback:
            response = reportinghttp.urlopen(request, progress_callback)
        else:
            response = urllib2.urlopen(request)
        rspXML = response.read()

        return self.parse_xmlnode(rspXML)

    @classmethod
    def test_failure(cls, rsp, exception_on_error=True):
        u"""Exit app if the rsp XMLNode indicates failure.""" #$NON-NLS-1$

        LOG.warn(u"FlickrAPI.test_failure has been deprecated and will be " #$NON-NLS-1$
                 u"removed in FlickrAPI version 1.2.") #$NON-NLS-1$

        if rsp[u'stat'] != u"fail": #$NON-NLS-2$ #$NON-NLS-1$
            return
        
        message = cls.get_printable_error(rsp)
        LOG.error(message)
        
        if exception_on_error:
            raise FlickrError(message)

    @classmethod
    def get_printable_error(cls, rsp):
        u"""Return a printed error message string of an XMLNode Flickr response.""" #$NON-NLS-1$

        LOG.warn(u"FlickrAPI.get_printable_error has been deprecated " #$NON-NLS-1$
                 u"and will be removed in FlickrAPI version 1.2.") #$NON-NLS-1$

        return u"%s: error %s: %s" % (rsp.name, cls.get_rsp_error_code(rsp), cls.get_rsp_error_msg(rsp)) #$NON-NLS-1$

    @classmethod
    def get_rsp_error_code(cls, rsp):
        u"""Return the error code of an XMLNode Flickr response, or 0 if no
        error.
        """ #$NON-NLS-1$

        LOG.warn(u"FlickrAPI.get_rsp_error_code has been deprecated and will be " #$NON-NLS-1$
                 u"removed in FlickrAPI version 1.2.") #$NON-NLS-1$

        if rsp[u'stat'] == u"fail": #$NON-NLS-2$ #$NON-NLS-1$
            return int(rsp.err[0][u'code']) #$NON-NLS-1$

        return 0

    @classmethod
    def get_rsp_error_msg(cls, rsp):
        u"""Return the error message of an XMLNode Flickr response, or "Success"
        if no error.
        """ #$NON-NLS-1$

        LOG.warn(u"FlickrAPI.get_rsp_error_msg has been deprecated and will be " #$NON-NLS-1$
                 u"removed in FlickrAPI version 1.2.") #$NON-NLS-1$

        if rsp[u'stat'] == u"fail": #$NON-NLS-2$ #$NON-NLS-1$
            return rsp.err[0][u'msg'] #$NON-NLS-1$

        return u"Success" #$NON-NLS-1$

    def validate_frob(self, frob, perms):
        u'''Lets the user validate the frob by launching a browser to
        the Flickr website.
        ''' #$NON-NLS-1$
        
        auth_url = self.auth_url(perms, frob)
        webbrowser.open(auth_url, True, True)
        
    def get_token_part_one(self, perms=u"read"): #$NON-NLS-1$
        u"""Get a token either from the cache, or make a new one from
        the frob.
        
        This first attempts to find a token in the user's token cache
        on disk. If that token is present and valid, it is returned by
        the method.
        
        If that fails (or if the token is no longer valid based on
        flickr.auth.checkToken) a new frob is acquired.  The frob is
        validated by having the user log into flickr (with a browser).
        
        To get a proper token, follow these steps:
            - Store the result value of this method call
            - Give the user a way to signal the program that he/she
              has authorized it, for example show a button that can be
              pressed.
            - Wait for the user to signal the program that the
              authorization was performed, but only if there was no
              cached token.
            - Call flickrapi.get_token_part_two(...) and pass it the
              result value you stored.
        
        The newly minted token is then cached locally for the next
        run.
        
        perms
            "read", "write", or "delete"           
        
        An example::
        
            (token, frob) = flickr.get_token_part_one(perms='write')
            if not token: raw_input("Press ENTER after you authorized this program")
            flickr.get_token_part_two((token, frob))
        """ #$NON-NLS-1$
        
        # see if we have a saved token
        token = self.token_cache.token
        frob = None

        # see if it's valid
        if token:
            LOG.debug(u"Trying cached token '%s'" % token) #$NON-NLS-1$
            try:
                rsp = self.auth_checkToken(auth_token=token, format=u'xmlnode') #$NON-NLS-1$

                # see if we have enough permissions
                tokenPerms = rsp.auth[0].perms[0].text
                if tokenPerms == u"read" and perms != u"read": token = None #$NON-NLS-2$ #$NON-NLS-1$
                elif tokenPerms == u"write" and perms == u"delete": token = None #$NON-NLS-2$ #$NON-NLS-1$
            except FlickrError:
                LOG.debug(u"Cached token invalid") #$NON-NLS-1$
                self.token_cache.forget()
                token = None

        # get a new token if we need one
        if not token:
            # get the frob
            LOG.debug(u"Getting frob for new token") #$NON-NLS-1$
            rsp = self.auth_getFrob(auth_token=None, format=u'xmlnode') #$NON-NLS-1$
            self.test_failure(rsp)

            frob = rsp.frob[0].text

            # validate online
            self.validate_frob(frob, perms)

        return (token, frob)
        
    def get_token_part_two(self, (token, frob)):
        u"""Part two of getting a token, see ``get_token_part_one(...)`` for details.""" #$NON-NLS-1$

        # If a valid token was obtained in the past, we're done
        if token:
            LOG.debug(u"get_token_part_two: no need, token already there") #$NON-NLS-1$
            self.token_cache.token = token
            return token
        
        LOG.debug(u"get_token_part_two: getting a new token for frob '%s'" % frob) #$NON-NLS-1$

        return self.get_token(frob)
    
    def get_token(self, frob):
        u'''Gets the token given a certain frob. Used by ``get_token_part_two`` and
        by the web authentication method.
        ''' #$NON-NLS-1$
        
        # get a token
        rsp = self.auth_getToken(frob=frob, auth_token=None, format=u'xmlnode') #$NON-NLS-1$
        self.test_failure(rsp)

        token = rsp.auth[0].token[0].text
        LOG.debug(u"get_token: new token '%s'" % token) #$NON-NLS-1$
        
        # store the auth info for next time
        self.token_cache.token = token

        return token

def set_log_level(level):
    u'''Sets the log level of the logger used by the FlickrAPI module.
    
    >>> import flickrapi
    >>> import logging
    >>> flickrapi.set_log_level(logging.INFO)
    ''' #$NON-NLS-1$
    
    import flickrapi.tokencache

    LOG.setLevel(level)
    flickrapi.tokencache.LOG.setLevel(level)


if __name__ == u"__main__": #$NON-NLS-1$
    print u"Running doctests" #$NON-NLS-1$
    import doctest
    doctest.testmod()
    print u"Tests OK" #$NON-NLS-1$
