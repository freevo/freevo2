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
from twisted.web.resource import Resource
from web_types import HTMLResource

TRUE = 1
FALSE = 0


class SearchResource(Resource):

    def render(self, request):
        fv = HTMLResource()
        form = request.args

        find = fv.formValue(form, 'find')

        (result, progs) = ri.findMatches(find)
        (result, favs) = ri.getFavorites()

        (result, recordings) = ri.getScheduledRecordings()
        rec_progs = recordings.getProgramList()

        fv.printHeader('Search Results', 'styles/main.css')

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<img src="images/logo_200x100.png" />', 'align="left"')
        fv.tableCell('Search Results', 'class="heading" align="left"')
        fv.tableRowClose()
        fv.tableClose()

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

            if rf.isProgAFavorite(prog, favs):
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
                cell = '<a href="record.cgi?chan=%s&start=%s&action=remove">Remove</a>' % (prog.channel_id, prog.start)
            elif status == 'recording':
                cell = '<a href="record.cgi?chan=%s&start=%s">Record</a>' % (prog.channel_id, prog.start)
            else:
                cell = '<a href="record.cgi?chan=%s&start=%s">Record</a>' % (prog.channel_id, prog.start)

            cell += ' | <a href="edit_favorite.cgi?chan=%s&start=%s&action=add">New favorite</a>' % (prog.channel_id, prog.start)
            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

            fv.tableRowClose()

        fv.tableClose()

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return fv.res
    
resource = SearchResource()

