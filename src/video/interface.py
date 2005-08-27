# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and video
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the video module of
# Freevo. It is loaded by __init__.py and will activate the mediamenu
# for video.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'PluginInterface' ]

# python imports
import os
import copy
import string

# kaa imports
import kaa.thumb

# freevo imports
import config
import util
import plugin
import fxditem
from menu import Files

# video imports
from videoitem import VideoItem
import database
import fxdhandler

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
        fxditem.add_parser(['video'], 'movie', fxdhandler.parse_movie)
        fxditem.add_parser(['video'], 'disc-set', fxdhandler.parse_disc_set)

        # update the database based on the current mimetypes
        database.update()
        # activate the mediamenu for video
        level = plugin.is_active('video')[2]
        plugin.activate('mediamenu', level=level, args='video')
        

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.VIDEO_SUFFIX


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []

        all_files = listing.match_suffix(config.VIDEO_SUFFIX)
        # sort all files to make sure 1 is before 2 for auto-join
        all_files.sort(lambda l, o: cmp(l.basename.upper(),
                                        o.basename.upper()))

        hidden_files = []

        for file in all_files:
            if parent and parent.type == 'dir' and \
                   hasattr(parent,'VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS') and \
                   parent.VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS:
                kaa.thumb.videothumb(file.filename, update=False)

#             if file in hidden_files:
#                 files.remove(file)
#                 continue
            
            x = VideoItem(file, parent)

            # join video files
#             if config.VIDEO_AUTOJOIN and file.find('1') > 0:
#                 pos = 0
#                 for count in range(file.count('1')):
#                     # only count single digests
#                     if file[pos+file[pos:].find('1')-1] in string.digits or \
#                            file[pos+file[pos:].find('1')+1] in string.digits:
#                         pos += file[pos:].find('1') + 1
#                         continue
#                     add_file = []
#                     missing  = 0
#                     for i in range(2, 6):
#                         current = file[:pos]+file[pos:].replace('1', str(i), 1)
#                         if current in all_files:
#                             add_file.append(current)
#                             end = i
#                         elif not missing:
#                             # one file missing, stop searching
#                             missing = i
                        
#                     if add_file and missing > end:
#                         if len(add_file) > 3:
#                             # more than 4 files, I don't belive it
#                             break
#                         # create new name
#                         name = file[:pos] + \
#                                file[pos:].replace('1', '1-%s' % end, 1)
#                         x = VideoItem(name, parent)
#                         x.files = Files()
#                         for f in [ file ] + add_file:
#                             x.files.append(f)
#                             x.subitems.append(VideoItem(f, x))
#                             hidden_files.append(f)
#                         break
#                     else:
#                         pos += file[pos:].find('1') + 1
                        
#             if parent.media:
#                 file_id = parent.media.id + \
#                           file[len(os.path.join(parent.media.mountdir,"")):]
#                 try:
#                     x.mplayer_options = database.discset[file_id]
#                 except KeyError:
#                     pass
            items.append(x)

        for dvd in listing.match_type('DVD'):
            # DVD Image
            items.append(VideoItem(dvd, parent))
        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        if not diritem.image and config.VIDEO_SHOW_DATA_DIR:
            base = os.path.basename(diritem.dir).lower()
            name = os.path.join(config.VIDEO_SHOW_DATA_DIR, base)
            diritem.image = util.getimage(name)

        if database.tv_shows.has_key(os.path.basename(diritem.dir).lower()):
            tvinfo = database.tv_shows[os.path.basename(diritem.dir).lower()]
            diritem.info.set_variables(tvinfo[1])
            if not diritem.image:
                diritem.image = tvinfo[0]
            if not diritem.skin_fxd:
                diritem.skin_fxd = tvinfo[3]


    def dirconfig(self, diritem):
        """
        adds configure variables to the directory
        """
        return [ ('VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS',
                  _('Directory Autobuild Thumbnails '),
                  _('Build video thumbnails for all items'),
                  False) ]


    def database(self):
        return database
