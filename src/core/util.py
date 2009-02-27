# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# util.py - misc utilities helper functions
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
#
# First Version: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import logging

# kaa imports
import kaa

# get logging object
log = logging.getLogger()


# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52560
def unique(s):
    """
    Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


class ObjectCache(object):
    """
    Provides a cache for objects indexed by a string. It should
    be slow for a large number of objects, since searching takes
    O(n) time. The cachesize given in the constructor is the
    maximum number of objects in the cache. Objects that have not
    been accessed for the longest time get deleted first.
    """

    def __init__(self, cachesize = 30, desc='noname'):
        self.cache = {}
        self.lru = []  # Least recently used (lru) list, index 0 is lru
        self.cachesize = cachesize
        self.desc = desc


    def __getitem__(self, key):
        if isinstance(key, str):
            key = kaa.str_to_unicode(key)

        try:
            del self.lru[self.lru.index(key)]
            self.lru.append(key)
            return self.cache[key]
        except:
            return None


    def __setitem__(self, key, object):
        if isinstance(key, str):
            key = kaa.str_to_unicode(key)

        try:
            # remove old one if key is already in cache
            del self.lru[self.lru.index(key)]
        except:
            pass

        # Do we need to delete the oldest item?
        if len(self.cache) > self.cachesize:
            # Yes
            lru_key = self.lru[0]
            del self.cache[lru_key]
            del self.lru[0]

        self.cache[key] = object
        self.lru.append(key)


    def __delitem__(self, key):
        if isinstance(key, str):
            key = kaa.str_to_unicode(key)

        if not key in self.cache:
            return

        del self.cache[key]
        del self.lru[self.lru.index(key)]


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
    matches = unique([f for f in all_files if match_suffix(f, suffix_list) ])
    matches.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return matches
