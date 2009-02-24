# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2006 Dirk Meyer, et al.
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
import os
import sys
import logging

# kaa imports
import kaa
import kaa.imlib2

# freevo imports
from .. import api as freevo

# get logging object
log = logging.getLogger('image')

# global viewer, will be set to the ImageViewer
viewer = None

class ImageViewer(freevo.Application):
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
        self.osd_mode = 0
        self.bitmapcache = freevo.util.ObjectCache(3, desc='viewer')
        self.slideshow = True
        self.sshow_timer = kaa.OneShotTimer(self._next)
        self.signals['stop'].connect_weak(self._cleanup)

    def _cleanup(self):
        """
        Application not running anymore, free cache
        """
        self.osd_mode = 0
        # we don't need the signalhandler anymore
        self.sshow_timer.stop()
        # reset bitmap cache
        self.bitmapcache = freevo.util.ObjectCache(3, desc='viewer')

    def _next(self):
        """
        Send PLAY_END to show next image.
        """
        event = freevo.Event(freevo.PLAY_END, self.item)
        event.set_handler(self.eventhandler)
        event.post()

    def view(self, item):
        """
        Show the image
        """
        self.eventmap = 'image'
        # Store item and playlist. We need to keep the playlist object
        # here to make sure it is not deleted when player is running in
        # the background.
        self.item = item
        self.playlist = self.item.get_playlist()
        if self.playlist:
            self.playlist.select(self.item)
        # update the screen
        self.cache(self.item)
        self.gui_context.image = self.bitmapcache[self.item.filename]
        self.gui_context.rotation = item.get('rotation') or 0
        self.gui_context.zoom = 1.0
        self.gui_context.pos = 0,0
        self.gui_context.menu = self.playlist
        self.status = freevo.STATUS_RUNNING
        # start timer
        if self.item.duration and self.slideshow and \
               not self.sshow_timer.active():
            self.sshow_timer.start(self.item.duration)
        # Notify everyone about the viewing
        freevo.PLAY_START.post(item)
        return None

    def stop(self):
        """
        Stop the current viewing
        """
        if self.status != freevo.STATUS_RUNNING:
            # already stopped
            return True
        # set status to stopping
        self.status = freevo.STATUS_STOPPING
        event = freevo.Event(freevo.PLAY_END, self.item)
        event.set_handler(self.eventhandler)
        event.post()

    def cache(self, item):
        """
        Cache the next image (most likely we need this)
        """
        if item.filename and len(item.filename) > 0 and \
               not self.bitmapcache[item.filename]:
            image = kaa.imlib2.Image(item.filename)
            self.bitmapcache[item.filename] = image

    def eventhandler(self, event):
        """
        Handle incoming events
        """
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

        if event == freevo.STOP:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == freevo.PLAYLIST_NEXT or event == freevo.PLAYLIST_PREV:
            # up and down will stop the slideshow and pass the
            # event to the playlist
            self.sshow_timer.stop()
            self.item.eventhandler(event)
            return True

        if event == freevo.PLAY_END:
            # Viewing is done, set application to stopped
            self.status = freevo.STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == freevo.STATUS_STOPPED:
                self.status = freevo.STATUS_IDLE
            return True

        if event == freevo.IMAGE_ROTATE:
            # rotate image
            if event.arg == 'left':
                self.gui_context.rotation = (self.gui_context.rotation + 270) % 360
            else:
                self.gui_context.rotation = (self.gui_context.rotation + 90) % 360
            return True

        if event in (freevo.ZOOM, freevo.ZOOM_IN, freevo.ZOOM_OUT):
            zoom = self.gui_context.zoom
            if event == freevo.ZOOM:
                self.gui_context.zoom = event.arg
            if event == freevo.ZOOM_IN:
                self.gui_context.zoom += event.arg
            if event == freevo.ZOOM_OUT:
                self.gui_context.zoom = max(1.0, self.gui_context.zoom + event.arg)
            if self.gui_context.zoom > 1.01:
                if zoom == 1.0:
                    self.eventmap = 'image_zoom'
                # update position based on scaling
                factor = float(self.gui_context.zoom) / zoom
                x, y = self.gui_context.pos
                self.gui_context.pos = int(x * factor), int(y * factor)
            else:
                if zoom > 1.0:
                    self.eventmap = 'image'
                self.gui_context.zoom = 1.0
                self.gui_context.pos = 0,0
            return True

        if event == freevo.IMAGE_MOVE:
            # move inside a zoomed image
            x, y = self.gui_context.pos
            self.gui_context.pos = x + event.arg[0], y + event.arg[1]
            return True

        if event == freevo.TOGGLE_OSD:
            # FIXME: update widget
            return True

        if event == freevo.IMAGE_SAVE:
            # FIXME
            return True

        # pass not handled event to the item
        return self.item.eventhandler(event)

# set viewer object
viewer = ImageViewer()
