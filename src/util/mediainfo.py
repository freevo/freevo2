#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/mediainfo.py - media info storage/parsing
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.46  2004/05/31 15:58:26  dischi
# do not cache bad info
#
# Revision 1.45  2004/05/28 15:53:46  dischi
# add chapters support
#
# Revision 1.44  2004/05/20 15:53:49  dischi
# prevent a crash
#
# Revision 1.43  2004/05/02 11:46:13  dischi
# make it possible to turn off image caching
#
# Revision 1.42  2004/04/11 08:39:54  dischi
# warn about old cache
#
# Revision 1.41  2004/03/28 03:14:53  krister
# oops
#
# Revision 1.40  2004/03/28 02:46:00  krister
# Fixed a typo
#
# Revision 1.39  2004/03/27 17:44:39  krister
# Fixed divide by zero bug.
#
# Revision 1.38  2004/03/22 11:04:51  dischi
# improve caching
#
# Revision 1.37  2004/03/21 09:39:54  dischi
# check for updated mmpython
#
# Revision 1.36  2004/03/13 23:44:02  dischi
# audio stream selection fixes
#
# Revision 1.35  2004/02/28 21:04:17  dischi
# unicode fixes
#
# Revision 1.34  2004/02/27 20:42:05  dischi
# save disc file info
#
# Revision 1.33  2004/02/27 20:27:18  dischi
# add number of files to rom drives
#
# Revision 1.32  2004/02/27 20:15:03  dischi
# more unicode fixes
#
# Revision 1.31  2004/02/23 19:27:07  dischi
# fix mmpython init
#
# Revision 1.30  2004/02/16 20:36:42  dischi
# fix crash
#
# Revision 1.29  2004/02/15 15:30:52  dischi
# improved item with track storage
#
# Revision 1.28  2004/02/14 13:05:04  dischi
# do not call skin.get_singleton() anymore
#
# Revision 1.27  2004/02/13 20:26:39  dischi
# small bugfix
#
# Revision 1.26  2004/02/13 19:42:44  dischi
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


import os, stat
import sys
import copy

import mmpython
from mmpython.disc.discinfo import cdrom_disc_id

import config
import util

class FileOutdatedException(Exception):
    pass


