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
# Revision 1.18  2004/08/10 12:54:22  outlyer
# An impressive update to the guide code from Jason Tackaberry that
# dramatically speeds up rendering and navigation of the guide.  I will be
# applying this patch to future 1.5.x Debian packages, but I'm not applying
# it to 1.5 branch of CVS unless people really want it.
#
# Revision 1.17  2004/05/20 15:45:07  outlyer
# Fixes for favorites containing the '&' symbol... covert it from the HTML
# "%26" into "&"
#
# Revision 1.16  2004/04/11 06:51:17  dischi
# unicode patch
#
# Revision 1.15  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.14  2004/02/22 23:28:12  gsbarbieri
# Better unicode handling, better (i18n) messages.
# Still no unicode with non-ascii names in Favorite(), marmelade problems.
#
# Revision 1.13  2004/02/22 21:41:21  rshortt
# Check result instead.
#
# Revision 1.12  2004/02/22 21:04:58  gsbarbieri
# Fix crash when server returns error message instead of program.
#
# Revision 1.11  2004/02/22 07:10:52  gsbarbieri
# Fix bug introduced by i18n changes.
#
# Revision 1.10  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.9  2004/02/09 21:23:42  outlyer
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
# Revision 1.8  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.7  2003/07/06 20:04:26  rshortt
# Change favorites to use tv_util.get_chan_displayname(prog) as
# favorite.channel rather than channel_id.
#
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

import sys, time, string

from tv.record_types import Favorite
import tv.epg_xmltv
import tv.record_client as ri

from www.web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0


class EditFavoriteResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        (server_available, message) = ri.connectionTest()
        if not server_available:
            fv.printHeader(_('Edit Favorite'), 'styles/main.css')
            fv.printMessagesFinish(
                [ '<b>'+_('ERROR')+'</b>: '+_('Recording server is unavailable.') ]
                )
            return String( fv.res )

        chan = Unicode(fv.formValue(form, 'chan'))
        if isinstance( chan, str ):
            chan = Unicode( chan, 'latin-1' )
        
        start = fv.formValue(form, 'start')
        action = fv.formValue(form, 'action')
        name = Unicode(fv.formValue(form, 'name'))
        name = string.replace(name,'%26','&')
        if isinstance( name, str ):
            name = Unicode( name, 'latin-1' )

        (result, favs) = ri.getFavorites()
        num_favorites = len(favs)

        if action == 'add' and chan and start:
            (result, prog) = ri.findProg(chan, start)

	    if not result:
                fv.printHeader('Edit Favorite', 'styles/main.css')
                fv.printMessagesFinish(
                    [ '<b>'+_('ERROR') + '</b>: ' + \
                      ( _('No program found on %s at %s.')%\
                        ( '<b>'+chan+'</b>',
                          '<b>'+time.strftime('%x %X',
                                              time.localtime(int(start))) + \
                          '</b>'
                         )
                        ) + (' <i>(%s)</i>' % String(prog)) ] )
                return String(fv.res)

            if prog:
                print 'PROG: %s' % String(prog)

            priority = num_favorites + 1

            fav = Favorite(prog.title, prog, TRUE, TRUE, TRUE, priority)
        elif action == 'edit' and name:
            (result, fav) = ri.getFavorite(name)
        else:
            pass

        if not result:
            fv.printHeader('Edit Favorite', 'styles/main.css')
            fv.printMessagesFinish(
                [ '<b>'+_('ERROR') + '</b>: ' + \
                  ( _('Favorite %s doesn\'t exists.') % \
                    ( '<b>'+name+'</b>' )
                    )+\
                  ( ' <i>(%s)</i>' % fav )
                  ] )
            return String(fv.res)


        guide = tv.epg_xmltv.get_guide()

        fv.printHeader(_('Edit Favorite'), 'styles/main.css')
        fv.res += '&nbsp;<br/>\n'
        # This seems out of place.
        #fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        #fv.tableRowOpen('class="chanrow"')
        #fv.tableCell('<img src="images/logo_200x100.png" />', 'align="left"')
        #fv.tableCell(_('Edit Favorite'), 'class="heading" align="left"')
        #fv.tableRowClose()
        #fv.tableClose()

        fv.res += '<br><form name="editfavorite" method="get" action="favorites.rpy">'

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell(_('Name of favorite'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Program'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Channel'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Day of week'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Time of day'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Action'), 'class="guidehead" colspan="1"')
        fv.tableRowClose()

        status = 'basic'

        fv.tableRowOpen('class="chanrow"')

        cell = '<input type="hidden" name="oldname" value="%s">' % fav.name
        cell += '<input type="text" size="20" name="name" value="%s">' % fav.name
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        cell = '<input type="hidden" name="title" value="%s">%s' % (fav.title, fav.title)
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        cell = '\n<select name="chan" selected="%s">\n' % fav.channel
        cell += '  <option value=ANY>'+_('ANY CHANNEL')+'</option>\n'

        i=1
        for ch in guide.chan_list:
            if ch.displayname == fav.channel:
                chan_index = i
            cell += '  <option value="%s">%s</option>\n' % (ch.displayname, ch.displayname)
            i = i +1

        cell += '</select>\n'
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        cell = '\n<select name="dow">\n' \
               '   <option value="ANY">'+_('ANY DAY')+'</option>\n' \
               '   <option value="0">'+_('Mon')+'</option>\n' \
               '   <option value="1">'+_('Tue')+'</option>\n' \
               '   <option value="2">'+_('Wed')+'</option>\n' \
               '   <option value="3">'+_('Thu')+'</option>\n' \
               '   <option value="4">'+_('Fri')+'</option>\n' \
               '   <option value="5">'+_('Sat')+'</option>\n' \
               '   <option value="6">'+_('Sun')+'</option>\n' \
               '</select>\n'
        
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        cell = '\n<select name="mod" selected="%s">\n' % fav.mod
        cell += '          <option value="ANY">'+_('ANY TIME')+'</option>\n'
        cell += """
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
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        # cell = '\n<select name="priority" selected="%s">\n' % fav.priority
        # for i in range(num_favorites+1):
        #     cell += '  <option value="%s">%s</option>\n' % (i+1, i+1)
        # cell += '</select>\n'
        # fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        cell = '<input type="hidden" name="priority" value="%s">' % fav.priority
        cell += '<input type="hidden" name="action" value="%s">' % action
        cell += '<input type="submit" value="'+_('Save')+'">' 
        fv.tableCell(cell, 'class="'+status+'" colspan="1"')

        fv.tableRowClose()

        fv.tableClose()

        fv.res += '</form>'

        fv.res += '<script language="JavaScript">'

        if fav.channel == 'ANY':
            fv.res += 'document.editfavorite.chan.options[0].selected=true\n'
        else:
            fv.res += 'document.editfavorite.chan.options[%s].selected=true\n' % chan_index

        if fav.dow == 'ANY':
            fv.res += 'document.editfavorite.dow.options[0].selected=true\n'
        else:
            fv.res += 'document.editfavorite.dow.options[(1+%s)].selected=true\n' % fav.dow

        if fav.mod == 'ANY':
            fv.res += 'document.editfavorite.mod.options[0].selected=true\n'
        else:
            mod_index = int(fav.mod)/30 + 1
            fv.res += 'document.editfavorite.mod.options[%s].selected=true\n' % mod_index

        fv.res += '</script>'

        fv.printSearchForm()

        fv.printLinks()

        fv.printFooter()

        return String( fv.res )
    
resource = EditFavoriteResource()

