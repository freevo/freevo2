#if 0 /*
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2003/11/23 17:01:34  dischi
# remove fxd stuff, it's handled by directory.py and FXDHandler now
#
# Revision 1.11  2003/10/04 09:31:39  dischi
# copy loop first
#
# Revision 1.10  2003/10/03 17:49:23  dischi
# add support for directory with one movie
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
import xml_parser
import os
import copy

from videoitem import VideoItem


# handler for parse video informations from a fxd file
FXDHandler = xml_parser.MovieParser

def cwd(parent, files):
    """
    return a list of items based on the files
    """
    items = []

    for file in util.find_matches(files, config.SUFFIX_VIDEO_FILES):
        x = VideoItem(file, parent)
        if parent.media:
            file_id = parent.media.id + file[len(os.path.join(parent.media.mountdir,"")):]
            try:
                x.mplayer_options = config.DISC_SET_INFORMATIONS_ID[file_id]
            except KeyError:
                pass
        items += [ x ]
        files.remove(file)

    return items



def update(parent, new_files, del_files, new_items, del_items, current_items):
    """
    update a directory. Add items to del_items if they had to be removed based on
    del_files or add them to new_items based on new_files
    """
    for item in current_items:

        # remove 'normal' files
        for file in util.find_matches(del_files, config.SUFFIX_VIDEO_FILES):
            if item.type == 'video' and item.filename == file and not \
               item in del_items:
                del_items += [ item ]
                del_files.remove(file)

    # add new 'normal' files
    for file in util.find_matches(new_files, config.SUFFIX_VIDEO_FILES):
        new_items += [ VideoItem(file, parent) ]
        new_files.remove(file)
