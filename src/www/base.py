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
# Revision 1.8  2005/02/03 16:05:38  rshortt
# Minor cosmetics fix.
#
# Revision 1.7  2005/02/02 02:13:16  rshortt
# Revive search page, add more search options.
#
# Revision 1.6  2005/01/13 20:19:33  rshortt
# Place the authentication into www/server.py to protect mote than just
# the .py files.
#
# Revision 1.5  2005/01/13 18:40:47  rshortt
# Add support for encrypted passwords, which is actually now required, you may
# use the passwd helper to generate crypted passwords for local_conf.py.
#
# Revision 1.4  2005/01/13 17:02:16  rshortt
# Reactivate authentication.
# TODO:
#  - SSL
#  - encrypted passwords
#
# Revision 1.3  2004/12/28 00:38:45  rshortt
# Reactivating web guide and scheduling recordings, this is still a major work
# in progress and there are still missing pieces.
#
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

import base64
import os
import sys
import time
import crypt

import config


class FreevoResource:

    def render(self, request):
        pass


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
        self.res += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        self.res += '<html>\n<head>\n'
        self.res += '\t<title>Freevo | '+title+'</title>\n'
        self.res += '\t<meta http-equiv="Content-Type" content= "text/html; charset='+ config.encoding +'" />\n'
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
                 (_('TV Guide'),_('View TV Listings'),'%sguide' % str(strprefix)),
                 (_('Scheduled Recordings'),_('View Scheduled Recordings'),'%srec' % str(strprefix)),
#                  (_('Favorites'),_('View Favorites'),'%sfavorites.rpy' % str(strprefix)),
#                  (_('Media Library'),_('View Media Library'),'%slibrary.rpy' % str(strprefix)),
#                  (_('Manual Recording'),_('Schedule a Manual Recording'),'%smanualrecord.rpy' % str(strprefix)),
                 (_('Search'),_('Advanced Search Page'),'%ssearch' % str(strprefix)),
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
        self.res += '</ul>\n</div><br clear="all" />'
        
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
    <form id="SearchForm" action="search" method="get">
    <div class="searchform"><b>"""+_('Search')+""":</b>
    <input type="text" name="find" size="20" />
    <input type="hidden" name="search_title" value="on" />
    <input type="hidden" name="search_subtitle" value="on" />
    <input type="hidden" name="search_description" value="on" /></div>
    </form>
    """

    def printAdvancedSearchForm(self):
        self.res += """
        <div class="searchform">
        <form id="SearchForm" action="search" method="get">
        <table border="0">
          <tr><td align="left"><b>"""+ _('Search')+ """:</b>
          <input type="text" name="find" size="20" /></td></tr>
          <tr><td align="left">
            <input type="checkbox" checked=1 name="search_title" />
            """+ _('Search title') +"""
          </td></tr>
          <tr><td align="left">
            <input type="checkbox" checked=1 name="search_subtitle" />
            """+ _('Search subtitle') +"""
          </td></tr>
          <tr><td align="left">
            <input type="checkbox" checked=1 name="search_description" />
            """+ _('Search description') +"""
          </td></tr>
          <tr><td align="left">
            <input type="submit" value=" """+ _('Go!') +""" " />
          </td></tr>
        </table>
        </form>
        </div>
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
