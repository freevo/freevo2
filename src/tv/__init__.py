# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# tv - Freevo tv plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

# freevo core plugins
import freevo.ipc

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui.mainmenu import MainMenuItem, MainMenuPlugin
from freevo.ui.menu import Item, Menu

# connect to tvserver using freevo.ipc
mbus = freevo.ipc.Instance('freevo')
mbus.connect('freevo.ipc.tvserver')

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class Info(Item):
    def __getitem__(self, key):
        if key in ('comingup', 'running'):
            return getattr(tvserver.recordings, key)
        if key == 'recordserver':
            return tvserver.recordings.server
        return Info.__getitem__(self, key)


class TVMenu(MainMenuItem):
    """
    The TV main menu.
    """
    skin_type = 'tv'

    def select(self):
        items = []
        plugins_list = MainMenuPlugin.plugins('tv')
        for p in plugins_list:
            items += p.items(self)

        m = Menu(_('TV Main Menu'), items, type = 'tv main menu')
        m.infoitem = Info()
        self.pushmenu(m)


class PluginInterface(MainMenuPlugin):
    """
    Plugin interface to integrate the tv module into Freevo
    """
        
    def items(self, parent):
        """
        return the tv menu
        """
        return [ TVMenu(parent) ]
