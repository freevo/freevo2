#if 0 /*
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
# Revision 1.19  2004/01/28 03:35:01  outlyer
# Cleanup...
#
# o Indent paragraphs
# o Use normal 'href' links in the main bar as well as the javascript so
# non-javascript browsers can still work.
#
# Revision 1.18  2004/01/14 22:07:26  outlyer
# The new header code...
#
# Revision 1.17  2004/01/09 19:35:49  outlyer
# Inherit DEBUG parameter from config, move some prints into DEBUG
#
# Revision 1.16  2003/11/06 19:55:28  mikeruelle
# remove hard links so we can run when proxied
#
# Revision 1.15  2003/09/23 18:22:42  dischi
# use absolute path names
#
# Revision 1.14  2003/09/12 20:34:16  dischi
# start internal help system
#
# Revision 1.13  2003/09/12 19:39:35  gsbarbieri
# <thead>, <tbody> and <tfoot> support.
#
# Revision 1.12  2003/09/06 22:11:40  gsbarbieri
# Rewoked Popup box so it looks better in Internet Exploder.
# Guide now has configurable precision, defaults to 5 minutes.
#
# Revision 1.11  2003/09/02 22:41:08  mikeruelle
# adding icecast if the user asks for it.
#
# Revision 1.10  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.9  2003/07/14 19:30:36  rshortt
# Library update from Mike Ruelle.  Now you can view other media types and
# download as well.
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

import os, sys, time

import config

from twisted.web.woven import page
from twisted.web.resource import Resource

DEBUG = config.DEBUG
TRUE = 1
FALSE = 0


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
            return TRUE
        else:
            return FALSE


class HTMLResource:

    def __init__(self):
        self.res = ''


    def printContentType(self, content_type='text/html'):
        self.res += 'Content-type: %s\n\n' % content_type


    def printHeader(self, title='unknown page', style=None, script=None):
        self.res += '<html>\n\t<head>\n'
        self.res += '<title>Freevo | '+title+'</title>\n'
        if style != None:
            self.res += '<link rel="stylesheet" href="styles/main.css" type="text/css" />\n'
        if script != None:
            self.res += '<script language="JavaScript" src="'+script+'"></script>\n'
        self.res += '</head>\n'
        self.res += '\n\n\n\n<body>\n'
        # Header
        self.res += '<!-- Header Logo and Status Line -->'
        self.res += '<div id="titlebar"></div>\n'
        self.res += '<div id="subtitle">\n'
        self.res += str(title) + '\n'
        self.res += '</div>\n'
        self.res += '<!-- Main Content -->'
        self.res+=('<br />')



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
        # self.res += '</ul>\n'
        self.res += "</body></html>\n"
    
    
    def printSearchForm(self):
        self.res += """
    <form name="SearchForm" action="search.rpy" METHOD="GET">
    <div class="searchform"><b>Search:</b><input type="text" name="find" size="20" onBlur="document.SearchForm.submit()" /></div>
    </form>
    """
    
    
    def printLinks(self, prefix=0):
        strprefix = '../' * prefix
        self.res += """
    <center>
    <table border="0" cellpadding="0" cellspacing="0">
      <tr>
        <td height="24" width="11" background="images/round_left.png">&nbsp;</td>
        <td class="tablelink" onClick="document.location=\'%sindex.rpy\'"><a title="Home" href="%sindex.rpy">Home</a></td>
        <td class="tablelink" onClick="document.location=\'%sguide.rpy\'"><a title="View Guide" href="%sguide.rpy">TV Guide</a></td>
        <td class="tablelink" onClick="document.location=\'%srecord.rpy\'"><a title="View Scheduled Recordings" href="%srecord.rpy">Scheduled Recordings</a></td>
        <td class="tablelink" onClick="document.location=\'%sfavorites.rpy\'"><a title="View Favourites" href="%sfavorites.rpy">Favorites</a></td>
        <td class="tablelink" onClick="document.location=\'%slibrary.rpy\'"><a title="View Media Library" href="%slibrary.rpy">Media Library</a></td>
        <td class="tablelink" onClick="document.location=\'%smanualrecord.rpy\'"><a title="Schedule a Manual Recording" href="%smanualrecord.rpy">Manually Record</a></td>
     """ % (strprefix,strprefix,strprefix,strprefix,strprefix,strprefix,
            strprefix,strprefix,strprefix,strprefix,strprefix,strprefix)
        try:
            if config.ICECAST_WWW_PAGE:
                self.res += '<td class="tablelink" onClick="document.location=\'%siceslistchanger.rpy\'">Change Icecast List</td>' % strprefix
        except AttributeError:
            pass

        self.res += '<td class="tablelink" onClick="document.location=\'%shelp/\'"><a href="%shelp/" title="Get Help with Freevo">Help</a></td>' % (strprefix, strprefix)

        self.res += """
	<td height="24" width="11" background="images/round_right.png" cellpadding=0 cellspacing=0>&nbsp;</td>
      </tr>
    </table>
    </center>
    """

