# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# db.py -
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

__all__ = [ 'Cache', 'FileCache', 'save', 'get' ]

# python imports
import time
import os
import stat
import re
import logging

# freevo imports
import config
import util.vfs as vfs
import util.cache as cache
from util.callback import *

# mediadb imports
import parser

# get logging object
log = logging.getLogger('mediadb')

VERSION = 2.4

class CacheList:
    def __init__(self):
        self.caches = {}

    def get(self, dirname):
        if dirname in self.caches:
            cache = self.caches[dirname]
            mtime = os.stat(cache.file)[stat.ST_MTIME]
            if mtime == cache.mtime:
                return cache
        c = Cache(dirname)
        self.caches[dirname] = c
        return c

    def save(self):
        for cache in self.caches.values():
            cache.save()


# global object
_cache_list = CacheList()

class Cache:
    """
    A cache object for the mediainfo holding one directory.
    """
    def __init__(self, dirname):
        self.dirname = dirname
        self.overlay_file = vfs.getoverlay(dirname)
        self.file = self.overlay_file + '/freevo.db'
        self.data = None
        self.changed = False
        self.check_time = 0
        if os.path.isfile(self.file):
            # load cache file
            self.data = cache.load(self.file, VERSION)
            self.mtime = os.stat(self.file)[stat.ST_MTIME]
        elif not os.path.isdir(os.path.dirname(self.overlay_file)):
            # create vfs overlay dir; we will need it anyway for
            # storing the db file
            os.makedirs(os.path.dirname(self.overlay_file))
        if not self.data:
            # create a new cache data dict
            self.data  = {'items_mtime': 0,
                          'items': {},
                          'overlay_mtime': {},
                          'overlay': {},
                          'cover': '',
                          'audiocover': '',
                          }
            # save file to make sure the file itself exist in the future
            # process and to avoid directory changes just because the cache
            # is saved to a new file.
            self.changed = True
            self.save()
        # 'normal' files
        self.items   = self.data['items']
        # file sin the overlay dir
        self.overlay = self.data['overlay']
        # internal stuff about changes
        self.__added   = []
        self.__changed = []
        self.__check_global = False
        # a hidden list of files only to check when checking the cache
        self.reduce_files = []


    def reduce(self, files):
        """
        Reduce the files to be checked to the given list of basenames.
        """
        self.reduce_files = files


    def check(self, overlay = False):
        """
        Check the directory for changes.
        """
        if overlay:
            # handling the overlay dir
            dirname = self.overlay_file
            listing = self.overlay
            mtime   = 'overlay_mtime'
        else:
            # handling the 'normal' dir
            dirname = self.dirname
            listing = self.items
            mtime   = 'items_mtime'

        deleted = []
        # get mtime (may be 0 for devices)
        data_mtime = os.stat(dirname)[stat.ST_MTIME]
        if data_mtime != self.data[mtime] or not data_mtime:
            log.debug('check %s' % dirname)
            # mtime differs, check directory for added and deleted files
            if not self.reduce_files:
                # store new mtime
                self.data[mtime] = data_mtime
            # get a current filelisting
            files = os.listdir(dirname)
            for file, info in listing.items():
                if file in files:
                    # in cache already
                    files.remove(file)
                else:
                    # deleted
                    deleted.append(file)
            for d in deleted:
                log.debug('deleted: %s' % d)
                # FIXME: if this file is an image, search every item in
                # the list if it uses this file as cover image.
                del listing[d]

            for f in files:
                # check all files f not in the cache
                if self.reduce_files and not f in self.reduce_files:
                    # ignore the file for now
                    continue
                if f in ('CVS', 'lost+found') or f.startswith('.'):
                    # ignore such files
                    continue
                if overlay and (f == 'freevo.db' or f.find('.thumb.') > 0 or \
                                f.endswith('.raw') or f.endswith('.cache')):
                    # ignore such files in overlay
                    continue
                fullname = dirname + '/' + f
                if overlay and os.path.isdir(fullname):
                    # ignore directories in overlay
                    continue
                # add as added
                self.__added.append((f, fullname))

        for basename, info in listing.items():
            # check all files for changes (compare mtime)
            if self.reduce_files and not basename in self.reduce_files:
                continue
            filename = dirname + '/' + basename
            mtime = os.stat(filename)[stat.ST_MTIME]
            if mtime != info['mtime']:
                # changed
                info['mtime'] = mtime
                self.__changed.append((basename, filename, info))
            elif info.has_key('isdir'):
                # For directories also check the overlay directory. A change
                # in the overlay will change the directory, too
                overlay = vfs.getoverlay(filename)
                if os.path.isdir(overlay):
                    mtime = os.stat(overlay)[stat.ST_MTIME]
                    if mtime != info['overlay_mtime']:
                        info['overlay_mtime'] = mtime
                        self.__changed.append((basename, filename, info))

        if deleted and len(self.__added):
            self.__check_global = True
            self.changed = True
        if overlay:
            self.check_time = time.time()
            if self.changed:
                call_later(self.save)
            return
        self.check(True)


    def save(self):
        """
        Save the cache.
        """
        if not self.changed:
            return
        log.debug('save %s' % self.file)
        cache.save(self.file, self.data, VERSION)
        self.mtime = os.stat(self.file)[stat.ST_MTIME]
        self.changed = False


    def parse(self, callback):
        """
        Parse added and changed files. If callback is not None, the callback
        will be called after each file.
        """
        if not self.__added and not self.__changed and \
               not self.__check_global:
            return

        self.changed = True

        for basename, filename in self.__added:
            # check new files
            log.debug('new: %s' % basename)
            ext = basename[basename.rfind('.')+1:].lower()
            if ext == basename:
                ext = ''
            info = { 'ext'      : ext,
                     'mtime'    : os.stat(filename)[stat.ST_MTIME],
                     'mtime_dep': []
                     }
            parser.parse(filename, info)

            prefix = basename[:-len(ext)]
            if ext in ('png', 'jpg', 'gif'):
                # the new item is an image, search all items for a similar
                # name to add the file as cover
                for i_basename, i_info in self.items.items():
                    if i_basename[:-len(i_info['ext'])] == prefix:
                        i_info['cover'] = filename
            else:
                # search the items in the list for covers matching the
                # basename of the new item
                for ext in ('png', 'jpg', 'gif'):
                    if prefix + ext in self.items:
                        info['cover'] = self.dirname + '/' + prefix + ext
                    if prefix + ext in self.overlay:
                        info['cover'] = self.overlay_file + '/' + prefix + ext
            if vfs.isoverlay(filename):
                self.overlay[basename] = info
            else:
                self.items[basename] = info
            if callback:
                callback()

        for basename, filename, info in self.__changed:
            # check changed files
            log.debug('changed: %s' % filename)
            parser.parse(filename, info)
            log.debug(info['mtime_dep'])
            for key in info['mtime_dep']:
                del info[key]
            if callback:
                callback()

        if self.__check_global:
            # check global data when files are added or deleted
            for cover in ('cover.png', 'cover.jpg', 'cover.gif'):
                if self.items.has_key(cover):
                    # directory cover image
                    self.data['cover'] = self.dirname + '/' + cover
                    self.data['audiocover'] = self.data['cover']
                    break
                if self.overlay.has_key(cover):
                    # cover in overlay
                    self.data['cover'] = self.overlay_file + '/' + cover
                    self.data['audiocover'] = self.data['cover']
                    break
            else:
                # no cover, try to find at least some image that can be used
                # as cover for audio items
                self.data['cover'] = ''
                self.data['audiocover'] = ''
                cover = []
                for f, i in self.items.items():
                    if i['ext'] in ('png', 'jpg', 'gif'):
                        cover.append(f)
                        if len(cover) > 10:
                            cover = []
                            break
                if len(cover) == 1:
                    self.data['audiocover'] = cover[0]
                else:
                    cover = filter(parser.cover_filter, cover)
                    if cover:
                        self.data['audiocover'] = cover[0]

            if callback:
                callback()

        self.save()
        self.__added   = []
        self.__changed = []
        self.__check_global = False
        self.reduce_files = []


    def list(self):
        """
        Return all items.
        """
        return self.items.items() + self.overlay.items()


    def num_changes(self):
        """
        Return the number of changes in the directory. If the number is
        greater than zero, parse _must_ be called.
        """
        if self.reduce_files or self.check_time + 2 < time.time():
            self.check()
        changes = len(self.__added) + len(self.__changed)
        if self.__check_global:
            return changes + 1
        if not changes:
            self.reduce_files = []
        return changes


    def __str__(self):
        """
        Return string for debugging.
        """
        return 'mediadb.db.Cache for %s' % self.dirname

        
class FileCache:
    """
    Cache for one file
    """
    def __init__(self, filename, db):
        self.file = db
        self.data = None
        if os.path.isfile(self.file):
            # load cache file
            self.data = cache.load(self.file, VERSION)
            self.mtime = os.stat(self.file)[stat.ST_MTIME]
        if not self.data:
            # create a new cache data dict
            self.data  = { 'ext': '',
                           'cover': '',
                           'audiocover': '',
                           'mtime'    : os.stat(filename)[stat.ST_MTIME],
                           'mtime_dep': []
                           }
            # save file to make sure the file itself exist in the future
            # process and to avoid directory changes just because the cache
            # is saved to a new file.
            self.changed = True
            parser.parse(filename, self.data)
            self.save()


    def save(self):
        """
        Save the cache.
        """
        if not self.changed:
            return
        log.info('save %s' % self.file)
        cache.save(self.file, self.data, VERSION)
        self.mtime = os.stat(self.file)[stat.ST_MTIME]
        self.changed = False



def save():
    _cache_list.save()


def get(dirname):
    return _cache_list.get(dirname)

