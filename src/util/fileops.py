#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/fileops.py - Some File Operation Utilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/11/03 18:25:36  dischi
# fix
#
# Revision 1.3  2003/11/02 09:24:35  dischi
# Check for libs and make it possible to install runtime from within
# freevo
#
# Revision 1.2  2003/10/17 17:28:41  dischi
# bugfix
#
# Revision 1.1  2003/10/11 11:20:11  dischi
# move util.py into a directory and split it into two files
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

import os
import sys
import statvfs
import string
import copy
import cPickle, pickle # pickle because sometimes cPickle doesn't work
import fnmatch
import traceback

if float(sys.version[0:3]) < 2.3:
    PICKLE_PROTOCOL = 1
else:
    PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL

for t in traceback.extract_stack():
    if t[0][0].find('install.py') > 0:
        break
else:
    # Configuration file. Determines where to look for AVI/MP3 files, etc
    import config

    # import stuff from util.misc
    import misc


#
#
# misc file ops
#
#

def getdirnames(dirname):
    """
    Get all subdirectories in the given directory.
    Returns a list that is case insensitive sorted.
    """

    try:
        dirnames = [ os.path.join(dirname, dname) for dname in os.listdir(dirname)
                     if os.path.isdir(os.path.join(dirname, dname)) ]
    except OSError:
        return []
    
    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return dirnames



def gzopen(file):
    """
    open a gzip file and return the fd. If it's not a gzip file, try
    to open it as plain text file.
    """
    import gzip
    m = open(file)
    magic = m.read(2)
    m.close
    if magic == '\037\213':
         f = gzip.open(file)
    else:
         f = open(file)
    return f


def readfile(filename):
    """
    return the complete file as list
    """
    fd = open(str(filename), 'r')
    ret = fd.readlines()
    fd.close()
    return ret


def freespace(path):
    """
    freespace(path) -> integer
    Return the number of bytes available to the user on the file system
    pointed to by path.
    """
    s = os.statvfs(path)
    return s[statvfs.F_BAVAIL] * long(s[statvfs.F_BSIZE])
        

def totalspace(path):
    """
    totalspace(path) -> integer
    Return the number of total bytes available on the file system
    pointed to by path.
    """
    s = os.statvfs(path)
    return s[statvfs.F_BLOCKS] * long(s[statvfs.F_BSIZE])
        

def touch(file):
    """
    touch a file (maybe create it)
    """
    try:
        fd = open(file,'w+')
        fd.close()
    except IOError:
        pass
    return 0


def rmrf_helper(result, dirname, names):
    """
    help function for rm -rf
    """
    for name in names:
        fullpath = os.path.join(dirname, name)
        if os.path.isfile(fullpath):
            result[0].append(fullpath)
    result[1] = [dirname] + result[1]
    return result


def rmrf(top=None):
    """
    Pure python version of 'rm -rf'
    """
    if not top == '/' and not top == '' and not top == ' ' and top:
        files = [[],[]]
        path_walk = os.path.walk(top, rmrf_helper, files)
        for f in files[0]:
            try:
                os.remove(f)
            except IOError:
                pass
        for d in files[1]:
            try:
                os.rmdir(d)
            except IOError:
                pass


#
#
# find files by pattern or suffix
#
#

def match_suffix(filename, suffixlist):
    """
    Check if a filename ends in a given suffix, case is ignored.
    """

    fsuffix = os.path.splitext(filename)[1].lower()[1:]

    for suffix in suffixlist:
        if fsuffix == suffix:
            return 1

    return 0


def match_files(dirname, suffix_list):
    """
    Find all files in a directory that has matches a list of suffixes.
    Returns a list that is case insensitive sorted.
    """

    try:
        files = [ os.path.join(dirname, fname) for fname in os.listdir(dirname) if
                  os.path.isfile(os.path.join(dirname, fname)) ]
    except OSError:
        print 'util:match_files(): Got error on dir = "%s"' % dirname
        return []

    matches = [ fname for fname in files if match_suffix(fname, suffix_list) ]
        
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return matches


