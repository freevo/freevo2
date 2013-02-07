# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Image viewer kaa.candy backend
# -----------------------------------------------------------------------------
# This file is imported by the backend process in the clutter
# mainloop. Importing and using clutter is thread-safe.
#
# It would have been possible to place this file in the gui
# subdirectory but it only belongs to this plugin and is a good
# example to to add backend code in plugins.
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2013 Dirk Meyer, et al.
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

__all__ = [ 'PhotoGroup' ]

# Python imports
import os
import tempfile
import random

# kaa imports
import kaa
import kaa.imlib2

# clutter imports
from gi.repository import Clutter as clutter
from gi.repository import GObject as gobject

# candy backend import
import candy

# register the thread pool for loading images
kaa.register_thread_pool('candy::photo', kaa.ThreadPool())

CENTER = clutter.Point()
CENTER.x = 0.5
CENTER.y = 0.5

class Widget(candy.Widget):
    """
    Backend widget class
    """
    def create(self):
        """
        Create the clutter object
        """
        self.obj = clutter.Group.new()
        self.obj.show()
        self.textures = {}
        self.current = None
        self.previous = None
        self.previous_animation = None

    @kaa.threaded('candy::photo')
    def loadimage_async(self, filename):
        """
        Load the image in an extra thread
        """
        # clutter has problems with large images and may
        # crash. Theerefore, we load the images using kaa.imlib2 and
        # scale them before loading them into clutter.
        i = kaa.imlib2.Image(filename)
        if float(self.width) / self.height < float(i.width) / i.height:
            i = i.scale((self.width, -1))
        else:
            i = i.scale((-1, self.height))
        fd, cachefile = tempfile.mkstemp(prefix='candy', suffix='.png', dir='/dev/shm')
        os.close(fd)
        i.save(cachefile)
        self.loadimage_clutter(filename, cachefile, i.width, i.height)

    @kaa.threaded(kaa.GOBJECT)
    def loadimage_clutter(self, filename, cachefile, width, height):
        """
        Load the image into a clutter texture
        """
        t = clutter.Texture.new()
        t.set_from_file(cachefile)
        os.unlink(cachefile)
        self.textures[filename] = t, width, height
        self.showimage()

    def start_animation_scale(self, duration, x, y, factor):
        """
        Animation function
        """
        self.current.set_scale(factor*5, factor*5)
        self.current.save_easing_state()
        self.current.set_easing_duration(duration)
        self.current.set_scale(factor, factor)
        self.current.restore_easing_state()
        if self.previous:
            self.previous.save_easing_state()
            self.previous.set_easing_duration(duration)
            self.previous.set_scale(0.1, 0.1)
            self.previous.restore_easing_state()

    def start_animation_move_x(self, duration, x, y, factor):
        """
        Animation function
        """
        self.current.set_property('x', x + self.width)
        self.current.save_easing_state()
        self.current.set_easing_duration(duration)
        self.current.set_property('x', x)
        self.current.restore_easing_state()
        if self.previous:
            self.previous.save_easing_state()
            self.previous.set_easing_duration(duration)
            self.previous.set_property('x', -self.width)
            self.previous.restore_easing_state()

    def start_animation_rotate(self, duration, x, y, factor):
        """
        Animation function
        """
        self.current.set_property('rotation-angle-x', 90)
        self.current.set_property('rotation-angle-y', 90)
        self.current.set_property('rotation-angle-z', self.rotation-90)
        self.current.save_easing_state()
        self.current.set_easing_duration(duration)
        self.current.set_property('rotation-angle-x', 0)
        self.current.set_property('rotation-angle-y', 0)
        self.current.set_property('rotation-angle-z', self.rotation)
        self.current.restore_easing_state()
        if self.previous:
            self.previous.save_easing_state()
            self.previous.set_easing_duration(duration / 2)
            self.previous.set_property('opacity', 0)
            self.previous.restore_easing_state()

    def start_animation_scale_move(self, duration, x, y, factor):
        """
        Animation function
        """
        if self.previous:
            self.previous.set_property('opacity', 0)
        self.current.set_property('scale_x', factor*5)
        self.current.set_property('scale_y', factor*5)
        self.current.set_property('x', x-self.width/5)
        self.current.set_property('y', y-self.height/5)
        self.current.set_property('opacity', 0)

        self.current.save_easing_state()
        self.current.set_easing_duration(200)
        self.current.set_property('opacity', 255)
        self.current.restore_easing_state()

        self.current.save_easing_state()
        self.current.set_easing_duration(duration*0.8)
        self.current.set_position(x, y)
        self.current.restore_easing_state()

        self.current.save_easing_state()
        self.current.set_easing_duration(duration/2)
        self.current.set_scale(factor*1.8, factor*1.8)
        self.current.restore_easing_state()

        self.current.save_easing_state()
        self.current.set_easing_delay(duration/2)
        self.current.set_easing_duration(duration/2)
        self.current.set_scale(factor, factor)
        self.current.restore_easing_state()

    def start_animation_rotation_x(self, duration, x, y, factor):
        """
        Animation function
        """
        self.current.set_property('rotation-angle-x', 90)
        self.current.animatev(clutter.AnimationMode.EASE_OUT_QUAD, duration, ['rotation-angle-x'], [ 0 ])
        if self.previous:
            self.previous.animatev(clutter.AnimationMode.EASE_OUT_QUAD, 200, ['opacity'], [ 0 ])

    def start_animation_rotation_y(self, duration, x, y, factor):
        """
        Animation function
        """
        self.current.set_property('rotation-angle-y', 90)
        self.current.animatev(clutter.AnimationMode.EASE_OUT_QUAD, duration, ['rotation-angle-y'], [ 0 ])
        if self.previous:
            self.previous.animatev(clutter.AnimationMode.EASE_OUT_QUAD, 200, ['opacity'], [ 0 ])

    def animation_finished(self):
        """
        Callback when the animation is finished
        """
        if self.previous:
            self.obj.remove_actor(self.previous)
        self.previous = None
        self.showimage()
        return False

    def showimage(self):
        """
        Show the current image (gobject thread)
        """
        if not self.textures.get(self.filename, None) or self.previous:
            # either not loaded or animation still in progress
            return
        width, height = self.textures[self.filename][1:]
        factor = 1
        if self.rotation in (90, 270):
            factor = min(float(self.width) / height, float(self.height) / width)
        if self.current != self.textures[self.filename][0]:
            # new photo
            if self.current:
                self.previous = self.current
            self.current, width, height = self.textures[self.filename]
            x = y = 0
            if width < self.width:
                x = (self.width - width) / 2
            if height < self.height:
                y = (self.height - height) / 2
            self.current.set_position(x, y)
            self.current.set_size(width, height)
            self.current.set_property('pivot-point', CENTER)
            self.current.set_property('opacity', 255)
            self.current.set_scale(factor, factor)
            self.current.set_property('rotation-angle-z', self.rotation)
            self.current_rotation = self.rotation
            if not self.previous or self.blend_mode == 'none':
                # fade in
                self.current.set_property('opacity', 0)
                self.current.save_easing_state()
                self.current.set_easing_duration(200)
                self.current.set_property('opacity', 255)
                self.current.restore_easing_state()
                if self.previous:
                    self.previous.save_easing_state()
                    self.previous.set_easing_duration(200)
                    self.previous.set_property('opacity', 0)
                    self.previous.restore_easing_state()
                    gobject.timeout_add(200, self.animation_finished)
            else:
                # transition between images
                duration = 1000
                if self.blend_mode == 'random':
                    a = self.previous_animation
                    while a == self.previous_animation:
                        a = random.choice([ a for a in dir(self) if a.startswith('start_animation') ])
                else:
                    a = 'start_animation_' + self.blend_mode
                self.previous_animation = a
                getattr(self, a)(duration, x, y, factor)
                gobject.timeout_add(duration, self.animation_finished)
            self.current.show()
            self.obj.add_actor(self.current)
        elif self.current_rotation != self.rotation:
            # rotation changed
            if self.rotation == 0 and self.current_rotation == 270:
                self.current.set_property('rotation-angle-z', -90)
            if self.rotation == 270 and self.current_rotation == 0:
                self.current.set_property('rotation-angle-z', 360)
            self.current.animatev(clutter.AnimationMode.EASE_OUT_QUAD, 200,
                   ['rotation-angle-z', 'scale_x', 'scale_y'],
                   [self.rotation, factor, factor])
            self.current_rotation = self.rotation

    def update(self, modified):
        """
        Render the widget (gobject thread)
        """
        super(Widget, self).update(modified)
        if 'cached' in modified:
            for f in self.cached:
                if not f in self.textures:
                    self.textures[f] = None
                    self.loadimage_async(f)
            for f in self.textures.keys()[:]:
                if not f in self.cached:
                    del self.textures[f]
        if 'filename' in modified or 'rotation' in modified:
            self.showimage()
        if 'width' in modified or 'height' in modified:
            self.obj.set_clip(0, 0, self.width, self.height)

