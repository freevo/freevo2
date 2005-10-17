# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - the Freevo interface to the games section
# -----------------------------------------------------------------------------
#
# Populates the games section with the available roms
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
import config
from gameitem import GameItem

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of game items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'games' ]

        import logging
        self.__log = logging.getLogger('games')

        # activate the mediamenu for video
        plugin.activate('mediamenu', level=plugin.is_active('games')[2],
                        args='games')

    def suffix(self):
        """
        the suffixes are specified in the config file.
        """
        suf = []
        for item in config.GAMES_ITEMS:
            suf += item[2][4]

        self.__log.debug('The supported suffixes are %s' % suf)
        return suf

    def get(self, parent, listing):
        items = []

        self.__log.info('Adding %s to menu' % listing)

        systemmarker = None
        dirname = listing.dirname[:-1]
        for item in config.GAMES_ITEMS:
            if item[1] == dirname:
                systemmarker = item[2][0]
                break

        all_files = listing.match_suffix(self.suffix())
        all_files.sort(lambda l, o: cmp(l.basename.upper(),
                                        o.basename.upper()))

        for file in all_files:
            # TODO: Build snapshots of roms.
            items.append(GameItem(parent, file, systemmarker))
            
        return items
