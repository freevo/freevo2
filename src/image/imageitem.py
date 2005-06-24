# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imageitem.py - Item for image files
# -----------------------------------------------------------------------------
# $Id$
#
# An ImageItem is an Item handling image files for Freevo. It will
# use the viewer in viewer.py to display the image
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'ImageItem' ]

# python imports
import os
import time

# freevo imports
import config
from menu import MediaItem, Action
from event import *
from viewer import *

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
        return [ Action(_('View Image'), self.play) ]


    def cache(self):
        """
        caches (loads) the next image
        """
        imageviewer().cache(self)


    def play(self):
        """
        view the image
        """
        imageviewer().view(self, rotation=self['rotation'])


    def stop(self):
        """
        stop viewing this item
        """
        imageviewer().stop()
