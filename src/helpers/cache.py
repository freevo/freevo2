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
# Revision 1.32  2004/04/18 08:14:31  dischi
# fix crash for bad paths
#
# Revision 1.31  2004/03/22 11:04:51  dischi
# improve caching
#
# Revision 1.30  2004/03/21 09:39:54  dischi
# check for updated mmpython
#
# Revision 1.29  2004/03/13 22:36:16  dischi
# do not remove num_ infos we already have
#
# Revision 1.28  2004/02/27 20:41:38  dischi
# better rebuild
#
# Revision 1.27  2004/02/27 20:27:45  dischi
# increase cache version
#
# Revision 1.26  2004/02/27 20:15:02  dischi
# more unicode fixes
#
# Revision 1.25  2004/02/14 19:31:31  dischi
# also cache playlist dir
#
# Revision 1.23  2004/02/12 12:22:03  dischi
# update cache to new directory metainfo
#
# Revision 1.22  2004/02/09 20:14:40  dischi
# add xmltv
#
# Revision 1.21  2004/02/08 17:41:55  dischi
# add more caching:
# o playlist metainfo
# o directory metainfo (e.g. number of items)
# cleanup
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

import util.mediainfo
import plugin
import directory
import playlist
import fxditem

# use this number to keep track of changes in
# this helper. Check this against util/mediainfo
VERSION = 3

def delete_old_files_1():
    """
    delete old files from previous versions of freevo which are not
    needed anymore
    """
    print 'deleting old cache files from older freevo version....',
    sys.__stdout__.flush()
    del_list = []

    for name in ('image-viewer-thumb.jpg', 'thumbnails', 'audio', 'mmpython', 'disc'):
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
            for metafile in ('cover.png', 'cover.png.raw', 'cover.jpg', 'cover.jpg.raw',
                             'mmpython.cache', 'freevo.cache'):
                if os.path.isfile(os.path.join(file, metafile)):
                    os.unlink(os.path.join(file, metafile))
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
    if rebuild:
        print 'deleting cache files..................................',
        sys.__stdout__.flush()
        for f in util.recursefolders(config.OVERLAY_DIR,1,'mmpython.cache',1):
            os.unlink(f)
        if rebuild == 2:
            for f in util.match_files(config.OVERLAY_DIR + '/disc/metadata', ['mmpython']):
                os.unlink(f)
        print 'done'

    all_dirs = []
    print 'checking mmpython cache files.........................',
    sys.__stdout__.flush()
    for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
        if os.path.isdir(d[1]):
            all_dirs.append(d[1])
    util.mediainfo.cache_recursive(all_dirs, verbose=True)
    

def cache_thumbnails():
    """
    cache all image files by creating thumbnails
    """
    import cStringIO
    import stat
    
    print 'checking thumbnails...................................',
    sys.__stdout__.flush()

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

        for bad_dir in ('.xvpics', '.thumbnails', '.pics'):
            if filename.find('/' + bad_dir + '/') > 0:
                try:
                    files.remove(filename)
                except:
                    pass
                
    print '%s file(s)' % len(files)
        
    for filename in files:
        fname = filename
        if len(fname) > 65:
            fname = fname[:20] + ' [...] ' + fname[-40:]
        print '  %4d/%-4d %s' % (files.index(filename)+1, len(files), fname)

        util.cache_image(filename)

    if files:
        print

    
