# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# server.py - a simple webserver for use with pyNotifier
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: add doc
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Version: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Based on ideas from the ASPN Python Cookbook:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/259148/
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

__all__ = [ 'RequestHandler', 'Server' ]

import socket
import SimpleHTTPServer
import base64
import cgi
import crypt
import cStringIO
import os
import traceback
import logging

import config
import notifier
import util.fsocket as fsocket


# get logging object
log = logging.getLogger('www')

            
class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def __init__(self,conn,addr,server):
        self.client_address=addr
        self.connection=conn
        self.connection.setblocking(0)
        self.server=server
        self.rfile=fsocket.Socket(conn)
        self.rfile.set_condition(lambda x: x.find('\r\n\r\n') != -1,
                                 self.handle_request_line)
        self.wfile=self.rfile


    def log_message(self, format, *args):
        """
        Override BaseHTTPRequestHandler logging
        """
        log.info(format, *args)

        
    def do_GET(self):
        """
        Begins serving a GET request
        """
        path = self.path
        if os.path.splitext(path)[1]:
            for htdocs in self.server.htdocs:
                path = os.path.abspath(htdocs + self.path)
                if not path.startswith(htdocs):
                    log.warning('Sandbox violation: %s' % path)
                    self.send_error(404, "File not found")
                    return None
                if os.path.isfile(path):
                    break
            else:
                self.send_error(404, "File not found")
                
            ctype = self.guess_type(path)
            if ctype.startswith('text/'):
                mode = 'r'
            else:
                mode = 'rb'
            try:
                f = open(path, mode)
            except IOError:
                self.send_error(404, "File not found")
                return None
            self.send_response(200)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
            self.end_headers()

            self.wfile.writefd(f)
            return None
            
        for script_dir, script_import in self.server.scripts:
            path = self.path
            if os.path.isdir(script_dir + path):
                path += '/index'
            path = path.replace('//', '/')
            if os.path.isfile(script_dir + path + '.py'):
                try:
                    module = path[1:].replace('/', '.')
                    if not self.server.resources.has_key(path):
                        exec('import %s.%s as r' % \
                             (script_import, module))
                        self.server.resources[path] = r
                    else:
                        reload(self.server.resources[path])
                    break
                except Exception:
                    self.send_response(501)
                    self.send_header("Content-type", 'text/html')
                    self.end_headers()
                    error = '<h1>Webserver: Internal Server Error</h1>'
                    self.wfile.write(error)
                    self.wfile.write('<pre>')
                    traceback.print_exc(file=self.wfile)
                    self.wfile.write('</pre>')
                    return
        else:
            self.send_error(404, "File not found")
            return
        
        try:
            data = self.server.resources[path].resource.render(self)
        except Exception:
            self.send_response(501)
            self.send_header("Content-type", 'text/html')
            self.end_headers()
            self.wfile.write('<h1>Webserver: Internal Server Error</h1>')
            self.wfile.write('<pre>')
            traceback.print_exc(file=self.wfile)
            self.wfile.write('</pre>')
            return
        if not data:
            return

        mode = 'r'
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

        self.wfile.write(data)

        
    def __query(self, parsedQuery):
        """
        Returns the QUERY dictionary, similar to the result of cgi.parse_qs
        except that :
        - if the key ends with [], returns the value (a Python list)
        - if not, returns a string, empty if the list is empty, or with the
        first value in the list
        """
        res={}
        for item in parsedQuery.keys():
            value=parsedQuery[item] # a Python list
            if item.endswith("[]"):
                res[item[:-2]]=value
            else:
                if len(value)==0:
                    res[item]=''
                else:
                    res[item]=value[0]
        return res


    def handle_request_line(self, socket):
        """
        Called when the http request line and headers have been received
        """
        # prepare attributes needed in parse_request()
        self.raw_requestline=self.rfile.readline()
        self.parse_request()

        # if there is a Query String, decodes it in a QUERY dictionary
        if self.path.find('?')>=0:
            query_string = self.path[self.path.find('?')+1:]
            self.path    = self.path[:self.path.find('?')]
            self.query   = self.__query(cgi.parse_qs(query_string,1))
        else:
            self.query = {}

        auth = self.headers.getheader('Authorization')
        if auth and auth.startswith('Basic '):
            auth = base64.decodestring(auth[6:])

        if not self.__auth_user(auth):
            self.send_response(401, ' Authorization Required')
            self.send_header("Content-type", 'text/html')
            self.send_header("WWW-Authenticate", 'Basic realm="Freevo')
            self.end_headers()
            self.wfile.write('''
            <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
            <html><head>
            <title>401 Authorization Required</title>
            </head><body>
            <h1>Authorization Required</h1>
            <p>This server could not verify that you
            are authorized to access the document
            requested.  Either you supplied the wrong
            credentials (e.g., bad password), or your
            browser doesn\'t understand how to supply
            the credentials required.</p>
            <hr>
            ''')
            self.finish()
            return

        if self.command in ['GET','HEAD']:
            # if method is GET or HEAD, call do_GET or do_HEAD and finish
            method="do_"+self.command
            if hasattr(self,method):
                getattr(self,method)()
                self.finish()
        else:
            self.send_error(501, "Unsupported method (%s)" % self.command)


    def __auth_user(self, auth):
        if not auth: return False

        (username, password) = auth.split(':', 1)
        cryptedpassword = config.WWW_USERS.get(username)

        if cryptedpassword:
            return crypt.crypt(password, cryptedpassword[:2]) == cryptedpassword

        return False


    def finish(self):
        self.wfile.close()



class Server:
    def __init__ (self, ip, port, handler, scripts, htdocs):
        self.handler   = handler
        self.htdocs    = htdocs
        self.scripts   = scripts
        self.resources = {}
        try:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        except:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)

        # try to re-use a server port if possible
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass
        
        self.socket.bind((ip, port))
        self.socket.listen(5)
        notifier.addSocket( self.socket, self.accept )
        config.detect('channels')


    def accept (self, socket):
        try:
            conn, addr = socket.accept()
        except socket.error:
            log.error('warning: server accept() threw an exception')
            return True
        except TypeError:
            log.error('warning: server accept() threw EWOULDBLOCK')
            return True
        # creates an instance of the handler class to handle the
        # request/response on the incoming connexion
        self.handler(conn, addr, self)
        return True
