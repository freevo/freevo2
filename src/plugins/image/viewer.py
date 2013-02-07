# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Freevo image viewer
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

__all__ = [ 'viewer' ]

# python imports
import logging

# kaa imports
import kaa
import kaa.candy

# freevo imports
from ... import core as freevo
from ... import gui

# get logging object
log = logging.getLogger('image')

# global viewer, will be set to the ImageViewer
viewer = None

class Widget(kaa.candy.Widget):
    """
    Imageviewer widget for kaa.candy
    """
    candyxml_name = 'photo'

    # Use the backend code from backend.py. This allows us to use the
    # full power of clutter in this plugin, outside the main Freevo
    # GUI code or kaa.candy. The backend,py should NEVER be imported
    # from within Freevo, the kaa.candy display process will do
    # this. Only this process should import clutter.

    candy_backend = 'backend.Widget'
    attributes = [ 'cached', 'filename', 'rotation', 'blend_mode' ]


class ImageViewer(freevo.Player):
    """
    Full screen image viewer for imageitems
    """

    name = 'imageviewer'

    def __init__(self):
        """
        create an image viewer application
        """
        capabilities = (freevo.CAPABILITY_TOGGLE, freevo.CAPABILITY_FULLSCREEN)
        super(ImageViewer, self).__init__('image', capabilities)
        self.slideshow = True
        self.sshow_timer = kaa.OneShotTimer(self.slideshow_next)
        self.signals['stop'].connect_weak(self.application_stop)

    def application_stop(self):
        """
        Application not running anymore
        """
        # we don't need the signalhandler anymore
        self.sshow_timer.stop()

    def slideshow_next(self):
        """
        Send PLAY_END to show next image.
        """
        event = freevo.Event(freevo.PLAY_END, self.item)
        event.handler = self.eventhandler
        event.post()

    @kaa.coroutine()
    def view(self, item):
        """
        Show the image
        """
        if not (yield super(ImageViewer, self).play(item, ['VIDEO'])):
            yield False
        items = [ self.item.filename ]
        try:
            idx = self.playlist.choices.index(self.item)
            if idx + 1 == len(self.playlist.choices):
                items.append(self.playlist.choices[0].filename)
            else:
                items.append(self.playlist.choices[idx + 1].filename)
            if idx == 0:
                items.append(self.playlist.choices[len(self.playlist.choices) - 1].filename)
            else:
                items.append(self.playlist.choices[idx - 1].filename)
        except:
            log.exception('error creating cache')
        self.player = self.widget.get_widget('player')
        self.player.cached = items
        self.player.filename = self.item.filename
        self.player.rotation = self.item.orientation or 0
        self.player.blend_mode = str(freevo.config.image.viewer.blend_mode)
        self.eventmap = 'image'
        # start timer
        if self.item.duration and self.slideshow and \
               not self.sshow_timer.active:
            self.sshow_timer.start(self.item.duration)
        # Notify everyone about the viewing
        freevo.PLAY_START.post(item)
        yield None

    def do_stop(self):
        """
        Stop the current viewing
        """
        event = freevo.Event(freevo.PLAY_END, self.item)
        event.handler = self.eventhandler
        event.post()

    def eventhandler(self, event):
        """
        Handle incoming events
        """
        if super(ImageViewer, self).eventhandler(event):
            # Generic start/stop handling
            if event == freevo.PLAY_END and self.player:
                self.player = None
            return True
        if not self.player:
            # No player object and therefore, no playback control
            return self.item.eventhandler(event)
        if event == freevo.PAUSE or event == freevo.PLAY:
            if self.slideshow:
                freevo.OSD_MESSAGE.post(_('pause'))
                self.slideshow = False
                self.sshow_timer.stop()
            else:
                freevo.OSD_MESSAGE.post(_('play'))
                self.slideshow = True
                self.sshow_timer.start(1)
            return True
        if event == freevo.PLAYLIST_NEXT or event == freevo.PLAYLIST_PREV:
            # up and down will stop the slideshow and pass the
            # event to the playlist
            self.sshow_timer.stop()
            self.item.eventhandler(event)
            return True
        if event == freevo.IMAGE_ROTATE:
            # rotate image
            if event.arg == 'left':
                self.player.rotation = (self.player.rotation + 270) % 360
            else:
                self.player.rotation = (self.player.rotation + 90) % 360
            self.item.orientation = self.player.rotation
            return True
        # pass not handled event to the item
        return self.item.eventhandler(event)

# set viewer object
viewer = ImageViewer()
