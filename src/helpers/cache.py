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
# Revision 1.18  2004/02/05 20:39:11  dischi
# check mmpython cache version
#
# Revision 1.17  2004/02/01 17:50:43  dischi
# fix, it deleted all infos on caching :-)
#
# Revision 1.16  2004/01/19 20:25:53  dischi
# sync metainfo before stopping
#
# Revision 1.15  2004/01/18 16:48:29  dischi
# expand caching (including extendedadd.py)
#
# Revision 1.14  2004/01/17 20:30:18  dischi
# use new metainfo
#
# Revision 1.13  2004/01/04 17:20:44  dischi
# support for generating video thumbnails
#
# Revision 1.12  2004/01/03 17:42:03  dischi
# o OVERLAY_DIR is now used everytime
# o added support to delete old cachefile in the overlay dir
# o remove unneeded subdirs in the overlay dir
#
# Revision 1.11  2003/12/31 16:43:28  dischi
# also cache thumbnails for config.OVERLAY_DIR_STORE_THUMBNAILS:
#
# Revision 1.10  2003/12/30 15:36:42  dischi
# support OVERLAY_DIR_STORE_MMPYTHON_DATA
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
import copy

def delete_old_files_1():
    """
    delete old files from previous versions of freevo which are not
    needed anymore
    """
    print 'deleting old cache files from older freevo version....',
    sys.__stdout__.flush()
    del_list = []

    for name in ('image-viewer-thumb.jpg', 'thumbnails', 'audio', 'mmpython'):
        if os.path.exists(os.path.join(config.FREEVO_CACHEDIR, name)):
            del_list.append(os.path.join(config.FREEVO_CACHEDIR, name))

    del_list += util.recursefolders(config.OVERLAY_DIR,1,'mmpython',1)
    del_list += util.match_files(config.OVERLAY_DIR+'/disc', ['mmpython', 'freevo'])

    for file in util.match_files_recursively(config.OVERLAY_DIR, ['png']):
        if file.endswith('.fvt.png'):
            del_list.append(file)

    for f in del_list:
        if os.path.isdir(f):
            util.rmrf(f)
        else:
            os.unlink(f)
    print 'deleted %s file(s)' % len(del_list)


def delete_old_files_2():
    """
    delete cachfiles/entries for files which don't exists anymore
    """
    print 'deleting old cachefiles...............................',
    sys.__stdout__.flush()
    num = 0
    for file in util.match_files_recursively(config.OVERLAY_DIR, ['raw']):
        if not vfs.isfile(file[len(config.OVERLAY_DIR):-4]):
            os.unlink(file)
            num += 1
    print 'deleted %s file(s)' % num

    print 'deleting cache for directories not existing anymore...',
    subdirs = util.get_subdirs_recursively(config.OVERLAY_DIR)
    subdirs.reverse()
    for file in subdirs:
        if not os.path.isdir(file[len(config.OVERLAY_DIR):]) and not \
               file.startswith(config.OVERLAY_DIR + '/disc'):
            if os.path.isfile(os.path.join(file, 'mmpython.cache')):
                os.unlink(os.path.join(file, 'mmpython.cache'))
            if os.path.isfile(os.path.join(file, 'freevo.cache')):
                os.unlink(os.path.join(file, 'freevo.cache'))
            if not os.listdir(file):
                os.rmdir(file)
    print 'done'

    print 'deleting old entries in metainfo......................',
    sys.__stdout__.flush()
    for filename in util.recursefolders(config.OVERLAY_DIR,1,'freevo.cache',1):
        if filename.startswith(config.OVERLAY_DIR + '/disc'):
            continue
        dirname = os.path.dirname(filename)[len(config.OVERLAY_DIR):]
        data    = util.read_pickle(filename)
        for key in copy.copy(data):
            if not os.path.exists(dirname + '/' + key):
                del data[key]
        util.save_pickle(data, filename)
    print 'done'
    

def cache_directories(rebuild):
    """
    cache all directories with mmpython
    rebuild:
    0   no rebuild
    1   rebuild all files on disc
    2   like 1, but also delete discinfo data
    """
    import util.mediainfo
    try:
        import mmpython.version

        info = None
        cachefile = os.path.join(config.FREEVO_CACHEDIR, 'mediainfo')
        if os.path.isfile(cachefile):
            info = util.read_pickle(cachefile)
        if not info:
            print
            print 'Unable to detect last complete rebuild, forcing rebuild'
            rebuild         = 2
            complete_update = int(time.time())
        else:
            mmchanged, part_update, complete_update = info
    except ImportError:
        print
        print 'Error: unable to read mmpython version information'
        print 'Please update mmpython to the latest release or if you use'
        print 'Freevo CVS versions, please also use mmpython CVS.'
        print
        print 'Some functions in Freevo may not work or even crash!'
        print
        print

    if rebuild:
        print 'deleting cache files..................................',
        sys.__stdout__.flush()
        for f in util.recursefolders(config.OVERLAY_DIR,1,'mmpython.cache',1):
            os.unlink(f)
        if rebuild == 2:
            for f in util.match_files(config.OVERLAY_DIR + '/disc/metadata', ['mmpython']):
                os.unlink(f)
                print f
        print 'done'

    print
    all_dirs = []
    print 'caching directories...'
    for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
        if os.path.isdir(d[1]):
            all_dirs.append(d[1])
    util.mediainfo.cache_recursive(all_dirs, verbose=True)
    print

    try:
        import mmpython.version
        util.save_pickle((mmpython.version.CHANGED, int(time.time()), complete_update),
                         cachefile)
        print 
    except ImportError:
        pass
    

