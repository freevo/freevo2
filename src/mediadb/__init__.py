# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediadb
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: o remove old functions (see below)
#       o include extendedmeta
#       o add SQLListing
#       o maybe preload whole cache? Expire cache?
#       o add InfoItem for / and network url
#       o add InfoItem for subditems
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

# python imports
import os
import logging

# mmpython
from mmpython.disc.discinfo import cdrom_disc_id

# freevo imports
import sysconfig

# mediadb imports
from db import Cache, FileCache, save
from item import ItemInfo
from listing import Listing, FileListing

# get logging object
log = logging.getLogger('mediadb')


def disc_info(media, force=False):
    """
    Return information for the media
    """
    type, id  = cdrom_disc_id(media.devicename)
    if not id:
        # bad disc, e.g. blank disc
        return ItemInfo(None, None, None)
    cachefile = os.path.join(sysconfig.VFS_DIR, 'disc/metadata/%s.db' % id)
    if force and os.path.isfile(cachefile):
        os.unlink(cachefile)
    cache = FileCache(media.devicename, cachefile)
    info = ItemInfo('', '', cache.data, cache)
    info.filename = info['mime'][6:] + '://'
    return info


#
# FIXME: the following functions will be removed in the future
# also missing the attribute mmdata used by videoitem.py
#

def get(filename):
    # used by directory.py, item.py, videoitem.py and extendedmeta.py
    log.warning('get simple info %s', filename)
    listing = FileListing( [ filename ] )
    if listing.num_changes:
        listing.update()
    return listing.get_by_name(os.path.basename(filename))


def del_cache():
    # used by cache.py
    log.error('del_cache not defined anymore')


def set(filename, key, value):
    # used by extendedmeta.py
    log.error('set not defined anymore')


def cache_dir(dirname, callback=None):
    # used by cache.py, extendedmeta.py
    log.error('cache_dir not defined anymore')