class Cache:
    """
    Class to cache objects
    """
    def __init__(self, filename):
        self.filename = filename
        
        self.current_objects    = {}
        self.current_cachefile  = None
        self.current_cachedir   = None
        self.cache_modified     = False
        self.uncachable_keys    = {}

        # file database
        self.all_directories  = {}
                

    def __get_filename__(self, dirname):
        """
        return the cache filename for that directory/device
        """
        cachefile = vfs.getoverlay(dirname)
        if not os.path.exists(cachefile):
            os.makedirs(cachefile)
        return os.path.join(cachefile, self.filename)
            

    def __need_update__(self, dirname):
        """
        check if the cache needs an update
        """
        cachefile = self.__get_filename__(dirname)
        if os.path.isfile(cachefile) and \
               os.stat(cachefile)[stat.ST_MTIME] > os.stat(dirname)[stat.ST_MTIME]:
            return 0
        return 1
    
        
    def save_cache(self):
        """
        save a modified cache file
        """
        if self.cache_modified:
            _debug_('save cache %s' % self.current_cachefile, 2)
            util.save_pickle(self.current_objects, self.current_cachefile)
            self.cache_modified = False
            if config.MEDIAINFO_USE_MEMORY:
                self.all_directories[self.current_cachefile] = self.current_objects


    def load_cache(self, dirname):
        """
        load a new cachefile
        """
        if dirname == self.current_cachedir:
            return

        if self.cache_modified:
            self.save_cache()
            
        cachefile = self.__get_filename__(dirname)
        _debug_('load cache %s' % cachefile, 2)

        if config.MEDIAINFO_USE_MEMORY and self.all_directories.has_key(cachefile):
            self.current_objects = self.all_directories[cachefile]
        else:
            if os.path.isfile(cachefile):
                self.current_objects = util.read_pickle(cachefile)
            else:
                self.current_objects = {}
            if config.MEDIAINFO_USE_MEMORY:
                self.all_directories[cachefile] = self.current_objects
            
        self.current_cachefile = cachefile
        self.current_cachedir  = dirname
        self.cache_modified    = False

        
    def check_cache(self, directory):
        """
        Return how many files in this directory are not in the cache. It's
        possible to guess how much time the update will need.
        """
        if not self.__need_update__(directory):
            return 0
        
        new = 0
        for filename in os.listdir(directory):
            fullname  = os.path.join(directory, filename)
            try:
                info = self.find(filename, directory, fullname)
            except (KeyError, FileOutdatedException):
                new += 1
            except (OSError, IOError):
                pass
        return new
    
        

    def cache_dir(self, directory, callback):
        """
        cache every file in the directory for future use
        """
        if not self.__need_update__(directory):
            return 0

        self.load_cache(directory)
        
        objects = {}
        for filename in os.listdir(directory):
            try:
                key       = filename
                fullname  = os.path.join(directory, filename)
                timestamp = os.stat(fullname)[stat.ST_MTIME]

                info = self.find(filename, directory, fullname)
            except KeyError:
                info = self.create(fullname)
                if callback:
                    callback()
            except FileOutdatedException:
                info = self.find(filename, directory, fullname, update_check=False)
                info = self.update(fullname, info)
                if callback:
                    callback()
            except (IOError, OSError):
                try:
                    timestamp
                except:
                    timestamp = 0
                info = {}
            
            objects[key] = (info, timestamp)

        self.current_objects   = objects
        self.cache_modified    = True
        self.save_cache()
        return objects


    def set(self, filename, dirname, fullname, info):
        """
        set a variable
        """
        if dirname != self.current_cachedir:
            self.load_cache(dirname)
        try:
            self.current_objects[filename] = (info, os.stat(fullname)[stat.ST_MTIME])
            self.cache_modified = True
        except OSError:
            # key, the file is gone now
            pass
        
        
    def get(self, filename, create=True):
        """
        get info about a file
        """
        fullname  = filename

        # we know this are absolute paths, so we speed up
        # by not using the os.path functions.
        dirname  = filename[:filename.rfind('/')]
        filename = filename[filename.rfind('/')+1:]

        if dirname != self.current_cachedir:
            self.load_cache(dirname)

        if create:
            try:
                obj, t = self.current_objects[filename]
                if not self.update_needed(fullname, t):
                    return obj
                else:
                    info = self.update(fullname, obj)
            except KeyError:
                info = self.create(fullname)
            except (IOError, OSError):
                return {}
            self.set(filename, dirname, fullname, info)
            return info

        try:
            return self.current_objects[filename][0]
        except:
            return {}
            

    def find(self, filename, dirname, fullname, update_check=True):
        """
        Search the cache for informations about that file. The functions
        returns that information. Because the information can be 'None',
        the function raises a KeyError if the cache has
        no or out-dated informations.
        """
        if dirname != self.current_cachedir:
            self.load_cache(dirname)

        obj, t = self.current_objects[filename]
        if update_check:
            if self.update_needed(fullname, t):
                raise FileOutdatedException
        return obj



# ======================================================================


