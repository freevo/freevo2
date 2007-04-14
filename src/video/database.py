# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# database.py - interface to access all video fxd files
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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


__all__ = [ 'update', 'get_media', 'discset', 'tv_shows' ]

# python imports
import os
import re
import copy

import logging
log = logging.getLogger('video')

# variables for the hashing function
fxd      = {}
discset  = {}
tv_shows = {}


def update():
    """
    hash fxd movie files in some directories. This is used e.g. by the
    rom drive plugin, but also for a directory and a videoitem.
    """
    global tv_shows
    global discset
    global fxd

    return

    # import fxditem here, we may get in trouble doing it at the
    # beginning (maybe, maybe not). FIXME!
    from freevo.ui import fxditem
    
    fxd['id']    = {}
    fxd['label'] = []
    discset      = {}
    tv_shows     = {}

    log.info("Building the xml hash database...")

    files = []

    # BEACON_FIXME
    # discset2 = ?? + '/disc-set'
    # if os.path.isdir(discset2):
    #     listing = Listing(discset)
    #     files += listing.get('fxd')

    for info in fxditem.mimetype.parse(None, files, [], display_type='video'):
        if info.type != 'video':
            continue
        k = os.path.splitext(os.path.basename(info.files.fxd_file))[0]
        tv_shows[k] = (info.image, info.info, info.mplayer_options)
        if hasattr(info, '__fxd_rom_info__'):
            for fo in info.__fxd_files_options__:
                discset[fo['file-id']] = fo['mplayer-options']
        if hasattr(info, '__fxd_rom_label__'):
            for label in info.__fxd_rom_label__:
                fxd['label'].append((re.compile(label), info))
        if hasattr(info, '__fxd_rom_id__'):
            for id in info.__fxd_rom_id__:
                fxd['id'][id] = info
    log.info('done')
    return 1


def get_media(media):
    """
    Return informations based on the id or label. Return None if not found.
    """
    if media.id in fxd['id']:
        return fxd['id'][media.id]
    for (re_label, movie_info_t) in fxd['label']:
        if re_label.match(media.label):
            movie_info = copy.copy(movie_info_t)
            if movie_info.name:
                title = movie_info.name
                m = re_label.match(media.label).groups()
                re_count = 1

                # found, now change the title with the regexp.
                # E.g.: label is "bla_2", the label regexp
                # "bla_[0-9]" and the title is "Something \1",
                # the \1 will be replaced with the first item in
                # the regexp group, here 2. The title is now
                # "Something 2"
                for g in m:
                    title = title.replace('\\%s' % re_count, g)
                    re_count += 1
                movie_info.name = title
                return movie_info
    return None