def find_matches(files, suffix_list):
    """
    return all files in 'files' that match one of the suffixes in 'suffix_list'
    """
    return [ fname for fname in files if match_suffix(fname, suffix_list) ]


def match_files_recursively_helper(result, dirname, names):
    """
    help function for match_files_recursively
    """
    for name in names:
        fullpath = os.path.join(dirname, name)
        result.append(fullpath)
    return result


def match_files_recursively(dir, suffix_list):
    """
    get all files matching suffix_list in the dir and in it's subdirectories
    """
    all_files = []
    os.path.walk(dir, match_files_recursively_helper, all_files)

    matches = misc.unique([f for f in all_files if match_suffix(f, suffix_list) ])

    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    
    return matches


def recursefolders(root, recurse=0, pattern='*', return_folders=0):
    """
    Before anyone asks why I didn't use os.path.walk; it's simple, 
    os.path.walk is difficult, clunky and doesn't work right in my
    mind. 
    
    Here's how you use this function:
    
    songs = recursefolders('/media/Music/Guttermouth',1,'*.mp3',1):
    for song in songs:
          print song      
    
    Should be easy to add to the mp3.py app.
    """
    
    # initialize
    result = []

    # must have at least root folder
    try:
        names = os.listdir(root)
    except os.error:
        return result

    # expand pattern
    pattern = pattern or '*'
    pat_list = string.splitfields( pattern , ';' )

    # check each file
    for name in names:
        fullname = os.path.normpath(os.path.join(root, name))

        # grab if it matches our pattern and entry type
        for pat in pat_list:
            if fnmatch.fnmatch(name, pat):
                if os.path.isfile(fullname) or \
                   (return_folders and os.path.isdir(fullname)):
                    result.append(fullname)
                continue

        # recursively scan other folders, appending results
        if recurse:
            if os.path.isdir(fullname) and not os.path.islink(fullname):
                result = result + recursefolders( fullname, recurse,
                                                  pattern, return_folders )

    return result


#
#
# Media stuff
#
#

mounted_dirs = []

def umount(dir):
    """
    umount a directory
    """
    global mounted_dirs
    if os.path.ismount(dir):
        os.system("umount %s" % dir)
        if not os.path.ismount(dir) and dir in mounted_dirs:
            mounted_dirs.remove(dir)


def mount(dir, force=0):
    """
    mount a directory
    """
    global mounted_dirs
    if not os.path.ismount(dir):
        os.system("mount %s 2>/dev/null" % dir)
        if os.path.ismount(dir) and not dir in mounted_dirs:
            mounted_dirs.append(dir)
    if force and not dir in mounted_dirs:
        mounted_dirs.append(dir)
        
    
def umount_all():
    """
    umount all mounted directories
    """
    global mounted_dirs
    for d in copy.copy(mounted_dirs):
        umount(d)
        
            
def resolve_media_mountdir(media_id, file):
    """
    get the mount point of the media with media_id
    """
    mountdir = None
    full_filename = file
    # Find on what media it is located
    for media in config.REMOVABLE_MEDIA:
        if media_id == media.id:
            # Then set the filename
            mountdir = media.mountdir
            full_filename = os.path.join(media.mountdir, file)
            break

    return mountdir, full_filename


def check_media(media_id):
    """
    check if media_id is a valid media in one of the drives
    """
    for media in config.REMOVABLE_MEDIA:
        if media_id == media.id:
            return media
    return None



#
#
# pickle helper
#
#

def read_pickle(file):
    """
    read a file with pickle
    """
    try:
        f = open(file, 'r')
        try:
            data = cPickle.load(f)
        except:
            data = pickle.load(f)
        f.close()
        try:
            os.utime(file, None)
        except OSError:
            _debug_('can change access time for %s' % file)
        return data
    except:
        return None


def save_pickle(data, file):
    """
    save the data with pickle to the given file
    """
    try:
        if os.path.isfile(file):
            os.unlink(file)
        f = open(file, 'w')
        cPickle.dump(data, f, PICKLE_PROTOCOL)
        f.close()
    except IOError:
        print 'unable to save to cachefile %s' % file


            

