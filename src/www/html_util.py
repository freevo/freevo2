#if 0 /*
# -----------------------------------------------------------------------
# html_util.py - HTML helper functions.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/02/28 17:55:05  krister
# Bugfix, the output fp was not set to sys.stdout at the time of the call, instead it used the value at startup time. sys.stdout is re-routed dynamically by the internal python webserver after the client connects.
#
# Revision 1.5  2003/02/27 02:04:33  rshortt
# Committed some code by Michael Ruelle which adds highlighting and file
# size descriptions to library.cgi.
#
# Revision 1.4  2003/02/26 01:16:43  rshortt
# Added manualrecord.cgi to the links.  We may soon need to think of a better layout for the links as the interface grows.
#
# Revision 1.3  2003/02/20 21:52:26  rshortt
# Added a link 'Video Library' to library.cgi which was contributed by Mike Ruelle.
#
# Revision 1.2  2003/02/08 18:35:26  dischi
# added new version of freevoweb from Rob Shortt
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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

import os, sys
from time import *


def cgiIsCaller():
    return os.environ.has_key("HTTP_HOST")


def debug():
    print "Content-type: text/plain"
    print ""
    sys.stderr = sys.stdout


def printContentType(content_type="text/html", fp=None):
    if not fp:
        fp = sys.stdout
    if cgiIsCaller():
        fp.write('Content-type: %s\n\n' % content_type)


def printHeader(title="unknown page", style=None, script=None, fp=None):
    if not fp:
        fp = sys.stdout
    fp.write('<html><head>\n')
    fp.write('<title>'+title+'</title>\n')
    if style != None:
        # fp.write('<style ContentType="text/css" src="'+style+'"></style>\n')
        fp.write('<link rel="stylesheet" href="styles/main.css" type="text/css" />\n')
    if script != None:
        fp.write('<script language="JavaScript" src="'+script+'"></script>\n')
    fp.write('</head>\n')
    fp.write('<body>\n')


def tableOpen(opts="", fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("<table "+opts+">\n")


def tableClose(fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("</table>\n")


def tableRowOpen(opts="", fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("  <tr "+opts+">\n")


def tableRowClose(fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("  </tr>\n")


def tableCell(data="", opts="", fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("    <td "+opts+">"+data+"</td>\n")


def formValue(form=None, key=None):
    if not form or not key:
        return None

    try: 
        val = form[key].value
    except: 
        val = None

    return val


def printFooter(fp=None):
    if not fp:
        fp = sys.stdout
    fp.write('<hr>\n')
    fp.write("</body></html>\n")


def printSearchForm(fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("""
<form name="SearchForm" action="search.cgi" METHOD="GET">
<table>
  <tr>
    <td><font color="white"><b>Search:</b></font>&nbsp;</td>
    <td><input type="text" name="find" size=20 onBlur="document.SearchForm.submit()"></td>
  </tr>
</table>
</form>
""")


def printLinks(fp=None):
    if not fp:
        fp = sys.stdout
    fp.write("""
<center>
<table border=0 cellpadding=4 cellspacing=1>
  <tr>
    <td class="tablelink" onClick="document.location=\'guide.cgi\'">TV Guide</td>
    <td class="tablelink" onClick="document.location=\'record.cgi\'">Scheduled Recordings</td>
    <td class="tablelink" onClick="document.location=\'favorites.cgi\'">Favorites</td>
    <td class="tablelink" onClick="document.location=\'library.cgi\'">Video Library</td>
    <td class="tablelink" onClick="document.location=\'manualrecord.cgi\'">Manually Record</td>
  </tr>
</table>
</center>
""")


def descfsize(size):
    if size < 1024:
        return "%d bytes" % size
    elif size < 1048576:
        size = size / 1024
        return "%s KB" % size
    elif size < 1073741824:
        size = size / 1048576.0
        return "%.1f MB" % size
    else:
        size = size / 1073741824.0
        return "%.3f GB" % size


