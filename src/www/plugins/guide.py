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
# Revision 1.2  2005/06/26 10:53:16  dischi
# use kaa.epg instead of pyepg
#
# Revision 1.1  2005/02/13 18:42:09  dischi
# move pages into plugins and pages subdir
#
# Revision 1.5  2005/02/03 16:05:38  rshortt
# Minor cosmetics fix.
#
# Revision 1.4  2005/01/14 22:41:45  rshortt
# More fixes: variable guide start time, category box, recordserver message.
# TODO:
#   -find out from kaa.epg when our last program is scheduled to let us better
#    determine how far forward to let users skip
#   -find out from kaa.epg which program categories it has (ie: news, sports)
#
# Revision 1.3  2005/01/13 20:19:33  rshortt
# Place the authentication into www/server.py to protect mote than just
# the .py files.
#
# Revision 1.2  2005/01/06 18:49:04  dischi
# remove old tv_util
#
# Revision 1.1  2004/12/28 00:38:45  rshortt
# Reactivating web guide and scheduling recordings, this is still a major work
# in progress and there are still missing pieces.
#
# Revision 1.30  2004/08/14 01:30:21  rshortt
# Change guide access a bit.
#
# Revision 1.29  2004/08/14 01:23:30  rshortt
# Use the chanlist/epg from cache.
#
# Revision 1.28  2004/08/10 16:02:39  rshortt
# Remove comma from between tag attributes.
#
# Revision 1.27  2004/08/10 12:54:22  outlyer
# An impressive update to the guide code from Jason Tackaberry that
# dramatically speeds up rendering and navigation of the guide.  I will be
# applying this patch to future 1.5.x Debian packages, but I'm not applying
# it to 1.5 branch of CVS unless people really want it.
#
# Revision 1.26  2004/08/08 19:07:55  rshortt
# Use tv_util to cache the guide.
#
# Revision 1.25  2004/03/12 03:05:50  outlyer
# Use the episode title where available.
#
# Revision 1.24  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.23  2004/02/22 06:25:15  gsbarbieri
# Fix bugs introduced by i18n changes.
#
# Revision 1.22  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.21  2004/02/09 21:37:43  outlyer
# Removed the rounded edges I was trying for the guide; they don't work
# consistently and look very ugly in some browsers. I'll have to rethink
# them.
#
# Revision 1.20  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.19  2003/10/20 02:24:17  rshortt
# more tv_util fixes
#
# Revision 1.18  2003/09/07 18:50:56  dischi
# make description shorter if it's too long
#
# Revision 1.17  2003/09/07 01:02:13  gsbarbieri
# Fixed a bug in guide that appeared with the new PRECISION thing.
#
# Revision 1.16  2003/09/06 22:58:13  mikeruelle
# fix something i don't think sould have a gap

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
import config
import logging

from www.base import HTMLResource, FreevoResource

import util
import config 
import record.client

import kaa.epg

# get logging object
log = logging.getLogger('www')