class MMCache(Cache):
    """
    cache for mmpython informations
    """
    def __init__(self):
        Cache.__init__(self, 'mmpython.cache')
        self.uncachable_keys = [ 'thumbnail', 'url' ]


    def simplify(self, object):
        """
        mmpython has huge objects to cache, we don't need them.
        This function simplifies them to be only string, intger, dict or
        list of one of those above. This makes the caching much faster
        """
        ret = {}
        for k in object.keys:
            if not k in self.uncachable_keys and getattr(object,k) != None:
                value = getattr(object,k)
                if isstring(value):
                    value = Unicode(value.replace('\0', '').lstrip().rstrip())
                if value:
                    ret[k] = value

        for k in  ( 'video', 'audio'):
            # if it's an AVCORE object, also simplify video and audio
            # lists to string and it
            if hasattr(object, k) and getattr(object, k):
                ret[k] = []
                for o in getattr(object, k):
                    ret[k].append(self.simplify(o))

        for k in ('subtitles', 'chapters', 'mime', 'id', 'tracks' ):
            if hasattr(object, k) and getattr(object, k):
                ret[k] = getattr(object, k)

        return ret

    
    def create(self, filename):
        """
        create mmpython information about the given file
        """
        info = mmpython.Factory().create(filename)
        if info:
            thumbnail = None
            if info.has_key('thumbnail'):
                thumbnail = info.thumbnail
                
            info = self.simplify(info)
            name = util.getname(filename)
            if name == name.upper() and info.has_key('type') and \
                   info['type'] in ('DVD', 'VCD'):
                name = util.getname(filename.lower())
            info['title:filename'] = name

            if info.has_key('video'):
                for video in info['video']:
                    for variable in ('width', 'height', 'length', 'aspect'):
                        if video.has_key(variable) and not \
                           (info.has_key(variable) and info[variable]):
                            info[variable] = video[variable]

            if thumbnail and config.IMAGE_USE_EXIF_THUMBNAIL and config.CACHE_IMAGES:
                util.cache_image(filename, thumbnail)
            elif config.CACHE_IMAGES and info.has_key('mime') and info['mime'] and \
                     info['mime'].startswith('image'):
                util.cache_image(filename)

            return info
        return {}


    def update_needed(self, filename, timestamp):
        """
        return true if the information needs an update
        """
        return timestamp < os.stat(filename)[stat.ST_MTIME]

        
    def update(self, filename, info):
        """
        update mmpython cache information
        """
        return self.create(filename)


# ======================================================================


class MetaCache(Cache):
    """
    cache for other freevo metadata
    """
    def __init__(self):
        Cache.__init__(self, 'freevo.cache')

    def save_cache(self):
        """
        Save a modified cache file. This version removed all entries having
        no informations and removes to cachefile if no object has informations
        anymore. This speeds up searching.
        """
        for key in copy.copy(self.current_objects):
            # delete all empty objects
            if not self.current_objects[key][0]:
                del self.current_objects[key]
                self.cache_modified = True
        if not self.current_objects:
            # delete cache file is no object has any infos
            if self.current_cachefile and os.path.isfile(self.current_cachefile):
                os.unlink(self.current_cachefile)
            self.cache_modified = False
            if config.MEDIAINFO_USE_MEMORY:
                self.all_directories[self.current_cachefile] = self.current_objects
            return
        # call save_file from 'Cache'
        Cache.save_cache(self)

    def create(self, filename):
        return {}

    def update_needed(self, filename, timestamp):
        return False
        
    def update(self, filename, info):
        return info


# ======================================================================

# info values in metacache that should not be returned
bad_info = [ '__various__', ]

# the two cache objects
mmpython_cache  = MMCache()
meta_cache      = MetaCache()

# ======================================================================

