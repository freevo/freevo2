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
# Revision 1.16  2004/05/20 15:45:07  outlyer
# Fixes for favorites containing the '&' symbol... covert it from the HTML
# "%26" into "&"
#
# Revision 1.15  2004/03/13 18:32:29  rshortt
# Make sure the dow key is a str.
#
# Revision 1.14  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.13  2004/02/22 23:29:31  gsbarbieri
# Better unicode support, still no non-ascii in names in Favorite() due
# marmelade problems.
#
# Revision 1.12  2004/02/22 07:12:17  gsbarbieri
# Add more i18n and fix bugs introduced by last i18n changes.
#
# Revision 1.11  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.10  2004/02/09 21:23:42  outlyer
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
# Revision 1.9  2004/01/23 00:57:55  outlyer
# Can't edit favourites with '&' in the name unless you use the proper 'query'
# string, in this case %26
#
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

import sys, time, string
import urllib

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
            fv.printHeader(_('Favorites'), 'styles/main.css', selected=_('Favorites'))
            fv.printMessagesFinish(
                [ '<b>'+_('ERROR')+'</b>: '+_('Recording server is unavailable.') ]
                )

            return String( fv.res )

        action = fv.formValue(form, 'action')
        oldname = fv.formValue(form, 'oldname')
        name = fv.formValue(form, 'name')
        name = string.replace(name,'%26','&')
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
            '0' : _('Monday'),
            '1' : _('Tuesday'),
            '2' : _('Wednesday'),
            '3' : _('Thursday'),
            '4' : _('Friday'),
            '5' : _('Saturday'),
            '6' : _('Sunday')
        }

        fv.printHeader(_('Favorites'), 'styles/main.css',selected=_('Favorites'))
        fv.res +='&nbsp;'
        fv.tableOpen('')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell(_('Favorite Name'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Program'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Channel'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Day of week'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Time of day'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Actions'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Priority'), 'class="guidehead" colspan="1"')
        fv.tableRowClose()

        f = lambda a, b: cmp(a.priority, b.priority)
        favs = favorites.values()
        favs.sort(f)
        for fav in favs:
            status = 'favorite'
            if fav.channel == 'ANY':
                fchan = _('ANY')
            else:
                fchan = fav.channel
                
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(Unicode(fav.name), 'class="'+status+'" colspan="1"')
            fv.tableCell(Unicode(fav.title), 'class="'+status+'" colspan="1"')
            fv.tableCell(fchan, 'class="'+status+'" colspan="1"')

            if fav.dow != 'ANY':
                cell = '%s' % days[str(fav.dow)]
            else:
                cell = _('ANY')
            fv.tableCell(cell, 'class="'+status+'" colspan="1"')

            if fav.mod != 'ANY':
                cell = '%s' % tv_util.minToTOD(fav.mod)
            else:
                cell = _('ANY')
            fv.tableCell(cell, 'class="'+status+'" colspan="1"')

            fname_esc = urllib.quote(String(fav.name.replace('&','%26')))
            # cell = '<input type="hidden" name="action" value="%s">' % action
            cell = ('<a href="edit_favorite.rpy?action=edit&name=%s">'+_('Edit')+'</a>, ') % fname_esc
            cell += ('<a href="favorites.rpy?action=remove&name=%s">'+_('Remove')+'</a>') % fname_esc
            fv.tableCell(cell, 'class="'+status+'" colspan="1"')

            cell = ''

            if favs.index(fav) != 0:
                tmp_prio = int(fav.priority) - 1
                cell += ('<a href="favorites.rpy?action=bump&name=%s&priority=-1">'+_('Higher')+'</a>') % fname_esc

            if favs.index(fav) != 0 and favs.index(fav) != len(favs)-1:
                cell += ' | '

            if favs.index(fav) != len(favs)-1:
                tmp_prio = int(fav.priority) + 1
                cell += ('<a href="favorites.rpy?action=bump&name=%s&priority=1">'+_('Lower')+'</a>') % fname_esc

            fv.tableCell(cell, 'class="'+status+'" colspan="1"')
        
            fv.tableRowClose()

        fv.tableClose()

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return String( fv.res )
    
resource = FavoritesResource()

