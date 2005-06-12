# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# imageitem.py - Item for image files
# -----------------------------------------------------------------------
# $Id$
#
# An ImageItem is an Item handling image files for Freevo. It will
# use the viewer in viewer.py to display the image
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.32  2005/06/12 18:49:53  dischi
# adjust to new menu code
#
# Revision 1.31  2005/04/10 17:58:45  dischi
# switch to new mediainfo module
#
# Revision 1.30  2004/09/13 18:00:49  dischi
# last cleanups for the image module in Freevo
#
# Revision 1.29  2004/09/07 18:57:43  dischi
# image viwer auto slideshow
#
# Revision 1.28  2004/08/27 14:22:01  dischi
# The complete image code is working again and should not crash. The zoom
# handling got a complete rewrite. Only the gphoto plugin is not working
# yet because my camera is a storage device.
#
# Revision 1.27  2004/08/23 20:36:42  dischi
# rework application handling
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


# python imports
import util
import os
import time

# freevo imports
import config
from menu import MediaItem
from event import *
from viewer import *
import util.thumbnail

class ImageItem(MediaItem):
    """
    An item for image files
    """
    def __init__(self, url, parent, duration = config.IMAGEVIEWER_DURATION):
        # set autovars to 'rotation' so that this value is
        # stored between Freevo sessions
        self.autovars = { 'rotation': 0 }
        MediaItem.__init__(self, parent, type='image')
        # set url and parse the name
        self.set_url(url, search_cover=False)
        self.duration = duration
        if self.url.startswith('file://'):
            self.image = self.filename


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
                t = str(MediaItem.__getitem__(self, key))
                if t:
                    t = time.strptime(t, '%Y:%m:%d %H:%M:%S')
                    return time.strftime(config.TV_DATETIMEFORMAT, t)
            except:
                pass

        return MediaItem.__getitem__(self, key)


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return u'%s%s' % (os.stat(self.filename).st_ctime,
                              Unicode(self.filename))
        return Unicode(self.name)


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ ( self.play, _('View Image') ) ]


    def cache(self):
        """
        caches (loads) the next image
        """
        imageviewer().cache(self)


    def play(self, arg=None, menuw=None):
        """
        view the image
        """
        if not self.menuw:
            self.menuw = menuw
        self.parent.current_item = self

        imageviewer().view(self, rotation=self['rotation'])

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()


    def stop(self, arg=None, menuw=None):
        """
        stop viewing this item
        """
        imageviewer().stop()
