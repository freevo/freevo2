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
# Revision 1.7  2003/01/21 14:16:54  dischi
# Fix to avoid a crash if bins fails (xml parser broken or invalid xml file)
#
# Revision 1.6  2002/12/22 12:59:34  dischi
# Added function sort() to (audio|video|games|image) item to set the sort
# mode. Default is alphabetical based on the name. For mp3s and images
# it's based on the filename. Sort by date is in the code but deactivated
# (see mediamenu.py how to enable it)
#
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
    def __init__(self, filename, parent, name = None, duration = 0):
        Item.__init__(self, parent)
        self.type     = 'image'
        self.filename = filename
        self.image    = filename

        # variables only for ImageItem
        self.duration = duration
	self.binsdesc = {}
	self.binsexif = {}

        # This should check for bins compatable info
	if os.path.isfile(filename + '.xml'):
            try:
                binsinfo = bins.get_bins_desc(filename)
                self.binsdesc = binsinfo['desc']
                self.binsexif = binsinfo['exif']
            except:
                pass
        # set name
        if name:
            self.name = name
	elif self.binsdesc.has_key('title'):
	    self.name = self.binsdesc['title']
        else:
            self.name = util.getname(filename)

        self.image_viewer = viewer.get_singleton()



    def copy(self, obj):
        """
        Special copy value ImageItem
        """
        Item.copy(self, obj)
        if obj.type == 'image':
            self.duration = obj.duration
            self.binsdesc = obj.binsdesc

        
    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)
        return self.filename


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ ( self.view, 'View Image' ) ]


    def cache(self):
        """
        caches (loads) the next image
        """
        self.image_viewer.cache(self)


    def view(self, arg=None, menuw=None):
        """
        view the image
        """
        self.parent.current_item = self
        self.image_viewer.view(self)

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()
