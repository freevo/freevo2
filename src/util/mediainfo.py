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
# Revision 1.2  2004/01/17 21:19:56  dischi
# small bugfix
#
# Revision 1.1  2004/01/17 20:27:45  dischi
# new file to handle meta information
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


import os, stat
import copy

import mmpython
from mmpython.disc.discinfo import cdrom_disc_id

import config
import util


class FileNotFoundException(Exception):
    pass

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


    def __get_filename__(self, dirname):
        """
        return the cache filename for that directory/device
        """
        cachefile = vfs.getoverlay(os.path.join(dirname, self.filename))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return cachefile
            

    def save_cache(self,store_empty=True):
        """
        save a modified cache file
        """
        print 'save %s' % self.current_cachefile
        if not store_empty:
            for key in copy.copy(self.current_objects):
                if not self.current_objects[key][0]:
                    del self.current_objects[key]
            if not self.current_objects:
                if os.path.isfile(self.current_cachefile):
                    os.unlink(self.current_cachefile)
                return
        util.save_pickle(self.current_objects, self.current_cachefile)
        self.cache_modified    = False


    def load_cache(self, dirname):
        """
        load a new cachefile
        """
        if dirname == self.current_cachedir:
            return

        if self.cache_modified:
            print 'mod'
            self.save_cache()
            
        cachefile = self.__get_filename__(dirname)
        if os.path.isfile(cachefile):
            self.current_objects = util.read_pickle(cachefile)
        else:
            self.current_objects = {}
            
        self.current_cachefile = cachefile
        self.current_cachedir  = dirname
        self.cache_modified    = False

        
    def check_cache(self, directory):
        """
        Return how many files in this directory are not in the cache. It's
        possible to guess how much time the update will need.
        """
        cachefile = self.__get_filename__(directory)
        if os.path.isfile(cachefile) and \
               os.stat(cachefile)[stat.ST_MTIME] > os.stat(directory)[stat.ST_MTIME]:
            return 0
        
        new = 0
        for filename in os.listdir(directory):
            fullname  = os.path.join(directory, filename)
            try:
                info = self.find(filename, directory, fullname)
            except (FileNotFoundException, FileOutdatedException):
                new += 1
            except (OSError, IOError):
                pass
        return new
    
        

    def cache_dir(self, directory, callback):
        """
        cache every file in the directory for future use
        """
        cachefile = self.__get_filename__(directory)

        if os.path.isfile(cachefile) and \
               os.stat(cachefile)[stat.ST_MTIME] > os.stat(directory)[stat.ST_MTIME]:
            return

        objects = {}
        for filename in os.listdir(directory):
            fullname  = os.path.join(directory, filename)
            timestamp = os.stat(fullname)[stat.ST_MTIME]
            key       = filename

            try:
                info = self.find(filename, directory, fullname)
            except FileNotFoundException:
                info = self.create(fullname)
                if callback:
                    callback()
            except FileOutdatedException:
                info = self.find(filename, directory, fullname, update_check=False)
                info = self.update(fullname, info)
                if callback:
                    callback()
            except (IOError, OSError):
                pass
            
            if info:
                for k in self.uncachable_keys:
                    if info.has_key(k):
                        del info[k]
                if hasattr(info, '_tables'):
                    del info._tables
            objects[key] = (info, timestamp)

        self.current_objects   = objects
        self.current_cachefile = cachefile
        self.current_cachedir  = directory
        self.cache_modified    = False
        print 's'
        self.save_cache()
        return objects


    def set(self, filename, dirname, fullname, info):
        """
        set a variable
        """
        if dirname != self.current_cachedir:
            self.load_cache(dirname)
        self.current_objects[filename] = (info, os.stat(fullname)[stat.ST_MTIME])
        print 'set: %s' % filename
        print self.current_cachefile
        self.cache_modified = True
        
        
    def get(self, filename, create=True):
        """
        get info about a file
        """
        fullname  = filename
        dirname   = os.path.dirname(filename)
        filename  = os.path.basename(filename)
        if create:
            try:
                return self.find(filename, dirname, fullname)
            except FileNotFoundException:
                info = self.create(fullname)
            except FileOutdatedException:
                info = self.find(filename, dirname, fullname, update_check=False)
                info = self.update(fullname, info)
            except (IOError, OSError):
                return None
            print 'do %s' % filename
            self.set(filename, dirname, fullname, info)
            return info
        try:
            return self.find(filename, dirname, fullname)
        except:
            return {}
            

    def find(self, filename, dirname, fullname, update_check=True):
        """
        Search the cache for informations about that file. The functions
        returns that information. Because the information can be 'None',
        the function raises a FileNotFoundException if the cache has
        no or out-dated informations.
        """
        key = filename
        if dirname != self.current_cachedir:
            self.load_cache(dirname)

        if self.current_objects.has_key(key):
            obj, t = self.current_objects[key]
            if update_check:
                if self.update_needed(fullname, t):
                    raise FileOutdatedException
            return obj
        else:
            raise FileNotFoundException


