# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# viewer.py - Freevo image viewer
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
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

# kaa imports
import kaa.candy

# gui imports
from application import Application

# get logging object
log = logging.getLogger('image')

class ImageViewer(Application):
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
        super(ImageViewer, self).sync_context()

    # def _candy_replace_child(self, child, replace, context):
    #     """
    #     Replace child with a new one.
    #     """
    #     if child.name == 'view':
    #         # replace view area with a fade animation
    #         child.animate(0.5, unparent=True).behave('opacity', child.opacity, 0)
    #         replace.opacity = 0
    #         replace.animate(0.5).behave('opacity', 0, 255)
    #     super(ImageViewer, self)._candy_replace_child(child, replace, context)

    # def _candy_prepare(self):
    #     """
    #     Prepare rendering
    #     """
    #     super(ImageViewer, self)._candy_prepare()
    #     view = self.get_widget('view')
    #     if not view:
    #         # FIXME: this may happen if we scroll to fast. It has to
    #         # be a thread problem. This needs more investigation. Wild
    #         # guess: we ask for the widget the same time the clutter
    #         # thread is replacing it.
    #         return
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

    # def _candy_context_sync(self, context):
    #     """
    #     Set a new context.

    #     @param context: dict of context key,value pairs
    #     """
    #     super(ImageViewer, self)._candy_context_sync(context)
    #     # trigger new context evaluation
    #     self._candy_prepare()
