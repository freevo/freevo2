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
# Revision 1.13  2003/09/06 17:53:58  mikeruelle
# plugin in the genre page if we have categories
#
# Revision 1.12  2003/09/06 17:16:55  gsbarbieri
# Make programs have same width and some enhancements to the CSS.
#
# Revision 1.11  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.10  2003/08/20 03:51:48  rshortt
# Patch from Mike so that the option boxes default to the day and time as
# displayed in the guide.
#
# Revision 1.9  2003/08/18 01:20:10  rshortt
# Another patch from Mike, this one adds the option to select the time you
# would like to view in the guide.
#
# Revision 1.8  2003/08/11 19:58:39  rshortt
# Patch from Mike Ruelle to add a row with the time in it every so many rows.
# Something like this could also be done using style sheets.
#
# Revision 1.7  2003/05/30 18:26:52  rshortt
# More mods from Mike including bugfixes and pretty(er) arrows.
#
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

from www.web_types import HTMLResource, FreevoResource
from twisted.web.woven import page

import tv.tv_util
import util
import config 
import tv.epg_xmltv 
import tv.record_client as ri
from twisted.web import static

DEBUG = 0

TRUE = 1
FALSE = 0


class GuideResource(FreevoResource):

    def makecategorybox(self, chanlist):
        allcategories = []
        for chan in chanlist:
            for prog in chan.programs:
                if prog.categories:
                    allcategories.extend(prog.categories)
        if allcategories:
            allcategories=util.unique(allcategories)
            allcategories.sort()
        else:
            return ''
        retval = '<select name="category">' + "\n"
        for cat in allcategories:
            retval += '<option value="%s" ' % cat
            retval += '>%s' % cat
            retval += "\n"
        retval += '</select>' + "\n"
        return retval

    def maketimejumpboxday(self, gstart):
        retval='<select name="day">\n'
        myt = time.time()
        myt_t = time.localtime(myt)
        gstart_t = time.localtime(gstart)
        myt = time.mktime((myt_t[0], myt_t[1], myt_t[2], 0, 0, 5, 
                           myt_t[6], myt_t[7], -1))
        listh = tv.tv_util.when_listings_expire()
        if listh == 0:
            return retval + '</select>\n'
        listd = int((listh/24)+2)
        for i in range(1, listd):
            retval += '<option value="' + str(myt) + '"'
            myt_t = time.localtime(myt)
            if (myt_t[0] == gstart_t[0] and \
                myt_t[1] == gstart_t[1] and \
                myt_t[2] == gstart_t[2]):
                retval += ' SELECTED '
            retval += '>' + time.strftime('%a %b %d', myt_t) + '\n'
            myt += 60*60*24
        retval += '</select>\n'
        return retval


    def maketimejumpboxoffset(self, gstart):
        retval = '<select name="offset">\n'
        myt = gstart
        myt_t = time.localtime(myt)
        hrstart = time.mktime((myt_t[0], myt_t[1], myt_t[2], 0, 0, 5, 
                               myt_t[6], myt_t[7], -1))
        hrinc = hrstart
        hrstop = hrstart + (60*60*24)
        while (hrinc < hrstop):
            myoff = hrinc - hrstart
            retval += '<option value="' + str(myoff) + '"'
            if (abs(gstart - hrinc) < 60):
                retval += ' SELECTED '
            retval += '>' + time.strftime('%H:%M', time.localtime(hrinc)) + '\n'
            hrinc += config.WWW_GUIDE_INTERVAL
        retval += '</select>\n'
        return retval


    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        INTERVAL = config.WWW_GUIDE_INTERVAL
        n_cols = config.WWW_GUIDE_COLS

        mfrguidestart = time.time()
        mfrguideinput = fv.formValue(form, 'stime')
        mfrguideinputday = fv.formValue(form, 'day')
        mfrguideinputoff = fv.formValue(form, 'offset')
        if mfrguideinput:
            mfrguidestart = int(mfrguideinput)
        elif mfrguideinputday and mfrguideinputoff:
            mfrguidestart = float(mfrguideinputday) + float(mfrguideinputoff)
        now = int(mfrguidestart / INTERVAL) * INTERVAL
        now2 = int(time.time() / INTERVAL) * INTERVAL
        mfrnextguide = now + INTERVAL * n_cols
        mfrnextguide += 10
        mfrprevguide = now - INTERVAL * n_cols
        mfrprevguide += 10
        if mfrprevguide < now2:
            mfrprevguide = 0

        guide = tv.epg_xmltv.get_guide()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        fv.printHeader('TV Guide', config.WWW_STYLESHEET, config.WWW_JAVASCRIPT)

        if not got_schedule:
            fv.res += '<h4>The recording server is down, recording information is unavailable.</h4>'

        pops = ''
        desc = ''

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<form>Jump&nbsp;to:&nbsp;' + self.maketimejumpboxday(now) + self.maketimejumpboxoffset(now) + '<input type=submit value="Change"></form>', 'class="guidehead"')
        categorybox =  self.makecategorybox(guide.chan_list)
        if categorybox:
            fv.tableCell('<form action="genre.rpy">Show&nbsp;Category:&nbsp;'+categorybox+'<input type=submit value="Change"></form>', 'class="guidehead"')
        fv.tableRowClose()
        fv.tableClose()

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" cols=\"%d\" width="100%%"' % ( n_cols + 1) )

        showheader = 0
        for chan in guide.chan_list:
            #put guidehead every X rows
            if showheader % 15 == 0:
                fv.tableRowOpen('class="chanrow"')
                headerstart = int(mfrguidestart / INTERVAL) * INTERVAL
                fv.tableCell(time.strftime('%b %d', time.localtime(headerstart)), 'class="guidehead"')
                for i in range(n_cols):
                    if i == n_cols-1 or i == 0:
                        dacell = ''
                        datime = time.strftime('%H:%M', time.localtime(headerstart))
                        if i == n_cols-1:
                            dacell = datime + '&nbsp;&nbsp;<a href="guide.rpy?stime=%i"><img src="images/RightArrow.png" border="0"></a>' % mfrnextguide
                        else:
                            if mfrprevguide > 0:
                                dacell = '<a href="guide.rpy?stime=%i"><img src="images/LeftArrow.png" border="0"></a>&nbsp;&nbsp;' % mfrprevguide + datime
                            else:
                                dacell = datime
                        fv.tableCell(dacell, 'class="guidehead"')
                    else:
                        fv.tableCell(time.strftime('%H:%M', time.localtime(headerstart)), 'class="guidehead"')
                    headerstart += INTERVAL
                fv.tableRowClose()
            showheader+= 1
                
            now = mfrguidestart
            fv.tableRowOpen('class="chanrow"')
            # chan.displayname = string.replace(chan.displayname, "&", "SUB")
            fv.tableCell(chan.displayname, 'class="channel"')
            c_left = n_cols

            if not chan.programs:
                fv.tableCell('&lt;&lt; NO DATA &gt;&gt;', 'class="programnodata" colspan="%s"' % n_cols)

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
                        style = ''
                        if colspan == n_cols:
                            style += 'text-align: center; '
                        
                        fv.tableCell(cell, 'class="'+status+'" onclick="showPop(\'%s\', this)" colspan="%s" style="%s"' % (popid, colspan, style))
                        now += INTERVAL*colspan
                        c_left -= colspan

            fv.tableRowClose()
        fv.tableClose()
        
        fv.res += pops

        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return fv.res


resource = GuideResource()