class MMCache(Cache):
    """
    cache for mmpython informations
    """
    def __init__(self):
        Cache.__init__(self, 'mmpython.cache')
        self.uncachable_keys = [ 'thumbnail' ]


    def create(self, filename):
        return mmpython.Factory().create(filename, ext_only=True)

    def update_needed(self, filename, timestamp):
        return timestamp != os.stat(filename)[stat.ST_MTIME]

        
    def update(self, filename, info):
        return mmpython.Factory().create(filename, ext_only=True)


class MetaCache(Cache):
    """
    cache for other freevo metadata
    """
    def __init__(self):
        Cache.__init__(self, 'freevo.cache')

    def create(self, filename):
        return {}

    def update_needed(self, filename, timestamp):
        return False
        
    def update(self, filename, info):
        return info


# info values in metacache that should not be returned
bad_info = [ '__various__', ]

# the two cache objects
mmpython_cache  = MMCache()
meta_cache      = MetaCache()


class Info:
    """
    Container for all kind of informations. This information includes
    mmpython parsed information and some user stored stuff.
    """
    def __init__(self, filename, mmdata, metadata):
        self.filename  = filename
        self.disc      = False
        self.mmdata    = {}
        self.metadata  = {}
        self.variables = {}
        if mmdata:
            self.mmdata    = mmdata
        if metadata:
            self.metadata  = metadata
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
                if result:
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


    def __save__(self):
        if self.disc:
            util.save_pickle(self.metadata, self.filename)
        else:
            meta_cache.save_cache()
        
    def store(self, key, value):
        """
        store the key/value in metadata and save the cache
        """
        self.metadata[key] = value
        if self.disc:
            self.metadata[key] = value
        elif not self.filename:
            print 'unable to store info, no filename'
            return
        else:
            meta_cache.set(os.path.basename(self.filename), os.path.dirname(self.filename),
                           self.filename, self.metadata)
        self.__save__()
        

    def delete(self, key):
        """
        delete the key in metadata and save the cache
        """
        if self.disc:
            if self.metadata.has_key(key):
                del self.metadata[key]
        elif not self.filename:
            print 'unable to delete info, no filename'
            return
        if self.metadata.has_key(key):
            del self.metadata[key]
            meta_cache.set(os.path.basename(self.filename), os.path.dirname(self.filename),
                           self.filename, self.metadata)
        self.__save__()

        
    def set_variables(self, variables):
        """
        set personal user variables (not to storage) to 'variables'
        """
        self.variables = variables
        self.dicts     = ( self.mmdata, self.variables, self.metadata )
        


# Interface to the rest of Freevo:

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


def disc_info(media):
    """
    return mmpython disc information for the media
    """
    type, id  = cdrom_disc_id(media.devicename)
    cachedir  = os.path.join(config.OVERLAY_DIR, 'disc/metadata')
    cachefile = os.path.join(cachedir, id + '.mmpython')
    
    if os.path.isfile(cachefile):
        mmdata = util.read_pickle(cachefile)
    else:
        mmdata = mmpython.parse(media.devicename)
        util.save_pickle(mmdata, cachefile)

    cachefile = os.path.join(cachedir, id + '.freevo')

    if os.path.isfile(cachefile):
        metainfo = util.read_pickle(cachefile)
    else:
        metainfo = {}
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

        
def set(filename, key, value):
    """
    set a variable (key) in the meta_cache to value and saves the cache
    """
    info = meta_cache.get(filename)
    info[key] = value
    fullname  = filename
    dirname   = os.path.dirname(filename)
    filename  = os.path.basename(filename)
    meta_cache.set(filename, dirname, fullname, info)
    meta_cache.save_cache()

