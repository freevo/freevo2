#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# search.rpy - Web interface to search the Freevo EPG.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/05/30 19:17:27  rshortt
# Removing the old header, it was being printed too.
#
# Revision 1.7  2003/05/22 21:33:24  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.6  2003/05/16 03:21:33  rshortt
# Bugfix.
#
# Revision 1.5  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.4  2003/05/12 23:26:10  rshortt
# small bugfix
#
# Revision 1.3  2003/05/12 23:02:41  rshortt
# Adding HTTP BASIC Authentication.  In order to use you must override WWW_USERS
# in local_conf.py.  This does not work for directories yet.
#
# Revision 1.2  2003/05/12 11:21:51  rshortt
# bugfixes
#
# Revision 1.1  2003/05/11 22:48:21  rshortt
# Replacements for the cgi files to be used with the new webserver.  These
# already use record_client / record_server.
#
# Revision 1.2  2003/02/11 06:40:57  krister
# Applied Robs patch for std fileheaders.
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

import sys, time

import record_client as ri
from web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0


class SearchResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader('Search Results', 'styles/main.css')
            fv.res += '<h4>ERROR: recording server is unavailable</h4>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

            return fv.res

        find = fv.formValue(form, 'find')

        (got_matches, progs) = ri.findMatches(find)

        if got_matches: 
            (result, favs) = ri.getFavorites()
            (result, recordings) = ri.getScheduledRecordings()
            if result:
                rec_progs = recordings.getProgramList()

        fv.printHeader('Search Results', 'styles/main.css')

        if not got_matches: 
            fv.res += '<h3>No matches</h3>'

        else:
            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Start Time', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Stop Time', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Title', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Program Description', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()

            for prog in progs:

                status = 'basic'

                for rp in rec_progs.values():

                    if rp.start == prog.start and rp.channel_id == prog.channel_id:
                        status = 'scheduled'
                        try:
                            if rp.isRecording == TRUE:
                                status = 'recording'
                        except:
                            sys.stderr.write('isRecording not set')
    
                if ri.isProgAFavorite(prog, favs):
                    status = 'favorite'
    
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.start)), 'class="'+status+'" align="left" colspan="1"')
                fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.stop)), 'class="'+status+'" align="left" colspan="1"')
                fv.tableCell(prog.channel_id, 'class="'+status+'" align="left" colspan="1"')
                fv.tableCell(prog.title, 'class="'+status+'" align="left" colspan="1"')
    
                if prog.desc == '':
                    cell = 'Sorry, the program description for "%s" is unavailable.' % prog.title
                else:
                    cell = prog.desc
                fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')
    
                if status == 'scheduled':
                    cell = '<a href="record.rpy?chan=%s&start=%s&action=remove">Remove</a>' % (prog.channel_id, prog.start)
                elif status == 'recording':
                    cell = '<a href="record.rpy?chan=%s&start=%s&action=add">Record</a>' % (prog.channel_id, prog.start)
                else:
                    cell = '<a href="record.rpy?chan=%s&start=%s&action=add">Record</a>' % (prog.channel_id, prog.start)
    
                cell += ' | <a href="edit_favorite.rpy?chan=%s&start=%s&action=add">New favorite</a>' % (prog.channel_id, prog.start)
                fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')
    
                fv.tableRowClose()

            fv.tableClose()

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return fv.res
    
resource = SearchResource()

