# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# misc.py - misc utilities helper functions
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains some smaller helper functions needed in Freevo and other
# util modules.
#
# TODO: More cleanups here. What need to be here? What is not needed anymore?
#       Split into different files?
#
# Note: I removed some functiosn we don't need anymore to clean up this file.
#       Other functions only needed once are moved to the file were they
#       are needed.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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
import string
import re
import copy
import htmlentitydefs

# freevo imports
import sysconfig

# util imports
import vfs
from vfs import abspath as vfs_abspath

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


def escape(sql):
    """
    Escape a SQL query in a manner suitable for sqlite. Also convert
    Unicode to normal string object.
    """
    if sql:
        sql = sql.replace('\'','\'\'')
        return String(sql)
    else:
        return 'null'



FILENAME_REGEXP = re.compile("^(.*?)_(.)(.*)$")

def getimage(base, default=None):
    """
    return the image base+'.png' or base+'.jpg' if one of them exists.
    If not return the default
    """
    for suffix in ('.png', '.jpg', '.gif'):
        image = vfs_abspath(base+suffix)
        if image:
            return image
    return default


def getname(file, skip_ext=True):
    """
    make a nicer display name from file
    """
    if len(file) < 2:
        return Unicode(file)

    # basename without ext
    if file.rfind('/') < file.rfind('.') and skip_ext:
        name = file[file.rfind('/')+1:file.rfind('.')]
    else:
        name = file[file.rfind('/')+1:]
    if not name:
        # Strange, it is a dot file, return the complete
        # filename, I don't know what to do here. This should
        # never happen
        return Unicode(file)

    name = name[0].upper() + name[1:]

    while file.find('_') > 0 and FILENAME_REGEXP.match(name):
        m = FILENAME_REGEXP.match(name)
        if m:
            name = m.group(1) + ' ' + m.group(2).upper() + m.group(3)
    if name.endswith('_'):
        name = name[:-1]
    return Unicode(name)


def smartsort(x,y):
    """
    Compares strings after stripping off 'The' and 'A' to be 'smarter'
    Also obviously ignores the full path when looking for 'The' and 'A'
    """
    m = os.path.basename(x)
    n = os.path.basename(y)

    for word in ('The', 'A'):
        word += ' '
        if m.find(word) == 0:
            m = m.replace(word, '', 1)
        if n.find(word) == 0:
            n = n.replace(word, '', 1)

    return cmp(m.upper(),n.upper()) # be case insensitive


def find_start_string(s1, s2):
    """
    Find similar start in both strings
    """
    ret = ''
    tmp = ''
    while True:
        if len(s1) < 2 or len(s2) < 2:
            return ret
        if s1[0] == s2[0]:
            tmp += s2[0]
            if s1[1] in (u' ', u'-', u'_', u',', u':', '.') and \
               s2[1] in (u' ', u'-', u'_', u',', u':', '.'):
                ret += tmp + u' '
                tmp = ''
            s1 = s1[1:].lstrip(u' -_,:.')
            s2 = s2[1:].lstrip(u' -_,:.')
        else:
            return ret

def remove_start_string(string, start):
    """
    remove start from the beginning of string.
    """
    start = start.replace(u' ', '')
    for i in range(len(start)):
        string = string[1:].lstrip(' -_,:.')

    return string[0].upper() + string[1:]


def htmlenties2txt(string):
    """
    Converts a string to a string with all html entities resolved.
    Returns the result as Unicode object (that may conatin chars outside 256.
    """
    e = copy.deepcopy(htmlentitydefs.entitydefs)
    e['ndash'] = "-";
    e['bull'] = "-";
    e['rsquo'] = "'";
    e['lsquo'] = "`";
    e['hellip'] = '...'

    string = Unicode(string).replace("&#039", "'").replace("&#146;", "'")

    i = 0
    while i < len(string):
        amp = string.find("&", i) # find & as start of entity
        if amp == -1: # not found
            break
        i = amp + 1

        semicolon = string.find(";", amp) # find ; as end of entity
        if string[amp + 1] == "#": # numerical entity like "&#039;"
            entity = string[amp:semicolon+1]
            replacement = Unicode(unichr(int(entity[2:-1])))
        else:
            entity = string[amp:semicolon + 1]
            if semicolon - amp > 7:
                continue
            try:
                # the array has mappings like "Uuml" -> "ü"
                replacement = e[entity[1:-1]]
            except KeyError:
                continue
        string = string.replace(entity, replacement)
    return string