def create_metadata():
    """
    scan files and create metadata
    """
    import util.extendedmeta
    print 'creating audio metadata...............................',
    sys.__stdout__.flush()
    for dir in config.AUDIO_ITEMS:
        if os.path.isdir(dir[1]):
            util.extendedmeta.AudioParser(dir[1], rescan=True)
    print 'done'

    print 'creating playlist metadata............................',
    sys.__stdout__.flush()
    pl  = []
    fxd = []
    for dir in config.AUDIO_ITEMS:
        if os.path.isdir(dir[1]):
            pl  += util.match_files_recursively(dir[1], playlist.mimetype.suffix())
            fxd += util.match_files_recursively(dir[1], fxditem.mimetype.suffix())
        elif isinstance(dir, list) or isinstance(dir, tuple):
            print
            print 'bad path: %s   ' % dir[1] ,
            sys.__stdout__.flush()
        elif util.match_suffix(dir, playlist.mimetype.suffix()):
            pl.append(dir)
        elif util.match_suffix(dir, fxditem.mimetype.suffix()):
            fxd.append(dir)
        elif util.match_suffix(dir[1], playlist.mimetype.suffix()):
            pl.append(dir[1])
        elif util.match_suffix(dir[1], fxditem.mimetype.suffix()):
            fxd.append(dir[1])

    
    items = playlist.mimetype.get(None, util.misc.unique(pl))

    # ignore fxd files for now, they can't store metainfo
    # for f in fxditem.mimetype.get(None, util.misc.unique(fxd)):
    #     if f.type == 'playlist':
    #         items.append(f)

    for i in items:
        util.extendedmeta.PlaylistParser(i)
    print 'done'

    print 'checking database.....................................',
    sys.__stdout__.flush()
    try:
        # The DB stuff
        import sqlite

        for dir in config.AUDIO_ITEMS:
            if os.path.isdir(dir[1]):
                util.extendedmeta.addPathDB(dir[1], dir[0], verbose=False)
        print 'done'
    except ImportError:
        print 'skipping'
        pass


    print 'creating directory metadata...........................',
    sys.__stdout__.flush()

    subdirs = { 'all': [] }

    # get all subdirs for each type
    for type in activate_plugins:
        subdirs[type] = []
        for d in getattr(config, '%s_ITEMS' % type.upper()):
            try:
                d = d[1]
            except:
                pass
            if not os.path.isdir(d):
                continue
            rec = util.get_subdirs_recursively(d)
            subdirs['all'] += rec
            subdirs[type]  += rec
                
    subdirs['all'] = util.misc.unique(subdirs['all'])
    subdirs['all'].sort(lambda l, o: cmp(l.upper(), o.upper()))

    # walk though each directory
    for s in subdirs['all']:
        if s.find('/.') > 0:
            continue

        # create the DirItems
        d = directory.DirItem(s, None)

        # rebuild metainfo
        d.create_metainfo()
        for type in activate_plugins:
            if subdirs.has_key(type) and s in subdirs[type]:
                d.display_type = type
                # scan again with display_type
                d.create_metainfo()

    print 'done'



def create_tv_pickle():
    print 'caching xmltv database................................',
    sys.__stdout__.flush()

    import tv.epg_xmltv
    tv.epg_xmltv.get_guide(verbose=False)
    print 'done'
    
    
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


    print 'Freevo cache'
    print
    print 'Freevo will now generate a metadata cache for all your files and'
    print 'create thumbnails from images for faster access.'
    print

    # check for current cache informations
    if (len(sys.argv)>1 and sys.argv[1] == '--rebuild'):
        rebuild = 1
    else:
        rebuild = 0
    try:
        import mmpython.version

        info = None
        cachefile = os.path.join(config.FREEVO_CACHEDIR, 'mediainfo')
        if os.path.isfile(cachefile):
            info = util.read_pickle(cachefile)
        if not info:
            print
            print 'Unable to detect last complete rebuild, forcing rebuild'
            rebuild = 2
            complete_update = int(time.time())
        else:
            if len(info) == 3:
                mmchanged, part_update, complete_update = info
                freevo_changed = 0
            else:
                mmchanged, freevo_changed, part_update, complete_update = info

            # let's warn about some updates
            if freevo_changed < VERSION or mmpython.version.CHANGED > mmchanged:
                print 'Cache too old, forcing rebuild'
                rebuild = 2
                complete_update = int(time.time())
                
    except ImportError:
        print
        print 'Error: unable to read mmpython version information'
        print 'Please update mmpython to the latest release or if you use'
        print 'Freevo CVS versions, please also use mmpython CVS.'
        print
        print 'Some functions in Freevo may not work or even crash!'
        print
        print

    start = time.clock()
    
    activate_plugins = []
    for type in ('video', 'audio', 'image', 'games'):
        if plugin.is_active(type):
            # activate all mimetype plugins
            plugin.init_special_plugin(type)
            activate_plugins.append(type)
            
    for type in 'VIDEO', 'AUDIO', 'IMAGE':
        for d in copy.copy(getattr(config, '%s_ITEMS' % type)):
            if not isstring(d):
                d = d[1]
            if d == '/':
                print 'ERROR: %s_ITEMS contains root directory, skipped.' % type
                setattr(config, '%s_ITEMS' % type, [])

    if os.path.isdir('%s/playlists' % config.FREEVO_CACHEDIR):
        config.AUDIO_ITEMS.append(('Playlists', '%s/playlists' % config.FREEVO_CACHEDIR))
    delete_old_files_1()
    delete_old_files_2()

    # we have time here, don't use exif thumbnails
    config.IMAGE_USE_EXIF_THUMBNAIL = 0
    
    cache_directories(rebuild)
    cache_thumbnails()
    create_metadata()
    create_tv_pickle()
    
# close db
util.mediainfo.sync()

# save cache info
try:
    import mmpython.version
    util.save_pickle((mmpython.version.CHANGED, VERSION,
                      int(time.time()), complete_update), cachefile)
except ImportError:
    print 'WARNING: please update mmpython'

print
print 'caching complete after %s seconds' % (time.clock() - start)
