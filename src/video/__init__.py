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
# Revision 1.4  2003/04/28 17:57:11  dischi
# exception handling for bad fxd files
#
# Revision 1.3  2003/04/26 16:38:57  dischi
# added patch from Matthieu Weber for mplayer options in disc
#
# Revision 1.2  2003/04/21 18:17:49  dischi
# Moved the code from interface.py for video/audio/image/games to __init__.py
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
import xml_parser
import os

from videoitem import VideoItem


def cwd(parent, files):
    """
    return a list of items based on the files
    """
    items = []

    for file in util.find_matches(files, config.SUFFIX_VIDEO_DEF_FILES):
        x = xml_parser.save_parseMovieFile(file, parent, files)
        if x:
            files.remove(file)
            items += x

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

        # remove xml files
        for file in util.find_matches(del_files, config.SUFFIX_VIDEO_DEF_FILES):
            if item.type == 'video' and item.xml_file == file:
                
                del_items += [ item ]
                del_files.remove(file)

                # if a xml file is removed, the covered files should appear
                for subitem in item.subitems:
                    if os.path.isfile(subitem.filename) and not \
                       subitem.filename in new_files:
                        new_files += [ subitem.filename ]

                if os.path.isfile(item.filename) and not \
                   item.filename in new_files:
                    new_files += [ item.filename ]
                
            
        # remove 'normal' files
        for file in util.find_matches(del_files, config.SUFFIX_VIDEO_FILES):
            if item.type == 'video' and item.filename == file and not \
               item in del_items:
                del_items += [ item ]
                del_files.remove(file)



    # add new xml files
    for file in util.find_matches(new_files, config.SUFFIX_VIDEO_DEF_FILES):
        x = xml_parser.save_parseMovieFile(file, parent, new_files)
        if x:
            new_files.remove(file)
            new_items += x

            # if a new xml file appears, remove items covered by this xml file
            # from the list
            for i in current_items:
                for item in x:
                    for subitem in item.subitems:
                        if i.filename == subitem.filename:
                            del_items += [ i ]
                    if i.filename == item.filename:
                        del_items += [ i ]
                    

    # add new 'normal' files
    for file in util.find_matches(new_files, config.SUFFIX_VIDEO_FILES):
        new_items += [ VideoItem(file, parent) ]
        new_files.remove(file)
