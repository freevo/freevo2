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
# Revision 1.30  2004/03/27 00:46:23  outlyer
# Fixed a crash. It occured when I used the "Configure Directory" option to
# show "all types" in a music directory.
#
# Revision 1.29  2004/03/22 03:04:28  krister
# Fixed a typo
#
# Revision 1.28  2004/02/15 15:22:42  dischi
# better dvd disc support
#
# Revision 1.27  2004/02/03 20:51:12  dischi
# fix/enhance dvd on disc
#
# Revision 1.26  2004/02/02 22:15:53  outlyer
# Support for mirrors of DVDs...
#
# (1) Make one using vobcopy, run 'vobcopy -m'
# (2) Put it in your movie directory and it'll look like a single file, and can
#     be played with XINE with all of the features of the original DVD (chapters,
#     audio tracks, etc) and works with dvdnav.
#
# Revision 1.25  2004/02/01 19:47:13  dischi
# some fixes by using new mmpython data
#
# Revision 1.24  2004/02/01 17:10:09  dischi
# add thumbnail generation as directory config variable
#
# Revision 1.23  2004/01/10 13:22:17  dischi
# reflect self.fxd_file changes
#
# Revision 1.22  2004/01/09 21:05:27  dischi
# set directory skin_settings for tv shows
#
# Revision 1.21  2004/01/03 17:40:27  dischi
# remove update function
#
# Revision 1.20  2003/12/29 22:08:54  dischi
# move to new Item attributes
#
# Revision 1.19  2003/12/09 19:43:01  dischi
# patch from Matthieu Weber
#
# Revision 1.18  2003/12/06 13:44:11  dischi
# move more info to the Mimetype
#
# Revision 1.17  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
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
import util.videothumb
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
            if parent and parent.type == 'dir' and hasattr(parent,'VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS') and \
                   parent.VIDEO_DIRECTORY_AUTOBUILD_THUMBNAILS:
                util.videothumb.snapshot(file, update=False, popup=True)

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
