# -*- coding: iso-8859-1 -*-
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
# Revision 1.11  2005/01/08 10:27:18  dischi
# remove unneeded skin_type parameter
#
# Revision 1.10  2004/10/06 18:59:52  dischi
# remove import rc
#
# Revision 1.9  2004/07/25 19:47:40  dischi
# use application and not rc.app
#
# Revision 1.8  2004/07/22 21:21:50  dischi
# small fixes to fit the new gui code
#
# Revision 1.7  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.6  2004/03/13 20:13:02  rshortt
# Fix return.
#
# Revision 1.5  2004/03/13 18:33:17  rshortt
# Handle an empty list better (still needs improving).
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


import os
import config, plugin, menu
import tv.record_client as record_client

from gui import AlertBox
from item import Item
from tv.program_display import ProgramItem


class ScheduledRecordingsItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.name = _('Scheduled Recordings')
        self.menuw = None


    def actions(self):
        return [ ( self.display_schedule , _('Display Scheduled Recordings') ) ]


    def display_schedule(self, arg=None, menuw=None):
        items = self.get_items()
        if not len(items):
            AlertBox(_('Nothing scheduled.')).show()
            return

        schedule_menu = menu.Menu(_( 'Scheduled Recordings'), items,
                                  reload_func = self.reload,
                                  item_types = 'tv program menu')
        self.menuw = menuw
        menuw.pushmenu(schedule_menu)
        menuw.refresh()


    def reload(self):
        menuw = self.menuw

        menu = menuw.menustack[-1]

        new_choices = self.get_items()
        if not menu.selected in new_choices and len(new_choices):
            sel = menu.choices.index(menu.selected)
            if len(new_choices) <= sel:
                menu.selected = new_choices[-1]
            else:
                menu.selected = new_choices[sel]

        menu.choices = new_choices

        return menu


    def get_items(self):
        items = []

        (server_available, msg) = record_client.connectionTest()
        if not server_available:
            AlertBox(_('Recording server is unavailable.')+(': %s' % msg)).show()
            return []

        (result, recordings) = record_client.getScheduledRecordings()
        if result:
            progs = recordings.getProgramList()

            f = lambda a, b: cmp(a.start, b.start)
            progs = progs.values()
            progs.sort(f)
            for prog in progs:
                items.append(ProgramItem(self, prog, context='schedule'))
        else:
            AlertBox(_('Get recordings failed')+(': %s' % recordings)).show()
            return []

        return items


class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin is used to display your currently scheduled recordings.

    plugin.activate('tv.scheduled_recordings')

    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
            return [ ScheduledRecordingsItem(parent) ]



