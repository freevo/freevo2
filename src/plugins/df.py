#if 0 /*
# -----------------------------------------------------------------------
# df.py - really simple diskfree plugin for freevo
# created by den_RDC
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/05/28 17:51:28  dischi
# added df item plugin for directories from den_RDC
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
import config
import statvfs
import plugin

class PluginInterface(plugin.ItemPlugin):

    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def actions(self, item): 
        if item.type == 'dir':
            diskfree = '%i of %i Mb free'  % \
                       ( (( self.freespace(item.dir) / 1024) / 1024),
                         ((self.totalspace(item.dir) /1024) /1024))
            return  [ ( self.dud, diskfree) ]
        else:
            print item.type
            return []

    def freespace(self, path):
        """ freespace(path) -> integer
        Return the number of bytes available to the user on the file system
        pointed to by path."""
        s = os.statvfs(path)
        return s[statvfs.F_BAVAIL] * long(s[statvfs.F_BSIZE])
        
        
    def totalspace(self, path):
        """ totalspace(path) -> integer
        Return the number of total bytes available on the file system
        pointed to by path."""
        s = os.statvfs(path)
        return s[statvfs.F_BLOCKS] * long(s[statvfs.F_BSIZE])
        
    def dud(self, arg=None, menuw=None):
        pass
