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
#       o do not import theme.py here
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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

# external modules
import mevas

# freevo imports
import config
import util

# gui imports
from gui import theme_engine as fxdparser
from gui import Rectangle, Text, Textbox, Image


class Area:
    """
    The base call for all areas. Each class inheriting from Area needs
    to define the update and the clear function.
    """
    def __init__(self, name):
        """
        Create an area. The area needs to have a 'name' to find the current
        settings in the theme definition.
        """
        self.area_name   = name
        self.area_values = None
        self.layout      = None
        self.name        = name
        self.screen      = None
        self.imagelib    = None
        self.__background__ = []


    def set_screen(self, screen, bg_layer, content_layer):
        """
        Move this area to a new screen object.
        """
        if self.screen:
            self.clear_all()
        self.screen   = screen
        self.imagelib = screen.imagelib
        self.bg_layer = bg_layer
        self.content_layer = content_layer


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
        if not self.screen:
            _debug_('ERROR in area %s: no screen defined' % self.name)
            return

        for b in self.__background__:
            b.unparent()
        self.__background__ = []
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

        self.__init_vars(settings, area_definitions)

        if not self.area_values.visible or not self.layout:
            self.clear_all()
            return

        self.layer = self.bg_layer
        self.__draw_background()
        self.layer = self.content_layer
        self.update()



    def calc_geometry(self, object, copy_object=0):
        """
        Calculate the real values of the object (e.g. content) based
        on the geometry of the area.
        """
        if copy_object:
            object = copy.copy(object)

        font_h=0

        if isinstance(object.width, str):
            object.width = int(eval(object.width,
                                    {'MAX': self.area_values.width}))

        if isinstance(object.height, str):
            object.height = int(eval(object.height,
                                     {'MAX': self.area_values.height}))

        if isinstance(object.x, str):
            object.x = int(eval(object.x, {'MAX':self.area_values.height}))

        if isinstance(object.y, str):
            object.y = int(eval(object.y, {'MAX':self.area_values.height}))

        object.x += self.area_values.x
        object.y += self.area_values.y

        if not object.width:
            object.width = self.area_values.width

        if not object.height:
            object.height = self.area_values.height

        if object.width + object.x > self.area_values.width + \
               self.area_values.x:
            object.width = self.area_values.width - object.x

        if object.height + object.y > self.area_values.height + \
               self.area_values.y:
            object.height = self.area_values.height + self.area_values.y - \
                            object.y

        return object


    def get_item_rectangle(self, rectangle, item_w, item_h):
        """
        Calculates the values for a rectangle to fit item_w and item_h
        inside it.
        """
        r = copy.copy(rectangle)

        # get the x and y value, based on MAX
        if isinstance(r.x, str):
            r.x = int(eval(r.x, {'MAX':item_w}))
        if isinstance(r.y, str):
            r.y = int(eval(r.y, {'MAX':item_h}))

        # set rect width and height to something
        if not r.width:
            r.width = item_w

        if not r.height:
            r.height = item_h

        # calc width and height based on MAX settings
        if isinstance(r.width, str):
            r.width = int(eval(r.width, {'MAX':item_w}))

        if isinstance(r.height, str):
            r.height = int(eval(r.height, {'MAX':item_h}))

        # correct item_w and item_h to fit the rect
        item_w = max(item_w, r.width)
        item_h = max(item_h, r.height)
        if r.x < 0:
            item_w -= r.x
        if r.y < 0:
            item_h -= r.y

        # return needed width and height to fit original width and height
        # and the rectangle attributes
        return max(item_w, r.width), max(item_h, r.height), r



    def __init_vars(self, settings, area):
        """
        Check which layout is used and set variables for the object
        """
        self.settings = settings

        try:
            area = getattr(area, self.area_name)
        except AttributeError:
            try:
                area = area.areas[self.area_name]
            except (KeyError, AttributeError):
                _debug_('no skin information for %s' % (self.area_name), )
                area = fxdparser.Area(self.area_name)
                area.visible = False

        if (not self.area_values) or area != self.area_values:
            area.r = (area.x, area.y, area.width, area.height)
            self.area_values = area

        self.layout = area.layout
        return


    def __draw_background(self):
        """
        Draw the <background> of the area.
        """
        area   = self.area_values

        background_image = []
        background_rect  = []

        for bg in self.layout.background:
            bg = copy.copy(bg)
            if isinstance(bg, fxdparser.Image) and bg.visible:
                self.calc_geometry(bg)
                imagefile = ''

                # if this is the real background image, ignore the
                # OVERSCAN to fill the whole screen
                if bg.label == 'background':
                    bg.x -= config.OSD_OVERSCAN_X
                    bg.y -= config.OSD_OVERSCAN_Y
                    bg.width  += 2 * config.OSD_OVERSCAN_X
                    bg.height += 2 * config.OSD_OVERSCAN_Y
                if bg.label == 'watermark' and self.menu.selected.image:
                    imagefile = self.menu.selected.image
                else:
                    imagefile = bg.filename

                # set to 'background' to be added to that image list
                if bg.label != 'top':
                    bg.label = 'background'

                if imagefile:
                    background_image.append((imagefile, bg.x, bg.y, bg.width,
                                             bg.height))

            elif isinstance(bg, fxdparser.Rectangle):
                self.calc_geometry(bg)
                background_rect.append((bg.x, bg.y, bg.width, bg.height,
                                        bg.bgcolor, bg.size, bg.color,
                                        bg.radius))


        for b in copy.copy(self.__background__):
            try:
                background_rect.remove(b.info)
            except ValueError:
                try:
                    background_image.remove(b.info)
                except ValueError:
                    self.__background__.remove(b)
                    b.unparent()

        for rec in background_rect:
            x, y, width, height, bgcolor, size, color, radius = rec
            box = self.drawbox(x, y, width, height, (bgcolor, size, color,
                                                     radius))
            self.__background__.append(box)
            box.info = rec
            box.set_zindex(-1)

        for image in background_image:
            imagefile, x, y, width, height = image
            i = self.drawimage(imagefile, (x, y, width, height),
                               background=True)
            if i:
                self.__background__.append(i)
                i.info = image
                i.set_zindex(-1)



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


    def drawstring(self, text, font, content, x=-1, y=-1, width=None,
                   height=None, align_h = None, align_v = None, mode='hard',
                   ellipses='...', dim=True):
        """
        Creates a text object (gui.widgets.text) and add it to the correct
        layer for drawing.
        """
        if not text:
            return None

        # set default values from 'content'
        if x == -1:
            x = content.x
        if y == -1:
            y = content.y

        if width == None:
            width  = content.width
        if height == None:
            height = content.height

        if not align_h and content:
            align_h = content.align
        if not align_h:
            align_h = 'left'

        if not align_v and content:
            align_v = content.valign
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

        # FIXME: that doesn't belong here
        # if isstring(image) and image.find(config.ICON_DIR) == 0 and \
        #        image.find(self.settings.icon_dir) == -1:
        #     # replace the icon
        #     new_image = os.path.join(self.settings.icon_dir,
        #                 image[len(config.ICON_DIR)+1:])
        #     if os.path.isfile(new_image):
        #         image = new_image
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
                    self.area_values.x == x and self.area_values.y == y and \
                    self.area_values.width == w and \
                    self.area_values.height == h:
                i = Image(image, (0, 0), (self.screen.width,
                                          self.screen.height))
                i.crop((x,y), (w,h))
                i.set_pos((x,y))
            else:
                i = Image(image, (x, y), (w, h))
            self.layer.add_child(i)
        else:
            i = Image(image, (x, y), (w, h))
            self.layer.add_child(i)
        return i


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('Area', self.name)
