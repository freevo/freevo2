# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# db.py -
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: check for images of files
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

__all__ = [ 'Cache', 'FileCache', 'save', 'get' ]

# python imports
import time
import os
import re
import md5
import logging
from stat import *

# kaa imports
from kaa.notifier import OneShotTimer

# freevo imports
import sysconfig
import util.vfs as vfs
import util.cache as cache

# mediadb imports
import parser
from globals import *

# get logging object
log = logging.getLogger('mediadb')

# internal format version
VERSION = 0.1

# cache dir for metadata
CACHE_DIR = vfs.BASE + '/metadata'

if not os.path.isdir(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    
class CacheList(object):
    """
    Internal list of all cache objects.
    """
    def __init__(self):
        self.caches = {}

    def get(self, dirname):
        """
        Get Cache object for dirname.
        """
        if dirname in self.caches:
            cache = self.caches[dirname]
            mtime = os.stat(cache.cachefile)[ST_MTIME]
            if mtime == cache.mtime:
                return cache
        c = Cache(dirname)
        self.caches[dirname] = c
        return c


    def save(self):
        """
        Save all cache files.
        """
        for cache in self.caches.values():
            cache.save(False)



# global object
_cache_list = CacheList()

class Cache(object):
    """
    A cache object for the mediadb holding one directory.
    """
    def __init__(self, dirname):
        # save timer
        self.__save_timer = OneShotTimer(self.save, False)
        self.__save_timer.restart_when_active = False
        # create full path
        dirname = os.path.normpath(os.path.abspath(dirname))
        # remove softlinks from path
        dirname = os.path.realpath(dirname)
        if not dirname.endswith('/'):
            dirname = dirname + '/'
        self.dirname = dirname

        for mp in vfs.mountpoints:
            if dirname.startswith(mp.mountdir):
                self.overlay_dir = mp.get_overlay(dirname)
                digest = md5.md5(mp.get_relative_path(dirname)).hexdigest()
                self.cachefile = mp.mediadb + '/' + digest + '.db'
                break
        else:
            self.overlay_dir = vfs.BASE + dirname
            digest = md5.md5(dirname).hexdigest()
            self.cachefile = CACHE_DIR + '/' + digest + '.db'

        self.data = None
        self.changed = False
        self.check_time = 0
        if os.path.isfile(self.cachefile):
            # load cache file
            self.data = cache.load(self.cachefile, VERSION)
            self.mtime = os.stat(self.cachefile)[ST_MTIME]

        if not self.data:
            # create a new cache data dict
            self.data  = { DATA_VERSION:  parser.VERSION,
                           ITEMS_MTIME:   0,
                           ITEMS:         {},
                           OVERLAY_MTIME: {},
                           OVERLAY_ITEMS: {},
                           COVER:         '',
                           EXTRA_COVER:   '',
                          }
            # save file to make sure the file itself exist in the future
            # process.
            self.changed = True
            self.save(False)
        # 'normal' files
        self.files   = self.data[ITEMS]
        # files in the overlay dir
        self.overlay = self.data[OVERLAY_ITEMS]
        # internal stuff about changes
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
            dirname = self.overlay_dir
            listing = self.overlay
            mtime   = OVERLAY_MTIME
        else:
            # handling the 'normal' dir
            dirname = self.dirname
            listing = self.files
            mtime   = ITEMS_MTIME

        deleted = []
        added = []
        try:
            # get mtime (may be 0 for devices)
            data_mtime = os.stat(dirname)[ST_MTIME]
        except OSError:
            # no overlay dir
            self.check_time = time.time()
            self.save()
            return

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
                if overlay and f.endswith('.raw'):
                    # ignore such files in overlay
                    continue
                filename = dirname + f
                try:
                    stat  = os.stat(filename)
                except OSError:
                    # unable to call stat, maybe it's a broken link
                    log.error('unable to check %s, skipping' % filename)
                    continue
                isdir = S_ISDIR(stat[ST_MODE])
                if overlay and isdir:
                    # ignore directories in overlay
                    continue
                # add file
                ext = f[f.rfind('.')+1:].lower()
                title = parser.getname(f, isdir)
                info = { EXTENTION : ext,
                         MTIME     : stat[ST_MTIME],
                         MTIME_DEP : [],
                         TITLE     : title,
                         FILETITLE : title,
                         NEW_FILE  : True
                         }
                if isdir:
                    info[ISDIR] = True
                added.append((f, info))
                self.__changed.append((f, filename, info))

        broken = []
        for basename, info in listing.items():
            # check all files for changes (compare mtime)
            if self.reduce_files and not basename in self.reduce_files:
                continue
            filename = dirname + basename
            if info.has_key(NEEDS_UPDATE):
                self.__changed.append((basename, filename, info))
                continue
            try:
                mtime = os.stat(filename)[ST_MTIME]
            except OSError:
                # unable to call stat, maybe it's a broken link
                log.error('unable to check %s, skipping' % filename)
                broken.append(basename)
                continue
            if mtime != info[MTIME]:
                # changed
                info[MTIME] = mtime
                self.__changed.append((basename, filename, info))
            elif info.has_key(ISDIR):
                # For directories also check the overlay directory. A
                # change in the overlay will change the directory, too
                overlay_dir = vfs.getoverlay(filename)
                if os.path.isdir(overlay_dir):
                    mtime = os.stat(overlay_dir)[ST_MTIME]
                    if mtime != info[OVERLAY_MTIME]:
                        info[OVERLAY_MTIME] = mtime
                        self.__changed.append((basename, filename, info))

        for key in broken:
            del listing[key]

        if deleted or added or broken:
            self.__check_global = True
            self.changed = True

        for filename, info in added:
            listing[filename] = info

        if overlay:
            self.check_time = time.time()
            self.save()
            return
        self.check(True)


    def save(self, later=True):
        """
        Save the cache.
        """
        if not self.changed:
            return
        if later:
            self.__save_timer.start(0)
            return
        log.debug('save %s' % self.cachefile)
        cache.save(self.cachefile, self.data, VERSION)
        self.mtime = os.stat(self.cachefile)[ST_MTIME]
        self.changed = False


    def parse_next(self):
        """
        Parse the next item in the changed list. Return True if more
        items are in the list, otherwise return False. This function
        should be called from the notifier to parse all items in the
        background.
        """
        if not self.__changed:
            return False
        basename, filename, info = self.__changed.pop()
        log.debug('parse_next: %s' % basename)
        parser.parse(basename, filename, info, self, self.items())
        self.changed = True
        if not self.__changed:
            return False
        return True
    

    def parse_item(self, item):
        """
        Parse the info for the given file if it is in the changed list.
        """
        for c in self.__changed:
            if c[2] == item.attr:
                basename, filename, info = c
                log.debug('parse_item: %s' % basename)
                parser.parse(basename, filename, info, self, self.items())
                self.changed = True
                self.__changed.remove(c)
                return True
        return False
        
                
    def parse(self, callback, fast_scan=False):
        """
        Parse added and changed files. If callback is not None, the callback
        will be called after each file.
        """
        if not self.__changed and not self.__check_global:
            return

        self.changed = True

        items = self.items()
        
        if fast_scan:
            for basename, filename, info in self.__changed:
                info[NEEDS_UPDATE] = True

        else:
            for basename, filename, info in self.__changed:
                # check changed files
                log.debug('changed: %s' % filename)
                parser.parse(basename, filename, info, self, items)
                if callback:
                    callback()
            self.__changed = []

        if self.__check_global:
            # check global data when files are added or deleted
            for cover in ('cover.png', 'cover.jpg', 'cover.gif'):
                if self.files.has_key(cover):
                    # directory cover image
                    self.data[COVER] = self.dirname + '/' + cover
                    self.data[EXTRA_COVER] = self.data[COVER]
                    break
                if self.overlay.has_key(cover):
                    # cover in overlay
                    self.data[COVER] = self.overlay_dir + '/' + cover
                    self.data[EXTRA_COVER] = self.data[COVER]
                    break
            else:
                # no cover, try to find at least some image that can be used
                # as cover for audio items
                self.data[COVER] = ''
                self.data[EXTRA_COVER] = ''
                cover = []
                for f, i in self.files.items():
                    if i[EXTENTION] in ('png', 'jpg', 'gif'):
                        cover.append(f)
                        if len(cover) > 10:
                            cover = []
                            break
                if len(cover) == 1:
                    self.data[EXTRA_COVER] = cover[0]
                else:
                    cover = filter(parser.cover_filter, cover)
                    if cover:
                        self.data[EXTRA_COVER] = cover[0]

            if callback:
                callback()

        self.save(False)
        self.__check_global = False
        self.reduce_files = []


    def items(self):
        """
        Return all items.
        """
        return self.files.items() + self.overlay.items()


    def keys(self):
        """
        Return all keys.
        """
        return self.files.keys() + self.overlay.keys()


    def filename(self, basename):
        """
        Return full filename of the basename (handles overlay).
        """
        if basename in self.files:
            return self.dirname + basename
        if basename in self.overlay:
            return self.overlay_dir + basename
        raise OSError('No key "%s" in cache' % basename)

    
    def num_changes(self):
        """
        Return the number of changes in the directory. If the number is
        greater than zero, parse _must_ be called.
        """
        if self.reduce_files or self.check_time + 2 < time.time():
            self.check()
        changes = len(self.__changed)
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


class FileCache(object):
    """
    Cache for one file
    """
    def __init__(self, filename, db):
        # save timer
        self.__save_timer = OneShotTimer(self.save, False)
        self.__save_timer.restart_when_active = False
        self.cachefile = db
        self.data = None
        if os.path.isfile(self.cachefile):
            # load cache file
            self.data = cache.load(self.cachefile, VERSION)
            self.mtime = os.stat(self.cachefile)[ST_MTIME]
        if not self.data:
            # create a new cache data dict
            self.data  = { DATA_VERSION: parser.VERSION,
                           EXTENTION   : '',
                           COVER       : '',
                           EXTRA_COVER : '',
                           MTIME       : os.stat(filename)[ST_MTIME],
                           MTIME_DEP   : []
                           }
            # save file to make sure the file itself exist in the future
            # process and to avoid directory changes just because the cache
            # is saved to a new file.
            self.changed = True
            basename = filename[filename.rfind('/'):]
            parser.parse(basename, filename, self.data, self, [])
            self.save(False)
        self.filename = filename
        

    def save(self, later=True):
        """
        Save the cache.
        """
        if not self.changed:
            return
        if later:
            self.__save_timer.start(0)
            return
        log.debug('save %s' % self.cachefile)
        cache.save(self.cachefile, self.data, VERSION)
        self.mtime = os.stat(self.cachefile)[ST_MTIME]
        self.changed = False


    def __str__(self):
        """
        Return string for debugging.
        """
        return 'mediadb.db.FileCache for %s' % self.filename




def save():
    """
    Save all cache files.
    """
    _cache_list.save()


def get(dirname):
    """
    Get cache object for the given dirname.
    """
    return _cache_list.get(dirname)
