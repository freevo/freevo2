#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# cache.py - delete old cache files and update the cache
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/12/30 15:36:42  dischi
# support OVERLAY_DIR_STORE_MMPYTHON_DATA
#
# Revision 1.9  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.8  2003/10/03 16:46:13  dischi
# moved the encoding type (latin-1) to the config file config.LOCALE
#
# Revision 1.7  2003/09/26 11:28:59  dischi
# add rebuild option
#
# Revision 1.6  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.5  2003/08/23 09:09:18  dischi
# moved some helpers to src/helpers
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


import sys
import os

import config
import util
import stat
import time

def delete_old_files():
    print 'deleting old cache files from older freevo version...'
    del_list = []
    for file in ('image-viewer-thumb.jpg', 'thumbnails/image-viewer-thumb.jpg'):
        file = os.path.join(config.FREEVO_CACHEDIR, file)
        if os.path.isfile(file):
            del_list.append(file)

    d = os.path.join(config.FREEVO_CACHEDIR, 'audio')
    if os.path.isdir(d):
        del_list.append(d)

    del_list += util.match_files(os.path.join(config.FREEVO_CACHEDIR, 'thumbnails'), ['jpg',])

    for f in del_list:
        if os.path.isdir(f):
            util.rmrf(f)
        else:
            os.unlink(f)
    print '  deleted %s file(s)' % len(del_list)
    print


def delete_old_thumbails():
    print 'deleting thumbnails not accessed in the last 60 days...'
    num = 0
    for file in util.match_files(os.path.join(config.FREEVO_CACHEDIR,
                                              'thumbnails'), ['raw',]):
        sinfo = os.stat(file)
        last = max(sinfo[stat.ST_ATIME], sinfo[stat.ST_MTIME])
        diff = int(time.time()) - last
        days = diff / (60 * 60 * 24)
        if days > 60:                   # older than 2 month
            os.unlink(file)
            num += 1
    print '  deleted %s file(s)' % num
    print


def delete_old_mmpython_cache():
    print 'deleting cache for directories not existing anymore...'
    mmcache = '%s/mmpython' % config.FREEVO_CACHEDIR
    if not os.path.isdir(mmcache):
        return
    
    files = ([ os.path.join(mmcache, fname) for fname in os.listdir(mmcache) ])
    for f in files:
        data = util.read_pickle(f)
        if data and data[1] and data[1].keys():
            key = data[1].keys()[0]
            if key.find('/') > 0:
                d = os.path.dirname(key[key.find('/'):])
                if not os.path.isdir(d):
                    print '  deleting cachefile for %s' % d
                    os.unlink(f)
    print

    
def cache_helper(result, dirname, names):
    if not dirname in result and not \
           os.path.basename(dirname) in ('.xvpics', '.thumbnails', 'CVS'):
        result.append(dirname)
    return result


def cache_directories(rebuild=True):
    import mmpython

    mmcache = '%s/mmpython' % config.FREEVO_CACHEDIR
    if not os.path.isdir(mmcache):
        os.mkdir(mmcache)
    mmpython.use_cache(mmcache)
    mmpython.mediainfo.DEBUG = 0
    mmpython.factory.DEBUG   = 0

    if config.OVERLAY_DIR_STORE_MMPYTHON_DATA and mmpython.object_cache and \
           hasattr(mmpython.object_cache, 'md5_cachedir'):
        _debug_('use OVERLAY_DIR for mmpython cache')
        mmpython.object_cache.md5_cachedir = False
        mmpython.object_cache.cachedir     = config.OVERLAY_DIR

    if rebuild:
        print 'deleting cache files'
        for f in ([ os.path.join(mmcache, fname) for fname in os.listdir(mmcache) ]):
            if os.path.isfile(f):
                os.unlink(f)
    all_dirs = []
    print 'caching directories...'
    for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
        try:
            d = d[1]
        except:
            pass
        if not os.path.isdir(d):
            continue
        os.path.walk(d, cache_helper, all_dirs)
    for d in all_dirs:
        dname = d
        if len(dname) > 65:
            dname = dname[:20] + ' [...] ' + dname[-40:]
        print '  %4d/%-4d %s' % (all_dirs.index(d)+1, len(all_dirs), dname)
        mmpython.cache_dir(d)
        
    util.touch('%s/VERSION' % mmcache)


if __name__ == "__main__":
    os.umask(config.UMASK)
    if len(sys.argv)>1 and sys.argv[1] == '--help':
        print 'freevo cache helper to delete unused cache entries and to'
        print 'cache all files in your data directories.'
        print
        print 'usage freevo cache [--rebuild]'
        print 'If the --rebuild option is given, Freevo will delete the cache first'
        print 'to rebuild the cache from start. Caches from discs won\'t be affected'
        print
        sys.exit(0)

    delete_old_files()
    delete_old_thumbails()

    if len(sys.argv)>1 and sys.argv[1] == '--rebuild':
        cache_directories(1)
    else:
        delete_old_mmpython_cache()
        cache_directories(0)
