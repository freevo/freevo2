# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# details.py - Plugin for displaying movie details
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#        You can also bind it to a key (in this case key 2):
#        EVENTS['menu']['2'] = Event(MENU_CALL_ITEM_ACTION, arg='show_details')
#
# Todo:  
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.2  2004/07/08 12:35:43  dischi
# add warning that this plugin may not work
#
# Revision 1.1  2004/03/14 19:46:22  dischi
# Plugin to replace the item menu for video
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


import os

import menu
import config
import plugin
import skin
import item


class PluginInterface(plugin.ItemPlugin):        
    """
    This plugin shows more details for a movie item.

    It replaces the item menu with a menu showing informations about the file.
    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)
        skin.register('video_details', ('screen', 'title', 'view',
                                        'listing', 'info', 'plugin'))
        print
        print 'Activated plugin video.details'
        print 'This plugin may cause some problems because it changes the'
        print 'item menu and not all parts of Freevo may like this. If'
        print 'Freevo crashes inside the item menu, please remove this plugin.'
        print


    def actions(self, item):
        self.item = item
        if item.type == 'video':
            return [ ( self.info_showdata, _('Show details for this item'),
                       'MENU_SUBMENU') ]
        return []


    def info_showdata(self, arg=None, menuw=None):
        """
        show info for this item
        """
        actions = self.item.actions()
        plugins = plugin.get('item') + plugin.get('item_video')

        plugins.sort(lambda l, o: cmp(l._level, o._level))
            
        for p in plugins:
            if p != self:
                for a in p.actions(self.item):
                    if isinstance(a, menu.MenuItem):
                        actions.append(a)
                    else:
                        actions.append(a[:2])

        items = []
        for a in actions:
            if not isinstance(a, item.Item):
                a = menu.MenuItem(a[1], a[0])
            a.subtitle = self.item.name
            a.title    = self.item.name
            items.append(a)

        m = menu.Menu(_('Details'), items)
        m.infoitem   = self.item
        m.viewitem   = self.item
        m.item_types = 'video details'
        m.is_submenu = True
        menuw.pushmenu(m)
