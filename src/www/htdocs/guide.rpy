#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# guide.rpy - Web interface to the Freevo EPG.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/05/29 23:06:56  rshortt
# The ability to previous / next added by Mike Ruelle.  We'll make it pretty later.  Also some comment cleanup.
#
# Revision 1.5  2003/05/22 21:33:23  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.4  2003/05/14 12:28:00  rshortt
# Forgot to comment out a 'SUB'.
#
# Revision 1.3  2003/05/14 00:04:54  rshortt
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

import sys, string
import time

from web_types import HTMLResource, FreevoResource
from twisted.web.woven import page

import web

import config 
import xmltv
import epg_xmltv 
import record_client as ri
from twisted.web import static

DEBUG = 0

TRUE = 1
FALSE = 0


class GuideResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        INTERVAL = web.INTERVAL
        n_cols = web.n_cols

        mfrguidestart = time.time()
        mfrguideinput = fv.formValue(form, 'stime')
        if mfrguideinput:
            mfrguidestart = int(mfrguideinput)
        now = int(mfrguidestart / INTERVAL) * INTERVAL
        now2 = int(time.time() / INTERVAL) * INTERVAL
        mfrnextguide = now + INTERVAL * n_cols
        mfrprevguide = now - INTERVAL * n_cols
        if mfrprevguide < now2:
            mfrprevguide = 0

        guide = epg_xmltv.get_guide()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        fv.printHeader('TV Guide', web.STYLESHEET, web.JAVASCRIPT)

        if not got_schedule:
            fv.res += '<h4>The recording server is down, recording information is unavailable.</h4>'

        pops = ''
        desc = ''

        if mfrprevguide > 0:
            fv.res += '<a href="guide.rpy?stime=%i">Prev</a>&nbsp;&nbsp;' % mfrprevguide
        fv.res += '<a href="guide.rpy?stime=%i">Next</a><br />' % mfrnextguide

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1"')

        fv.tableRowOpen('class="chanrow"')
        fv.tableCell(time.strftime('%b %d'), 'class="guidehead"')
        now = int(mfrguidestart / INTERVAL) * INTERVAL
        for i in range(n_cols):
            fv.tableCell(time.strftime('%H:%M', time.localtime(now)), 'class="guidehead"')
            now += INTERVAL
        fv.tableRowClose()

        for chan in guide.chan_list:
            now = mfrguidestart
            fv.tableRowOpen('class="chanrow"')
            # chan.displayname = string.replace(chan.displayname, "&", "SUB")
            fv.tableCell(chan.displayname, 'class="channel"')
            c_left = n_cols

            if not chan.programs:
                fv.tableCell('&lt;&lt; NO DATA &gt;&gt;', 'class="program" colspan="%s"' % n_cols)

            for prog in chan.programs:
                if prog.stop > mfrguidestart and \
                   prog.start < mfrnextguide and \
                   c_left > 0:

                    status = 'program'

                    if got_schedule:
                        (result, message) = ri.isProgScheduled(prog, schedule)
                        if result:
                            status = 'scheduled'
                            really_now = time.time()
                            if prog.start <= really_now and prog.stop >= really_now:
                                # in the future we should REALLY see if it is 
                                # recording instead of just guessing
                                status = 'recording'

                    if prog.start <= now and prog.stop >= now:
                        cell = ""
                        if prog.start <= now - INTERVAL:
                            # show started earlier than the guide start,
                            # insert left arrows
                            cell += '&lt;&lt; '
                        showtime_left = int(prog.stop - now)
                        intervals = showtime_left / INTERVAL
                        colspan = intervals + 1
                        # prog.title = string.replace(prog.title, "&", "SUB")
                        # prog.desc = string.replace(prog.desc, "&", "SUB")
                        cell += '%s' % prog.title
                        if colspan > c_left:
                            # show extends past visible range,
                            # insert right arrows
                            cell += '  &gt;&gt;'
                            colspan = c_left
                        popid = '%s:%s' % (prog.channel_id, prog.start)
                        pops += '<div id="%s"  class="proginfo" >\n' % popid
                        pops += '  <div class="move" onmouseover="focusPop(\'%s\');" onmouseout="unfocusPop(\'%s\');" style="cursor:move">%s</div>\n' % (popid, popid, prog.title)
                        if prog.desc == '':
                            desc = 'Sorry, the program description for %s is unavailable.' % prog.title
                        else:
                            desc = prog.desc
                        pops += '  <div class="progdesc"><br /><font color="black">%s</font><br /><br /></div>\n' % desc
                        pops += '  <div class="poplinks" style="cursor:hand">\n' 
                        pops += '    <table width="100%" border="0" cellpadding="4" cellspacing="0">\n'
                        pops += '      <tr>\n'
                        pops += '        <td class="popbottom" '
                        pops += 'onClick="document.location=\'record.rpy?chan=%s&start=%s&action=add\'">Record</td>\n' % (prog.channel_id, prog.start)
                        pops += '        <td class="popbottom" '
                        pops += 'onClick="document.location=\'edit_favorite.rpy?chan=%s&start=%s&action=add\'">Add to Favorites</td>\n' % (prog.channel_id, prog.start)
                        pops += '        <td class="popbottom" '
                        pops += 'onClick="javascript:closePop(\'%s\');">Close Window</td>\n' % popid
                        pops += '      </tr>\n'
                        pops += '    </table>\n'
                        pops += '  </div>\n'
                        pops += '</div>\n'
                        fv.tableCell(cell, 'class="'+status+'" onclick="showPop(\'%s\', this)" colspan="%s"' % (popid, colspan))
                        now += INTERVAL*colspan
                        c_left -= colspan

            fv.tableRowClose()
        fv.tableClose()
        
        fv.res += pops

        if mfrprevguide > 0:
            fv.res += '<a href="guide.rpy?stime=%i">Prev</a>&nbsp;&nbsp;' % mfrprevguide
        fv.res += '<a href="guide.rpy?stime=%i">Next</a><br /><br />' % mfrnextguide

        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return fv.res


resource = GuideResource()
