# -*- coding: iso-8859-1 -*-
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
# Revision 1.10  2004/10/26 19:14:52  dischi
# adjust to new sysconfig file
#
# Revision 1.9  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.8  2004/06/23 20:05:16  dischi
# fix bad bug in the object cache, much faster again
#
# Revision 1.7  2004/06/21 12:06:38  dischi
# fix strange crash with try except
#
# Revision 1.6  2004/04/20 17:11:21  dischi
# fix strange crash
#
# Revision 1.5  2004/02/04 17:20:24  dischi
# fix crash when object is None
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


import sysconfig

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
    