class GuideResource(FreevoResource):

    def makecategorybox(self):
        # TODO: get the categories from kaa.epg (from the DB)
        allcategories = ['Sports', 'News']
        allcategories.sort()
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
        # Default to one week ahead, at least until we have a good way to
        # see when our listings expire.
        listh = 24*7
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
            myoff = int(hrinc - hrstart)
            retval += '<option value="' + str(myoff) + '"'
            if (abs(gstart - hrinc) < 60):
                retval += ' SELECTED '
            retval += '>' + time.strftime(config.TV_TIMEFORMAT, time.localtime(hrinc)) + '\n'
            hrinc += config.WWW_GUIDE_INTERVAL * 60
        retval += '</select>\n'
        return retval


    def render(self, request):
        fv = HTMLResource()
        log.debug(dir(request))
        form = request.query

        INTERVAL = config.WWW_GUIDE_INTERVAL * 60
        PRECISION = config.WWW_GUIDE_PRECISION * 60
        cpb = INTERVAL / PRECISION # cols per block/interval
        n_cols = config.WWW_GUIDE_COLS

        mfrguidestart = time.time()
        mfrguideinput = form.get('stime')
        mfrguideinputday = form.get('day')
        mfrguideinputoff = form.get('offset')

        if mfrguideinput:
            mfrguidestart = float(mfrguideinput)
        elif mfrguideinputday and mfrguideinputoff:
            mfrguidestart = float(mfrguideinputday) + float(mfrguideinputoff)
        elif mfrguideinputoff:
            mfrguidestart = mfrguidestart + float(mfrguideinputoff)

        now = int(mfrguidestart / INTERVAL) * INTERVAL
        now2 = int(time.time() / INTERVAL) * INTERVAL
        mfrnextguide = now + INTERVAL * n_cols
        mfrnextguide += 10
        mfrprevguide = now - INTERVAL * n_cols
        mfrprevguide += 10
        if mfrprevguide < now2:
            mfrprevguide = 0

        fv.printHeader(_('TV Guide'), config.WWW_STYLESHEET, config.WWW_JAVASCRIPT, selected=_('TV Guide'))
        fv.res += '<div id="content">\n';

        # Fool "is prog scheduled" until that is hooked up.
        got_schedule = False

        if not record.client.recordings.server:
            fv.res += '<p class="alert"><b>'+_('Notice')+'</b>: ' \
                      +_('The recording server is down.')+'</p>\n'

        desc = ''

        fv.tableOpen()
        fv.tableRowOpen('class="chanrow"')

        fv.tableCell('<form>'+_('Time')+':&nbsp;' + self.maketimejumpboxday(now) + self.maketimejumpboxoffset(now) + '<input type=submit value="'+_('View')+'"></form>', 'class="utilhead"')

        categorybox =  self.makecategorybox()
        fv.tableCell('<form action="genre">'+_('Show')+'&nbsp;'+_('Category')+':&nbsp;'+categorybox+'<input type=submit value="'+_('Change')+'"></form>', 'class="utilhead"')

        fv.tableRowClose()
        fv.tableClose()

        fv.tableOpen('id="guide" cols=\"%d\"' % \
                     ( n_cols*cpb + 1 ) )
        showheader = 0
        # for chan in get_channels().get_all():
        for chan in kaa.epg.channels:
            #chan = chan.epg
            #put guidehead every X rows
            if showheader % 15 == 0:
                fv.tableRowOpen('class="chanrow"')
                headerstart = int(mfrguidestart / INTERVAL) * INTERVAL
                fv.tableCell(time.strftime('%b %d', time.localtime(headerstart)), 'class="guidehead"')
                for i in range(n_cols):
                    if i == n_cols-1 or i == 0:
                        dacell = ''
                        datime = time.strftime(config.TV_TIMEFORMAT, time.localtime(headerstart))
                        if i == n_cols-1:
                            dacell = datime + '&nbsp;&nbsp;<a href="guide?stime=%i">&raquo;</a>' % mfrnextguide
                        else:                            
                            if mfrprevguide > 0:
                                dacell = '<a href="guide?stime=%i">&laquo;</a>&nbsp;&nbsp;' % mfrprevguide + datime
                            else:
                                dacell = datime
                        fv.tableCell(dacell, 'class="guidehead"  colspan="%d"' % cpb)
                    else:
                        fv.tableCell(time.strftime(config.TV_TIMEFORMAT, time.localtime(headerstart)),
                                     'class="guidehead" colspan="%d"' % cpb)
                    headerstart += INTERVAL
                fv.tableRowClose()
            showheader+= 1
                
            rowdata = []
            now = mfrguidestart
            # chan.displayname = string.replace(chan.displayname, "&", "SUB")
            rowdata.append(u'<tr class="chanrow">')
            rowdata.append(u'<td class="channel">%s</td>' % chan.title)
            c_left = n_cols * cpb

            progs = chan[mfrguidestart:mfrnextguide]
            if not len(progs):
                rowdata.append(u'<td class="programnodata" colspan="%s">&laquo; ' % (n_cols*cpb) + _('This channel has no data loaded') + ' &raquo;' )

            for prog in progs:
                if prog.stop > mfrguidestart and \
                   prog.start < mfrnextguide and \
                   c_left > 0:

                    status = u'program'

                    if got_schedule:
                        # (result, message) = ri.isProgScheduled(prog, schedule)
                        result = False
                        message = 'no message'
                        if result:
                            status = u'scheduled'
                            really_now = time.time()
                            if prog.start <= really_now and prog.stop >= really_now:
                                # in the future we should REALLY see if it is 
                                # recording instead of just guessing
                                status = u'recording'

                    if prog.start <= now and prog.stop >= now:
                        cell = u''
                        if prog.start <= now - INTERVAL:
                            # show started earlier than the guide start,
                            # insert left arrows
                            cell += u'&laquo; '
                        showtime_left = int(prog.stop - now + ( now % INTERVAL ) )
                        intervals = showtime_left / PRECISION
                        colspan = intervals
                        # prog.title = string.replace(prog.title, "&", "SUB")
                        # prog.desc = string.replace(prog.desc, "&", "SUB")
                        cell += u'%s' % Unicode(prog.title)
                        if colspan > c_left:                            
                            # show extends past visible range,
                            # insert right arrows
                            cell += u'   &raquo;'
                            colspan = c_left
                        popid = u'%s:%s' % (chan.id, prog.start)

                        style = u''
                        if colspan == n_cols * cpb:
                            style += u'text-align: center; '

                        rowdata.append(u'<td class="%s" onclick="guide_click(this, event)" id="%s" colspan="%s" style="%s">%s</td>' % (status, popid, colspan, style, cell))
                        now += colspan * PRECISION
                        c_left -= colspan

            rowdata.append(u"</tr>")
            fv.res += string.join(rowdata, u"\n")
        fv.tableClose()
        
        fv.printSearchForm()
        fv.printLinks()
        fv.res += '</div>'
        fv.res += (
            u"<div id=\"popup\" class=\"proginfo\" style=\"display:none\">\n"\
            u"<div id=\"program-waiting\" style=\"background-color: #0B1C52; position: absolute\">\n"\
            u"  <br /><b>Fetching program information ...</b>\n"\
            u"</div>\n"\
            u"   <table id=\"program-info\" class=\"popup\">\n"\
            u"      <thead>\n"\
            u"         <tr>\n"\
            u"            <td id=\"program-title\">\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"      </thead>\n"\
            u"      <tbody>\n"\
            u"         <tr>\n"\
            u"            <td class=\"progdesc\" id=\"program-desc\">\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"         <tr>\n"\
            u"         <td class=\"progtime\">\n"\
            u"            <b>"+_('Start')+u":</b> <span id=\"program-start\"></span>, \n"\
            u"            <b>"+_('Stop')+u":</b> <span id=\"program-end\"></span>, \n"\
            u"            <b>"+_('Runtime')+u":</b> <span id=\"program-runtime\"></span> min\n"\
            u"            </td>\n"\
            u"         </td>\n"\
            u"      </tbody>\n"\
            u"      <tfoot>\n"\
            u"         <tr>\n"\
            u"            <td>\n"\
            u"               <table class=\"popupbuttons\">\n"\
            u"                  <tbody>\n"\
            u"                     <tr>\n"\
            u"                        <td id=\"program-record-button\">\n"\
            u"                           "+_('Record')+u"\n"\
            u"                        </td>\n"\
            u"                        <td id=\"program-favorites-button\">\n"\
            u"                        "+_('Add to Favorites')+u"\n"\
            u"                        </td>\n"\
            u"                        <td onclick=\"program_popup_close();\">\n"\
            u"                        "+_('Close Window')+u"\n"\
            u"                        </td>\n"\
            u"                     </tr>\n"\
            u"                  </tbody>\n"\
            u"               </table>\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"      </tfoot>\n"\
            u"   </table>\n"\
            u"</div>\n" )
        fv.res += "<iframe id='hidden' style='visibility: hidden; width: 1px; height: 1px'></iframe>\n"
        fv.printFooter()

        return String( fv.res )


resource = GuideResource()
