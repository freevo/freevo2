# -*- coding: iso-8859-1 -*-
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
# Revision 1.10  2005/01/09 10:47:53  dischi
# gb patch
#
# Revision 1.9  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.8  2003/10/21 21:17:41  gsbarbieri
# Some more i18n improvements.
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


import plugin
import util

class PluginInterface(plugin.ItemPlugin):
    """
    This plugin adds an item to your Audio, Video, Games, and Pictures Items. It
    states how much memory is free on the partition that directory belongs to.

    to activate it, put this in your local_conf.py:

    plugin.activate('df') 

    to see the disk usage go to any directory listing and, press ENTER ('e' key or
    key it maps to on your remote) and you will see the disk usage under the Browse
    directory option. This also works on the main directory listings where you see
    your cdrom drives.
    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)

    def actions(self, item): 
        if item.type == 'dir':
            freespace = util.freespace(item.dir)
            totalspace = util.totalspace(item.dir)

            if (totalspace > 1073741824): # more than 1024 Mb
                diskfree = _('%i free of %i Gb total (%i%% free)') % \
                           ( (((freespace / 1024) / 1024) / 1024),
                             (((totalspace / 1024) / 1024) / 1024), (freespace*100.0/totalspace) )
            else:
                diskfree = _('%i free of %i Mb total (%i%% free)') % \
                           ( ((freespace / 1024) / 1024),
                             ((totalspace / 1024) / 1024), (freespace*100.0/totalspace) )
            return  [ ( self.dud, diskfree) ]
        else:
            return []


    def dud(self, arg=None, menuw=None):
        pass
