# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# area.py - An area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
#
# This is the main class for all area.
#
# If you want to create a new Area, please keep my problems in mind:
#
#
# 1. Not all areas are visible at the same time, some areas may change
#    the settings and others don't
# 2. The listing and the view area can overlap, at the next item the image
#    may be gone
# 3. alpha layers are slow to blit on a non alpha surface.
# 4. the blue_round1 draws two alpha masks, one for the listing, one
#    for the view area. They overlap, but the overlapping area
#    shouldn't be an addition of the transparent value
# 5. If you drop an alpha layer on the screen, you can't get the original
#    background back by making a reverse alpha layer.
#
# For more informations contact me (dmeyer@tzi.de)
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.14  2004/09/07 18:47:10  dischi
# each area has it's own layer (CanvasContainer) now
#
# Revision 1.13  2004/08/27 14:17:15  dischi
# remove old plugin code
#
# Revision 1.12  2004/08/26 18:13:18  dischi
# always use Text not Textbox
#
# Revision 1.11  2004/08/26 15:29:18  dischi
# make the tv guide work again (but very slow)
#
# Revision 1.10  2004/08/24 16:42:41  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.9  2004/08/23 12:36:09  dischi
# crop bg image if the screen area is smaller than the screen
#
# Revision 1.8  2004/08/22 20:06:18  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.7  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
#
# Revision 1.6  2004/08/05 17:30:24  dischi
# cleanup
#
# Revision 1.5  2004/07/27 18:52:30  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.4  2004/07/25 18:17:34  dischi
# interface update
#
# Revision 1.3  2004/07/24 17:49:05  dischi
# interface cleanup
#
# Revision 1.2  2004/07/24 12:21:30  dischi
# use new renderer and screen features
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.1  2004/07/16 19:51:54  dischi
# new screen design test code, read future_ideas
#
# Revision 1.41  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.40  2004/04/25 12:38:22  dischi
# move idlebar image to background
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# -----------------------------------------------------------------------


import copy
import os

import mevas

import config
import util

# FIXME: this is really bad, correct this so fxdparser a.k.a theme
# is not needed anymore
from gui import theme_engine as fxdparser
from gui import Rectangle, Text, Textbox, Image


class SkinObjects:
    """
    object which stores the different types of objects
    an area wants to draw
    """
    def __init__(self):
        self.bgimages   = []
        self.rectangles = []
        self.images     = []
        self.text       = []


