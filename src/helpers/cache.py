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
# Revision 1.5  2003/08/23 09:09:18  dischi
# moved some helpers to src/helpers
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
#endif


import sys
import os

import config
import util


def delete_old_files():
    print 'deleting old cache files from older freevo version'
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


def cache_helper(result, dirname, names):
    if not dirname in result and not \
           os.path.basename(dirname) in ('.xvpics', '.thumbnails', 'CVS'):
        result.append(dirname)
    return result

def cache_directories():
    import mmpython

    mmcache = '%s/mmpython' % config.FREEVO_CACHEDIR
    if not os.path.isdir(mmcache):
        os.mkdir(mmcache)
    mmpython.use_cache(mmcache)
    mmpython.mediainfo.DEBUG = 0
    mmpython.factory.DEBUG = 0
    
    all_dirs = []
    print 'caching directories...'
    for n, d in config.DIR_MOVIES + config.DIR_AUDIO + config.DIR_IMAGES:
        os.path.walk(d, cache_helper, all_dirs)
    for d in all_dirs:
        print d
        mmpython.cache_dir(d)
        
    util.touch('%s/VERSION' % mmcache)


if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] == '--help':
        print 'freevo cache helper to delete unused cache entries and to'
        print 'cache all files in your data directories.'
        print
        print 'this script has no options (yet)'
        print
        sys.exit(0)
        
    delete_old_files()
    cache_directories()
    
