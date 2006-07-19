# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fileops.py - Some file operation utilities
# -----------------------------------------------------------------------------
# $Id$
#
# This module provides some file operation utils needed by Freevo. This
# includes basic functions for removable media handling
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


# python imports
import sys
import os
import statvfs
import string
import copy
import fnmatch
import gzip
import stat
import logging

# kaa imports
import kaa.notifier

# freevo imports
import sysconfig
import misc

# get logging object
log = logging.getLogger()


#
# misc file ops
#

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


def unlink(filename):
    try:
        if os.path.isdir(filename) or \
               os.stat(filename)[stat.ST_SIZE] > 1000000:
            base = '.' + os.path.basename(filename) + '.freevo~'
            name = os.path.join(os.path.dirname(filename), base)
            os.rename(filename, name)
            kaa.notifier.Process(['rm', '-rf', name]).start()
        else:
            os.unlink(filename)
    except (OSError, IOError), e:
        log.error('can\'t delete %s: %s' % (filename, e))
        

#
# find files by pattern or suffix
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


def match_files(dirname, suffix_list, recursive = False):
    """
    Find all files in a directory that has matches a list of suffixes.
    Returns a list that is case insensitive sorted.
    """
    if recursive:
        return match_files_recursively(dirname, suffix_list)
    
    try:
        files = [ os.path.join(dirname, fname) \
                  for fname in os.listdir(dirname) if
                  os.path.isfile(os.path.join(dirname, fname)) ]
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
    if dirname.find('/') != -1 and dirname[dirname.rfind('/'):][1] == '.':
        # ignore directories starting with a dot
        # Note: subdirectories of that dir will still be searched
        return result
    for name in names:
        if not name in ('CVS', '.xvpics', '.thumbnails', '.pics',
                        'folder.fxd', 'lost+found'):
            fullpath = os.path.abspath(os.path.join(dirname, name))
            result.append(fullpath)
    return result


def match_files_recursively(dir, suffix_list):
    """
    get all files matching suffix_list in the dir and in it's subdirectories
    """
    all_files = []
    if dir.endswith('/'):
        dir = dir[:-1]
    os.path.walk(dir, _match_files_recursively_helper, all_files)
    matches = misc.unique([f for f in all_files if \
                           match_suffix(f, suffix_list) ])
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return matches


def find_file_in_path( file, path = None ):
    if not path and os.environ.has_key( 'PATH' ):
        path = os.environ[ 'PATH' ].split( ':' )
    if not path: return None
    for p in path:
        abs = os.path.join( p, file )
        if os.path.isfile( abs ):
            return abs

    return None
