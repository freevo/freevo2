# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and games
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.20  2004/07/22 21:21:48  dischi
# small fixes to fit the new gui code
#
# Revision 1.19  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.18  2004/03/13 09:23:46  dischi
# fix doc
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */


import config
import util
import types
import time

import menu
import mame_cache
import plugin

from mameitem import MameItem
from snesitem import SnesItem, snesromExtensions
from genesisitem import GenesisItem, genesisromExtensions
from genericitem import GenericItem
from gui import PopupBox


class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of games items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'games' ]

        # activate the mediamenu for image
        plugin.activate('mediamenu', level=plugin.is_active('games')[2], args='games')
        

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return []


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []

        if not hasattr(parent, 'add_args') or type(parent.add_args) is not types.TupleType: 
            pop = PopupBox(text=_('please update GAMES_ITEMS in local_conf.py'))
            pop.show()
            time.sleep(2)
            pop.destroy()
            return []

        (gtype, cmd, args, imgpath, suffixlist) = parent.add_args[0]
        if gtype == 'MAME':
            mame_files = util.find_matches(files, [ 'zip' ] )
            # This will only add real mame roms to the cache.
            (rm_files, mame_list) = mame_cache.getMameItemInfoList(mame_files, cmd)
            for rm_file in rm_files:
                files.remove(rm_file)
            for ml in mame_list:
                items += [ MameItem(ml[0], ml[1], ml[2], cmd, args, imgpath, parent, ml[3]) ]
        elif gtype == 'SNES':
            for file in util.find_matches(files, snesromExtensions + [ 'zip' ]):
                items += [ SnesItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)
        elif gtype == 'GENESIS':
            for file in util.find_matches(files, genesisromExtensions + ['zip']):
                items += [ GenesisItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)
        elif gtype == 'GENERIC':
            for file in util.find_matches(files, suffixlist):
                items += [ GenericItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)

        return items
