# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# rec.py - webserver page for recordings
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import sys
import time
import traceback
import logging

# epg support
import kaa.epg

# freevo imports
import config

# recordserver bindings
from record.client import recordings

# webserver basics
from www.base import HTMLResource, FreevoResource

# get logging object
log = logging.getLogger('www')


class RecordResource(FreevoResource):
    """
    Ressource for rendering the 'rec' page
    """
    def render(self, request):
        """
        Render the page based on the given request.
        """
        fv     = HTMLResource()
        form   = request.query
        chan   = form.get('chan')
        start  = form.get('start')
        action = form.get('action')
        progs = []

        if not recordings.server:
            fv.printHeader('Scheduled Recordings', 'styles/main.css')
            fv.printMessagesFinish(
                [ '<b>'+_('ERROR')+'</b>: '+\
                  _('Recording server is unavailable.') ]
                )
            return String( fv.res )

        if action == 'remove':
            progs = recordings.list()

            prog = None
            for p in progs:
                if Unicode(chan) == \
                       kaa.epg.get_channel_by_id(p.channel).title \
                   and int(start) == p.start:
                    prog = p

            if prog:
                log.info('remove prog: %s' % String(prog))
                recordings.remove(prog.id)
                progs = recordings.wait_on_list()

        elif action == 'add':
            try:
                prog = kaa.epg.get_channel(chan)[int(start)]
            except:
                fv.printHeader('Scheduled Recordings', 'styles/main.css')
                fv.printMessagesFinish(
                    [ '<b>'+_('ERROR') + '</b>: ' + \
                      ( _('No program found on %s at %s.')%\
                        ( '<b>'+chan+'</b>',
                          '<b>'+\
                          time.strftime('%x %X', time.localtime(int(start)))+\
                          '</b>'
                          )
                        )+\
                      ( ' <i>(%s:%s)</i><br>%s' % (chan, start,
                                                   traceback.print_exc()) ) ] )
                return String(fv.res)
            recordings.schedule(prog)

            progs = recordings.wait_on_list()


        if not len(progs):
            progs = recordings.list()

        fv.printHeader(_('Scheduled Recordings'), 'styles/main.css',
                       selected=_('Scheduled Recordings'))

        fv.res += '&nbsp;\n'

        fv.tableOpen('')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell(_('Start Time'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Stop Time'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Channel'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Title'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Episode'),'class="guidehead" colspan="1"')
        fv.tableCell(_('Program Description'), 'class="guidehead" colspan="1"')
        fv.tableCell(_('Actions'), 'class="guidehead" colspan="1"')
        fv.tableRowClose()

        f = lambda a, b: cmp(a.start, b.start)
        progs.sort(f)
        progs = filter(lambda x: x.start >= time.time(), progs)

        for prog in progs:
            if not prog.has_key('title'):
                continue
            if not prog.status != u'deleted':
                continue

            status  = 'basic'
            colspan = 'class="' + status + '" colspan="1"'
        
            channel = kaa.epg.get_channel_by_id(prog.channel).title

            fv.tableRowOpen('class="chanrow"')
            t = time.strftime('%b %d ' + config.TV_TIMEFORMAT,
                              time.localtime(prog.start))
            fv.tableCell(t, colspan)
            t = time.strftime('%b %d ' + config.TV_TIMEFORMAT,
                              time.localtime(prog.stop))
            fv.tableCell(t, colspan)

            fv.tableCell(Unicode(channel), colspan)
            fv.tableCell(Unicode(prog['title']), colspan)
            if prog.has_key('subtitle'):
                fv.tableCell(Unicode(prog['subtitle']), colspan)
            else:
                fv.tableCell(u'', colspan)

            if prog.has_key('description'):
                cell = Unicode(prog['description'])
            else:
                cell = _('no description available')
            fv.tableCell(cell, colspan)

            cell = ('<a href="recordings?chan=%s&amp;start=%s&amp;action=remove" '+\
                    'title="Remove Scheduled Recording">'+_('Remove')+'</a>'+\
                    '|' + '<a href="search?find=%s&search_title=on" ' +\
                    'title="Search for other airings">' + _('Search') +
                    '</a>') % (channel, prog.start, Unicode(prog['title']))
            fv.tableCell(cell, colspan)
            fv.tableRowClose()

        fv.tableClose()

        fv.printSearchForm()
        fv.printFooter()

        return String( fv.res )

resource = RecordResource()
