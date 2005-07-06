# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# cache.py - caching helper for faster mediadb usage
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

# python imports
import os
import sys
import time
import copy

import kaa.metadata.version
import kaa.thumb

# freevo imports
import config
import util
import mediadb
import util.thumbnail as thumbnail
import util.videothumb
import util.fileops as fileops

# use this number to keep track of changes in this helper
VERSION = 4

class ProgressBox(object):
    def __init__(self, msg, max):
        self.msg = msg
        self.max = max
        self.pos = 0
        print '\r%-70s   0%%' % msg,
        sys.__stdout__.flush()
        
    def callback(self):
        self.pos += 1
        progress = '%3d%%' % (self.pos * 100 / self.max)
        print '\r%-70s %s' % (self.msg, progress),
        sys.__stdout__.flush()


def cache_directories(directories):
    """
    cache all directories
    """
    print 'checking database files...............................',
    sys.__stdout__.flush()
    listings = []
    for d in directories:
        if d.num_changes:
            listings.append(d)
    print '%s changes' % len(listings)
    
    # cache all dirs
    for l in listings:
        name = l.dirname
        if len(name) > 55:
            name = name[:15] + ' [...] ' + name[-35:]
        msg = ProgressBox('  %4d/%-4d %s' % (listings.index(l) + 1,
                                             len(listings), name),
                          l.num_changes)
        l.update(msg.callback)
        l.cache.save()
        print


def get_directory_listings(dirlist, msg):
    """
    Get a list of Listings recursive of all given directories.
    """
    subdirs  = []
    listings = []
    for dir in dirlist:
        progress = '%3d%%' % (dirlist.index(dir) * 100 / len(dirlist))
        print '\r%s %s' % (msg, progress),
        sys.__stdout__.flush()
        for dirname in fileops.get_subdirs_recursively(dir):
            if not dirname in subdirs:
                subdirs.append(dirname)
                listings.append(mediadb.Listing(dirname))
        if not dir in subdirs:
            subdirs.append(dir)
            listings.append(mediadb.Listing(dir))
    return listings


def delete_old_files_1():
    """
    delete old files from previous versions of freevo which are not
    needed anymore
    """
    print 'deleting old cache files from older freevo version....',
    sys.__stdout__.flush()
    del_list = []

    for name in ('image-viewer-thumb.jpg', 'thumbnails', 'audio', 'mmpython',
                 'disc'):
        if os.path.exists(os.path.join(config.FREEVO_CACHEDIR, name)):
            del_list.append(os.path.join(config.FREEVO_CACHEDIR, name))
    del_list += util.match_files(config.OVERLAY_DIR+'/disc',
                                 ['mmpython', 'freevo'])

    for file in util.match_files_recursively(config.OVERLAY_DIR, ['raw']):
        if not file.endswith('.fxd.raw'):
            del_list.append(file)

    for file in util.match_files_recursively(config.OVERLAY_DIR,
                                             config.IMAGE_SUFFIX):
        if file.find('.thumb.') > 0:
            del_list.append(file)

    for db in ('freevo.cache', 'freevo.db', 'mmpython.cache', '*.raw.tmp',
               '*.raw-[0-9][0-9][0-9]x[0-9][0-9][0-9]', '*.fvt.png',
               'mmpython'):
        del_list += util.recursefolders(config.OVERLAY_DIR,1,db,1)
    
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
        if file.startswith(config.OVERLAY_DIR + '/disc/'):
            continue
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
            for metafile in ('cover.png', 'cover.jpg'):
                if os.path.isfile(os.path.join(file, metafile)):
                    os.unlink(os.path.join(file, metafile))
        if not os.listdir(file):
            os.rmdir(file)
    print 'done'
    

def cache_thumbnails(directories):
    """
    cache all image files by creating thumbnails
    """
    import cStringIO
    import stat
    
    print 'checking thumbnails...................................',
    sys.__stdout__.flush()

    files = []
    for d in directories:
        files += util.match_files_recursively(d, config.IMAGE_SUFFIX)

    files = util.misc.unique(files)
    for filename in copy.copy(files):
        if thumbnail.get_name(filename)[0] in \
               (kaa.thumb.LARGE, kaa.thumb.FAILED):
            files.remove(filename)
        else:
            for bad_dir in ('.xvpics', '.thumbnails', '.pics'):
                if filename.find('/' + bad_dir + '/') > 0:
                    files.remove(filename)

    
    print '%s file(s)' % len(files)
    files.sort(lambda l, o: cmp(l, o))
        
    for filename in files:
        fname = filename
        if len(fname) > 65:
            fname = fname[:20] + ' [...] ' + fname[-40:]
        print '  %4d/%-4d %s' % (files.index(filename)+1, len(files), fname)
        thumbnail.create(filename)

    if files:
        print

    

os.umask(config.UMASK)
if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'freevo cache helper to delete unused cache entries and to'
    print 'cache all files in your data directories.'
    print
    print 'usage "freevo cache [--rebuild]"'
    print 'If the --rebuild option is given, Freevo will delete the cache'
    print 'first to rebuild the cache from start. Caches from discs won\'t be'
    print 'affected'
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
    if sys.argv[2] == '--recursive':
        dirname = os.path.abspath(sys.argv[3])
        files = util.match_files_recursively(dirname, config.VIDEO_SUFFIX)
    elif os.path.isdir(sys.argv[2]):
        dirname = os.path.abspath(sys.argv[2])
        files = util.match_files(dirname, config.VIDEO_SUFFIX)
    else:
        files = [ os.path.abspath(sys.argv[2]) ]
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

info = None
cachefile = os.path.join(config.FREEVO_CACHEDIR, 'mediainfo')
if os.path.isfile(cachefile):
    info = util.cache.load(cachefile)
if not info:
    print
    print 'Unable to detect last complete rebuild, forcing rebuild'
    rebuild = 1
    complete_update = int(time.time())
else:
    if len(info) == 3:
        mmchanged, part_update, complete_update = info
        freevo_changed = 0
    else:
        mmchanged, freevo_changed, part_update, complete_update = info

    # let's warn about some updates
    if freevo_changed < VERSION or \
           kaa.metadata.version.CHANGED > mmchanged:
        print 'Cache too old, forcing rebuild'
        rebuild = 1
        complete_update = int(time.time())


start = time.clock()

delete_old_files_1()
delete_old_files_2()

directories = []
for d in config.VIDEO_ITEMS + config.AUDIO_ITEMS + config.IMAGE_ITEMS:
    if os.path.isdir(d[1]) and d[1] != '/':
        directories.append(d[1])

if rebuild:
    print 'deleting cache files..................................',
    sys.__stdout__.flush()
    for d in directories:
        for f in util.match_files_recursively(vfs.getoverlay(d), ['db']):
            if f.endswith('/freevo.db'):
                os.unlink(f)
    print 'done'

msg = 'scanning directory structure..........................'
print msg,
sys.__stdout__.flush()
listings = get_directory_listings(directories, msg)
print '\r%s done' % msg

cache_thumbnails(directories)
cache_directories(listings)

l = mediadb.FileListing(directories)
if l.num_changes:
    l.update()

mediadb.cache(l)
mediadb.save()

# save cache info
util.cache.save(cachefile, (kaa.metadata.version.CHANGED, VERSION,
                            int(time.time()), complete_update))

print
print 'caching complete after %s seconds' % (time.clock() - start)
