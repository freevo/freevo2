#if 0 /*
# -----------------------------------------------------------------------
# scheduled_recordings.py - A plugin to view your list of scheduled 
#                           recordings.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/02/23 08:22:10  gsbarbieri
# i18n: help translators job.
#
# Revision 1.1  2004/02/23 03:48:14  rshortt
# A plugin to view a list of scheduled recordings instead of hardcoding it
# into tvmenu.py.  This uses ProgramItem and blurr2 will present an info area
# with details of the program in question.
#
# plugin.activate('tv.scheduled_recordings')
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import os
import config, plugin, menu, rc
import tv.record_client as record_client

from item import Item
from tv.program_display import ProgramItem


class ScheduledRecordingsItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='tv')
        self.name = _('Scheduled Recordings')


    def actions(self):
        return [ ( self.display_schedule , _('Display Scheduled Recordings') ) ]


    def display_schedule(self, arg=None, menuw=None):
        items = []

        (server_available, msg) = record_client.connectionTest()
        if not server_available:
            AlertBox(_('Recording server is unavailable.')+(': %s' % msg),
                     self, Align.CENTER).show()
            return

        (result, recordings) = record_client.getScheduledRecordings()
        if result:
            progs = recordings.getProgramList()

            f = lambda a, b: cmp(a.start, b.start)
            progs = progs.values()
            progs.sort(f)
            for prog in progs:
                items.append(ProgramItem(self, prog, context='schedule'))
        else:
            AlertBox(_('Get recordings failed')+(': %s' % recordings),
                     self, Align.CENTER).show()
            return

        schedule_menu = menu.Menu(_( 'Scheduled Recordings'), items,
                                  item_types = 'tv program menu')
        rc.app(None)
        menuw.pushmenu(schedule_menu)
        menuw.refresh()


class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin is used to display your currently scheduled recordings.

    plugin.activate('tv.scheduled_recordings')

    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
            return [ ScheduledRecordingsItem(parent) ]



