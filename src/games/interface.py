# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and games
# -----------------------------------------------------------------------------
# $Id$
#
# This creates the MainMenuEntry and loads all the sub plugins for the game
# entry.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Mathias Weber <mweb@gmx.ch>
# Maintainer:    Mathias Weber <mweb@gmx.ch>
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

import logging

# freevo imports
from freevo.ui.mainmenu import MainMenuItem, MainMenuPlugin
from freevo.ui.menu import Menu

log = logging.getLogger('games')

class PluginInterface(MainMenuPlugin):
    """
    Create the GamesMenu Item.
    """

    def items(self, parent):
        for p in MainMenuPlugin.plugins('games'):
            if p.items(self):
                # at least one games plugin is working
                return [ GamesMenu(parent) ]
        # no games plugin returns items
        return []


class GamesMenu(MainMenuItem):
    """
    The Games main menu.
    """
    skin_type = 'games'

    def select(self):
        items = []
        for p in MainMenuPlugin.plugins('games'):
            items += p.items(self)
        m = Menu(_('Games Main Menu'), items, type = 'games main menu')
        self.get_menustack().pushmenu(m)
