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
# Revision 1.26  2005/01/08 15:40:55  dischi
# remove TRUE, FALSE, DEBUG and HELPER
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


import os, sys, time

import config

from twisted.web.woven import page
from twisted.web.resource import Resource


class FreevoPage(page.Page):
    
    def __init__(self, model=None, template=None):

        if not model:
            model = {'foo': 'bar'}
        if not template:
            template = '<html><head><title>ERROR</title></head>' + \
                       '<body>ERROR: no template</body></html>'

        page.Page.__init__(self, model, template=template)

        self.addSlash = 0


class FreevoResource(Resource):

    def render(self, request):
        username = request.getUser()
        password = request.getPassword()

        if not self.auth_user(username, password):
            request.setResponseCode(401, 'Authentication needed')
            # request.setHeader('Connection', 'close')
            request.setHeader('WWW-Authenticate', 'Basic realm="unknown"')
            request.setHeader('Content-Length', str(len('401: = Authorization needed.')))
            request.setHeader('Content-Type', 'text/html')
            return '<h1>401 Authentication required</h1>'
        else:
            return self._render(request)


    def auth_user(self, username, password):
        realpass = config.WWW_USERS.get(username)
        if password == realpass:
            return True
        else:
            return False


class HTMLResource:

    def __init__(self):
        self.res = ''


    def printContentType(self, content_type='text/html'):
        self.res += 'Content-type: %s\n\n' % content_type


    def printHeader(self, title='unknown page', style=None, script=None, selected='Help',prefix=0):

        strprefix = '../' * prefix

        self.res += '<?xml version="1.0" encoding="'+ config.encoding +'"?>\n'
        self.res += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
        self.res += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
        self.res += '<html>\n\t<head>\n'
        self.res += '\t<title>Freevo | '+title+'</title>\n'
        self.res += '\t<meta http-equiv="Content-Type" content= "text/html; charset='+ config.encoding +'"/>\n'
        if style != None:
            self.res += '\t<link rel="stylesheet" href="styles/main.css" type="text/css" />\n'
        if script != None:
            self.res += '\t<script language="JavaScript" src="'+script+'"></script>\n'
        self.res += '</head>\n'
        self.res += '\n\n\n\n<body>\n'
        # Header
        self.res += '<!-- Header Logo and Status Line -->\n'
        self.res += '<div id="titlebar"><span class="name"><a href="http://freevo.sourceforge.net/" target="_blank">Freevo</a></span></div>\n'
     
        items = [(_('Home'),_('Home'),'%sindex.rpy' % str(strprefix)),
                 (_('TV Guide'),_('View TV Listings'),'%sguide.rpy' % str(strprefix)),
                 (_('Scheduled Recordings'),_('View Scheduled Recordings'),'%srecord.rpy' % str(strprefix)),
                 (_('Favorites'),_('View Favorites'),'%sfavorites.rpy' % str(strprefix)),
                 (_('Media Library'),_('View Media Library'),'%slibrary.rpy' % str(strprefix)),
                 (_('Manual Recording'),_('Schedule a Manual Recording'),'%smanualrecord.rpy' % str(strprefix)),
                 (_('Search'),_('Advanced Search Page'),'%ssearch.rpy' % str(strprefix)),
                 (_('Help'),_('View Online Help and Documentation'),'%shelp/' % str(strprefix))]

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
