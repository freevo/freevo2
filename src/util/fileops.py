# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fileops.py - Some file operation utilities
# -----------------------------------------------------------------------------
# $Id$
#
# This module provides some file operation utils needed by Freevo. This
# includes basic functions for removable media handling
#
# TODO: remove read_pickle and save_pickle, this functions are now in
#       cache.py.
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
import statvfs
import string
import copy
import fnmatch
import gzip
import stat

# freevo imports
import sysconfig
import misc
import vfs


#
# misc file ops
#

def getdirnames(dirname, softlinks=True, sort=True):
    """
    Get all subdirectories in the given directory.
    Returns a list that is case insensitive sorted.
    """
    if not dirname.endswith('/'):
        dirname += '/'

    try:
        dirnames = [ dirname + dname for dname in os.listdir(dirname) if \
                     os.path.isdir(dirname + dname) and \
                     (softlinks or not os.path.islink(dirname + dname))]
    except OSError:
        return []

    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return dirnames



def gzopen(file):
    """
    open a gzip file and return the fd. If it's not a gzip file, try
    to open it as plain text file.
    """
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


def mtime(filename):
    """
    helper function to get the modification time of a file
    """
    return os.stat(filename)[stat.ST_MTIME]


def _rmrf_helper(result, dirname, names):
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
        path_walk = os.path.walk(top, _rmrf_helper, files)
        for f in files[0]:
            try:
                os.remove(f)
            except IOError:
                pass
        for d in files[1]:
            try:
                os.rmdir(d)
            except (IOError, OSError), e:
                print 'fileops.rmrf: %s' % e


#
# find files by pattern or suffix
#

def match_suffix(filename, suffixlist):
    """
    Check if a filename ends in a given suffix, case is ignored.
    """
    fsuffix = vfs.splitext(filename)[1].lower()[1:]
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
        files = [ vfs.join(dirname, fname) for fname in os.listdir(dirname) if
                  vfs.isfile(vfs.join(dirname, fname)) ]
    except OSError, e:
        print 'fileops:match_files: %s' % e
        return []
    matches = [ fname for fname in files if match_suffix(fname, suffix_list) ]
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return matches


def find_matches(files, suffix_list):
    """
    return all files in 'files' that match one of the suffixes in 'suffix_list'
    The correct implementation is
    filter(lambda x: os.path.splitext(x)[1].lower()[1:] in suffix_list, files)
    but this one should also work and is _much_ faster. On a Duron 800,
    Python 2.2 and 700 photos 0.01 secs instead of 0.2.
    """
    return filter(lambda x: x[x.rfind('.')+1:].lower() in suffix_list, files)


def _match_files_recursively_helper(result, dirname, names):
    """
    help function for match_files_recursively
    """
    for name in names:
        if not name in ('CVS', '.xvpics', '.thumbnails', '.pics',
                        'folder.fxd', 'lost+found'):
            fullpath = vfs.join(dirname, name)
            result.append(fullpath)
    return result


def match_files_recursively(dir, suffix_list):
    """
    get all files matching suffix_list in the dir and in it's subdirectories
    """
    all_files = []
    os.path.walk(dir, _match_files_recursively_helper, all_files)
    matches = misc.unique([f for f in all_files if \
                           match_suffix(f, suffix_list) ])
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return matches


def get_subdirs_recursively(dir):
    """
    get all subdirectories recursively in the given directory
    """
    all_files = []
    os.path.walk(dir, _match_files_recursively_helper, all_files)
    matches = misc.unique([f for f in all_files if os.path.isdir(f) ])
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
        fullname = os.path.normpath(vfs.join(root, name))
        # grab if it matches our pattern and entry type
        for pat in pat_list:
            if fnmatch.fnmatch(name, pat):
                if vfs.isfile(fullname) or \
                   (return_folders and vfs.isdir(fullname)):
                    result.append(fullname)
                continue
        # recursively scan other folders, appending results
        if recurse:
            if vfs.isdir(fullname) and not vfs.islink(fullname):
                result = result + recursefolders( fullname, recurse,
                                                  pattern, return_folders )
    return result





#
# Media stuff
#

_mounted_dirs = []

def umount(dir):
    """
    umount a directory
    """
    if not dir:
        return
    if os.path.ismount(dir):
        os.system("umount %s" % dir)
        if not os.path.ismount(dir) and dir in _mounted_dirs:
            _mounted_dirs.remove(dir)


def mount(dir, force=0):
    """
    mount a directory
    """
    if not dir:
        return
    if not os.path.ismount(dir):
        os.system("mount %s 2>/dev/null" % dir)
        if os.path.ismount(dir) and not dir in _mounted_dirs:
            _mounted_dirs.append(dir)
    if force and not dir in _mounted_dirs:
        _mounted_dirs.append(dir)


def umount_all():
    """
    umount all mounted directories
    """
    for d in copy.copy(_mounted_dirs):
        umount(d)


def is_mounted(dir):
    """
    return if the dir is mounted
    """
    return dir in _mounted_dirs


def resolve_media_mountdir(*arg):
    """
    get the mount point of the media with media_id
    """
    if len(arg) == 1 and isinstance(arg[0], dict):
        media_id = arg[0]['media_id']
        file     = arg[0]['file']
    elif len(arg) == 2:
        media_id = arg[0]
        file     = arg[1]
    else:
        raise KeyError

    mountdir = ''
    # Find on what media it is located
    for media in sysconfig.REMOVABLE_MEDIA:
        if media_id == media.id:
            # Then set the filename
            mountdir = media.mountdir
            file     = vfs.join(media.mountdir, file)
            break

    return mountdir, file


def check_media(media_id):
    """
    check if media_id is a valid media in one of the drives
    """
    for media in sysconfig.REMOVABLE_MEDIA:
        if media_id == media.id:
            return media
    return None



# FIXME: remove this!!!

import cache

def read_pickle(file):
    return cache.load(file)

def save_pickle(data, file):
    return cache.save(file, data)
