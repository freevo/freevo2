# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# listing.py -
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'Listing', 'FileListing' ]

# python imports
import logging

# mediadb imports
import db
from db import Cache, FileCache
from item import ItemInfo
import parser
from globals import *

log = logging.getLogger('mediadb')

class Listing(object):
    """
    A directory listing with items from the mediadb. After creating a listing,
    check the 'num_changes' variable. If it is greater zero, the listing is
    invalid until update() is called.
    """
    def __init__(self, dirname):
        try:
            self.cache = db.get(dirname)
        except:
            log.exception('Listing error for %s' % dirname)
            self.data = []
            self.visible = []
            self.num_changes = 0
            return
        self.num_changes = self.cache.num_changes()
        self.dirname = dirname
        self.data = []
        if self.num_changes > 0:
            self.visible = []
            return
        for basename, item in self.cache.items():
            self.data.append(ItemInfo(basename, dirname, item, self.cache))
        self.visible = self.data


    def update(self, callback=None, fast=False):
        """
        Update the directory listing. This means parsing all changed / new
        files. If fast is True, only new files will be updated and metadata
        checking is disabled. The listing is still not correct then. If
        callback not not None, callback will be called on each item.
        """
        if self.num_changes == 0:
            return
        self.cache.parse(callback, fast)
        dirname = self.dirname
        cache = self.cache
        for basename, item in self.cache.items():
            self.data.append(ItemInfo(basename, dirname, item, cache))
        self.num_changes = 0
        self.visible = self.data
            

    def get_dir(self):
        """
        Return all directory items.
        """
        ret = filter(lambda x: x.attr.has_key(ISDIR), self.visible)
        self.visible = filter(lambda x: not x.attr.has_key(ISDIR),
                              self.visible)
        return ret


    def remove(self, item_or_name):
        """
        Remove the given item from the list of visible items.
        """
        if isinstance(item_or_name, ItemInfo):
            self.visible.remove(item_or_name)
            return
        for item in self.visible:
            if item.filename == item_or_name or \
                   item.basename == item_or_name:
                self.visible.remove(item)
                return


    def get_by_name(self, name):
        """
        Get an item by name.
        """
        for item in self.visible:
            if item.basename == name:
                self.visible.remove(item)
                return item
        return None


    def match_suffix(self, suffix_list):
        """
        Return all items with a suffix in the suffix list.
        """
        visible = self.visible
        self.visible = []
        ret = []
        for v in visible:
            if v.attr[EXTENTION] in suffix_list: ret.append(v)
            else: self.visible.append(v)
        return ret


    def match_type(self, type):
        """
        Return all items with the given type. Note: most items have no type
        set and can't be returned by this function. Use match_suffix in this
        case.
        """
        visible = self.visible
        self.visible = []
        ret = []
        for v in visible:
            if v.attr.has_key(TYPE) and \
                   v.attr[TYPE].lower() == type.lower():
                ret.append(v)
            else:
                self.visible.append(v)
        return ret


    def reset(self):
        """
        Reset listing by setting all items in the directory visible again.
        """
        self.visible = self.data


    def __iter__(self):
        """
        Walk through all visible items.
        """
        return self.visible.__iter__()




class FileListing(Listing):
    """
    A listing containing files from different directories.
    """
    def __init__(self, files):
        self.caches = {}
        for f in files:
            if f == '/':
                # root directory in the list, ignore it for now
                log.error('unable to parse root directory')
                continue
            if f.endswith('/'):
                dirname  = f[:f[:-1].rfind('/')]
                basename = f[f[:-1].rfind('/')+1:-1]
            else:
                dirname = f[:f.rfind('/')]
                basename = f[f[:-1].rfind('/')+1:]
            try:
                if len(dirname) == 0:
                    dirname = '/'
                if not dirname in self.caches:
                    cache = db.get(dirname)
                    self.caches[dirname] = ( cache, [ basename ] )
                else:
                    self.caches[dirname][1].append(basename)
            except:
                log.exception('Listing error for %s' % dirname)

        self.num_changes = 0
        for cache, files in self.caches.values():
            cache.reduce(files)
            self.num_changes += cache.num_changes()

        self.data = []
        if self.num_changes > 0:
            self.visible = []
            return

        for dirname, ( cache, all_files ) in self.caches.items():
            for basename, item in cache.items():
                if basename in all_files:
                    self.data.append(ItemInfo(basename, dirname, item, cache))
        self.visible = self.data


    def update(self, callback=None):
        """
        Update the listing.
        """
        for dirname, ( cache, all_files ) in self.caches.items():
            cache.parse(callback)
            for basename, item in cache.items():
                if basename in all_files:
                    self.data.append(ItemInfo(basename, dirname, item, cache))
        self.num_changes = 0
        self.visible = self.data