class Geometry:
    """
    Simple object with x, y, with, height values
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height


class CanvasContainer(mevas.CanvasContainer):
    def __init__(self, name):
        self.name = name
        mevas.CanvasContainer.__init__(self)

    def __str__(self):
        return 'AreaContainer %s' % self.name

    
class Area:
    """
    the base call for all areas. Each child needs two functions:

    def update_content_needed
    def update_content
    """
    def __init__(self, name, imagecachesize=5):
        self.area_name   = name
        self.area_values = None
        self.layout      = None
        self.name        = name
        self.screen      = None
        self.imagelib    = None
        self.objects     = SkinObjects()
        self.layer       = CanvasContainer(name)
        if name == 'screen':
            self.layer.set_zindex(-10)
        self.__background__ = []
        self.imagecache = util.objectcache.ObjectCache(imagecachesize,
                                                       desc='%s_image' % self.name)


    def set_screen(self, screen):
        """
        move this area to a new screen object
        """
        if self.screen:
            self.clear_all()
        self.screen   = screen
        self.imagelib = screen.imagelib

        
    def update_content_needed(self):
        """
        this area needs a content update
        """
        return True


    def update_content(self):
        """
        there is no content in this area
        """
        return True
    

    def update(self):
        """
        there is no content in this area
        """
        pass
    

    def clear(self):
        """
        clear the content objects
        """
        pass


    def clear_all(self):
        if not self.screen:
            _debug_('ERROR in area %s: no screen defined' % self.name)
            return

        for b in self.__background__:
            b.unparent()
        self.__background__ = []
        self.clear()
            

    def draw(self, settings, obj, viewitem, infoitem, area_definitions):
        """
        this is the main draw function. This function draws the background,
        checks if redraws are needed and calls the two update functions
        for the different types of areas
        """
        if not self.screen:
            return

        self.menu     = obj
        self.viewitem = viewitem
        self.infoitem = infoitem
            
        if self.area_values:
            visible = self.area_values.visible
        else:
            visible = False

        redraw = self.init_vars(settings, area_definitions)

        # maybe we are NOW invisible
        if visible and not self.area_values.visible:
            _debug_('FIXME: handle %s' % self.area_values.name, 0)

        if not self.area_values.visible or not self.layout:
            self.clear_all()
            return


        self.__draw_background__()
        self.update()



    def calc_geometry(self, object, copy_object=0):
        """
        calculate the real values of the object (e.g. content) based
        on the geometry of the area
        """
        if copy_object:
            object = copy.copy(object)

        font_h=0

        if isinstance(object.width, str):
            object.width = int(eval(object.width, {'MAX':self.area_values.width}))

        if isinstance(object.height, str):
            object.height = int(eval(object.height, {'MAX':self.area_values.height}))

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

        if object.width + object.x > self.area_values.width + self.area_values.x:
            object.width = self.area_values.width - object.x

        if object.height + object.y > self.area_values.height + self.area_values.y:
            object.height = self.area_values.height + self.area_values.y - object.y

        return object

        
    def get_item_rectangle(self, rectangle, item_w, item_h):
        """
        calculates the values for a rectangle to fit item_w and item_h
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
    


    def init_vars(self, settings, area):
        """
        check which layout is used and set variables for the object
        """
        redraw = False
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
            self.area_values = area
            redraw = True

        if not area.layout:
            return redraw

        old_layout  = self.layout
        self.layout = area.layout

        if old_layout and old_layout != self.layout:
            redraw = True

        area.r = (area.x, area.y, area.width, area.height)

        return redraw
        

    def __draw_background__(self):
        """
        draw the <background> of the area
        """
        area   = self.area_values
        redraw = True

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
                    redraw    = True    # bg changed
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
                background_rect.append((bg.x, bg.y, bg.width, bg.height, bg.bgcolor,
                                        bg.size, bg.color, bg.radius))


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
            box = self.drawbox(x, y, width, height, (bgcolor, size, color, radius))
            self.__background__.append(box)
            box.info = rec
            box.set_zindex(-1)
            
        for image in background_image:
            imagefile, x, y, width, height = image
            i = self.drawimage(imagefile, (x, y, width, height), background=True)
            if i:
                self.__background__.append(i)
                i.info = image
                i.set_zindex(-1)
            


    # functions for the area to draw stuff on the screen
    #
    # drawbox
    # drawimage
    # drawstring

    def drawbox(self, x, y, width, height, rect):
        """
        draw a round box ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """
        try:
            r = Rectangle((x, y), (width, height), rect.bgcolor, rect.size,
                          rect.color, rect.radius )
        except AttributeError, e:
            r = Rectangle((x, y), (width, height), rect[0], rect[1], rect[2], rect[3])

        self.layer.add_child(r)
        return r
    
            
    def drawstring(self, text, font, content, x=-1, y=-1, width=None, height=None,
                   align_h = None, align_v = None, mode='hard', ellipses='...',
                   dim=True):
        """
        writes a text ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
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

        t = Text(text, (x, y), (width, height), font, align_h, align_v, mode, ellipses, dim)
        self.layer.add_child(t)
        return t

    

    def loadimage(self, image, val):
        """
        load an image (use self.imagecache)
        """
        return None
        if image.find(config.ICON_DIR) == 0 and image.find(self.settings.icon_dir) == -1:
            new_image = os.path.join(self.settings.icon_dir, image[len(config.ICON_DIR)+1:])
            if os.path.isfile(new_image):
                image = new_image

        if isinstance(val, tuple) or isinstance(val, list):
            w = val[0]
            h = val[1]
        else:
            w = val.width
            h = val.height

        if w == -1:
            w = None
        if h == -1:
            h = None

        if h == None and w == None:
            return None

        return self.imagelib.load(image, (w, h), self.imagecache)

        
    def drawimage(self, image, val, background=False):
        """
        draws an image ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """
        if not image:
            return None

        # FIXME: that doesn't belong here
        if isstring(image) and image.find(config.ICON_DIR) == 0 and \
               image.find(self.settings.icon_dir) == -1:
            # replace the icon
            new_image = os.path.join(self.settings.icon_dir, image[len(config.ICON_DIR)+1:])
            if os.path.isfile(new_image):
                image = new_image

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
                    self.area_values.width == w and self.area_values.height == h:
                i = Image(image, (0, 0), (self.screen.width, self.screen.height))
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
