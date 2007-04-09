# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# pcgames.py - the pycgames item and player
# -----------------------------------------------------------------------------
# $Id$
#
# The PcGamesItem represents a PC game that can be started through the
# PcGamesPlayer. Both classes are derived from the corresponding classes
# in emulator module.
# The PluginInterface class creates the list with all the games. The games
# here have to be listed in the config file since there are no roms involved.
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

# python imports
import logging

# kaa imports
import kaa.notifier

# Freevo imports
from freevo.ui.menu import ActionItem, Menu, Action
from freevo.ui.config import config
from freevo.ui.event import Event, STOP

# games imports
from freevo.ui.games.emulator import *
import freevo.ui.games.player as gameplayer

# get logging object
log = logging.getLogger('games')

# get config object
config = config.games.plugin.pcgames


class PcGamePlayer(EmulatorPlayer):
    """
    The PcGamePlayer loader.
    """

    def open(self, item):
        """
        Open a PcGameItem, get executable and parameters for playing
        """
        self.command_name = item.binary
        self.parameters = item.parameters


    def play(self):
        """
        Play PcGame
        """
        log.info('Start playing PcGame (%s %s)', self.command_name, self.parameters)
        self.child = kaa.notifier.Process(self.command_name)
        self.child.start(self.parameters).connect(self.completed)
        self.signals = self.child.signals
        stop = kaa.notifier.WeakCallback(self.stop)
        self.child.set_stop_command(stop)


    def completed(self, child):
        """
        The game was quit. Send Stop event to get back to the menu.
        """
        Event(STOP, handler=gameplayer.player.eventhandler).post()
        log.info('Game completed')


    def actions(self):
        """
        The actions for the games
        """
        return [ Action(_('Play %s') % self.name, self.play) ]


class PcGameItem(EmulatorItem):
    """
    Item for a PC game.
    """

    def __init__(self, parent, name, bin, parameters=""):
        EmulatorItem.__init__(self, parent, name)
        self.binary = bin
        self.parameters = parameters


    def play(self):
        """
        Start the game.
        """
        gameplayer.play(self, PcGamePlayer())


class PluginInterface(EmulatorPlugin):
    """
    Add PC game to games menu
    """

    def roms(self, parent):
        """
        Show all games.
        """
        items = []
        for item in config.items:
            i = PcGameItem(parent, item.name, item.bin, item.parameters)
            items.append(i)
        parent.pushmenu(Menu(_('PC Games'), items, type='games'))


    def items(self, parent):
        """
        Return the main menu item.
        """
        if not config.items:
            # no items defined
            return []
        return [ ActionItem(config.name, parent, self.roms) ]
