# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# database.py - interface to access all video fxd files
# -----------------------------------------------------------------------
# $Id$
#
# Notes: The file is ugly. The acces to the data should be covered
#        by a freevo global database interface
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/11/20 18:23:05  dischi
# use python logger module for debug
#
# Revision 1.2  2004/10/22 18:42:28  dischi
# fix crash when item is no VideoItem
#
# Revision 1.1  2004/09/14 20:05:19  dischi
# split __init__ into interface.py and database.py
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

__all__ = [ 'fxd_database', 'discset_informations', 'tv_show_informations',
            'create_movie_database' ]

# python imports
import os
import re

# freevo imports
import config
import util

import logging
log = logging.getLogger('video')

# variables for the hashing function
fxd_database         = {}
discset_informations = {}
tv_show_informations = {}


def create_movie_database():
    """
    hash fxd movie files in some directories. This is used e.g. by the
    rom drive plugin, but also for a directory and a videoitem.
    """
    global tv_show_informations
    global discset_informations
    global fxd_database

    # import fxditem here, we may get in trouble doing it at the
    # beginning (maybe, maybe not). FIXME!
    import fxditem
    
    fxd_database['id']    = {}
    fxd_database['label'] = []
    discset_informations  = {}
    tv_show_informations  = {}

    rebuild_file = os.path.join(config.FREEVO_CACHEDIR,
                                'freevo-rebuild-database')
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

    log.info("Building the xml hash database...")

    files = []
    if not config.VIDEO_ONLY_SCAN_DATADIR:
        if len(config.VIDEO_ITEMS) == 2:
            for name,dir in config.VIDEO_ITEMS:
                files += util.recursefolders(dir,1,'*.fxd',1)

    for subdir in ('disc', 'disc-set'):
        files += util.recursefolders(vfs.join(config.OVERLAY_DIR, subdir),
                                     1, '*.fxd', 1)

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
            if info.type != 'video':
                continue
            k = vfs.splitext(vfs.basename(info.files.fxd_file))[0]
            tv_show_informations[k] = (info.image, info.info,
                                       info.mplayer_options, info.skin_fxd)
            if hasattr(info, '__fxd_rom_info__'):
                for fo in info.__fxd_files_options__:
                    discset_informations[fo['file-id']] = fo['mplayer-options']
            
    log.info('done')
    return 1
