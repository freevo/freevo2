#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# genre.rpy - Show what is on for today for a particular category
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/08/24 21:41:44  mikeruelle
# adding a new page to see shows of a certain category
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

import sys, time, string

import record_client as ri
from web_types import HTMLResource, FreevoResource
import web
import epg_xmltv
import util
import tv_util
import config

TRUE = 1
FALSE = 0

class GenreResource(FreevoResource):

# need sub to get list of possible categories

    def makecategorybox(self, categories, category):
        retval = '<select name="category">' + "\n"
        for cat in categories:
            retval += '<option value="%s" ' % cat
            if cat == category:
                retval += 'SELECTED '
            retval += '>%s' % cat
            retval += "\n"
        retval += '</select>' + "\n"
        return retval

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        mfrguidestart = time.time()
        mfrguideinput = fv.formValue(form, 'stime')
        if mfrguideinput:
            mfrguidestart = int(mfrguideinput)
        # a little before midnight the day of mfrguidestart
        myt_t=time.localtime(mfrguidestart)
        mfrnextguide=time.mktime((myt_t[0], myt_t[1], myt_t[2], 23, 59, 5, myt_t[6], myt_t[7], -1))
        # a little after midnight the day before mfrguidestart
        mfrprevguide=time.mktime((myt_t[0], myt_t[1], myt_t[2]-1, 0, 0, 5, myt_t[6], myt_t[7], -1))
        # kill mfrprevguide to zero if it is less than now
        if mfrprevguide < time.time():
            now_t = time.localtime(time.time())
            newmyt2 = myt_t[2]-1
            if (myt_t[0] == now_t[0] and myt_t[1] == now_t[1] and newmyt2 == now_t[2]):
                mfrprevguide = time.time()
            else:
                mfrprevguide = 0

        category = fv.formValue(form, 'category')

        guide = epg_xmltv.get_guide()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        fv.printHeader('TV Genre for %s' % time.strftime('%a %b %d', time.localtime(mfrguidestart)), web.STYLESHEET, web.JAVASCRIPT)

        if not got_schedule:
            fv.res += '<h4>The recording server is down, recording information is unavailable.</h4>'

        allcategories = []
        for chan in guide.chan_list:
            for prog in chan.programs:
                if prog.categories:
                    allcategories.extend(prog.categories)
        if allcategories:
            allcategories=util.unique(allcategories)
            allcategories.sort()

        stime=''
        if mfrguideinput:
            stime='<input name="stime" type="hidden" value="%i">' % int(mfrguideinput)
        keepcat = ''
        if category:
            keepcat = '&category=%s' % category
        bforcell=''
        acelltime=mfrnextguide + 60
        aftercell='&nbsp;&nbsp;&nbsp;<a href="genre.rpy?stime=%i%s"><img src="images/RightArrow.png" border="0"></a>' % (acelltime, keepcat)
        if mfrprevguide > 0:
            bforcell='<a href="genre.rpy?stime=%i%s"><img src="images/LeftArrow.png" border="0"></a>&nbsp;&nbsp;&nbsp;' % (mfrprevguide, category)
        
        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<form>'+bforcell+'Show&nbsp;Category:&nbsp;' + self.makecategorybox(allcategories, category)+stime+'<input type=submit value="Change">'+aftercell+'</form>', 'class="guidehead"')
        fv.tableRowClose()
        fv.tableClose()
 
        if not category:
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
            return fv.res

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Channel', 'class="guidehead"')
        fv.tableCell('Program', 'class="guidehead"')
        fv.tableCell('Start', 'class="guidehead"')
        fv.tableCell('Stop', 'class="guidehead"')
        fv.tableRowClose()

        pops = ''
        desc = ''

        for chan in guide.chan_list:
            for prog in chan.programs:
                if prog.stop > mfrguidestart and prog.start < mfrnextguide:
                    status = 'program'

                    # match the category
                    if category in prog.categories:
                        print 'found it'
                    else:
                        continue

                    # figure out if in progress

                    if got_schedule:
                        (result, message) = ri.isProgScheduled(prog, schedule)
                        if result:
                            status = 'scheduled'
                            really_now = time.time()
                            if prog.start <= really_now and prog.stop >= really_now:
                                # in the future we should REALLY see if it is 
                                # recording instead of just guessing
                                status = 'recording'

                    fv.tableRowOpen('class="chanrow"')
                    fv.tableCell(chan.displayname, 'class="channel"')
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
                    fv.tableCell(prog.title, 'class="'+status+'" onclick="showPop(\'%s\', this)" width="80%%"' % popid )
                    fv.tableCell(time.strftime('%H:%M', time.localtime(prog.start)), 'class="channel"')
                    fv.tableCell(time.strftime('%H:%M', time.localtime(prog.stop)), 'class="channel"')
                    fv.tableRowClose()
        fv.tableClose()
        fv.res += pops

        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return fv.res
    

resource = GenreResource()
