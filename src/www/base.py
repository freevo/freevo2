# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# guide.py - web interface basic classes
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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

# python imports
import base64
import os
import sys
import time
import crypt

# webserver imports
import conf


class FreevoResource(object):

    def render(self, request):
        pass


class HTMLResource(object):

    def __init__(self):
        self.res = ''


    def printContentType(self, content_type='text/html'):
        self.res += 'Content-type: %s\n\n' % content_type


    def printHeader(self, title='unknown page', style=None, script=None,
                    selected='Help', prefix=0, extrahead=''):

        strprefix = '../' * prefix

        self.res += '<?xml version="1.0" encoding="'+ conf.ENCODING +'"?>\n'
        self.res += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
        self.res += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        self.res += '<html>\n<head>\n'
        self.res += '\t<title>Freevo | '+title+'</title>\n'
        self.res += '\t<meta http-equiv="Content-Type" content= "text/html; charset='+ conf.ENCODING +'" />\n'
        if style != None:
            self.res += '\t<link rel="stylesheet" href="%sstyles/main.css" type="text/css" />\n' % strprefix
        if script != None:
            self.res += '\t<script language="JavaScript" src="'+script+'"></script>\n'
        self.res += '\t%s\n' % extrahead
        self.res += '</head>\n'
        self.res += '\n\n\n\n<body>\n'
        # Header
        self.res += '<!-- Header Logo and Status Line -->\n'
        self.res += '<div id="titlebar"><span class="name"><a href="http://freevo.sourceforge.net/" target="_blank">Freevo</a></span></div>\n'
     
        items = [(_('Home'),_('Home'),'%sindex' % str(strprefix)),
                 (_('TV Guide'),_('View TV Listings'),'%sguide' % str(strprefix)),
                 (_('Scheduled Recordings'),_('View Scheduled Recordings'),'%srecordings' % str(strprefix)),
#                  (_('Favorites'),_('View Favorites'),'%sfavorites.rpy' % str(strprefix)),
#                  (_('Media Library'),_('View Media Library'),'%slibrary.rpy' % str(strprefix)),
#                  (_('Manual Recording'),_('Schedule a Manual Recording'),'%smanualrecord.rpy' % str(strprefix)),
                 (_('Search'),_('Advanced Search Page'),'%ssearch' % str(strprefix)),
                 (_('Doc'),_('View Online Help and Documentation'),'%sdoc' % str(strprefix))]

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
        return
