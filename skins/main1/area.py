#if 0
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
# Revision 1.2  2003/04/19 21:25:38  dischi
# don't load buggy skins
#
# Revision 1.1  2003/04/06 21:19:44  dischi
# Switched to new main1 skin
#
#
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
#endif


import copy
import pygame

import osd
import config
import objectcache

import xml_skin

# Create the OSD object
osd = osd.get_singleton()

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class SkinObjects:
    def __init__(self):
        self.bgimages   = []
        self.rectangles = []
        self.images     = []
        self.text       = []


class Screen:
    """
    this call is a set of surfaces for the area to do it's job
    """

    def __init__(self):
        self.s_content  = osd.screen.convert()
        self.s_alpha    = self.s_content.convert_alpha()
        self.s_bg       = self.s_content.convert()

        self.s_alpha.fill((0,0,0,0))

        self.update_bg      = None
        self.update_alpha   = []
        self.update_content = []

        self.drawlist = []

        
    def clear(self):
        self.update_bg      = None
        self.update_alpha   = []
        self.update_content = []

        self.drawlist = []


    def draw(self, obj):
        self.drawlist.append(obj)


    def update(self, layer, rect):
        if layer == 'content':
            self.update_content.append(rect)
        elif layer == 'alpha':
            self.update_alpha.append(rect)
        else:
            if self.update_bg:
                self.update_bg = ( min(self.update_bg[0], rect[0]),
                                   min(self.update_bg[1], rect[1]),
                                   max(self.update_bg[2], rect[2]),
                                   max(self.update_bg[3], rect[3]) )
            else:
                self.update_bg = rect

            
    def in_update(self, x1, y1, x2, y2, update_area, full=FALSE):
        if full:
            for ux1, uy1, ux2, uy2 in update_area:
                # if the area is not complete inside the area but is inside on
                # some pixels, return FALSE
                if (not (ux1 >= x1 and uy1 >= y1 and ux2 <= x2 and uy2 <= y2)) and \
                   (not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2)):
                    return FALSE
            return TRUE
        
        for ux1, uy1, ux2, uy2 in update_area:
            if not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2):
                return TRUE
        return FALSE


    def show(self, force_redraw=FALSE):
        """
        the main drawing function
        """

        if osd.must_lock:
            self.s_bg.lock()
            self.s_alpha.lock()
            self.s_content.lock()
            osd.screen.lock()
        
        objects = SkinObjects()
        for area in self.drawlist:
            objects.bgimages   += area.bgimages
            objects.rectangles += area.rectangles
            objects.images     += area.images
            objects.text       += area.text
            
        if force_redraw:
            self.update_bg      = (0,0,osd.width, osd.height)
            self.update_alpha   = []
            self.update_content = []

        update_area = self.update_alpha

        # if the background has some changes ...
        if self.update_bg:
            ux1, uy1, ux2, uy2 = self.update_bg 
            for x1, y1, x2, y2, image in objects.bgimages:
                if not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2):
                    self.s_bg.blit(image, (ux1, uy1), (ux1-x1, uy1-y1, ux2-ux1, uy2-uy1))

            update_area.append(self.update_bg)
            
        if update_area:
            # clear it
            self.s_alpha.fill((0,0,0,0))

            for x1, y1, x2, y2, bgcolor, size, color, radius in objects.rectangles:
                # only redraw if necessary
                if self.in_update(x1, y1, x2, y2, update_area):
                    # if the radius and the border is not inside the update area,
                    # use drawbox, it's faster
                    if self.in_update(x1+size+radius, y1+size+radius, x2-size-radius,
                                      y2-size-radius, update_area, full=TRUE):
                        osd.drawbox(x1, y1, x2, y2, color=bgcolor, fill=1,
                                    layer=self.s_alpha)
                    else:
                        osd.drawroundbox(x1, y1, x2, y2, color=bgcolor,
                                         border_size=size, border_color=color,
                                         radius=radius, layer=self.s_alpha)

            # and than blit only the changed parts of the screen
            for x0, y0, x1, y1 in update_area:
                self.s_content.blit(self.s_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))
                self.s_content.blit(self.s_alpha, (x0, y0), (x0, y0, x1-x0, y1-y0))
                osd.screen.blit(self.s_content, (x0, y0), (x0, y0, x1-x0, y1-y0))


        # if the content has changed ...
        if self.update_content:
            # ... blit back the alphabg surface
            for x0, y0, x1, y1 in self.update_content:
                osd.screen.blit(self.s_content, (x0, y0), (x0, y0, x1-x0, y1-y0))


        update_area += self.update_content

        # if something changed redraw all content objects
        if update_area:
            for x1, y1, x2, y2, image in objects.images:
                if self.in_update(x1, y1, x2, y2, update_area):
                    osd.screen.blit(image, (x1, y1))

            for x1, y1, x2, y2, text, font, height, align_h, align_v, mode, \
                ellipses in objects.text:
                if self.in_update(x1, y1, x2, y2, update_area):
                    width = x2 - x1
                    if font.shadow.visible:
                        osd.drawstringframed(text, x1+font.shadow.x, y1+font.shadow.y,
                                             width, height, font.shadow.color, None,
                                             font=font.name, ptsize=font.size,
                                             align_h = align_h, align_v = align_v,
                                             mode=mode, ellipses=ellipses)
                    osd.drawstringframed(text, x1, y1, width, height, font.color, None,
                                         font=font.name, ptsize=font.size,
                                         align_h = align_h, align_v = align_v,
                                         mode=mode, ellipses=ellipses)

        if osd.must_lock:
            self.s_bg.unlock()
            self.s_alpha.unlock()
            self.s_content.unlock()
            osd.screen.unlock()



