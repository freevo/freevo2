#if 0 /*
# -----------------------------------------------------------------------
# imageitem.py - Item for image files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2002/12/02 18:25:27  dischi
# Added bins/exif patch from John M Cooper
#
# Revision 1.4  2002/11/28 19:56:12  dischi
# Added copy function
#
# Revision 1.3  2002/11/27 20:25:17  dischi
# small "name" fix
#
# Revision 1.2  2002/11/26 16:28:10  dischi
# added patch for better bin support
#
# Revision 1.1  2002/11/24 13:58:45  dischi
# code cleanup
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

import config
import util
import os

import viewer
import bins


from item import Item

class ImageItem(Item):
    def __init__(self, file, parent, name = None, duration = 0):
        Item.__init__(self, parent)
        self.type     = 'image'
        self.file     = file
        self.image    = file

        # variables only for ImageItem
        self.duration = duration
	self.binsdesc = {}
	self.binsexif = {}

        # This should check for bins compatable info
	if os.path.isfile(file + '.xml'):
	    binsinfo = bins.get_bins_desc(file)
	    self.binsdesc = binsinfo['desc']
	    self.binsexif = binsinfo['exif']

        # set name
        if name:
            self.name = name
	elif self.binsdesc.has_key('title'):
	    self.name = self.binsdesc['title']
        else:
            self.name = util.getname(file)

        self.image_viewer = viewer.get_singleton()



    def copy(self, obj):
        """
        Special copy value ImageItem
        """
        Item.copy(self, obj)
        if obj.type == 'image':
            self.duration = obj.duration
            self.binsdesc = obj.binsdesc

        
    def actions(self):
        return [ ( self.view, 'View Image' ) ]


    def cache(self):
        self.image_viewer.cache(self)


    def view(self, arg=None, menuw=None):
        self.parent.current_item = self
        self.image_viewer.view(self)

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()
