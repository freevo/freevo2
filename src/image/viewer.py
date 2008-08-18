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
from kaa.strutils import to_unicode

# freevo imports
from freevo import plugin
from freevo.ui import config

# cache for loading images
from freevo.ui.util import ObjectCache

from freevo.ui.event import *
from freevo.ui.application import Application, STATUS_RUNNING, STATUS_STOPPING, \
     STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_FULLSCREEN

# get logging object
log = logging.getLogger('image')

# global viewer, will be set to the ImageViewer
viewer = None

config = config.image.viewer

if 'epydoc' in sys.modules:
    # make epydoc happy because gettext is not running
    __builtins__['_'] = lambda x: x


class ImageViewerWidget(Application.Widget):
    __application__ = 'imageviewer'
    candyxml_style  = 'simple'

    def __init__(self, widgets, context):
        super(ImageViewerWidget, self).__init__(widgets, context)
        self.zoom = 1.0
        self.update()

    def update(self):
        image = self.get_widget('view')
        if self.zoom != self.eval_context('zoom'):
            self.zoom = self.eval_context('zoom')
            image.animate(0.2).behave('scale', image.scale, (self.zoom, self.zoom))

    def set_context(self, context):
        super(ImageViewerWidget, self).set_context(context)
        self.update()


ImageViewerWidget.candyxml_register()

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

        self.osd_mode = 0    # Draw file info on the image
        self.bitmapcache = ObjectCache(3, desc='viewer')
        self.slideshow   = True
        self.filename    = None
        self.sshow_timer = kaa.OneShotTimer(self._next)
        self.signals['stop'].connect_weak(self._cleanup)


    def _cleanup(self):
        """
        Application not running anymore, free cache and remove items
        from the screen.
        """
        self.osd_mode = 0
        self.filename = None
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


    def view(self, item, rotation=0):
        """
        Show the image
        """
        self.set_eventmap('image')
        # FIXME: switch eventmap
        # self.set_eventmap('image_zoom')

        # Store item and playlist. We need to keep the playlist object
        # here to make sure it is not deleted when player is running in
        # the background.
        self.item = item
        self.playlist = self.item.get_playlist()
        if self.playlist:
            self.playlist.select(self.item)
        self.filename = item.filename

        # FIXME: preload image

        # update the screen
        self.gui_context['image'] = self.filename
        self.gui_context['rotation'] = 0
        self.gui_context['zoom'] = 1.0
        self.gui_update()
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
        # FIXME: preload next image
        return
        if item.filename and len(item.filename) > 0 and \
               not self.bitmapcache[item.filename]:
            image = imagelib.load(item.filename)
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
                rotation = (self.gui_context['rotation'] + 270) % 360
            else:
                rotation = (self.gui_context['rotation'] + 90) % 360
            # FIXME: update widget
            return True

        if event == ZOOM:
            self.gui_context['zoom'] = event.arg
            self.gui_update()
        if event == ZOOM_IN:
            self.gui_context['zoom'] += event.arg
            self.gui_update()
        if event == ZOOM_OUT:
            self.gui_context['zoom'] = max(1.0, self.gui_context['zoom'] + event.arg)
            self.gui_update()

        if event == TOGGLE_OSD:
            # FIXME: update widget
            return True

        if event == IMAGE_MOVE:
            # move inside a zoomed image
            coord = event.arg
            # FIXME: update widget
            return True

        if event == IMAGE_SAVE:
            # FIXME
            return True

        # pass not handled event to the item
        return self.item.eventhandler(event)

# set viewer object
if not 'epydoc' in sys.modules:
    viewer = ImageViewer()