class Info:
    """
    Container for all kind of informations. This information includes
    mmpython parsed information and some user stored stuff.
    """
    def __init__(self, filename, mmdata, metadata):
        self.filename  = filename
        self.disc      = False
        self.variables = {}
        if mmdata:
            self.mmdata    = mmdata
        else:
            self.mmdata    = {}
        if metadata:
            self.metadata  = metadata
        else:
            self.metadata  = {}
        self.dicts     = ( self.mmdata, self.variables, self.metadata )

        
    def __getitem__(self, key):
        """
        get the value of 'key'
        """
        result = ''
        for var in self.dicts:
            if var and var.has_key(key):
                val = var[key]
                if not var == self.metadata or not val in bad_info:
                    result = val
                if result != None and result != '':
                    return result
        return result

        
    def __setitem__(self, key, val):
        """
        set the value of 'key' to 'val'
        """
        self.variables[key] = val


    def has_key(self, key):
        """
        check if the object has a key 'key'
        """
        for var in self.dicts:
            if var and var.has_key(key):
                return True
        return False


    def store(self, key, value):
        """
        store the key/value in metadata and save the cache
        """
        self.metadata[key] = value
        if self.disc:
            self.metadata[key] = value
            util.save_pickle(self.metadata, self.filename)
            return True
        elif not self.filename:
            return False
        else:
            meta_cache.set(os.path.basename(self.filename), os.path.dirname(self.filename),
                           self.filename, self.metadata)
            return True
        

    def delete(self, key):
        """
        delete the key in metadata and save the cache
        """
        if self.disc:
            if self.metadata.has_key(key):
                del self.metadata[key]
                util.save_pickle(self.metadata, self.filename)
            return True
        elif not self.filename:
            return False
        if self.metadata.has_key(key):
            del self.metadata[key]
            meta_cache.set(os.path.basename(self.filename), os.path.dirname(self.filename),
                           self.filename, self.metadata)
            return True

        
    def set_variables(self, variables):
        """
        set personal user variables (not to storage) to 'variables'
        """
        self.variables = variables
        self.dicts     = ( self.mmdata, self.variables, self.metadata )
        

    def get_variables(self):
        """
        return the personal variables
        """
        return self.variables

    

# ======================================================================
# Interface to the rest of Freevo
# ======================================================================

def check_cache(dirname):
    """
    check the cache how many files need an update
    """
    return mmpython_cache.check_cache(dirname)
        
    
def cache_dir(dirname, callback=None):
    """
    cache the complete directory
    """
    mmpython_cache.cache_dir(dirname, callback)


class CacheStatus:
    def __init__(self, num_changes, txt):
        self.num_changes = num_changes
        self.txt         = txt
        self.pos         = 0
        self.callback()
        
    def callback(self):
        if self.num_changes != 0:
            progress = '%3d%%' % (self.pos * 100 / self.num_changes)
        else:
            progress = '??%%'
        print '\r%-70s %s' % (self.txt, progress),
        sys.__stdout__.flush()
        self.pos += 1


def cache_recursive(dirlist, verbose=False):
    """
    cache a list of directories recursive
    """
    all_dirs = []

    # create a list of all subdirs
    for dir in dirlist:
        for dirname in util.get_subdirs_recursively(dir):
            if not dirname in all_dirs and not \
                   os.path.basename(dirname) in ('.xvpics', '.thumbnails', 'CVS'):
                all_dirs.append(dirname)
        if not dir in all_dirs:
            all_dirs.append(dir)

    # if verbose, remove all dirs that need no caching
    if verbose:
        for d in copy.copy(all_dirs):
            if not check_cache(d):
                all_dirs.remove(d)

    print '%s changes' % len(all_dirs)

    # cache all dirs
    for d in all_dirs:
        if verbose:
            dname = d
            if len(dname) > 55:
                dname = dname[:15] + ' [...] ' + dname[-35:]
            cache_status = CacheStatus(check_cache(d), '  %4d/%-4d %s' % \
                                       (all_dirs.index(d)+1, len(all_dirs), dname))
            cache_dir(d, cache_status.callback)
            print
        else:
            cache_dir(d)
    if all_dirs:
        print

        
