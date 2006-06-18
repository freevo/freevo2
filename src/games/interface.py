# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - the Freevo interface to the games section
# -----------------------------------------------------------------------------
#
# Populates the games section with the available roms
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
import plugin
import config
import machine
from gameitem import GameItem

import logging
log = logging.getLogger('games')


class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of game items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'games' ]
        self.index = 0

        # activate the mediamenu for video
        plugin.activate('mediamenu', level=plugin.is_active('games')[2],
                        args='games')


    def suffix(self):
        """
        the suffixes are specified in the config file.
        """

        if config.GAMES_ITEMS[self.index][0] is 'USER':
          suf = config.GAMES_ITEMS[self.index][5]
        else:
          suf = machine.ext(config.GAMES_ITEMS[self.index][0])

        log.debug('The supported suffixes are %s' % suf)
        return suf


    def get(self, parent, listing):
        items = []

        log.info('PARENT %s' % parent)

        try:
            file = listing.visible[0]
        except:
            log.warning("Empty directory")
            return items

        log.info('Adding %s to menu' % file.dirname)

        systemmarker = imgpath = None
        dirname = file.dirname
        self.index, done = 0, 0

        for item in config.GAMES_ITEMS:
            for dir in item[2]:
                if dir in dirname:
                    systemmarker = item[0]
                    imgpath = item[4]
                    done = 1
                    break
            if done:
                break
            self.index = self.index + 1

        all_files = listing.match_suffix(self.suffix())
        all_files.sort(lambda l, o: cmp(l.basename.upper(),
                                        o.basename.upper()))

        for file in all_files:
            # TODO: Build snapshots of roms.
            items.append(GameItem(parent, file, self.index, imgpath))
            
        return items
