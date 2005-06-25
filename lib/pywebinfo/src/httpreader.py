# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# httpreader.py - http implementation keeping the notifier alive.
# -----------------------------------------------------------------------------
# $Id$
#
# Todo: Add support for SSL, IPv6, Auth?
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Viggo Fredriksen <viggo@katatonic.org>
#
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

# python modules
import re
import os
import socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, EISCONN
from cStringIO import StringIO

import logging
log = logging.getLogger('pywebinfo')

# notifier to keep main loop alive
import notifier
if notifier.loop == None:
    notifier.init()

# socket timeouts
try:
    import timeoutsocket
    timeoutsocket.setDefaultSocketTimeout(1)
except ImportError:
    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(1)


class HTTPReader(object):
    """
    This class fetches documents with HTTP. This is done by
    using callbacks to the registered handler. The handler must
    support the following callbacks:

      - handle_progress(url, bytes_fetched_since_last, bytes_total_length):
          Makes it possible to do progress calculations.
      - handle_header(url, header):
          Makes it possible to do stuff with the header if nec.
      - handle_line(url, line):
          One line of data returned from socket of the body.
      - handle_finished(url):
          A request was completed. If an error occurs during the
          transfer, this will also be called.
      - handle_error(url, reason):
          A request failed to url with error reason.

    Creation of the class was motivated by the fact that I could
    not find a proper way of using sockets for the notifier with
    the existing python libs. Both urllib, urllib2 and httplib
    seems to do their own internal caching, and can not guarantee
    proper behaviour of their file-objects. This could lead to
    some nasty blocking issues for Freevo.

    @param url     : url to fetch
    @param handler : handler for callbacks
    @param language: agent language
    """

    # regular expressions
    m_chunk = re.compile('^([\dA-Fa-f]+).*$').match
    m_url   = re.compile('http:/+([^/:]*):*([^/]*)(.*)').match

    # connection info    
    length     = None
    connected  = False


    def __init__(self, url, handler, language='en-US'):
        self.url = url

        # extract url info
        match_url = self.m_url(url)

        if not match_url:
            # invalid url
            self.__fail('URL not supported or invalid')
        else:
            host = match_url.group(1)
            port = match_url.group(2)
            uri  = match_url.group(3)
    
            if port == '':
                # default to port 80
                port = 80
            else:
                # port defined
                port = int(port)
    
            # chunk information
            self.__chunked      = False
            self.__chunked_left = 0
            self.__chunked_over = None
    
            # header information
            self.__header  = {}
            self.__header_complete = False
    
            # handler for this connection
            self.__handler = handler
    
            # connection information
            self.__address     = (host, port)
            self.__in          = StringIO()
            self.__out         = ''
            self.__out_pointer = 0
            self.__out_length  = 0
            self.connected     = False
            self.length        = None
   
            # create the socket
            self.__socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.setblocking(0)
    
            # create a GET header
            self.add_header('GET %s HTTP/1.1\r\n' % uri)
            self.add_header('Host: %s:%i\r\n' % (host, port))
            self.add_header('User-Agent: Freevo (pywebinfo)\r\n')
            self.add_header('Accept-Language: %s\r\n' % language)
            self.add_header('Connection: close\r\n')
            self.header_finalize()
    
            # add the socket to the notifier
            notifier.addSocket(self.__socket, self.__write, notifier.IO_WRITE)


    def add_header(self, header):
        """
        Add to header
        """
        self.__out += header


    def header_finalize(self):
        """
        Complete the header
        """
        # add terminator
        self.add_header('\r\n')

        # set initial values
        self.__out_pointer = 0
        self.__out_length  = len(self.__out)


    def __fail(self, reason):
        """
        Handle failures
        """
        self.__handler.handle_progress(self.url, 1, 1)
        self.__handler.handle_error(self.url, reason)
        self.__cleanup()


    def __cleanup(self):
        """
        Clean up
        """
        try:
            # ensure the socket was closed.
            self.__socket.close()
        except:
            pass

        try:
            # Free the string buffer
            self.__in.close()
        except:
            pass

        self.connected = False
        self.__header  = None
        self.__in      = None
        self.__out     = None
        self.__socket  = None
        self.__handler = None


    def __connect(self, fd):
        """
        Connect to host.
        """
        try:
            err = fd.connect_ex(self.__address)
        except socket.gaierror, e:
            # address error
            self.__fail('Connection failure: %s' % e[1])
            return False

        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            # not yet connected
            return True

        elif err in (0, EISCONN):
            # connected to host
            self.connected = True
            return True

        # something wrong has happend
        self.__fail('Connection failure: %s' % os.strerror(err))
        return False


    def __write(self, fd):
        """
        Write output-buffer.
        """
        if not self.connected:
            # need to connect first
            return self.__connect(fd)

        try:
            # send as much data as possible
            self.__out_pointer += fd.send( self.__out[self.__out_pointer:] )
        
        except socket.error, e:
            self.__fail('Error sending to socket: %s' % e)
            return False

        except socket.timeout:
            self.__fail('Error sending to socket: socket timeout')
            return False

        if self.__out_pointer == self.__out_length:
            # done sending, start reading the response
            notifier.addSocket(self.__socket, self.__read, notifier.IO_READ)
            return False
        
        # continue sending
        return True


    def __read(self, fd):
        """
        read callback from notifier
        """
        try:
            # read data from the socket
            # FIXME: This value needs tuning.
            chunk = fd.recv(100)
        except socket.error, e:
            self.__fail('Error reading from socket: %s' % e)
            return False
        except socket.timeout:
            self.__fail('Error reading from socket: socket timeout')
            return False
        
        # write the data to the input-buffer
        self.__in.write(chunk)
        self.__in.seek(0)

        while 1:
            # FIXME: while 1: is dangerous if something
            #        unexpected happens.
            # read one line of data
            tell = self.__in.tell()
            line = self.__in.readline()

            if not line.endswith('\n'):
                # Incomplete read, seek back
                # before readline so we don't
                # miss any data.
                self.__in.seek(tell)
                break

            if not self.__header_complete:
                # Header parsing. Send header to
                # handler when header is complete.
                if not line.strip():
                    # reached end of header,
                    # no further reading nec.
                    self.__handler.handle_header(self.url, self.__header)
                    self.__header_complete = True
                    break
            
                if ':' in line:
                    # header value, split line at the colon
                    key, value = line.split(':', 1)
                    self.__server_header(key, value)

                elif line.startswith('HTTP'):
                    # http response code.
                    # FIXME: Handle 100 continue here!
                    self.__server_header('httpcode', line.split(' ')[1])
            else:
                # body handling, send lines to handler.
                # handle chunked data properly.
                if self.__chunked:
                    # handle chunked data
                    if self.__chunked_left <= 0:
                        # data is chunked, find the offset
                        m_chunk = self.m_chunk(line)
                        if m_chunk:
                            self.__chunked_left = int(m_chunk.group(1), 16)
                            continue

                    self.__chunked_left -= len(line)

                    if self.__chunked_over:
                        # add the leftover from last chunk
                        # to remove CRLF from previous line
                        line = ''.join([self.__chunked_over, line])
                        self.__chunked_over = None

                    if self.__chunked_left == 0:
                        self.__chunked_over = line[:-1]
                        continue

                    elif self.__chunked_left < 0:
                        self.__chunked_over = line[:-2]
                        continue
                
                # return the line to the parser
                self.__handler.handle_line(self.url, line)

        # remove the extracted info
        data = self.__in.read()
        self.__in.seek(0)
        self.__in.write(data)
        self.__in.truncate()

        if not chunk:
            # finished reading, return remaining lines
            # FIXME: verify that this is the correct sequence.
            if self.__chunked_over:
                # something has been left over
                self.__handler.handle_line(self.url, self.__chunked_over)
                self.__chunked_over = None

            line = self.__in.getvalue()
            if line:
                # something is left in the input buffer
                self.__handler.handle_line(self.url, line)
            
            self.__socket.close()

            if not self.length:
                # make sure we are 100% finished
                self.__handler.handle_progress(self.url, 1, 1)

            self.__handler.handle_finished(self.url)
            self.__cleanup()

            # remove socket
            return False

        # callback for progress indication
        self.__handler.handle_progress(self.url, len(chunk), self.length)

        # more information to be read.
        return True


    def __server_header(self, key, value):
        """
        Add a header to the request.
        """
        key   = key.lower()
        value = value.strip()

        self.__header[key] = value

        if key == 'content-length':
            # set the content length
            self.length = int(value)
    	elif key == 'transfer-encoding' and value == 'chunked':
            # the content is chunked
            self.__chunked = True
