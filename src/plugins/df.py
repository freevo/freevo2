#if 0 /*
# -----------------------------------------------------------------------
# df.py - really simple diskfree plugin for freevo
# created by den_RDC
# -----------------------------------------------------------------------
# $Id$
#
# Notes: but plugin.activate('df') in your local_conf.py. You can see the
#        disc usage by pressing ENTER on a directory item
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/07/15 16:52:47  dischi
# removed some debug
#
# Revision 1.3  2003/07/05 17:00:01  dischi
# added doc
#
# Revision 1.2  2003/05/28 17:58:48  dischi
# moved freespace and totalspace from df.py to util.py
#
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


import plugin
import util

class PluginInterface(plugin.ItemPlugin):

    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def actions(self, item): 
        if item.type == 'dir':
            diskfree = '%i of %i Mb free'  % \
                       ( (( util.freespace(item.dir) / 1024) / 1024),
                         ((util.totalspace(item.dir) /1024) /1024))
            return  [ ( self.dud, diskfree) ]
        else:
            return []


    def dud(self, arg=None, menuw=None):
        pass
