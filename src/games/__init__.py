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

import mame_cache
from mameitem import MameItem
from snesitem import SnesItem
from genesisitem import GenesisItem
from genericitem import GenericItem


def cwd(parent, files):
    """
    return a list of items based on the files
    """
    items = []

    (type, cmd, args, imgpath, suffixlist) = parent.add_args[0]
    if type == 'MAME':
        print 'Type : %s' % type
        mame_files = util.find_matches(files, [ 'zip' ] )
        # This will only add real mame roms to the cache.
        (rm_files, mame_list) = mame_cache.getMameItemInfoList(mame_files, cmd)
        for rm_file in rm_files:
            files.remove(rm_file)
        for ml in mame_list:
            items += [ MameItem(ml[0], ml[1], ml[2], cmd, args, imgpath, parent) ]
    elif type == 'SNES':
        for file in util.find_matches(files, [ 'smc', 'fig' ]):
            items += [ SnesItem(file, cmd, args, imgpath, parent) ]
            files.remove(file)
    elif type == 'GENESIS':
        for file in util.find_matches(files, [ 'smd', 'bin' ]):
            items += [ GenesisItem(file, cmd, args, imgpath, parent) ]
            files.remove(file)
    elif type == 'GENERIC':
        for file in util.find_matches(files, suffixlist):
            items += [ GenericItem(file, cmd, args, imgpath, parent) ]
            files.remove(file)

    return items



def update(parent, new_files, del_files, new_items, del_items, current_items):
    """
    update a directory. Add items to del_items if they had to be removed based on
    del_files or add them to new_items based on new_files
    """

    (type, cmd, args, shots, suffixlist) = parent.add_args[0]
    if type == 'MAME':
        for item in current_items:
            for file in util.find_matches(del_files, [ 'zip' ] ):
                if item.type == 'mame' and item.filename == file:
                    # In the future will add code to remove the mame rom
                    # from the cache.
                    del_items += [ item ]
                    del_files.remove(file)
    elif type == 'SNES':
        for file in util.find_matches(del_files, [ 'smc', 'fig' ]):
            if item.type == 'snes' and item.filename == file:
                del_items += [ item ]
                del_files.remove(file)
    elif type == 'GENESIS':
        for file in util.find_matches(del_files, suffixlist):
            if item.type == 'genesis' and item.filename == file:
                del_items += [ item ]
                del_files.remove(file)
    elif type == 'GENERIC':
        for file in util.find_matches(del_files, suffixlist):
            if item.type == 'generic' and item.filename == file:
                del_items += [ item ]
                del_files.remove(file)

    new_items += cwd(parent, new_files)