def cache_thumbnails():
    """
    cache all image files by creating thumbnails
    """
    import cStringIO
    import stat
    import Image
    
    print 'caching thumbnails...'

    files = []
    for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
        try:
            d = d[1]
        except:
            pass
        if not os.path.isdir(d):
            continue
        files += util.match_files_recursively(d, config.IMAGE_SUFFIX) + \
                 util.match_files_recursively(vfs.getoverlay(d), config.IMAGE_SUFFIX)

    files = util.misc.unique(files)
    for filename in copy.copy(files):
        sinfo = os.stat(filename)
        thumb = vfs.getoverlay(filename + '.raw')
        try:
            if os.stat(thumb)[stat.ST_MTIME] > sinfo[stat.ST_MTIME]:
                files.remove(filename)
        except OSError:
            pass

    for filename in files:
        fname = filename
        if len(fname) > 65:
            fname = fname[:20] + ' [...] ' + fname[-40:]
        print '  %4d/%-4d %s' % (files.index(filename)+1, len(files), fname)

        sinfo = os.stat(filename)
        thumb = vfs.getoverlay(filename + '.raw')
        try:
            if os.stat(thumb)[stat.ST_MTIME] > sinfo[stat.ST_MTIME]:
                continue
        except OSError:
            pass

        try:
            image = Image.open(filename)
        except:
            continue

        if not image:
            continue

        try:
            if image.size[0] > 300 and image.size[1] > 300:
                image.thumbnail((300,300), Image.ANTIALIAS)

            if image.mode == 'P':
                image = image.convert('RGB')

            # save for future use
            data = (image.tostring(), image.size, image.mode)
            util.save_pickle(data, thumb)
        except:
            print 'error caching image %s' % filename
    print


    
def create_metadata():
    """
    scan files and create metadata
    """
    import util.extendedmeta
    print 'create audio metadata...'
    for dir in config.AUDIO_ITEMS:
        if os.path.isdir(dir[1]):
            print "  Scanning %s" % dir[0]
            util.extendedmeta.AudioParser(dir[1], rescan=True)
    print
    try:
        # The DB stuff
        import sqlite
    except:
        print 'no pysqlite installed, skipping db support'
        print
        return

    print 'checking database...'
    for dir in config.AUDIO_ITEMS:
        if os.path.isdir(dir[1]):
            print "  Scanning %s" % dir[0]
            util.extendedmeta.addPathDB(dir[1], dir[0])
    print


    
if __name__ == "__main__":
    os.umask(config.UMASK)
    if len(sys.argv)>1 and sys.argv[1] == '--help':
        print 'freevo cache helper to delete unused cache entries and to'
        print 'cache all files in your data directories.'
        print
        print 'usage "freevo cache [--rebuild]"'
        print 'If the --rebuild option is given, Freevo will delete the cache first'
        print 'to rebuild the cache from start. Caches from discs won\'t be affected'
        print
        print 'or "freevo cache --thumbnail [ --recursive ] dir"'
        print 'This will create thumbnails of your _video_ files'
        print
        print 'WARNING:'
        print 'Caching needs a lot free space in OVERLAY_DIR. The space is also'
        print 'needed when Freevo generates the files during runtime. Image'
        print 'caching is the worst. So make sure you have several hundred MB'
        print 'free! OVERLAY_DIR is set to %s' % config.OVERLAY_DIR
        print
        print 'It may be possible to turn off image caching in future versions'
        print 'of Freevo (but this will slow things down).'
        print
        sys.exit(0)

    if len(sys.argv)>1 and sys.argv[1] == '--thumbnail':
        import util.videothumb
        if sys.argv[2] == '--recursive':
            dirname = os.path.abspath(sys.argv[3])
            files = util.match_files_recursively(dirname, config.VIDEO_SUFFIX)
        else:
            dirname = os.path.abspath(sys.argv[2])
            files = util.match_files(dirname, config.VIDEO_SUFFIX)
            
        print 'creating video thumbnails....'
        for filename in files:
            print '  %4d/%-4d %s' % (files.index(filename)+1, len(files),
                                     os.path.basename(filename))
            util.videothumb.snapshot(filename, update=False)
        print
        sys.exit(0)
        
    delete_old_files_1()
    delete_old_files_2()

    for type in 'VIDEO', 'AUDIO', 'IMAGE':
        for d in copy.copy(getattr(config, '%s_ITEMS' % type)):
            if not isinstance(d, str):
                d = d[1]
            if d == '/':
                print '%s_ITEMS contains root directory, skipped.' % type
                setattr(config, '%s_ITEMS' % type, [])

    if len(sys.argv)>1 and sys.argv[1] == '--rebuild':
        cache_directories(1)
    else:
        cache_directories(0)

    create_metadata()
    cache_thumbnails()

# close db
util.mediainfo.sync()