def disc_info(media):
    """
    return mmpython disc information for the media
    """
    type, id  = cdrom_disc_id(media.devicename)
    if not id:
        # bad disc, e.g. blank disc
        return {}
    
    cachedir  = os.path.join(config.OVERLAY_DIR, 'disc/metadata')
    cachefile = os.path.join(cachedir, id + '.mmpython')
    
    if os.path.isfile(cachefile):
        mmdata = util.read_pickle(cachefile)
    else:
        mmdata = mmpython.parse(media.devicename)
        if not mmdata:
            print '*****************************************'
            print 'Error detecting the disc'
            print 'Please contact the developers'
            print '*****************************************'
        else:
            util.save_pickle(mmdata, cachefile)

    cachefile = os.path.join(cachedir, id + '.freevo')

    if os.path.isfile(cachefile):
        metainfo = util.read_pickle(cachefile)
    else:
        metainfo = {}

    if mmdata.mime == 'unknown/unknown' and not metainfo.has_key('disc_num_video'):
        media.mount()
        for type in ('video', 'audio', 'image'):
            items = getattr(config, '%s_SUFFIX' % type.upper())
            files = util.match_files_recursively(media.mountdir, items)
            metainfo['disc_num_%s' % type] = len(files)
        media.umount()
        util.save_pickle(metainfo, cachefile)
        
    info = Info(cachefile, mmdata, metainfo)
    info.disc = True
    return info

    
def get(filename):
    """
    return an Info object with all the informations Freevo has about
    the filename
    """
    return Info(filename, mmpython_cache.get(filename),
                meta_cache.get(filename, create=False))

        
def get_dir(dirname):
    """
    return an Info object with all the informations Freevo has about
    the directory
    """
    return Info(dirname, {}, meta_cache.get(dirname, create=False))

        
def set(filename, key, value):
    """
    set a variable (key) in the meta_cache to value and saves the cache
    """
    info      = meta_cache.get(filename)
    info[key] = value
    fullname  = filename
    dirname   = os.path.dirname(filename)
    filename  = os.path.basename(filename)
    meta_cache.set(filename, dirname, fullname, info)


def sync():
    """
    sync database to disc (force writing)
    """
    mmpython_cache.save_cache()
    meta_cache.save_cache()
    

def load_cache(dirname):
    """
    load the cache for dirname
    """
    mmpython_cache.load_cache(dirname)
    meta_cache.load_cache(dirname)
    



#
# setup mmpython
#

if config.DEBUG > 2:
    mmpython.mediainfo.DEBUG = config.DEBUG
    mmpython.factory.DEBUG   = config.DEBUG
else:
    mmpython.mediainfo.DEBUG = 0
    mmpython.factory.DEBUG   = 0

mmpython.USE_NETWORK = config.USE_NETWORK
mmpython.disc.discinfo.CREATE_MD5_ID = config.MMPYTHON_CREATE_MD5_ID



# some checking when starting Freevo
if __freevo_app__ == 'main':
    try:
        import mmpython.version
        import time
        
        cachefile = os.path.join(config.FREEVO_CACHEDIR, 'mediainfo')
        info = util.read_pickle(cachefile)
        if not info:
            print
            print 'Error: can\'t detect last cache rebuild'
            print 'Please run \'freevo cache\''
            print
        else:
            if len(info) == 3:
                mmchanged, part_update, complete_update = info
                freevo_changed = 0
            else:
                mmchanged, freevo_changed, part_update, complete_update = info
            # let's warn about some updates
            if freevo_changed < 3:
                print
                print 'Warning: Freevo cache helper/informations updated.'
                print 'Please rerun \'freevo cache\' to speed up Freevo'
                print
            elif mmpython.version.CHANGED > mmchanged:
                print
                print 'Warning: mmpython as changed.'
                print 'Please rerun \'freevo cache\' to get the latest updates'
                print
            elif (int(time.time()) - part_update) / (3600 * 24) > 7:
                print
                print 'Warning: cache is older than 7 days'
                print 'Running \'freevo cache\' is recommended.'
                print
    except:
        print
        print 'Error: unable to read mmpython version information'
        print 'Please update mmpython to the latest release or if you use'
        print 'Freevo CVS versions, please also use mmpython CVS.'
        print
        print 'Some functions in Freevo may not work or even crash!'
        print
        print