class Geometry:
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

    def __init__(self, name, screen, imagecachesize=5):
        self.area_name = name
        self.area_val  = None
        self.redraw    = TRUE
        self.layout    = None
        self.name      = name
        self.screen    = screen
        self.objects   = SkinObjects()
        
        self.imagecache = objectcache.ObjectCache(imagecachesize,
                                                  desc='%s_image' % self.name)
        self.dummy_layer = pygame.Surface((osd.width, osd.height))


    def draw(self, settings, obj, display_style=0, widget_type='menu', force_redraw=FALSE):
        """
        this is the main draw function. This function draws the background,
        checks if redraws are needed and calls the two update functions
        for the different types of areas
        """

        self.display_style = display_style

        if widget_type == 'menu':
            self.menuw = obj
            self.menu  = obj.menustack[-1]
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
        elif widget_type == 'tv':
            self.menuw = obj
            self.menu  = obj
            item_type = None
            self.viewitem = obj.selected
            self.infoitem = obj.selected
        else:
            item_type = None
            self.viewitem = obj
            self.infoitem = obj

        self.tmp_objects = SkinObjects()
        
        self.redraw = force_redraw
        
        area = self.area_val
        if area:
            visible = area.visible
        else:
            visible = FALSE

        self.redraw = self.init_vars(settings, item_type, widget_type)
            
        if area and area != self.area_val:
            old_area = area
        else:
            old_area = None
            
        area = self.area_val

        # maybe we are NOW invisible
        if visible and not area.visible and old_area:
            self.screen.update('background', (old_area.x, old_area.y,
                                              old_area.x + old_area.width,
                                              old_area.y + old_area.height))
            self.objects = SkinObjects()

        if not area.visible or not self.layout:
            self.objects = SkinObjects()
            return

        self.draw_background()

        # dependencies haven't changed
        if not self.redraw:
            # no update needed: return
            if not self.update_content_needed():
                self.screen.draw(self.objects)
                return

        self.update_content()

        bg_rect = ( osd.width, osd.height, 0, 0 )
        a_rect  = ( osd.width, osd.height, 0, 0 )
        c_rect  = ( osd.width, osd.height, 0, 0 )


        for b in self.tmp_objects.bgimages:
            try:
                self.objects.bgimages.remove(b)
            except ValueError:
                bg_rect = ( min(bg_rect[0], b[0]), min(bg_rect[1], b[1]),
                            max(bg_rect[2], b[2]), max(bg_rect[3], b[3]) )

        for b in self.objects.bgimages:
            if not b in self.tmp_objects.bgimages:
                bg_rect = ( min(bg_rect[0], b[0]), min(bg_rect[1], b[1]),
                            max(bg_rect[2], b[2]), max(bg_rect[3], b[3]) )



        for b in self.tmp_objects.rectangles:
            try:
                self.objects.rectangles.remove(b)
            except ValueError:
                a_rect = ( min(a_rect[0], b[0]), min(a_rect[1], b[1]),
                           max(a_rect[2], b[2]), max(a_rect[3], b[3]) )

        for b in self.objects.rectangles:
            if not b in self.tmp_objects.rectangles:
                a_rect = ( min(a_rect[0], b[0]), min(a_rect[1], b[1]),
                           max(a_rect[2], b[2]), max(a_rect[3], b[3]) )



        for b in self.tmp_objects.images:
            try:
                self.objects.images.remove(b)
            except ValueError:
                c_rect = ( min(c_rect[0], b[0]), min(c_rect[1], b[1]),
                           max(c_rect[2], b[2]), max(c_rect[3], b[3]) )

        for b in self.objects.images:
            if not b in self.tmp_objects.images:
                c_rect = ( min(c_rect[0], b[0]), min(c_rect[1], b[1]),
                           max(c_rect[2], b[2]), max(c_rect[3], b[3]) )



        for b in self.tmp_objects.text:
            try:
                self.objects.text.remove(b)
            except ValueError:
                c_rect = ( min(c_rect[0], b[0]), min(c_rect[1], b[1]),
                           max(c_rect[2], b[2]), max(c_rect[3], b[3]) )

        for b in self.objects.text:
            if not b in self.tmp_objects.text:
                c_rect = ( min(c_rect[0], b[0]), min(c_rect[1], b[1]),
                           max(c_rect[2], b[2]), max(c_rect[3], b[3]) )



        if bg_rect[0] < bg_rect[2]:
            self.screen.update('background', bg_rect)

        if a_rect[0] < a_rect[2]:
            self.screen.update('alpha', a_rect)
            if c_rect[0] < c_rect[2] and \
               not (c_rect[0] >= a_rect[0] and c_rect[1] >= a_rect[1] and \
                    c_rect[2] <= a_rect[2] and c_rect[3] <= a_rect[3]):
                self.screen.update('content', c_rect)

        elif c_rect[0] < c_rect[2]:
            self.screen.update('content', c_rect)


        self.objects = self.tmp_objects
        self.screen.draw(self.objects)


    def calc_geometry(self, object, copy_object=0):
        """
        calculate the real values of the object (e.g. content) based
        on the geometry of the area
        """
        if copy_object:
            object = copy.deepcopy(object)

        MAX = self.area_val.width
        object.width = eval('%s' % object.width)

        MAX = self.area_val.height
        object.height = eval('%s' % object.height)

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
        calculates the values for a rectangle inside the item tag
        """
        r = copy.copy(rectangle)
        
        if not r.width:
            r.width = item_w

        if not r.height:
            r.height = item_h

        MAX = item_w
        r.x = int(eval('%s' % r.x))
        r.width = int(eval('%s' % r.width))
            
        MAX = item_h
        r.y = int(eval('%s' % r.y))
        r.height = int(eval('%s' % r.height))

        if r.x < 0:
            item_w -= r.x

        if r.y < 0:
            item_h -= r.y

        return max(item_w, r.width), max(item_h, r.height), r
    

    def fit_item_in_rectangle(self, rectangle, width, height):
        """
        calculates the rectangle geometry and fits it into the area
        """
        x = 0
        y = 0
        r = self.get_item_rectangle(rectangle, width, height)[2]
        if r.width > width:
            r.width, width = width, width - (r.width - width)
        if r.height > height:
            r.height, height = height, height - (r.height - height)
        if r.x < 0:
            r.x, x = 0, -r.x
            width -= x
        if r.y < 0:
            r.y, y = 0, -r.y
            height -= y

        return Geometry(x, y, width, height), r
    

    def init_vars(self, settings, display_type, widget_type = 'menu'):
        """
        check which layout is used and set variables for the object
        """
        redraw = self.redraw
        self.settings = settings

        if widget_type == 'player':
            area = settings.player
        elif widget_type == 'tv':
            area = settings.tv
        else:
            # get the correct <menu>
            try:
                area = settings.menu[display_type]
            except:
                area = settings.menu['default']

            # get the correct style based on display_style
            if len(area.style) > self.display_style:
                area = area.style[self.display_style]
            else:
                try:
                    area = area.style[0]
                except IndexError:
                    print 'index error for %s %s' % (self.display_style, widget_type)
                    raise
                
            # get image or text view
            # FIXME: select text if necessary
            if area[0]:
                area = area[0]
            else:
                area = area[1]

        try:
            area = eval('area.%s' % self.area_name)
        except AttributeError:
            area = xml_skin.XML_area(self.area_name)
            area.visible = FALSE
            
        if (not self.area_val) or area != self.area_val:
            self.area_val = area
            redraw = TRUE
            
        if not area.layout:
            return redraw

        old_layout  = self.layout
        self.layout = area.layout

        if old_layout and old_layout != self.layout:
            redraw = TRUE

        area.r = (area.x, area.y, area.width, area.height)

        return redraw
        


    def draw_background(self):
        """
        draw the <background> of the area
        """
        area = self.area_val

        last_watermark = None

        if hasattr(self, 'watermark') and self.watermark:
            last_watermark = self.watermark

	    if hasattr(self.menu.selected,'image') and \
               self.menu.selected.image != self.watermark:
                self.watermark = None
                self.redraw = TRUE
            
        for bg in copy.deepcopy(self.layout.background):
            if isinstance(bg, xml_skin.XML_image):
                self.calc_geometry(bg)
                imagefile = ''
                
                # if this is the real background image, ignore the
                # OVERSCAN to fill the whole screen
                if bg.label == 'background':
                    bg.x -= config.OVERSCAN_X
                    bg.y -= config.OVERSCAN_Y
                    bg.width  += 2 * config.OVERSCAN_X
                    bg.height += 2 * config.OVERSCAN_Y

                if bg.label == 'watermark' and self.menu.selected.image:
                    imagefile = self.menu.selected.image
                    if last_watermark != imagefile:
                        self.redraw = TRUE
                    self.watermark = imagefile
                else:
                    imagefile = bg.filename

                if self.name == 'screen':
                    bg.label = 'background'
                    
                if imagefile:
                    cname = '%s-%s-%s' % (imagefile, bg.width, bg.height)
                    image = self.imagecache[cname]
                    if not image:
                        image = osd.loadbitmap(imagefile)
                        if image:
                            image = pygame.transform.scale(image,(bg.width,bg.height))
                            self.imagecache[cname] = image
                    if image:
                        self.draw_image(image, bg)
                            
            elif isinstance(bg, xml_skin.XML_rectangle):
                self.calc_geometry(bg)
                self.drawroundbox(bg.x, bg.y, bg.width, bg.height, bg)

            

    def drawroundbox(self, x, y, width, height, rect, redraw=TRUE):
        """
        draw a round box ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """

        self.tmp_objects.rectangles.append(( x, y, x + width, y + height, rect.bgcolor,
                                             rect.size, rect.color, rect.radius ))

            
    # Draws a text inside a frame based on the settings in the XML file
    def write_text(self, text, font, content, x=-1, y=-1, width=None, height=None,
                   align_h = None, align_v = None, mode='hard', ellipses='...',
                   return_area=FALSE):
        """
        writes a text ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """

        if not text:
            return
        
        if x == -1: x = content.x
        if y == -1: y = content.y

        if width == None:
            width  = content.width
        if height == None:
            height = content.height

        if not align_h:
            align_h = content.align
            if not align_h:
                align_h = 'left'
                
        if not align_v:
            align_v = content.valign
            if not align_v:
                align_v = 'top'

        height2 = height
        if height2 == -1:
            height2 = font.h + 2

        if return_area:
            ret = osd.drawstringframed(text, x, y, width, height, None, None,
                                       font=font.name, ptsize=font.size,
                                       align_h = align_h, align_v = align_v,
                                       mode=mode, ellipses=ellipses, layer=self.dummy_layer)

        self.tmp_objects.text.append((x, y, x+width, y+height2, text, font, height,
                                            align_h, align_v, mode, ellipses ))

        if return_area:
            return ret[1]
    

    def load_image(self, image, val, redraw=TRUE):
        """
        load an image (use self.imagecache
        """
        if isinstance(val, tuple) or isinstance(val, list):
            w = val[0]
            h = val[1]
        else:
            w = val.width
            h = val.height
            
        cname = '%s-%s-%s' % (image, w, h)
        cimage = self.imagecache[cname]
        if not cimage:
            try:
                image = pygame.transform.scale(osd.loadbitmap(image), (w, h))
                self.imagecache[cname] = image
            except:
                return None
        else:
            image = cimage
        return image

        
    def draw_image(self, image, val):
        """
        draws an image ... or better stores the information about this call
        in a variable. The real drawing is done inside draw()
        """

        if not image:
            return
        
        if isinstance(image, str):
            image = self.load_image(image, val)
                
        if not image:
            return
        
        if isinstance(val, tuple):
            self.tmp_objects.images.append((val[0], val[1], val[0] + image.get_width(),
                                            val[1] + image.get_height(), image))
            return
        
        elif hasattr(val, 'label') and val.label == 'background':
            self.tmp_objects.bgimages.append((val.x, val.y, val.x + val.width,
                                             val.y + val.height, image))
        else:
            self.tmp_objects.images.append((val.x, val.y, val.x + val.width,
                                            val.y + val.height, image))
