# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# area.py - An area template for the Freevo skin
# -----------------------------------------------------------------------------
# $Id$
#
# This file includes a template for an area used in the area code to draw
# images, info text, listing or something different. The areas itself are
# called by the AreaHandler defined in handler.py
#
# All areas used somewere in Freevo inherit from Area and only need to define
# an update function. The settings (theme) used in all areas are selected by
# the handler based on the current theme fxd file.
#
# The Area also defines helper drawing functions:
# drawbox(self, x, y, width, height, rect)
# drawimage(self, image, val, background=False)
# drawstring(self, text, font, content, x=-1, y=-1, width=None, height=None,
#            align_h = None, align_v = None, mode='hard', ellipses='...',
#            dim=True)
#
# TODO: o more cleanup here and in all areas used
#       o maybe make an area a widget
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

__all__ = [ 'Area' ]

# python imports
import copy
import os

# freevo imports
import config
import util

# gui imports
from gui.widgets import Rectangle, Text, Textbox, Image

import logging
log = logging.getLogger('gui')

class Area(object):
    """
    The base call for all areas. Each class inheriting from Area needs
    to define the update and the clear function.
    """
    def __init__(self, name):
        """
        Create an area. The area needs to have a 'name' to find the current
        settings in the theme definition.
        """
        self.area_name    = name
        self.screen       = None
        self.imagelib     = None
        self.__area       = None
        self.__layout     = None
        self.__background = []
        self.settings     = None

        
    def set_screen(self, screen):
        """
        Move this area to a new screen object.
        """
        if self.screen:
            self.clear_all()
        self.screen   = screen
        self.imagelib = screen.imagelib


    def update(self):
        """
        Update this area. The template has no content to draw.
        """
        pass


    def clear(self):
        """
        Clear the content objects.
        """
        pass


    def clear_all(self):
        """
        Clear the complete area. This clears the content and the background.
        """
        for b in self.__background:
            b.unparent()
        self.__background = []
        self.clear()


    def draw(self, settings, obj, viewitem, infoitem, area_definitions):
        """
        This is the main draw function. This function draws the background
        and calls the update function for the different types of areas.
        This function will be called by the AreaHandler.
        """
        if not self.screen:
            return

        self.menu     = obj
        self.viewitem = viewitem
        self.infoitem = infoitem

        try:
            # get the area based on the area name
            area = getattr(area_definitions, self.area_name)
        except AttributeError:
            try:
                # maybe areas is a special attribute
                area = area_definitions.areas[self.area_name]
            except (KeyError, AttributeError):
                # area defintions not found
                log.warning('no skin information for %s' % self.area_name)
                return

        if self.settings:
            self.settings.changed = False
            
        # check if the area definitions changed
        if (not self.__area) or area != self.__area:
            area.r = (area.x, area.y, area.width, area.height)
            self.__area = area
            # set layout
            self.__layout = area.layout
            if area.layout:
                # recalculate self.settings
                self.settings = self.__calc_geometry(area.layout.content)
                self.settings.images = area.images
                self.settings.changed = True
                self.settings.box_under_icon = settings.box_under_icon
                self.settings.icon_dir = settings.icon_dir
                
        elif area and self.__layout != area.layout:
            # set layout
            self.__layout = area.layout
            # recalculate self.settings
            self.settings = self.__calc_geometry(area.layout.content)
            self.settings.images = area.images
            self.settings.changed = True
            self.settings.box_under_icon = settings.box_under_icon
            self.settings.icon_dir = settings.icon_dir

        if not area.visible or not self.__layout:
            # not visible
            self.clear_all()
            return

        # set layer to background
        self.layer = self.screen.layer[0]
        # draw background
        self.__draw_background()
        # set layer to content
        self.layer = self.screen.layer[1]
        # draw content
        self.update()



    def __calc_geometry(self, obj, respect_area_geometry=True):
        """
        Calculate the real values of the obj (e.g. content) based
        on the geometry of the area.
        """
        obj = copy.copy(obj)
        font_h=0

        if isinstance(obj.width, str):
            obj.width = int(eval(obj.width, {'MAX': self.__area.width}))

        if isinstance(obj.height, str):
            obj.height = int(eval(obj.height,{'MAX': self.__area.height}))

        if isinstance(obj.x, str):
            obj.x = int(eval(obj.x, {'MAX':self.__area.height}))

        if isinstance(obj.y, str):
            obj.y = int(eval(obj.y, {'MAX':self.__area.height}))

        obj.x += self.__area.x
        obj.y += self.__area.y

        if not obj.width:
            obj.width = self.__area.width

        if not obj.height:
            obj.height = self.__area.height

        if respect_area_geometry:
            if obj.width + obj.x > self.__area.width + \
                   self.__area.x:
                obj.width = self.__area.width - obj.x

            if obj.height + obj.y > self.__area.height + \
                   self.__area.y:
                obj.height = self.__area.height + self.__area.y - obj.y

        return obj


    def __draw_background(self):
        """
        Draw the <background> of the area.
        """
        background_image = []
        background_rect  = []

        for bg in self.__layout.background:
            bg = self.__calc_geometry(bg, False)

            if bg.type == 'image' and bg.visible:
                # if this is the real background image, ignore the
                # OVERSCAN to fill the whole screen
                if bg.label == 'background':
                    bg.x -= config.GUI_OVERSCAN_X
                    bg.y -= config.GUI_OVERSCAN_Y
                    bg.width  += 2 * config.GUI_OVERSCAN_X
                    bg.height += 2 * config.GUI_OVERSCAN_Y
                if bg.label == 'watermark' and self.menu.selected.image:
                    imagefile = self.menu.selected.image
                else:
                    imagefile = bg.filename

                # set to 'background' to be added to that image list
                if bg.label != 'top':
                    bg.label = 'background'

                if imagefile:
                    background_image.append((imagefile, bg.x, bg.y, bg.width,
                                             bg.height, bg.alpha))

            elif bg.type == 'rectangle':
                background_rect.append((bg.x, bg.y, bg.width, bg.height,
                                        bg.bgcolor, bg.size, bg.color,
                                        bg.radius))


        for b in copy.copy(self.__background):
            # remove the background objects already on the screen
            try:
                # maybe it's a rectangle
                background_rect.remove(b.info)
            except ValueError:
                try:
                    # maybe it's an image
                    background_image.remove(b.info)
                except ValueError:
                    # not found, remove this old object
                    self.__background.remove(b)
                    b.unparent()

        for image in background_image:
            # add the new images to the screen
            imagefile, x, y, width, height, alpha = image
            i = self.drawimage(imagefile, (x, y, width, height),
                               background=True)
            if i:
                if alpha:
                    i.set_alpha(alpha)
                self.__background.append(i)
                i.info = image
                i.set_zindex(-1)

        for rec in background_rect:
            # add the new rectangles to the screen
            x, y, width, height, bgcolor, size, color, radius = rec
            box = self.drawbox(x, y, width, height, (bgcolor, size, color,
                                                     radius))
            self.__background.append(box)
            box.info = rec
            box.set_zindex(-1)



    def drawbox(self, x, y, width, height, rect):
        """
        Create a rectangle (gui.widgets.rectangle) and add it to the correct
        layer for drawing.
        """
        try:
            r = Rectangle((x, y), (width, height), rect.bgcolor, rect.size,
                          rect.color, rect.radius )
        except AttributeError, e:
            r = Rectangle((x, y), (width, height), rect[0], rect[1], rect[2],
                          rect[3])
        self.layer.add_child(r)
        return r


    def drawstring(self, text, font, settings, x=-1, y=-1, width=None,
                   height=None, align_h = None, align_v = None, mode='hard',
                   ellipses='...', dim=True):
        """
        Creates a text object (gui.widgets.text) and add it to the correct
        layer for drawing.
        """
        if not text:
            return None

        # set default values from 'settings'
        if x == -1:
            x = settings.x
        if y == -1:
            y = settings.y

        if width == None:
            width  = settings.width
        if height == None:
            height = settings.height

        if not align_h and settings:
            align_h = settings.align
        if not align_h:
            align_h = 'left'

        if not align_v and settings:
            align_v = settings.valign
        if not align_v:
            align_v = 'top'

        if height == -1:
            height = font.height

        t = Text(text, (x, y), (width, height), font, align_h, align_v, mode,
                 ellipses, dim)
        self.layer.add_child(t)
        return t



    def drawimage(self, image, val, background=False):
        """
        Create an image object (gui.widgets.image) and add it to the correct
        layer for drawing.
        """
        if not image:
            return None

        if isinstance(val, tuple):
            if len(val) == 2:
                x, y, w, h = val[0], val[1], image.width, image.height
            else:
                x, y, w, h = val[0], val[1], val[2], val[3]
        else:
            x, y, w, h = val.x, val.y, val.width, val.height

        if background:
            if not (x == 0 and y == 0 and w == self.screen.width and \
                    h == self.screen.height) and \
                    self.__area.x == x and self.__area.y == y and \
                    self.__area.width == w and \
                    self.__area.height == h:
                i = Image(image, (0, 0), (self.screen.width,
                                          self.screen.height))
                i.crop((x,y), (w,h))
                i.set_pos((x,y))
            else:
                i = Image(image, (x, y), (w, h))
        else:
            i = Image(image, (x, y), (w, h))
        self.layer.add_child(i)
        return i


    def __del__(self):
        """
        delete function of memory debugging
        """
        log.info('Delete Area %s' % self.area_name)
