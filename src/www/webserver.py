#if 0 /*
# -----------------------------------------------------------------------
# webserver.py - Simple httpd daemon
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/03/04 05:43:39  krister
# Added port settings for the builtin webserver. This is still work in progress!
#
# Revision 1.1  2003/02/28 17:52:41  krister
# First version of an internal python webserver. Work in progress.
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */
#endif

import os
import sys
import urllib
import time
from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler

import config # Freevo config

# CGI Script functions
import www.htdocs2.guide as guide
import www.htdocs2.edit_favorite as edit_favorite
import www.htdocs2.favorites as favorites
import www.htdocs2.library as library
import www.htdocs2.manualrecord as manualrecord
import www.htdocs2.record as record
import www.htdocs2.search as search 


def cgi_test():
    print 'Content-type: text/html'
    print ''
    print 'Hello from the test CGI app'
    

# Translate CGI script names into python module+function
# The modules are *not* reloaded, the webserver must be restarted
# if any changes are made.
cgi_apps = { 'guide.cgi' : guide.run_cgi,
             'edit_favorite.cgi' : edit_favorite.run_cgi,
             'favorites.cgi' : favorites.run_cgi,
             'library.cgi' : library.run_cgi,
             'manualrecord.cgi' : manualrecord.run_cgi,
             'record.cgi' : record.run_cgi,
             'search.cgi' : search.run_cgi,
             'tst.cgi' : cgi_test }


class FreevoHTTPServer(HTTPServer):

    def verify_request(self, request, client_address):
        ip = client_address[0]
        if not config.WWW_IP_ALLOW or ip in config.WWW_IP_ALLOW:
            return 1
        else:
            try:
                request.send('Content-type: text/plain\n\n')
                request.send('Error!\nClient IP %s not authorized!\n' % ip)
            except:
                pass
            return 0

    
class FreevoCGIHTTPRequestHandler(CGIHTTPRequestHandler):
    """This is a special CGI handler. It never executes external
    CGI apps, instead it knows about some builtin scripts that can
    be run.
    """
    
    def is_cgi(self):
        if '?' in self.path:
            if self.path.split('?')[0].endswith('.cgi'):
                return 1
            else:
                return 0
        else:
            if self.path.endswith('.cgi'):
                return 1
            else:
                return 0


    def run_cgi(self):
        """Execute a CGI script."""

        if '?' in self.path:
            cgi, query = os.path.basename(self.path).split('?')
        else:
            cgi = os.path.basename(self.path)
            query = ''

        self.log_message('CGI: "%s" "%s"', `cgi`, `query`)
        scriptname = cgi
        if cgi in cgi_apps:
            cgi_app = cgi_apps[cgi]
        else:
            self.send_error(404, "No such CGI script (%s)" % `scriptname`)
            return

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        rest = os.path.basename(self.path)
        env = {}
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['HTTP_HOST'] = self.server.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.server.server_port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.unquote(rest)
        env['PATH_INFO'] = uqrest
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        env['SCRIPT_NAME'] = scriptname
        if query:
            env['QUERY_STRING'] = query
        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]
        # XXX AUTH_TYPE
        # XXX REMOTE_USER
        # XXX REMOTE_IDENT
        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader
        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.getheader('user-agent')
        if ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(None, self.headers.getheaders('cookie'))
        if co:
            env['HTTP_COOKIE'] = ', '.join(co)
        # XXX Other HTTP_* headers
        os.environ.update(env)

        sys.stdout = self.wfile
        self.send_response(200, "Script output follows")

        t0 = time.time()
        cgi_app()
        self.log_message('CGI script done (%1.1f seconds)', (time.time() - t0))
        

def run():
    os.chdir('src/www/htdocs')
    srvaddr = ('', config.WWW_PORT)

    while 1:
        try:
            srvobj = FreevoHTTPServer(srvaddr, FreevoCGIHTTPRequestHandler)
            srvobj.serve_forever()
        except KeyboardInterrupt:
            sys.exit()
        except:
            pass
        sys.__stdout__.write('Ooops, server went down, restarting...\n')
        time.sleep(3)


if __name__ == '__main__':
    run()
