#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# edit_favorites.rpy - Web interface to edit your favorites.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/05/22 21:33:23  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
# Revision 1.5  2003/05/14 01:11:19  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.4  2003/05/13 01:20:23  rshortt
# Bugfixes.
#
# Revision 1.3  2003/05/12 23:27:54  rshortt
# Use record_types now.
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

from record_types import Favorite
import epg_xmltv
import record_client as ri

from web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0


class EditFavoriteResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader('Edit Favorite', 'styles/main.css')
            
	    fv.res += '<h4>ERROR: recording server is unavailable</h4>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

            return fv.res

        chan = fv.formValue(form, 'chan')
        start = fv.formValue(form, 'start')
        action = fv.formValue(form, 'action')
        name = fv.formValue(form, 'name')

        (result, favs) = ri.getFavorites()
        num_favorites = len(favs)

        if action == 'add' and chan and start:
            (result, prog) = ri.findProg(chan, start)

            if prog:
                print 'PROG: %s' % prog

            priority = num_favorites + 1

            fav = Favorite(prog.title, prog, TRUE, TRUE, TRUE, priority)
        elif action == 'edit' and name:
            (result, fav) = ri.getFavorite(name)
        else:
            pass


        guide = epg_xmltv.get_guide()

        fv.printHeader('Edit Favorite', 'styles/main.css')

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<img src="images/logo_200x100.png" />', 'align="left"')
        fv.tableCell('Edit Favorite', 'class="heading" align="left"')
        fv.tableRowClose()
        fv.tableClose()

        fv.res += '<br><form name="editfavorite" method="GET" action="favorites.rpy">'

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Name of favorite', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Program', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Day of week', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Time of day', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Action', 'class="guidehead" align="center" colspan="1"')
        fv.tableRowClose()

        status = 'basic'

        fv.tableRowOpen('class="chanrow"')

        cell = '<input type="hidden" name="oldname" value="%s">' % fav.name
        cell += '<input type="text" size="20" name="name" value="%s">' % fav.name
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        cell = '<input type="hidden" name="title" value="%s">%s' % (fav.title, fav.title)
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        cell = '\n<select name="chan" selected="%s">\n' % fav.channel_id
        cell += '  <option value=ANY>ANY CHANNEL</option>\n'

        i=1
        for ch in guide.chan_list:
            if ch.id == fav.channel_id:
                chan_index = i
            cell += '  <option value="%s">%s</option>\n' % (ch.id, ch.id)
            i = i +1

        cell += '</select>\n'
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        cell = '\n<select name="dow">\n' 
        cell += """
          <option value="ANY">ANY DAY</option>
          <option value="0">Mon</option>
          <option value="1">Tues</option>
          <option value="2">Wed</option>
          <option value="3">Thurs</option>
          <option value="4">Fri</option>
          <option value="5">Sat</option>
          <option value="6">Sun</option>
        </select>
        """
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        cell = '\n<select name="mod" selected="%s">\n' % fav.mod
        cell += """
          <option value="ANY">ANY TIME</option>
          <option value="0">12:00 AM</option>
          <option value="30">12:30 AM</option>
          <option value="60">1:00 AM</option>
          <option value="90">1:30 AM</option>
          <option value="120">2:00 AM</option>
          <option value="150">2:30 AM</option>
          <option value="180">3:00 AM</option>
          <option value="210">3:30 AM</option>
          <option value="240">4:00 AM</option>
          <option value="270">4:30 AM</option>
          <option value="300">5:00 AM</option>
          <option value="330">5:30 AM</option>
          <option value="360">6:00 AM</option>
          <option value="390">6:30 AM</option>
          <option value="420">7:00 AM</option>
          <option value="450">7:30 AM</option>
          <option value="480">8:00 AM</option>
          <option value="510">8:30 AM</option>
          <option value="540">9:00 AM</option>
          <option value="570">9:30 AM</option>
          <option value="600">10:00 AM</option>
          <option value="630">10:30 AM</option>
          <option value="660">11:00 AM</option>
          <option value="690">11:30 AM</option>
          <option value="720">12:00 PM</option>
          <option value="750">12:30 PM</option>
          <option value="780">1:00 PM</option>
          <option value="810">1:30 PM</option>
          <option value="840">2:00 PM</option>
          <option value="870">2:30 PM</option>
          <option value="900">3:00 PM</option>
          <option value="930">3:30 PM</option>
          <option value="960">4:00 PM</option>
          <option value="990">4:30 PM</option>
          <option value="1020">5:00 PM</option>
          <option value="1050">5:30 PM</option>
          <option value="1080">6:00 PM</option>
          <option value="1110">6:30 PM</option>
          <option value="1140">7:00 PM</option>
          <option value="1170">7:30 PM</option>
          <option value="1200">8:00 PM</option>
          <option value="1230">8:30 PM</option>
          <option value="1260">9:00 PM</option>
          <option value="1290">9:30 PM</option>
          <option value="1320">10:00 PM</option>
          <option value="1350">10:30 PM</option>
          <option value="1380">11:00 PM</option>
          <option value="1410">11:30 PM</option>
        </select>
        """
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        # cell = '\n<select name="priority" selected="%s">\n' % fav.priority
        # for i in range(num_favorites+1):
        #     cell += '  <option value="%s">%s</option>\n' % (i+1, i+1)
        # cell += '</select>\n'
        # fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        cell = '<input type="hidden" name="priority" value="%s">' % fav.priority
        cell += '<input type="hidden" name="action" value="%s">' % action
        cell += '<input type="submit" value="Save">' 
        fv.tableCell(cell, 'class="'+status+'" align="center" colspan="1"')

        fv.tableRowClose()

        fv.tableClose()

        fv.res += '</form>'

        fv.res += '<script language="JavaScript">'

        if fav.channel_id == 'ANY':
            fv.res += 'document.editfavorite.chan.options[0].selected=true'
        else:
            fv.res += 'document.editfavorite.chan.options[%s].selected=true' % chan_index

        if fav.dow == 'ANY':
            fv.res += 'document.editfavorite.dow.options[0].selected=true'
        else:
            fv.res += 'document.editfavorite.dow.options[(1+%s)].selected=true' % fav.dow

        if fav.mod == 'ANY':
            fv.res += 'document.editfavorite.mod.options[0].selected=true'
        else:
            mod_index = int(fav.mod)/30 + 1
            fv.res += 'document.editfavorite.mod.options[%s].selected=true' % mod_index

        fv.res += '</script>'

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return fv.res
    
resource = EditFavoriteResource()

