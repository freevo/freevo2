#if 0 /*
# -----------------------------------------------------------------------
# objectcache.py - A cache for objects identified by a string
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:       
# 
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/08/22 19:22:50  dischi
# small check to prevent crashes
#
# Revision 1.2  2003/04/24 19:55:51  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.1  2003/01/07 07:17:07  krister
# Added Thomas Schüppels objectcache layer for the OSD objects.
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

import config

DEBUG = config.DEBUG


class ObjectCache:
    '''Provides a cache for objects indexed by a string. It should
    be slow for a large number of objects, since searching takes
    O(n) time. The cachesize given in the constructor is the
    maximum number of objects in the cache. Objects that have not
    been accessed for the longest time get deleted first.'''
    

    def __init__(self, cachesize = 30, desc='noname'):
        self.cache = {}
        self.lru = []  # Least recently used (lru) list, index 0 is lru
        self.cachesize = cachesize
        self.desc = desc


    def __getitem__(self, key):
        if not key in self.cache:
            return None
        else:
            try:
                del self.lru[self.lru.index(key)]
                self.lru.append(key)
                return self.cache[key]
            except:
                return None

    def __setitem__(self, key, object):
        try:
            # Do we need to delete the oldest item?
            if len(self.cache) > self.cachesize:
                # Yes
                lru_key = self.lru[0]
                del self.cache[lru_key]
                del self.lru[0]
            self.cache[key] = object
            self.lru.append(key)
        except:
            pass
        

    def __delitem__(self, key):
        if not key in self.cache:
            return

        del self.cache[key]
        del self.lru[self.lru.index(key)]
        

#
# Simple test...
#
if __name__ == '__main__':
    cache = ObjectCache(2)
    cache['1'] = 'one'
    cache['2'] = 'zwei'
    cache['3'] = 'drei'
    cache['3'] = 'three'
    # delete something
    del cache['2']
    # delete an item that is not in the list
    del cache['2']
    cache['2'] = 'two'
    # One should have been overwritten
    # '2' should be 'two
    # '3' should be 'three'
    if cache['1'] != None:
        print "Test failed."
    print "two - three == %s - %s" % (cache['2'], cache['3'])
    
