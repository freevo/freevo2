#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# record.rpy - Web interface to your scheduled recordings.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/05/22 21:33:24  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.4  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.3  2003/05/14 00:18:56  rshortt
# Better error handling.
#
# Revision 1.2  2003/05/12 23:02:41  rshortt
# Adding HTTP BASIC Authentication.  In order to use you must override WWW_USERS
# in local_conf.py.  This does not work for directories yet.
#
# Revision 1.1  2003/05/11 22:48:21  rshortt
# Replacements for the cgi files to be used with the new webserver.  These
# already use record_client / record_server.
#
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

class RecordResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        chan = fv.formValue(form, 'chan')
        start = fv.formValue(form, 'start')
        action = fv.formValue(form, 'action')

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader('Scheduled Recordings', 'styles/main.css')
            fv.res += '<h4>ERROR: recording server is unavailable</h4>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

            return fv.res

        if action == 'remove':
            (status, recordings) = ri.getScheduledRecordings()
            progs = recordings.getProgramList()
    
            for what in progs.values():
                if start == '%s' % what.start and chan == '%s' % what.channel_id:
                    prog = what

            print 'want to remove prog: %s' % prog
            ri.removeScheduledRecording(prog)
        elif action == 'add':
            (status, prog) = ri.findProg(chan, start)
            print 'RESULT: %s' % status
            print 'PROG: %s' % prog
            ri.scheduleRecording(prog)


        (status, recordings) = ri.getScheduledRecordings()
        progs = recordings.getProgramList()
        (status, favs) = ri.getFavorites()

        fv.printHeader('Scheduled Recordings', 'styles/main.css')

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Start Time', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Stop Time', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Title', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Program Description', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
        fv.tableRowClose()

        f = lambda a, b: cmp(a.start, b.start)
        progl = progs.values()
        progl.sort(f)
        for prog in progl:
            status = 'basic'

            (isFav, junk) = ri.isProgAFavorite(prog, favs)
            if isFav:
                status = 'favorite'
            try:
                if prog.isRecording == TRUE:
                    status = 'recording'
            except:
                # sorry, have to pass without doing anything.
                pass

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
    
            cell = '<a href="record.rpy?chan=%s&start=%s&action=remove">Remove</a>' % (prog.channel_id, prog.start)
            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

            fv.tableRowClose()

        fv.tableClose()
    
        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return fv.res
    
resource = RecordResource()
