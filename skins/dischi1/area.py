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
# Revision 1.36  2003/03/31 19:00:37  dischi
# Removed all the lists in lists and list += [ blah ] stuff. I think it is
# faster now, at least not slower ;-)
#
# Revision 1.35  2003/03/30 14:13:23  dischi
# (listing.py from prev. checkin has the wrong log message)
# o tvlisting now has left/right items and the label width is taken from the
#   skin xml file. The channel logos are scaled to fit that space
# o add image load function to area
# o add some few lines here and there to make it possible to force the
#   skin to a specific layout
# o initial display style is set to config.SKIN_START_LAYOUT
#
# Revision 1.34  2003/03/27 20:10:56  dischi
# Fix endless loop on empty directories (and added a messages)
#
# Revision 1.33  2003/03/23 19:44:04  dischi
# added debug
#
# Revision 1.32  2003/03/22 22:26:46  dischi
# added some exception handling
#
# Revision 1.31  2003/03/22 22:19:01  dischi
# fixed a redraw bug
#
# Revision 1.30  2003/03/22 20:08:30  dischi
# Lots of changes:
# o blue2_big and blue2_small are gone, it's only blue2 now
# o Support for up/down arrows in the listing area
# o a sutitle area for additional title information (see video menu in
#   blue2 for an example)
# o some layout changes in blue2 (experimenting with the skin)
# o the skin searches for images in current dir, skins/images and icon dir
# o bugfixes
#
# Revision 1.29  2003/03/21 19:44:44  dischi
# only draw images when needed
#
# Revision 1.28  2003/03/20 18:55:45  dischi
# Correct the rectangle drawing
#
# Revision 1.27  2003/03/20 15:44:59  dischi
# faster now
#
# Revision 1.26  2003/03/19 11:00:22  dischi
# cache images inside the area and some bugfixes to speed up things
#
# Revision 1.25  2003/03/18 09:37:00  dischi
# Added viewitem and infoitem to the menu to set an item which image/info
# to take (only for the new skin)
#
# Revision 1.24  2003/03/16 19:33:12  dischi
# adjustments to the new xml_parser
#
# Revision 1.23  2003/03/14 19:38:02  dischi
# Support the new <menu> and <menuset> structure. See the blue2 skins
# for example
#
# Revision 1.22  2003/03/14 03:08:58  outlyer
# A fix for a crash problem I had with Dischi's version of my skin.
#
# Revision 1.21  2003/03/13 21:02:03  dischi
# misc cleanups
#
# Revision 1.20  2003/03/11 20:38:47  dischi
# some speed ups
#
# Revision 1.19  2003/03/11 20:25:59  dischi
# Small fixes
#
# Revision 1.18  2003/03/08 17:36:47  dischi
# integration of the tv guide
#
# Revision 1.17  2003/03/07 17:27:46  dischi
# added support for extended menus
#
# Revision 1.16  2003/03/05 22:14:06  dischi
# Bugfix: one enhancement doesn't work right
#
# Revision 1.15  2003/03/05 21:57:02  dischi
# Added audio player. The info area is empty right now, but this skin
# can player audio files
#
# Revision 1.14  2003/03/05 20:08:17  dischi
# More speed enhancements. It's now faster than the keyboard control :-)
#
# Revision 1.13  2003/03/05 19:20:45  dischi
# cleanip
#
# Revision 1.12  2003/03/04 22:46:32  dischi
# VERY fast now (IMHO as fast as we can get it). There are some cleanups
# necessary, but it's working. area.py only blits the parts of the screen
# that changed, Aubins idle bar won't blink at all anymore (except you change
# the background below it)
#
# Revision 1.11  2003/03/02 22:00:13  dischi
# bugfix
#
# Revision 1.10  2003/03/02 21:56:36  dischi
# Redraw bugfix for items that turn invisible
#
# Revision 1.9  2003/03/02 21:35:19  dischi
# Don't print the warning when the area is invisible
#
# Revision 1.8  2003/03/02 19:31:35  dischi
# split the draw function in two parts
#
# Revision 1.7  2003/03/02 15:04:08  dischi
# Added forced_redraw after Clear()
#
# Revision 1.6  2003/03/01 00:12:17  dischi
# Some bug fixes, some speed-ups. blue_round2 has a correct main menu,
# but on the main menu the idle bar still flickers (stupid watermarks),
# on other menus it's ok.
#
# Revision 1.5  2003/02/27 22:39:49  dischi
# The view area is working, still no extended menu/info area. The
# blue_round1 skin looks like with the old skin, blue_round2 is the
# beginning of recreating aubin_round1. tv and music player aren't
# implemented yet.
#
# Revision 1.4  2003/02/26 19:59:25  dischi
# title area in area visible=(yes|no) is working
#
# Revision 1.3  2003/02/26 19:18:52  dischi
# Added blue1_small and changed the coordinates. Now there is no overscan
# inside the skin, it's only done via config.OVERSCAN_[XY]. The background
# images for the screen area should have a label "background" to override
# the OVERSCAN resizes.
#
# Revision 1.2  2003/02/25 23:27:36  dischi
# changed max usage
#
# Revision 1.1  2003/02/25 22:56:00  dischi
# New version of the new skin. It still looks the same (except that icons
# are working now), but the internal structure has changed. Now it will
# be easier to do the next steps.
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
        self.s_bg       = pygame.Surface((osd.width, osd.height), 1, 32)
        self.s_alpha    = self.s_bg.convert_alpha()
        self.s_content  = self.s_bg.convert()

        self.s_alpha.fill((0,0,0,0))

        self.updatelist = {}
        self.updatelist['background'] = []
        self.updatelist['content']    = []

        self.drawlist = []

        
    def clear(self):
        self.updatelist['background'] = []
        self.updatelist['content']    = []

        self.drawlist = []


    def draw(self, obj):
        self.drawlist.append(obj)


    def update(self, layer, rect):
        self.updatelist[layer] += [ rect ]


    def in_update(self, x1, y1, x2, y2, update_area):
        for u in update_area:
            if not (x2 < u[0] or y2 < u[1] or x1 > u[2] or y1 > u[3]):
                return TRUE
        return FALSE


    def show(self, force_redraw=FALSE):
        """
        the main drawing function
        """

        objects = SkinObjects()
        for area in self.drawlist:
            objects.bgimages   += area.bgimages
            objects.rectangles += area.rectangles
            objects.images     += area.images
            objects.text       += area.text
            
        if force_redraw:
            self.updatelist['background'] = [ (0,0,osd.width, osd.height) ]
            self.updatelist['content']    = []


        update_area = self.updatelist['background']

        # if the background has some changes ...
        if update_area:
            # ... clear it ...
            self.s_alpha.fill((0,0,0,0))

            # and redraw all items
            for x1, y1, x2, y2, image in objects.bgimages:
                # redraw only the changed parts of the image (BROKEN)
                # for x0, y0, x1, y1 in self.updatelist['background']:
                # self.s_bg.blit(o[1], (x0, y0), (x0-o[2], y0-o[3], x1-x0, y1-y0))
                if self.in_update(x1, y1, x2, y2, update_area):
                    self.s_bg.blit(image, (x1, y1))

            for x1, y1, x2, y2, bgcolor, size, color, radius in objects.rectangles:
                # only redraw if necessary
                if self.in_update(x1, y1, x2, y2, update_area):
                    osd.drawroundbox(x1, y1, x2, y2, color=bgcolor,
                                     border_size=size, border_color=color,
                                     radius=radius, layer=self.s_alpha)

            # and than blit only the changed parts of the screen
            for x0, y0, x1, y1 in update_area:
                self.s_content.blit(self.s_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))
                self.s_content.blit(self.s_alpha, (x0, y0), (x0, y0, x1-x0, y1-y0))
                osd.screen.blit(self.s_content, (x0, y0), (x0, y0, x1-x0, y1-y0))


        update_area = self.updatelist['content']
            
        # if the content has changed ...
        if update_area:
            # ... blit back the alphabg surface
            for x0, y0, x1, y1 in update_area:
                osd.screen.blit(self.s_content, (x0, y0), (x0, y0, x1-x0, y1-y0))


        update_area = self.updatelist['background'] + self.updatelist['content']

        # if something changed redraw all content objects
        if update_area:
            for x1, y1, x2, y2, image in objects.images:
                # redraw only the changed parts of the image (BROKEN)
                # for x0, y0, x1, y1 in self.updatelist['background']:
                # self.s_bg.blit(o[1], (x0, y0), (x0-o[2], y0-o[3], x1-x0, y1-y0))
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
        self.dummy_layer = pygame.Surface((osd.width, osd.height), 1, 32)


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
                bg_rect = ( min(bg_rect[0], b[0]), min(bg_rect[1], b[1]),
                            max(bg_rect[2], b[2]), max(bg_rect[3], b[3]) )

        for b in self.objects.rectangles:
            if not b in self.tmp_objects.rectangles:
                bg_rect = ( min(bg_rect[0], b[0]), min(bg_rect[1], b[1]),
                            max(bg_rect[2], b[2]), max(bg_rect[3], b[3]) )



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
            if c_rect[0] < c_rect[2] and \
               not (c_rect[0] >= bg_rect[0] and c_rect[1] >= bg_rect[1] and \
                    c_rect[2] <= bg_rect[2] and c_rect[3] <= bg_rect[3]):
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
                    print 'index error for %s %s' % (display_style, widget_type)
                    print area
                    print area.style
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
