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
# If you want to create a new Skin_Area, please keep my problems in mind:
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



class Skin_Area:
    """
    the base call for all areas. Each child needs two functions:

    def update_content_needed
    def update_content
    """
    def __init__(self, name, imagecachesize=5):
        self.area_name = name
        self.area_val  = None
        self.layout    = None
        self.name      = name
        self.screen    = None
        self.objects   = SkinObjects()
        
        self.imagecache = util.objectcache.ObjectCache(imagecachesize,
                                                       desc='%s_image' % self.name)


    def set_screen(self, screen):
        """
        move this area to a new screen object
        """
        if self.screen:
            self.clear()
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
        pass
    

    def clear(self):
        if not self.screen:
            return
        try:
            for o in self.objects.bgimages:
                self.screen.remove('bg', o)
            for o in self.objects.rectangles:
                self.screen.remove('alpha', o)
            for o in self.objects.images:
                self.screen.remove('content', o)
            for o in self.objects.text:
                self.screen.remove('content', o)
        except:
            pass
        self.objects = SkinObjects()
            

    def draw(self, settings, obj, menu, display_style=0, widget_type='menu'):
        """
        this is the main draw function. This function draws the background,
        checks if redraws are needed and calls the two update functions
        for the different types of areas
        """
        if not self.screen:
            return

        self.display_style = display_style
        self.xml_settings  = settings
        self.widget_type   = widget_type

        self.menuw = obj
        if menu:
            self.menu = menu
            if self.menu.force_skin_layout != -1:
                self.display_style = self.menu.force_skin_layout
            
            if self.menu.viewitem:
                self.viewitem = self.menu.viewitem
            else:
                self.viewitem  = self.menu.selected
            if self.menu.infoitem:
                self.infoitem = self.menu.infoitem
            else:
                self.infoitem  = self.menu.selected
            item_type  = self.menu.item_types
            self.scan_for_text_view(self.menu)

        else:
            self.menu = obj
            item_type = None
            try:
                self.viewitem = obj.selected
                self.infoitem = obj.selected
            except AttributeError:
                self.viewitem = obj
                self.infoitem = obj

        area = self.area_val
        if area:
            visible = area.visible
        else:
            visible = False

        redraw = self.init_vars(settings, item_type, widget_type)
        area   = self.area_val

        # maybe we are NOW invisible
        if visible and not area.visible:
            print 'FIXME area.py:', area.name

        if not self.area_name == 'plugin':
            if not area.visible or not self.layout:
                self.clear()
                return

            self.tmp_objects = SkinObjects()
            redraw = self.__draw_background__() or redraw
        else:
            self.tmp_objects = SkinObjects()
            
        # dependencies haven't changed, if no update needed: return
        if not redraw and not self.update_content_needed():
            return

        self.update_content()

        for b in self.tmp_objects.bgimages:
            try:
                self.objects.bgimages.remove(b)
            except:
                self.screen.add('bg', b)

        for b in self.objects.bgimages:
            self.screen.remove('bg', b)


        for b in self.tmp_objects.rectangles:
            try:
                self.objects.rectangles.remove(b)
            except:
                self.screen.add('alpha', b)

        for b in self.objects.rectangles:
            self.screen.remove('alpha', b)


        for b in self.tmp_objects.images:
            try:
                self.objects.images.remove(b)
            except:
                self.screen.add('content', b)

        for b in self.objects.images:
            self.screen.remove('content', b)


        for b in self.tmp_objects.text:
            try:
                self.objects.text.remove(t)
            except:
                self.screen.add('content', b)

        for b in self.objects.text:
            self.screen.remove('content', b)

        # save and exit
        self.objects = self.tmp_objects


    def scan_for_text_view(self, menu):
        """
        scan if we have to fall back to text view. This will be done if some
        items have images and all images are the same. And the number of items
        must be greater 5. With that the skin will fall back to text view for
        e.g. mp3s inside a folder with cover file
        """
        try:
            self.use_text_view = menu.skin_force_text_view
            try:
                self.use_images      = menu.skin_default_has_images
                self.use_description = menu.skin_default_has_description
            except:
                self.use_images      = False
                self.use_description = False
            return
        except:
            pass

        image  = None
        folder = 0

        menu.skin_default_has_images       = False
        menu.skin_default_has_description = False

        if hasattr(menu, 'is_submenu'):
            menu.skin_default_has_images = True
            
        for i in menu.choices:
            if i.image:
                menu.skin_default_has_images = True
            if i['description'] or i.type:
                # have have a description if description is an attribute
                # or when the item has a type (special skin handling here)
                menu.skin_default_has_description = True
            if menu.skin_default_has_images and menu.skin_default_has_description:
                break
            
        self.use_images      = menu.skin_default_has_images
        self.use_description = menu.skin_default_has_description

        if len(menu.choices) < 6:
            try:
                if menu.choices[0].info_type == 'track':
                    menu.skin_force_text_view = True
                    self.use_text_view = True
                    return
            except:
                pass

            for i in menu.choices:
                if config.SKIN_FORCE_TEXTVIEW_STYLE == 1 and \
                       i.type == 'dir' and not i.media:
                    # directory with few items and folder:
                    self.use_text_view = False
                    return
                    
                if image and i.image != image:
                    menu.skin_force_text_view = False
                    self.use_text_view        = False
                    return
                image = i.image

            menu.skin_force_text_view = True
            self.use_text_view        = True
            return

        for i in menu.choices:
            if i.type == 'dir':
                folder += 1
                # directory with mostly folder:
                if config.SKIN_FORCE_TEXTVIEW_STYLE == 1 and folder > 3 and not i.media:
                    self.use_text_view = False
                    return
                    
            if image and i.image != image:
                menu.skin_force_text_view = False
                self.use_text_view        = False
                return
            image = i.image
            
        menu.skin_force_text_view = True
        self.use_text_view        = True

    
    def calc_geometry(self, object, copy_object=0):
        """
        calculate the real values of the object (e.g. content) based
        on the geometry of the area
        """
        if copy_object:
            object = copy.copy(object)

        font_h=0

        if isinstance(object.width, str):
            object.width = int(eval(object.width, {'MAX':self.area_val.width}))

        if isinstance(object.height, str):
            object.height = int(eval(object.height, {'MAX':self.area_val.height}))

        object.x += self.area_val.x
        object.y += self.area_val.y
        
        if not object.width:
            object.width = self.area_val.width

        if not object.height:
            object.height = self.area_val.height

        if object.width + object.x > self.area_val.width + self.area_val.x:
            object.width = self.area_val.width - object.x

        if object.height + object.y > self.area_val.height + self.area_val.y:
            object.height = self.area_val.height + self.area_val.y - object.y

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
    


    def init_vars(self, settings, display_type, widget_type = 'menu'):
        """
        check which layout is used and set variables for the object
        """
        redraw = False
        self.settings = settings

        if widget_type == 'menu':
            # get the correct <menu>
            if display_type and settings.special_menu.has_key(display_type):
                area = settings.special_menu[display_type]
            else:
                name = 'default'
                if self.use_description:
                    name += ' description'
                if not self.use_images:
                    name += ' no image'
                area = settings.default_menu[name]

            # get the correct style based on display_style
            if len(area.style) > self.display_style:
                area = area.style[self.display_style]
            else:
                try:
                    area = area.style[0]
                except IndexError:
                    print 'index error for %s %s' % (self.display_style, widget_type)
                    raise

            if area[0] and (not self.use_text_view):
                area = area[0]
            elif area[1]: 
                area = area[1]
            else:
                print 'want to fall back, but no text view defined'
                area = area[0]

        else:
            area = settings.sets[widget_type]
            if hasattr(area, 'style'):
                try:
                    area = area.style[self.display_style][1]
                except:
                    area = area.style[0][1]


        if self.area_name == 'plugin':
            if not self.area_val:
                self.area_val = fxdparser.Area(self.area_name)
                self.area_val.visible = True
                self.area_val.r = (0, 0, self.screen.width, self.screen.height)
            return True
        else:
            try:
                area = getattr(area, self.area_name)
            except AttributeError:
                try:
                    area = area.areas[self.area_name]
                except (KeyError, AttributeError):
                    print 'no skin information for %s:%s' % (widget_type, self.area_name)
                    area = fxdparser.Area(self.area_name)
                    area.visible = False

        if (not self.area_val) or area != self.area_val:
            self.area_val = area
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
        area   = self.area_val
        redraw = True

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
                    image = self.screen.renderer.loadbitmap(imagefile, self.imagecache,
                                                            bg.width, bg.height, True)
                    if image:
                        self.drawimage(image, bg)
                            
            elif isinstance(bg, fxdparser.Rectangle):
                self.calc_geometry(bg)
                self.drawbox(bg.x, bg.y, bg.width, bg.height, bg)
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
            return (0,0,0,0)

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

        self.tmp_objects.text.append(Text(x, y, x+width, y+height2, text, font, height,
                                          align_h, align_v, mode, ellipses, dim))


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
            return 0,0

        if isstring(image):
            if isinstance(val, tuple):
                image = self.loadimage(String(image), val[2:])
            else:
                image = self.loadimage(String(image), val)

        if not image:
            return 0,0
        
        if isinstance(val, tuple):
            if background:
                o = self.tmp_objects.bgimages
            else:
                o = self.tmp_objects.images
            o.append(Image(val[0], val[1], val[0] + image.get_width(),
                           val[1] + image.get_height(), image))
            return image.get_width(), image.get_height()

        try:
            if background or val.label == 'background':
                self.tmp_objects.bgimages.append(Image(val.x, val.y, val.x + val.width,
                                                       val.y + val.height, image))
                return val.width, val.height
        except:
            pass
        
        self.tmp_objects.images.append(Image(val.x, val.y, val.x + val.width,
                                             val.y + val.height, image))
        return val.width, val.height
        

