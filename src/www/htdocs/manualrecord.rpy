#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# manualrecord.rpy - Web interface to manually schedule recordings.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
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

import tv.epg_xmltv, tv.epg_types
import tv.record_client as ri

# Use the alternate strptime module which seems to handle time zones
#
# XXX Remove when we are ready to require Python 2.3
if float(sys.version[0:3]) < 2.3:
    import tv.strptime as strptime
else:
    import _strptime as strptime


from www.web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0

# maxinum number of days we can record
MAXDAYS = 7

# minimum amount of time it would take record_server.py to pick us up in seconds
# by default it is one minute plus a few seconds just in case
MINPICKUP = 70


class ManualRecordResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader('Manual Record', 'styles/main.css')
            fv.res += '<h4>ERROR: recording server is unavailable</h4>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

            return fv.res

        curtime_epoch = time.time()
        curtime = time.localtime(curtime_epoch)
        chan = fv.formValue(form, 'chan')
        startmonth = fv.formValue(form, 'startmonth')
        startday = fv.formValue(form, 'startday')
        starthour = fv.formValue(form, 'starthour')
        startminute = fv.formValue(form, 'startminute')
        startyear = curtime[0] 
        stopmonth = fv.formValue(form, 'stopmonth')
        stopday = fv.formValue(form, 'stopday')
        stophour = fv.formValue(form, 'stophour')
        stopminute = fv.formValue(form, 'stopminute')
        stopyear = curtime[0] 
        currentmonth = curtime[1] 
        desc = fv.formValue(form, 'desc')
        title = fv.formValue(form, 'title')
        action = fv.formValue(form, 'action')
        errormsg = ''

        # look for action to do an add
        if action:
            if action == "add":
                # handle the year wraparound
                if int(stopmonth) < currentmonth:
                    stopyear = str(int(stopyear) + 1)
                if int(startmonth) < currentmonth:
                    startyear = str(int(startyear) + 1)
                # create utc second start time
                starttime = time.mktime(strptime.strptime(str(startmonth)+" "+str(startday)+" "+str(startyear)+" "+str(starthour)+":"+str(startminute)+":00",'%m %d %Y %H:%M:%S'))
                # create utc stop time
                stoptime = time.mktime(strptime.strptime(str(stopmonth)+" "+str(stopday)+" "+str(stopyear)+" "+str(stophour)+":"+str(stopminute)+":00",'%m %d %Y %H:%M:%S'))
                # so we don't record for more then maxdays (maxdays day * 24hr/day * 60 min/hr * 60 sec/min)
                if abs(stoptime - starttime) < (MAXDAYS * 86400): 
                    if starttime < stoptime:
                        if stoptime < curtime_epoch + MINPICKUP:
                            errormsg = "Sorry, the stop time does not give enough time for cron to pickup the change.  Please set it to record for a few minutes longer."
                        else:
                            # assign attributes to object
                            prog = tv.epg_types.TvProgram()
                            prog.channel_id = chan
                            if title:
                                prog.title = title
                            else:
                                prog.title = "Manual Recorded"
                            if desc:
                                prog.desc = desc
                            prog.start = starttime
                            prog.stop = stoptime
                            # use ri to add to schedule
                            ri.scheduleRecording(prog)
                            return '<html><head><meta HTTP-EQUIV="REFRESH" CONTENT="0;URL=record.rpy"></head></html>'
                    else:
                        errormsg = "start time is not before stop time." 
                else:
                    errormsg = "Program would record for more than " + str(MAXDAYS) + " day(s)!"

        if errormsg or not action:
            guide = tv.epg_xmltv.get_guide()
            channelselect = '<select name="chan">'
            for ch in guide.chan_list:
                channelselect = channelselect + '<option value="'+ch.id+'">'+str(ch.displayname)+"\n"
            channelselect = channelselect + "</select>\n"

            #build some reusable date inputs
            #month
            monthselect = '<select name="%s" %s >'
            months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
            iter=1
            for m in months:
                if curtime[1] == iter:
                    monthselect = monthselect + '<option selected value="'+str(iter)+'">'+m+"\n"
                else:
                    monthselect = monthselect + '<option value="'+str(iter)+'">'+m+"\n"
                iter = iter + 1
            monthselect = monthselect + "</select>\n"

            #day
            dayselect = '<select name="%s" %s >'
            iter=1
            while iter < 31:
                if curtime[2] == iter:
                    dayselect = dayselect + '<option selected value="'+str(iter)+'">'+str(iter)+"\n"
                else:
                    dayselect = dayselect + '<option value="'+str(iter)+'">'+str(iter)+"\n"
                iter = iter + 1
            dayselect = dayselect + "</select>\n"

            #hour
            hourselect = '<select name="%s" %s >'
            iter=0
            while iter < 24:
                if curtime[3] == iter:
                    hourselect = hourselect + '<option selected value="'+str(iter)+'">'+str(iter)+"\n"
                else:
                    hourselect = hourselect + '<option value="'+str(iter)+'">'+str(iter)+"\n"
                iter = iter + 1
            hourselect = hourselect + "</select>\n"

            #minute
            minuteselect = '<select name="%s" %s >'
            iter=0
            while iter < 60:
                if (curtime[4] - (curtime[4] % 5)) == iter:
                    minuteselect = minuteselect + '<option selected value="'+str(iter)+'">'+str(iter)+"\n"
                else:
                    minuteselect = minuteselect + '<option value="'+str(iter)+'">'+str(iter)+"\n"
                iter = iter + 5
            minuteselect = minuteselect + "</select>\n"

            startcell = monthselect % ("startmonth", 'onChange="document.manrec.stopmonth.selectedIndex=document.manrec.startmonth.selectedIndex"')
            startcell = startcell + dayselect % ("startday", 'onChange="document.manrec.stopday.selectedIndex=document.manrec.startday.selectedIndex"')
            startcell = startcell + '@'
            startcell = startcell + hourselect % ("starthour", 'onChange="document.manrec.stophour.selectedIndex=document.manrec.starthour.selectedIndex"')
            startcell = startcell + ':' 
            startcell = startcell + minuteselect % ("startminute", 'onChange="document.manrec.stopminute.selectedIndex=document.manrec.startminute.selectedIndex"')

            stopcell = monthselect % ("stopmonth", " ")
            stopcell = stopcell + dayselect % ("stopday", " ")
            stopcell = stopcell + '@' 
            stopcell = stopcell + hourselect % ("stophour", " ")
            stopcell = stopcell + ':' 
            stopcell = stopcell + minuteselect % ("stopminute", " ")

            fv.printHeader('Manual Record', 'styles/main.css')

            if errormsg:
                fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell('Error Message', 'class="guidehead" align="center" colspan="1"')
                fv.tableRowClose()
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(errormsg, 'class="basic" align="center" colspan="1"')
                fv.tableRowClose()
                fv.tableClose()

            fv.res += '<form name="manrec" action="manualrecord.rpy" method="GET">'
            fv.res += '<center>'
            fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Start Time', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Stop Time', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Title', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Program Description', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()

            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(channelselect, 'class="basic" align="left" colspan="1"')
            fv.tableCell(startcell, 'class="basic" align="left" colspan="1" nowrap')
            fv.tableCell(stopcell, 'class="basic" align="left" colspan="1" nowrap')
            fv.tableCell('<input name="title" size="20">', 'class="basic" align="left" colspan="1"')
            fv.tableCell('<textarea name="desc" rows="1" cols="20" wrap="soft"></textarea>', 'class="basic" align="left" colspan="1"')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<center><input type="hidden" name="action" value="add" /><input type="submit" value="Add to Recording Schedule" /></center>', 'class="basic" align="center" colspan="5"')
            fv.tableRowClose()

            fv.tableClose()
            fv.res += '</center>'
            fv.res += '</form>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

        return fv.res
    
resource = ManualRecordResource()


