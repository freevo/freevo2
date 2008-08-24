# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
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

# python imports
import logging

# gui imports
from application import Application

# get logging object
log = logging.getLogger('image')

class ImageViewer(Application):
    """
    Widget for the Imageviewer. This is the kaa.candy part of the application
    """
    freevo_appname = 'imageviewer'
    candyxml_style = 'simple'

    def __init__(self, widgets, context):
        """
        Create a new widget. While the imageviewer controller is a singleton
        an object of this class is created every time Freevo switches to
        the image viewer.
        """
        super(ImageViewer, self).__init__(widgets, context)
        self._view = None

    def _child_replace(self, old, new):
        """
        Replace child with a new one. This function is a callback from
        set_context. It is used for changing images.
        """
        if old.name == 'view':
            # replace view area with a fade animation
            old.animate(0.5, unparent=True).behave('opacity', old.opacity, 0)
            new.opacity = 0
            new.animate(0.5).behave('opacity', 0, 255)
            new.parent = self
            return
        super(ImageViewer, self)._child_replace(old, new)

    def _candy_prepare_render(self):
        """
        Prepare rendering
        """
        super(ImageViewer, self)._candy_prepare_render()
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
        super(ImageViewer, self).set_context(context)
        self._queue_rendering()

# register widget to kaa.candy
ImageViewer.candyxml_register()
