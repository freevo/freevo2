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
# Revision 1.9  2003/04/06 21:12:57  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.8  2003/03/16 19:28:04  dischi
# Item has a function getattr to get the attribute as string
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
import bins
import exif

from item import Item

tags_check = { 'date':    [ 'Image DateTime','DateTime','EXIF'],
               'width':   [ 'EXIF ExifImageWidth','ExifImageWidth','EXIF'],
               'height':  [ 'EXIF ExifImageLength','ExifImageLength','EXIF'],
               'exp':     [ 'EXIF ExposureTime','ExposureTime','EXIF'],
               'light':   [ 'EXIF LightSource','LightSource','EXIF'],
               'flash':   [ 'EXIF Flash','Flash','EXIF'],
               'make':    [ 'Image Make','Make','EXIF'],
               'model':   [ 'Image Model','Model','EXIF'],
               'software':[ 'Image Software','Software','EXIF']
               }

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
        self.exiftags = None


    def copy(self, obj):
        """
        Special copy value ImageItem
        """
        Item.copy(self, obj)
        if obj.type == 'image':
            self.duration = obj.duration
            self.binsdesc = obj.binsdesc
            self.exiftags = obj.exiftags

        
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
        if not self.menuw:
            self.menuw = menuw
        self.parent.current_item = self

        if self.menuw.visible:
            self.menuw.hide()

        self.image_viewer.view(self)

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if self.exiftags == None:
            f = open(self.filename, 'r')
            self.exiftags = exif.process_file(f)
            f.close()
            
        if attr in tags_check:
            b = ''
            e = ''
            if self.binsexif.has_key(tags_check[attr][1]):
                b = str(self.binsexif[tags_check[attr][1]])
            if self.exiftags.has_key(tags_check[attr][0]):
                e = str(self.exiftags[tags_check[attr][0]])

            if tags_check[attr][2] == 'EXIF':
                if e:
                    return e
                return b
            if b:
                return b
            return e

        if attr in self.binsdesc:
            return str(self.binsdesc[attr])

        return Item.getattr(self, attr)
