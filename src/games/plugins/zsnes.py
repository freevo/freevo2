# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# zsnes.py - the plugin for the ZSnes player
# -----------------------------------------------------------------------------
# $Id$
#
# This is a plugin for the zsnes player. It uses the generic emulator player.
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

# freevo imports
from freevo.ui.config import config

# games imports
from freevo.ui.games.emulator import *

# get config object
config = config.games.plugin.zsnes

class PluginInterface(EmulatorPlugin):
    """
    Add the zsnes items to the games menu
    """

    def items(self, parent):
        """
        Return the main menu item.
        """
        if not config.path:
            # no items defined
            return []
        return [ EmulatorMenuItem(parent, config.name, config.path,
                                  self.roms, config) ]
