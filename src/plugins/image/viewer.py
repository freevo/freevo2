# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2011 Dirk Meyer, et al.
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

class Widget(gui.Application):
    """
    Widget for the Imageviewer. This is the kaa.candy part of the application
    """
    candyxml_style = 'imageviewer'

    __image = None
    __widget = None

    def show(self):
        self.sync_context()

    def sync_context(self):
        if self.context.image != self.__image:
            if self.__widget:
                self.__widget.parent = None
            self.__image = self.context.image
            self.__widget = kaa.candy.Image()
            self.__widget.image = self.__image
            self.__widget.xalign = self.__widget.yalign = kaa.candy.ALIGN_CENTER
            self.__widget.keep_aspect = True
            self.stage.add(self.__widget, layer=0)
        super(Widget, self).sync_context()

    #     if view is not self._view:
    #         self._zoom = 1.0
    #         self._rotation = 0
    #         self._view = view
    #         self._view.anchor_point = self.width / 2, self.height / 2
    #         self._pos = 0, 0
    #     animation = None
    #     # FIXME: if we do not zoom, we should upload a downscaled
    #     # version of the image to make it faster.
    #     if self._zoom != self.context.zoom:
    #         self._zoom = self.context.zoom
    #         animation = view.animate(0.2)
    #         animation.behave('scale', view.scale, (self._zoom, self._zoom))
    #     if self._pos != self.context.pos:
    #         if not animation:
    #             animation = view.animate(0.2)
    #         self._pos = self.context.pos
    #         animation.behave('move', (view.x, view.y), (-self._pos[0], -self._pos[1]))
    #     if self._rotation != self.context.rotation:
    #         self._rotation = self.context.rotation
    #         image = self.get_widget('image')
    #         image.rotation = self._rotation
    #         # Update image geometry. This is not a good solution but it helps
    #         # keeping the image in the view area. This is why there is a container
    #         # around the image widget: to keep everything working even when having
    #         # a rotated image.
    #         if self._rotation % 180:
    #             image.x = (self.width - self.height) / 2
    #             image.y = -image.x
    #             image.width, image.height = self.height, self.width
    #         else:
    #             image.x = image.y = 0
    #             image.width, image.height = self.width, self.height


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
        self.slideshow = True
        self.sshow_timer = kaa.OneShotTimer(self._next)
        self.signals['stop'].connect_weak(self._cleanup)

    def _cleanup(self):
        """
        Application not running anymore
        """
        self.osd_mode = 0
        # we don't need the signalhandler anymore
        self.sshow_timer.stop()

    def _next(self):
        """
        Send PLAY_END to show next image.
        """
        event = freevo.Event(freevo.PLAY_END, self.item)
        event.handler = self.eventhandler
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
        self.playlist = self.item.playlist
        if self.playlist:
            self.playlist.select(self.item)
        # update the screen
        self.context.image = self.item.filename
        self.context.rotation = item.get('rotation') or 0
        self.context.zoom = 1.0
        self.context.pos = 0,0
        self.context.menu = self.playlist
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
        event.handler = self.eventhandler
        event.post()

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
                self.context.rotation = (self.context.rotation + 270) % 360
            else:
                self.context.rotation = (self.context.rotation + 90) % 360
            return True

        if event in (freevo.ZOOM, freevo.ZOOM_IN, freevo.ZOOM_OUT):
            zoom = self.context.zoom
            if event == freevo.ZOOM:
                self.context.zoom = event.arg
            if event == freevo.ZOOM_IN:
                self.context.zoom += event.arg
            if event == freevo.ZOOM_OUT:
                self.context.zoom = max(1.0, self.context.zoom + event.arg)
            if self.context.zoom > 1.01:
                if zoom == 1.0:
                    self.eventmap = 'image_zoom'
                # update position based on scaling
                factor = float(self.context.zoom) / zoom
                x, y = self.context.pos
                self.context.pos = int(x * factor), int(y * factor)
            else:
                if zoom > 1.0:
                    self.eventmap = 'image'
                self.context.zoom = 1.0
                self.context.pos = 0,0
            return True

        if event == freevo.IMAGE_MOVE:
            # move inside a zoomed image
            x, y = self.context.pos
            self.context.pos = x + event.arg[0], y + event.arg[1]
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
