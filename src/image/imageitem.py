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
# Revision 1.17  2003/12/10 19:08:43  dischi
# no need for the eventhandler anymore
#
# Revision 1.16  2003/12/07 19:09:24  dischi
# add <slideshow> fxd support with background music
#
# Revision 1.15  2003/12/07 11:12:56  dischi
# small bugfix
#
# Revision 1.14  2003/11/21 11:46:07  dischi
# moved rotation info into the item
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

import util
import os

import viewer
import mmpython

from item import Item
from event import *


class ImageItem(Item):
    def __init__(self, filename, parent, name = None, duration = 0):
        if parent and parent.media:
            url = 'cd://%s:%s:%s' % (parent.media.devicename, parent.media.mountdir,
                                     filename[len(parent.media.mountdir)+1:])
        else:
            url = filename

        Item.__init__(self, parent, mmpython.parse(url))
        self.type     = 'image'
        self.filename = filename
        self.image    = filename
        self.duration = duration
        
        # set name
        if name:
            self.name = name
        elif not self.name:
            self.name = util.getname(filename)

        self.rotation     = 0

        
    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr in [ "geometry" ]:
            try:
                image = self.info
                if attr == 'geometry':
                    print "geometry=%sx%s" % (image.width, image.height)
                    return '%sx%s' % (image.width, image.height)
            except:
                pass
            
        return Item.getattr(self, attr)
        

    def copy(self, obj):
        """
        Special copy value VideoItems
        """
        Item.copy(self, obj)
        if obj.type == 'image':
            self.duration = obj.duration
            self.rotation = obj.rotation
            

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
        return [ ( self.view, _('View Image') ) ]


    def cache(self):
        """
        caches (loads) the next image
        """
        viewer.get_singleton().cache(self)


    def view(self, arg=None, menuw=None):
        """
        view the image
        """
        if not self.menuw:
            self.menuw = menuw
        self.parent.current_item = self

        if self.menuw.visible:
            self.menuw.hide()

        viewer.get_singleton().view(self, rotation=self.rotation)

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()
