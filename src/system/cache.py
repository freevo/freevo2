# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# cache.py - cache for auto detect code
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/09/28 18:30:24  dischi
# add autodetect system settings module
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

import os
import config
import util

VERSION = 1

class Cache:
    def __init__(self):
        self.cachefile = os.path.join(config.FREEVO_CACHEDIR, 'system-%s' % os.getuid())
        try:
            self.version, self.data = util.read_pickle(self.cachefile)
        except:
            self.data    = {}
            self.version = VERSION
        if not self.version == VERSION:
            self.data    = {}
            self.version = VERSION
            
    def __getitem__(self, key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    def __setitem__(self, key, value):
        self.data[key] = value
        if not key.startswith('_'):
            setattr(config, key, value)
            
    def save(self):
        util.save_pickle((self.version, self.data), self.cachefile)
        
    def keys(self):
        return filter(lambda x: not x.startswith('_'), self.data.keys())
    
    
