# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Item for image files
# -----------------------------------------------------------------------------
# An ImageItem is an Item handling image files for Freevo. It will use
# the viewer in viewer.py to display the image
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2013 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import time

# freevo imports
from ... import core as freevo
from viewer import viewer

class ImageItem(freevo.MediaItem):
    """
    An item for image files
    """
    type = 'image'

    # cached attributes
    CACHED_ATTRIBUTES_MTIME = ['orientation']

    def __init__(self, url, parent, duration = freevo.config.image.viewer.duration):
        super(ImageItem, self).__init__(parent)
        self.user_stop = False
        self.set_url(url)
        self.duration = duration

    @property
    def geometry(self):
        """
        Return width x height of the image or None
        """
        if self.get('width') and self.get('height'):
            return '%sx%s' % (self.get('width'), self.get('height'))
        return None

    @property
    def date(self):
        """
        Return timestamp of the image or None
        """
        if self.get('timestamp'):
            return time.strftime('%D %H:%M', time.localtime(self.get('timestamp')))
        return None

    def actions(self):
        """
        Return a list of possible actions on this item.
        """
        return [ freevo.Action(_('View Image'), self.play) ]

    def play(self):
        """
        View the image
        """
        viewer.view(self)

    def stop(self):
        """
        Stop viewing this item
        """
        viewer.stop()

    def eventhandler(self, event):
        """
        eventhandler for this item
        """
        if event == freevo.STOP:
            self.user_stop = True
        if event == freevo.PLAY_END:
            if not self.user_stop:
                self['last_played'] = int(time.time())
                self.user_stop = False
        return super(ImageItem, self).eventhandler(event)
