#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# favorites.rpy - Web interface to display your favorite programs.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/10/20 02:24:16  rshortt
# more tv_util fixes
#
# Revision 1.7  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.6  2003/07/06 20:04:26  rshortt
# Change favorites to use tv_util.get_chan_displayname(prog) as
# favorite.channel rather than channel_id.
#
# Revision 1.5  2003/05/22 21:33:23  outlyer
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

import tv.record_client as ri
import util.tv_util as tv_util

from www.web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0


class FavoritesResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader('Favorites', 'styles/main.css')
            fv.res += '<h4>ERROR: recording server is unavailable</h4>'
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

            return fv.res

        action = fv.formValue(form, 'action')
        oldname = fv.formValue(form, 'oldname')
        name = fv.formValue(form, 'name')
        title = fv.formValue(form, 'title')
        chan = fv.formValue(form, 'chan')
        dow = fv.formValue(form, 'dow')
        mod = fv.formValue(form, 'mod')
        priority = fv.formValue(form, 'priority')


        if action == 'remove':
            ri.removeFavorite(name)
        elif action == 'add':
            ri.addEditedFavorite(name, title, chan, dow, mod, priority)
        elif action == 'edit':
            ri.removeFavorite(oldname)
            ri.addEditedFavorite(name, title, chan, dow, mod, priority)
        elif action == 'bump':
            ri.adjustPriority(name, priority)
        else:
            pass

        (status, favorites) = ri.getFavorites()


        days = {
            '0' : 'Monday',
            '1' : 'Tuesday',
            '2' : 'Wednesday',
            '3' : 'Thursday',
            '4' : 'Friday',
            '5' : 'Saturday',
            '6' : 'Sunday'
        }

        fv.printHeader('Favorites', 'styles/main.css')

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Favorite Name', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Program', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Day of week', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Time of day', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Priority', 'class="guidehead" align="center" colspan="1"')
        fv.tableRowClose()

        f = lambda a, b: cmp(a.priority, b.priority)
        favs = favorites.values()
        favs.sort(f)
        for fav in favs:
            status = 'favorite'

            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(fav.name, 'class="'+status+'" align="left" colspan="1"')
            fv.tableCell(fav.title, 'class="'+status+'" align="left" colspan="1"')
            fv.tableCell(fav.channel, 'class="'+status+'" align="left" colspan="1"')

            if fav.dow != 'ANY':
                # cell = time.strftime('%b %d %H:%M', time.localtime(fav.start))
                cell = '%s' % days[fav.dow]
            else:
                cell = 'ANY'
            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

            if fav.mod != 'ANY':
                # cell = time.strftime('%b %d %H:%M', time.localtime(fav.start))
                cell = '%s' % tv_util.minToTOD(fav.mod)
            else:
                cell = 'ANY'
            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

            # cell = '<input type="hidden" name="action" value="%s">' % action
            cell = '<a href="edit_favorite.rpy?action=edit&name=%s">Edit</a>, ' % fav.name
            cell += '<a href="favorites.rpy?action=remove&name=%s">Remove</a>' % fav.name
            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

            cell = ''

            if favs.index(fav) != 0:
                tmp_prio = int(fav.priority) - 1
                cell += '<a href="favorites.rpy?action=bump&name=%s&priority=-1">Higher</a>' % fav.name

            if favs.index(fav) != 0 and favs.index(fav) != len(favs)-1:
                cell += ' | '

            if favs.index(fav) != len(favs)-1:
                tmp_prio = int(fav.priority) + 1
                cell += '<a href="favorites.rpy?action=bump&name=%s&priority=1">Lower</a>' % fav.name

            fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')
        
            fv.tableRowClose()

        fv.tableClose()

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return fv.res
    
resource = FavoritesResource()

