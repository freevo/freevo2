# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# web_types.py - Classes useful for the web interface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/12/18 18:18:39  dischi
# small update, still not working
#
# Revision 1.1  2004/10/21 18:02:13  dischi
# example resources for the webserver
#
# Revision 1.25  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.24  2004/03/09 00:14:35  rshortt
# Add advanced search and link to search page.  Next will probably add genre
# options.
#
# Revision 1.23  2004/02/23 08:31:55  gsbarbieri
# Helper functions.
# Please use them to print messages to user.
# printMessagesFinish() should be used to generate the page ending stuff (links,
# foot, ...)
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

import config
import base64
import os, sys, time

class Resource:
    def render(self, request):
        pass


class FreevoResource(Resource):

    def render(self, request):
        auth = request.headers.getheader('Authorization')
        if auth and auth.startswith('Basic '):
            auth = base64.decodestring(auth[6:])

        if 0 and not self.__auth_user(auth):
            request.send_response(401, ' Authorization Required')
            request.send_header("Content-type", 'text/html')
            request.send_header("WWW-Authenticate", 'Basic realm="Freevo')
            request.end_headers()
            request.wfile.write('''
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
        else:
            return self._render(request)


    def _render(self, request):
        pass

    
    def __auth_user(self, auth):
        auth_list = [ ('dmeyer', 'foo') ]
        for username, password in auth_list:
            if '%s:%s' % (username, password) == auth:
                return True
        return False


class HTMLResource:

    def __init__(self):
        self.res = ''


    def printContentType(self, content_type='text/html'):
        self.res += 'Content-type: %s\n\n' % content_type


    def printHeader(self, title='unknown page', style=None, script=None,
                    selected='Help',prefix=0):

        strprefix = '../' * prefix

        self.res += '<?xml version="1.0" encoding="'+ config.encoding +'"?>\n'
        self.res += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
        self.res += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
        self.res += '<html>\n\t<head>\n'
        self.res += '\t<title>Freevo | '+title+'</title>\n'
        self.res += '\t<meta http-equiv="Content-Type" content= "text/html; charset='+ config.encoding +'"/>\n'
        if style != None:
            self.res += '\t<link rel="stylesheet" href="%sstyles/main.css" type="text/css" />\n' % strprefix
        if script != None:
            self.res += '\t<script language="JavaScript" src="'+script+'"></script>\n'
        self.res += '</head>\n'
        self.res += '\n\n\n\n<body>\n'
        # Header
        self.res += '<!-- Header Logo and Status Line -->\n'
        self.res += '<div id="titlebar"><span class="name"><a href="http://freevo.sourceforge.net/" target="_blank">Freevo</a></span></div>\n'
     
        items = [(_('Home'),_('Home'),'%sindex' % str(strprefix)),
#                  (_('TV Guide'),_('View TV Listings'),'%sguide.rpy' % str(strprefix)),
#                  (_('Scheduled Recordings'),_('View Scheduled Recordings'),'%srecord.rpy' % str(strprefix)),
#                  (_('Favorites'),_('View Favorites'),'%sfavorites.rpy' % str(strprefix)),
#                  (_('Media Library'),_('View Media Library'),'%slibrary.rpy' % str(strprefix)),
#                  (_('Manual Recording'),_('Schedule a Manual Recording'),'%smanualrecord.rpy' % str(strprefix)),
#                  (_('Search'),_('Advanced Search Page'),'%ssearch.rpy' % str(strprefix)),
                 (_('Doc'),_('View Online Help and Documentation'),'%sdoc' % str(strprefix))]

        try:
            if config.ICECAST_WWW_PAGE:
                items.append((_('Icecast List'),_('Change Icecast List'),'%siceslistchanger.rpy' % (strprefix)))
        except AttributeError:
            pass

        self.res += '<div id="header">\n<ul>'

        for i in items:
            if selected == i[0]:
                self.res += '<li id="current">'
            else:
                self.res += '<li>'
            self.res += "<a href=\"%s\" title=\"%s\">%s</a></li>\n" % (i[2], i[1],i[0])
        self.res += '</ul>\n</div>'
        
        #self.res += '<li id="current"><a href="#">Home</a></li>\n'
        #self.res += '<li><a href="#">TV Guide</a></li>\n'
        #self.res += '<li><a href="#">Scheduled Recordings</a></li>\n'
        #self.res += '<li><a href="#">Media Library</a></li>\n'
        #self.res += '<li><a href="#">Manual Record</a></li>\n'
        #self.res += '<li><a href="#">Help</a></li>\n'
        #self.res += '</ul>\n'
        #self.res += '</div>\n<br/>'
 
        #self.res += '<div id="subtitle">\n'
        #self.res += str(title) + '\n'
        #self.res += '</div>\n'
        self.res += '\n<!-- Main Content -->\n';



    def tableOpen(self, opts=''):
        self.res += "<table "+opts+">\n"


    def tableClose(self):
        self.res += "</table>\n"


    def tableHeadOpen(self, opts=''):
        self.res += "  <thead "+opts+">\n"


    def tableHeadClose(self, opts=''):
        self.res += "  </thead>\n"

    def tableBodyOpen(self, opts=''):
        self.res += "  <tbody "+opts+">\n"


    def tableBodyClose(self, opts=''):
        self.res += "  </tbody>\n"


    def tableFootOpen(self, opts=''):
        self.res += "  <tfoot "+opts+">\n"


    def tableFootClose(self, opts=''):
        self.res += "  </tfoot>\n"



    def tableRowOpen(self, opts=''):
        self.res += "     <tr "+opts+">\n"


    def tableRowClose(self):
        self.res += "     </tr>\n"


    def tableCell(self, data='', opts=''):
        self.res += "       <td "+opts+">"+data+"</td>\n"


    def formValue(self, form=None, key=None):
        if not form or not key:
            return None

        try: 
            val = form[key][0]
        except: 
            val = None
    
        return val


    def printFooter(self):
        self.res += '</body>\n</html>\n'
    
    
    def printSearchForm(self):
        self.res += """
    <form id="SearchForm" action="search.rpy" method="get">
    <div class="searchform"><b>"""+_('Search')+""":</b><input type="text" name="find" size="20" /></div>
    </form>
    """

    def printAdvancedSearchForm(self):
        self.res += """
    <form id="SearchForm" action="search.rpy" method="get">
    <div class="searchform"><b>"""+_('Search')+""":</b><input type="text" name="find" size="20" />
    <input type="checkbox" selected=0 name="movies_only" />"""+_('Movies only')+"""
    <input type="submit" value=" """+_('Go!')+""" " />
    </div>
    </form>
    """

    def printMessages( self, messages ):
        self.res += "<h4>"+_("Messages")+":</h4>\n"
        self.res += "<ul>\n"
        for m in messages:
            self.res += "   <li>%s</li>\n" % m
            self.res += "</ul>\n"

    def printMessagesFinish( self, messages ):
        """
        Print messages and add the search form, links and footer.
        """
        self.printMessages( messages )
        self.printSearchForm()
        self.printLinks()
        self.printFooter()
        
    def printLinks(self, prefix=0):
        #   
        #try:
        #    if config.ICECAST_WWW_PAGE:
        #        self.res += '<a href="%siceslistchanger.rpy">Change Icecast List</a>' % strprefix
        #except AttributeError:
        #    pass
        return
