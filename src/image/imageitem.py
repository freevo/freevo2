# -*- coding: iso-8859-1 -*-
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
# Revision 1.27  2004/08/23 20:36:42  dischi
# rework application handling
#
# Revision 1.26  2004/08/01 10:44:20  dischi
# remove menuw hiding
#
# Revision 1.25  2004/07/17 08:18:56  dischi
# unicode fixes
#
# Revision 1.24  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.23  2004/02/13 20:27:30  dischi
# fix attr geometry and add formated date
#
# Revision 1.22  2004/01/24 18:56:45  dischi
# rotation is now stored in mediainfo
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


import util
import os
import time

import config
import viewer

from item import Item
from event import *


class ImageItem(Item):
    def __init__(self, url, parent, name = None, duration = 0):
        self.type = 'image'
        self.autovars = [ ( 'rotation', 0 ) ]
        Item.__init__(self, parent)

        if name:
            self.name = name

        self.set_url(url, search_image=False)

        if self.mode == 'file':
            self.image = self.filename
        self.duration = duration

        
    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == "geometry":
            if self['width'] and self['height']:
                return '%sx%s' % (self['width'], self['height'])
            return ''
        
        if key == "date":
            try:
                t = str(Item.__getitem__(self, key))
                if t:
                    return time.strftime(config.TV_DATETIMEFORMAT,
                                         time.strptime(t, '%Y:%m:%d %H:%M:%S'))
            except:
                pass
            
        return Item.__getitem__(self, key)
        

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return u'%s%s' % (os.stat(self.filename).st_ctime, Unicode(self.filename))
        return Unicode(self.filename)


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

        viewer.get_singleton().view(self, rotation=self['rotation'])

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()


    def stop(self):
        """
        stop viewing this item
        """
        viewer.get_singleton().stop()
