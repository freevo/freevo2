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
# Revision 1.17  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.16  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.15  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.14  2003/11/25 19:13:19  dischi
# fix xml file location
#
# Revision 1.13  2003/11/24 19:24:58  dischi
# move the handler for fxd from xml_parser to fxdhandler
#
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


import os
import copy
import re

import config
import util
import plugin

from videoitem import VideoItem

# variables for the hashing function
fxd_database         = {}
discset_informations = {}
tv_show_informations = {}


class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of video items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'video' ]
        if config.AUDIO_SHOW_VIDEOFILES:
            self.display_type = [ 'video', 'audio' ]

        # load the fxd part of video
        import fxdhandler

        plugin.register_callback('fxditem', ['video'], 'movie', fxdhandler.parse_movie)
        plugin.register_callback('fxditem', ['video'], 'disc-set', fxdhandler.parse_disc_set)

        # activate the mediamenu for video
        plugin.activate('mediamenu', level=plugin.is_active('video')[2], args='video')
        

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.VIDEO_SUFFIX


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []

        for file in util.find_matches(files, config.VIDEO_SUFFIX):
            x = VideoItem(file, parent)
            if parent.media:
                file_id = parent.media.id + \
                          file[len(os.path.join(parent.media.mountdir,"")):]
                try:
                    x.mplayer_options = discset_informations[file_id]
                except KeyError:
                    pass
            items += [ x ]
            files.remove(file)

        return items



    def update(self, parent, new_files, del_files, new_items, del_items, current_items):
        """
        update a directory. Add items to del_items if they had to be removed based on
        del_files or add them to new_items based on new_files
        """
        for item in current_items:

            # remove 'normal' files
            for file in util.find_matches(del_files, config.VIDEO_SUFFIX):
                if item.type == 'video' and item.filename == file and not \
                   item in del_items:
                    del_items += [ item ]
                    del_files.remove(file)

        # add new 'normal' files
        for file in util.find_matches(new_files, config.VIDEO_SUFFIX):
            new_items += [ VideoItem(file, parent) ]
            new_files.remove(file)




def hash_fxd_movie_database():
    """
    hash fxd movie files in some directories. This is used e.g. by the
    rom drive plugin, but also for a directory and a videoitem.
    """
    import fxditem
    
    global tv_show_informations
    global discset_informations
    global fxd_database

    fxd_database['id']    = {}
    fxd_database['label'] = []
    discset_informations  = {}
    tv_show_informations  = {}
    
    if vfs.exists("/tmp/freevo-rebuild-database"):
        try:
            os.remove('/tmp/freevo-rebuild-database')
        except OSError:
            print '*********************************************************'
            print
            print '*********************************************************'
            print 'ERROR: unable to remove /tmp/freevo-rebuild-database'
            print 'please fix permissions'
            print '*********************************************************'
            print
            return 0

    _debug_("Building the xml hash database...",1)

    files = []
    if not config.VIDEO_ONLY_SCAN_DATADIR:
        for name,dir in config.VIDEO_ITEMS:
            files += util.recursefolders(dir,1,'*.fxd',1)
    if config.OVERLAY_DIR:
        for subdir in ('disc', 'disc-set'):
            files += util.recursefolders(vfs.join(config.OVERLAY_DIR, subdir), 1, '*.fxd', 1)

    for info in fxditem.mimetype.parse(None, files, display_type='video'):
        for i in info.rom_id:
            fxd_database['id'][i] = info
        for l in info.rom_label:
            fxd_database['label'].append((re.compile(l), info))
        for fo in info.files_options:
            discset_informations[fo['file-id']] = fo['mplayer-options']

    if config.VIDEO_SHOW_DATA_DIR:
        files = util.recursefolders(config.VIDEO_SHOW_DATA_DIR,1, '*.fxd',1)
        for info in fxditem.mimetype.parse(None, files, display_type='video'):
            k = vfs.splitext(vfs.basename(info.xml_file))[0]
            tv_show_informations[k] = (info.image, info.info, info.mplayer_options,
                                       info.xml_file)
            
    _debug_('done',1)
    return 1
