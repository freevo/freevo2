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

import config
import util

import gui.fxdparser as fxdparser
from gui import Rectangle, Text, Image


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
        self.objects     = SkinObjects()
        self.NEW_STYLE   = True

        self.__background__ = []
        
        self.imagecache = util.objectcache.ObjectCache(imagecachesize,
                                                       desc='%s_image' % self.name)
        self.Rectangle = fxdparser.Rectangle
        self.Image     = fxdparser.Image


    def set_screen(self, screen):
        """
        move this area to a new screen object
        """
        if self.screen:
            self.clear_all()
        self.screen = screen

        
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
        if self.NEW_STYLE:
            for b in self.__background__:
                self.screen.remove(b)
            self.__background__ = []
            self.clear()
        else:
            try:
                for o in self.objects.bgimages:
                    self.screen.remove(o)
                for o in self.objects.rectangles:
                    self.screen.remove(o)
                for o in self.objects.images:
                    self.screen.remove(o)
                for o in self.objects.text:
                    self.screen.remove(o)
            except Exception, e:
                print e
            self.objects = SkinObjects()
            

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
            print 'FIXME area.py:', self.area_values.name

        if not self.area_values.visible or not self.layout:
            self.clear_all()
            return

        if self.NEW_STYLE:
            self.__draw_background__()
            self.update()
            return

        
        self.tmp_objects = SkinObjects()
        redraw = self.__draw_background__() or redraw

        # dependencies haven't changed, if no update needed: return
        if not redraw and not self.update_content_needed():
            return

        self.update_content()

        for b in self.tmp_objects.bgimages:
            try:
                self.objects.bgimages.remove(b)
            except:
                self.screen.add(b)

        for b in self.objects.bgimages:
            self.screen.remove(b)


        for b in self.tmp_objects.rectangles:
            try:
                self.objects.rectangles.remove(b)
            except:
                self.screen.add(b)

        for b in self.objects.rectangles:
            self.screen.remove(b)


        for b in self.tmp_objects.images:
            try:
                self.objects.images.remove(b)
            except:
                self.screen.add(b)

        for b in self.objects.images:
            self.screen.remove(b)


        for b in self.tmp_objects.text:
            try:
                self.objects.text.remove(b)
            except Exception, e:
                self.screen.add(b)

        for b in self.objects.text:
            self.screen.remove(b)

        # save and exit
        self.objects = self.tmp_objects


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

        if self.area_name == 'plugin':
            if not self.area_values:
                self.area_values = fxdparser.Area(self.area_name)
                self.area_values.visible = True
                self.area_values.r = (0, 0, self.screen.width, self.screen.height)
            return True
        else:
            try:
                area = getattr(area, self.area_name)
            except AttributeError:
                try:
                    area = area.areas[self.area_name]
                except (KeyError, AttributeError):
                    print 'no skin information for %s' % (self.area_name)
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
                    background_image.append((imagefile, bg.x, bg.y, bg.width, bg.height))

            elif isinstance(bg, fxdparser.Rectangle):
                self.calc_geometry(bg)
                background_rect.append((bg.x, bg.y, bg.width, bg.height, bg.bgcolor,
                                        bg.size, bg.color, bg.radius))

        if self.NEW_STYLE:
            for b in copy.copy(self.__background__):
                try:
                    background_rect.remove(b.info)
                except ValueError:
                    try:
                        background_image.remove(b.info)
                    except ValueError:
                        self.__background__.remove(b)
                        self.screen.remove(b)
                    
            for rec in background_rect:
                x, y, width, height, bgcolor, size, color, radius = rec
                box = self.drawbox(x, y, width, height, (bgcolor, size, color, radius))
                self.__background__.append(box)
                box.info = rec

                
            for image in background_image:
                imagefile, x, y, width, height = image
                i = self.screen.renderer.loadbitmap(imagefile, self.imagecache,
                                                    width, height, True)
                if i:
                    i = self.drawimage(i, (x, y, width, height), background=True)
                    self.__background__.append(i)
                    i.info = image
                    


        else:
            for x, y, width, height, bgcolor, size, color, radius in background_rect:
                self.drawbox(x, y, width, height, (bgcolor, size, color, radius))

            for imagefile, x, y, width, height in background_image:
                i = self.screen.renderer.loadbitmap(imagefile, self.imagecache,
                                                    width, height, True)
                if i:
                    self.drawimage(i, (x, y, width, height), background=True)
                            
        return redraw
            


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
            r = Rectangle(x, y, x + width, y + height, rect.bgcolor, rect.size,
                          rect.color, rect.radius )
        except AttributeError:
            r = Rectangle(x, y, x + width, y + height, rect[0], rect[1], rect[2], rect[3])

        r.layer = -3
        if self.NEW_STYLE:
            self.screen.add(r)
        else: 
            self.tmp_objects.rectangles.append(r)
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

        height2 = height
        if height2 == -1:
            height2 = font.h + 2

        t = Text(x, y, x+width, y+height2, text, font, height,
                 align_h, align_v, mode, ellipses, dim)

        if self.NEW_STYLE:
            self.screen.add(t)
        else: 
            self.tmp_objects.text.append(t)
        return t

    

    def loadimage(self, image, val):
        """
        load an image (use self.imagecache)
        """
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

        return self.screen.renderer.loadbitmap(image, self.imagecache, w, h)

        
    def drawimage(self, image, val, background=False):
        """
        draws an image ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """
        if not image:
            return None

        if isstring(image):
            if isinstance(val, tuple):
                image = self.loadimage(String(image), val[2:])
            else:
                image = self.loadimage(String(image), val)

        if not image:
            return None
        
        if isinstance(val, tuple):
            i = Image(val[0], val[1], val[0] + image.get_width(),
                      val[1] + image.get_height(), image)
            if self.NEW_STYLE:
                if background:
                    i.layer = -5
                self.screen.add(i)
                return i

            if background:
                i.layer = -5
                self.tmp_objects.bgimages.append(i)
            else:
                self.tmp_objects.images.append(i)
            return i

        i = Image(val.x, val.y, val.x + val.width, val.y + val.height, image)
        if self.NEW_STYLE:
            self.screen.add(i)
        else:
            self.tmp_objects.images.append(i)
        return i
        

