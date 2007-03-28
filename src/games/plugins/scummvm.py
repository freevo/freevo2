# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# scummvm.py - the scummvm player
# -----------------------------------------------------------------------------
# $Id$
#
# The scummvm player is a player for the scummvm. You need to have loaded
# the game previous with the scummvm. It will find all the configured
# games. In addition it will offer to run the scummvm without a game to
# configure a new game.
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
from subprocess import Popen, PIPE

# kaa imports
import kaa.utils

# Freevo imports
from freevo.ui.menu import ActionItem, Menu, Action
from freevo.ui.config import config

# games imports
from freevo.ui.games.emulator import EmulatorPlugin
import freevo.ui.games.player as gameplayer
from pcgames import PcGamePlayer, PcGameItem

# get logging object
log = logging.getLogger('games')

# get config object
config = config.games.plugin.scummvm

class ScummvmPlayer(PcGamePlayer):
    """
    The PcGamePlayer loader.
    """

    def open(self, item):
        """
        Open a PcGameItem, get executable and parameters for playing
        """
        self.emulator_item = item.binary


    def play(self):
        """
        Play PcGame
        """
        log.info('Start playing PcGame (Scummvm: %s)', self.emulator_item)
        parameters = '%s %s' % (config.parameters, self.emulator_item)
        self._releaseJoystick()
        self.child = kaa.notifier.Process(config.bin)
        self.child.start(parameters).connect(self.completed)
        self.signals = self.child.signals
        stop = kaa.notifier.WeakCallback(self.stop)
        self.child.set_stop_command(stop)


class ScummvmItem(PcGameItem):
    """
    A scummvm Item
    """

    def play(self):
        gameplayer.play(self, ScummvmPlayer())


class PluginInterface(EmulatorPlugin):
    """
    Add Scummvm games to the games menu
    """
    romlist = []
    finished = False

    def roms(self, parent):
        """
        Show all games.
        """
        items = []
        # get list of scummvm
        pipe = Popen([config.bin, '-t'], stdout=PIPE).stdout
        # FIXME: this blocks the notifier loop. Maybe better use
        # kaa.notifier.Process and yield_execution.
        for item in pipe.readlines()[2:]:
            name = item[:item.find(' ')]
            description = item[item.find(' '):].strip()
            items.append(ScummvmItem(parent, description, name))
        # append the scummvm it self, to configure new games
        items.append(ScummvmItem(parent, 'ScummVM', ''))
        parent.pushmenu(Menu(config.name, items, type='games'))


    def items(self, parent):
        """
        Return the main menu item.
        """
        if not config.bin or \
               (not config.bin.startswith('/') and not
                kaa.utils.which(config.bin)):
            # no binary defined or not found
            return []
        return [ ActionItem(config.name, parent, self.roms) ]
