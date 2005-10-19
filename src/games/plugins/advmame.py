# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# advmame.py - the Freevo advance mame support
# -----------------------------------------------------------------------------
#
# Add support for the advance mame emulator
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dan Casimiro <dan.casimiro@gmail.com>
# Maintainer:    Dan Casimiro <dan.casimiro@gmail.com>
#
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
# -----------------------------------------------------------------------------
import plugin
from emulator import Emulator

class PluginInterface(plugin.Plugin):
    """
    zsnes plugin for gaming.  This plugin allows you to use the zsnes
    super nintendo emulator from within freevo.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        plugin.register(AdvanceMame(), plugin.GAMES, True)

class AdvanceMame(Emulator):
    """
    Use this interface to control zsnes.
    """
    def __init__(self):
        Emulator.__init__(self, 'advmame', 'MAME')

    def title(self):
        import logging
        log = logging.getLogger('games')
        log.debug('AdvanceMAME is launching the %s rom' % \
                  (self.item.filename))

        try:
            # TODO: test this on python 2.4
            game_name = self.item.filename.rsplit('/', 1).split('.', 1)
        except AttributeError:
            # the string method rsplit is new in python 2.4
            # this code is to support python 2.3
            index = self.item.filename.rindex('/') + 1
            game_name = self.item.filename[index:].split('.', 1)[0]
            
        log.debug('AdvanceMAME game name is %s' % game_name)
        return game_name
