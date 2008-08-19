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

# cache for loading images
from freevo.ui.util import ObjectCache

from freevo.ui.event import *
from freevo.ui.application import Application, STATUS_RUNNING, STATUS_STOPPING, \
     STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_FULLSCREEN

# get logging object
log = logging.getLogger('image')

# global viewer, will be set to the ImageViewer
viewer = None


class ImageViewerWidget(Application.Widget):
    """
    Widget for the Imageviewer. This is the kaa.candy part of the application
    """
    __application__ = 'imageviewer'
    candyxml_style  = 'simple'

    def __init__(self, widgets, context):
        """
        Create a new widget. While the imageviewer controller is a singleton
        an object of this class is created every time Freevo switches to
        the image viewer.
        """
        super(ImageViewerWidget, self).__init__(widgets, context)
        self._view = None

    def _child_replace(self, old, new):
        """
        Replace child with a new one. This function is a callback from
        set_context. It is used for changing images.
        """
        if old.name == 'view':
            # replace view area with a fade animation
            old.animate(0.5, unparent=True).behave('opacity', 255, 0)
            new.opacity = 0
            new.animate(0.5).behave('opacity', 0, 255)
            new.parent = self
            return
        super(ImageViewerWidget, self)._child_replace(old, new)

    def _candy_prepare_render(self):
        """
        Prepare rendering
        """
        super(ImageViewerWidget, self)._candy_prepare_render()
        view = self.get_widget('view')
        if view is not self._view:
            self._zoom = 1.0
            self._rotation = 0
            self._view = view
            self._view.anchor_point = self.width / 2, self.height / 2
            self._pos = 0, 0
        animation = None
        if self._zoom != self.eval_context('zoom'):
            self._zoom = self.eval_context('zoom')
            animation = view.animate(0.2)
            animation.behave('scale', view.scale, (self._zoom, self._zoom))
        if self._pos != self.eval_context('pos'):
            if not animation:
                animation = view.animate(0.2)
            self._pos = self.eval_context('pos')
            animation.behave('move', (view.x, view.y), (-self._pos[0], -self._pos[1]))
        if self._rotation != self.eval_context('rotation'):
            self._rotation = self.eval_context('rotation')
            image = self.get_widget('image')
            image.rotation = self._rotation
            # Update image geometry. This is not a good solution but it helps
            # keeping the image in the view area. This is why there is a container
            # around the image widget: to keep everything working even when having
            # a rotated image.
            if self._rotation % 180:
                image.x = (self.width - self.height) / 2
                image.y = -image.x
                image.width, image.height = self.height, self.width
            else:
                image.x = image.y = 0
                image.width, image.height = self.width, self.height

    def set_context(self, context):
        """
        Set a new context.
        """
        super(ImageViewerWidget, self).set_context(context)
        self._queue_sync(rendering=True)


class ImageViewer(Application):
    """
    Full screen image viewer for imageitems
    """
    def __init__(self):
        """
        create an image viewer application
        """
        capabilities = (CAPABILITY_TOGGLE, CAPABILITY_FULLSCREEN)
        Application.__init__(self, 'imageviewer', 'image', capabilities)
        self.osd_mode = 0
        self.bitmapcache = ObjectCache(3, desc='viewer')
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
        self.bitmapcache = ObjectCache(3, desc='viewer')

    def _next(self):
        """
        Send PLAY_END to show next image.
        """
        event = Event(PLAY_END, self.item)
        event.set_handler(self.eventhandler)
        event.post()

    def view(self, item):
        """
        Show the image
        """
        self.set_eventmap('image')
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
        self.status = STATUS_RUNNING
        # start timer
        if self.item.duration and self.slideshow and \
               not self.sshow_timer.active():
            self.sshow_timer.start(self.item.duration)
        # Notify everyone about the viewing
        PLAY_START.post(item)
        return None

    def stop(self):
        """
        Stop the current viewing
        """
        if self.get_status() != STATUS_RUNNING:
            # already stopped
            return True
        # set status to stopping
        self.status = STATUS_STOPPING
        event = Event(PLAY_END, self.item)
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
        if event == PAUSE or event == PLAY:
            if self.slideshow:
                OSD_MESSAGE.post(_('pause'))
                self.slideshow = False
                self.sshow_timer.stop()
            else:
                OSD_MESSAGE.post(_('play'))
                self.slideshow = True
                self.sshow_timer.start(1)
            return True

        if event == STOP:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == PLAYLIST_NEXT or event == PLAYLIST_PREV:
            # up and down will stop the slideshow and pass the
            # event to the playlist
            self.sshow_timer.stop()
            self.item.eventhandler(event)
            return True

        if event == PLAY_END:
            # Viewing is done, set application to stopped
            self.status = STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == STATUS_STOPPED:
                self.status = STATUS_IDLE
            return True

        if event == IMAGE_ROTATE:
            # rotate image
            if event.arg == 'left':
                self.gui_context.rotation = (self.gui_context.rotation + 270) % 360
            else:
                self.gui_context.rotation = (self.gui_context.rotation + 90) % 360
            return True

        if event in (ZOOM, ZOOM_IN, ZOOM_OUT):
            zoom = self.gui_context.zoom
            if event == ZOOM:
                self.gui_context.zoom = event.arg
            if event == ZOOM_IN:
                self.gui_context.zoom += event.arg
            if event == ZOOM_OUT:
                self.gui_context.zoom = max(1.0, self.gui_context.zoom + event.arg)
            if self.gui_context.zoom > 1.01:
                if zoom == 1.0:
                    self.set_eventmap('image_zoom')
                # update position based on scaling
                factor = float(self.gui_context.zoom) / zoom
                x, y = self.gui_context.pos
                self.gui_context.pos = int(x * factor), int(y * factor)
            else:
                if zoom > 1.0:
                    self.set_eventmap('image')
                self.gui_context.zoom = 1.0
                self.gui_context.pos = 0,0
            return True

        if event == IMAGE_MOVE:
            # move inside a zoomed image
            x, y = self.gui_context.pos
            self.gui_context.pos = x + event.arg[0], y + event.arg[1]
            return True

        if event == TOGGLE_OSD:
            # FIXME: update widget
            return True

        if event == IMAGE_SAVE:
            # FIXME
            return True

        # pass not handled event to the item
        return self.item.eventhandler(event)


# register widget to kaa.candy
ImageViewerWidget.candyxml_register()

# set viewer object
viewer = ImageViewer()
