# -*- coding: iso-8859-1 -*-
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
# Revision 1.35  2004/08/28 17:17:19  dischi
# fix bug in auto join feature
#
# Revision 1.34  2004/07/11 10:26:49  dischi
# sort items before checking because of auto-join
#
# Revision 1.33  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.32  2004/06/20 13:06:19  dischi
# move freevo-rebuild-database to cache dir
#
# Revision 1.31  2004/06/02 21:36:49  dischi
# auto detect movies with more than one file
#
# Revision 1.30  2004/03/27 00:46:23  outlyer
# Fixed a crash. It occured when I used the "Configure Directory" option to
# show "all types" in a music directory.
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


import os
import copy
import re
import string

import config
import util
import util.videothumb
import plugin

from videoitem import VideoItem, FileInformation

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

        all_files = util.find_matches(files, config.VIDEO_SUFFIX)
        # sort all files to make sure 1 is before 2 for auto-join
        all_files.sort(lambda l, o: cmp(l.upper(), o.upper()))

        hidden_files = []

        for file in all_files:
            if parent and parent.type == 'dir' and \
                   hasattr(parent,'VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS') and \
                   parent.VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS:
                util.videothumb.snapshot(file, update=False, popup=True)

            if file in hidden_files:
                files.remove(file)
                continue
            
            x = VideoItem(file, parent)

            # join video files
            if config.VIDEO_AUTOJOIN and file.find('1') > 0:
                pos = 0
                for count in range(file.count('1')):
                    # only count single digests
                    if file[pos+file[pos:].find('1')-1] in string.digits or \
                           file[pos+file[pos:].find('1')+1] in string.digits:
                        pos += file[pos:].find('1') + 1
                        continue
                    add_file = []
                    missing  = 0
                    for i in range(2, 6):
                        current = file[:pos] + file[pos:].replace('1', str(i), 1)
                        if current in all_files:
                            add_file.append(current)
                            end = i
                        elif not missing:
                            # one file missing, stop searching
                            missing = i
                        
                    if add_file and missing > end:
                        if len(add_file) > 3:
                            # more than 4 files, I don't belive it
                            break
                        # create new name
                        name = file[:pos] + file[pos:].replace('1', '1-%s' % end, 1)
                        x = VideoItem(name, parent)
                        x.files = FileInformation()
                        for f in [ file ] + add_file:
                            x.files.append(f)
                            x.subitems.append(VideoItem(f, x))
                            hidden_files.append(f)
                        break
                    else:
                        pos += file[pos:].find('1') + 1
                        
            if parent.media:
                file_id = parent.media.id + \
                          file[len(os.path.join(parent.media.mountdir,"")):]
                try:
                    x.mplayer_options = discset_informations[file_id]
                except KeyError:
                    pass
            items.append(x)
            files.remove(file)

        for i in copy.copy(files):
            if os.path.isdir(i+'/VIDEO_TS'):
                # DVD Image, trailing slash is important for Xine
                items.append(VideoItem('dvd://' + i[1:] + '/VIDEO_TS/', parent))
                files.remove(i)

        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        global tv_show_informations
        if not diritem.image and config.VIDEO_SHOW_DATA_DIR:
            diritem.image = util.getimage(vfs.join(config.VIDEO_SHOW_DATA_DIR,
                                                   vfs.basename(diritem.dir).lower()))

        if tv_show_informations.has_key(vfs.basename(diritem.dir).lower()):
            tvinfo = tv_show_informations[vfs.basename(diritem.dir).lower()]
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
                  _('Build video thumbnails for all items (may take a while when entering).'),
                  False) ]



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

    rebuild_file = os.path.join(config.FREEVO_CACHEDIR, 'freevo-rebuild-database')
    if vfs.exists(rebuild_file):
        try:
            os.remove(rebuild_file)
        except OSError:
            print '*********************************************************'
            print
            print '*********************************************************'
            print 'ERROR: unable to remove %s' % rebuild_file
            print 'please fix permissions'
            print '*********************************************************'
            print
            return 0

    _debug_("Building the xml hash database...",1)

    files = []
    if not config.VIDEO_ONLY_SCAN_DATADIR:
        for name,dir in config.VIDEO_ITEMS:
            files += util.recursefolders(dir,1,'*.fxd',1)

    for subdir in ('disc', 'disc-set'):
        files += util.recursefolders(vfs.join(config.OVERLAY_DIR, subdir), 1, '*.fxd', 1)

    for info in fxditem.mimetype.parse(None, files, display_type='video'):
        if hasattr(info, '__fxd_rom_info__'):
            for i in info.__fxd_rom_id__:
                fxd_database['id'][i] = info
            for l in info.__fxd_rom_label__:
                fxd_database['label'].append((re.compile(l), info))
            for fo in info.__fxd_files_options__:
                discset_informations[fo['file-id']] = fo['mplayer-options']

    if config.VIDEO_SHOW_DATA_DIR:
        files = util.recursefolders(config.VIDEO_SHOW_DATA_DIR,1, '*.fxd',1)
        for info in fxditem.mimetype.parse(None, files, display_type='video'):
            k = vfs.splitext(vfs.basename(info.files.fxd_file))[0]
            tv_show_informations[k] = (info.image, info.info, info.mplayer_options,
                                       info.skin_fxd)
            if hasattr(info, '__fxd_rom_info__'):
                for fo in info.__fxd_files_options__:
                    discset_informations[fo['file-id']] = fo['mplayer-options']
            
    _debug_('done',1)
    return 1
