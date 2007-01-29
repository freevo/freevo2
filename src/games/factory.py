# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# factory.py - the Freevo game factory
# -----------------------------------------------------------------------------
#
# Returns the correct game player based on the game item.
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
from singleton import Singleton
from freevo.ui import plugin

class Factory(Singleton):
    def init(self):
        import logging
        self.__log = logging.getLogger('games')
        self.__log.debug('Initiated the games factory')
        # get a list of available emulators
        self.__players = plugin.getbyname(plugin.GAMES, True)

    def player(self, gameitem):
        import logging
        log = logging.getLogger('games')
        log.debug('Loading an emulator of type %s' % gameitem.system)

        for player in self.__players:
            if gameitem.system == player.systemtype:
                return player

        return None
