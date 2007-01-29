# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# emu.py - the Freevo emulator base class
# -----------------------------------------------------------------------------
#
# This is a generic emulator class that all of the supported emulators extend. 
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dan Casimiro <dan.casimiro@gmail.com>
# Maintainer:    Dan Casimiro <dan.casimiro@gmail.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
from freevo.ui import plugin
import logging
import config

from application import ChildApp
from freevo.ui.event import *

log = logging.getLogger('games')


class Emu(ChildApp):
    """
    Code used by all supported emulators

    This is a generic emulator class that all of the supported emulators
    extend.  It is a nice place to store all the similar code.
    """
    def __init__(self, cmdline):
        ChildApp.__init__(self, cmdline, 'games', True, has_display=True)
        self.__rom = None
        self.__cmd = cmdline

    def __get_rom(self):
        return self.__rom

    def launch(self, rom):
        self.__rom = rom

        if plugin.is_active('input.joystick'):
            plugin.getbyname('JOYSTICK').activate(False)

        log.warn(self.__cmd + ' ' + self.title())

        self.child_start(self.__cmd + ' "' + self.title() + '"')

    def eventhandler(self, event):
        log.debug('The emulator eventhandler got an event: %s' % event)
        if event == STOP:
            self.stop()
            if plugin.is_active('input.joystick'):
                plugin.getbyname('JOYSTICK').activate(True)

            return True

        return ChildApp.eventhandler(self, event)

    def title(self):
        return self.item.filename

    item = property(__get_rom, None)
 

class UserEmu(Emu):
    def __init__(self, gameitem):
        cmdline = config.GAMES_ITEMS[gameitem.gi_ind][3][0][1] + ' ' +\
                  config.GAMES_ITEMS[gameitem.gi_ind][3][0][2]

        Emu.__init__(self, cmdline)
