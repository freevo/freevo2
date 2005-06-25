# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# objectcache.py - A cache for objects identified by a string
# -----------------------------------------------------------------------------
# $Id$
#
# Provides a cache for objects indexed by a string. It should be slow for
# a large number of objects, since searching takes O(n) time. The cachesize
# given in the constructor is the maximum number of objects in the cache.
# Objects that have not been accessed for the longest time get deleted first.
#
# TODO: make it faster :)
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

import sysconfig

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
            key = unicode(key, sysconfig.CONF.encoding)

        try:
            del self.lru[self.lru.index(key)]
            self.lru.append(key)
            return self.cache[key]
        except:
            return None
        

    def __setitem__(self, key, object):
        if isinstance(key, str):
            key = unicode(key, sysconfig.CONF.encoding)

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
            key = unicode(key, sysconfig.CONF.encoding)

        if not key in self.cache:
            return

        del self.cache[key]
        del self.lru[self.lru.index(key)]
        
