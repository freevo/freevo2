#if 0 /*
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
# Revision 1.12  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.11  2003/11/29 11:39:38  dischi
# use the given menuw abd not a global one
#
# Revision 1.10  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.9  2003/11/16 17:41:04  dischi
# i18n patch from David Sagnol
#
# Revision 1.8  2003/09/21 13:20:03  dischi
# destroy the popup after some time
#
# Revision 1.7  2003/09/16 20:45:02  mikeruelle
# warn user about old GAMES_ITEMS entry
#
# Revision 1.6  2003/09/12 22:25:00  dischi
# prevent a possible crash
#
# Revision 1.5  2003/09/05 20:48:34  mikeruelle
# new game system
#
# Revision 1.4  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
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
#endif

import config
import util
import types
import time

import menu
import mame_cache
import plugin

from mameitem import MameItem
from snesitem import SnesItem
from genesisitem import GenesisItem
from genericitem import GenericItem
from gui.AlertBox import PopupBox


class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of audio items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'image' ]

        # activate the mediamenu for image
        plugin.activate('mediamenu', level=plugin.is_active('image')[2], args='image')
        

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
                items += [ MameItem(ml[0], ml[1], ml[2], cmd, args, imgpath, parent) ]
        elif gtype == 'SNES':
            for file in util.find_matches(files, [ 'smc', 'fig' ]):
                items += [ SnesItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)
        elif gtype == 'GENESIS':
            for file in util.find_matches(files, [ 'smd', 'bin' ]):
                items += [ GenesisItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)
        elif gtype == 'GENERIC':
            for file in util.find_matches(files, suffixlist):
                items += [ GenericItem(file, cmd, args, imgpath, parent) ]
                files.remove(file)

        return items


    def update(self, parent, new_files, del_files, new_items, del_items, current_items):
        """
        update a directory. Add items to del_items if they had to be removed based on
        del_files or add them to new_items based on new_files
        """

        (gtype, cmd, args, shots, suffixlist) = parent.add_args[0]
        if gtype == 'MAME':
            for item in current_items:
                for file in util.find_matches(del_files, [ 'zip' ] ):
                    if item.type == 'mame' and item.filename == file:
                        # In the future will add code to remove the mame rom
                        # from the cache.
                        del_items += [ item ]
                        del_files.remove(file)
        elif gtype == 'SNES':
            for file in util.find_matches(del_files, [ 'smc', 'fig' ]):
                if item.type == 'snes' and item.filename == file:
                    del_items += [ item ]
                    del_files.remove(file)
        elif gtype == 'GENESIS':
            for file in util.find_matches(del_files, suffixlist):
                if item.type == 'genesis' and item.filename == file:
                    del_items += [ item ]
                    del_files.remove(file)
        elif gtype == 'GENERIC':
            for file in util.find_matches(del_files, suffixlist):
                if item.type == 'generic' and item.filename == file:
                    del_items += [ item ]
                    del_files.remove(file)

        new_items += cwd(parent, new_files)


