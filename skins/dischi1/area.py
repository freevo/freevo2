#if 0
# -----------------------------------------------------------------------
# area.py - An area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
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

import xml_skin


# Create the OSD object
osd = osd.get_singleton()

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class Skin_Area:
    def __init__(self, name):
        self.area_name = name
        self.alpha     = None           # alpha layer for rectangles
        self.screen    = None           # backup of the final screen
        self.area_val  = None
        self.redraw    = TRUE
        self.depends   = ()
        self.bg        = [ None, None ]
        self.layout    = None
        
    def draw(self, settings, menuw):
        menu = menuw.menustack[-1]

        self.redraw = FALSE
        for d in self.depends:
            self.redraw = d.redraw or self.redraw
        
        dep_redraw = self.redraw
        self.redraw = self.init_vars(settings, menu.item_types)

        # we need to redraw the area we want to draw in
        if not dep_redraw and self.redraw and self.bg[0]:
            osd.screen.blit(self.bg[0][0], self.bg[0][1:])
        self.draw_background()

        # dependencies haven't changed
        if not self.redraw:
            # no update needed: return
            if not self.update_content_needed(settings, menuw):
                return

            # restore the background
            osd.screen.blit(self.bg[1], (self.area_val.x, self.area_val.y))

        self.update_content(settings, menuw)
        

    def calc_geometry(self, object, copy_object=0, fit_area=1):
        if copy_object:
            object = copy.deepcopy(object)

        MAX = self.area_val.width
        object.width = eval('%s' % object.width)

        MAX = self.area_val.height
        object.height = eval('%s' % object.height)

        if fit_area:
            object.x += self.area_val.x
            object.y += self.area_val.y

        if not object.width:
            object.width = self.area_val.width

        if not object.height:
            object.height = self.area_val.height

        return object

        
    def init_vars(self, settings, display_type):
        redraw = self.redraw
        
        if settings.menu.has_key(display_type):
            area_val = settings.menu[display_type][0]
        else:
            area_val = settings.menu['default'][0]

        area_val = eval('area_val.%s' % self.area_name)
        
        if (not self.area_val) or area_val != self.area_val:
            self.area_val = area_val
            redraw = TRUE
            
        if not settings.layout.has_key(area_val.layout):
            print '*** layout <%s> not found' % area_val.layout
            return FALSE

        old_layout = self.layout
        self.layout = settings.layout[area_val.layout]

        if old_layout and old_layout != self.layout:
            redraw = TRUE

        return redraw
        


    def draw_background(self):
        if not self.redraw:
            return

        area = self.area_val

        self.bg = [ [ None, area.x, area.y ], None ]
        self.bg[0][0] = osd.createlayer(area.width, area.height)
        self.bg[0][0].blit(osd.screen, (0,0), (area.x, area.y,
                                               area.x + area.width,
                                               area.y + area.height))

        self.alpha = None
        for bg in copy.deepcopy(self.layout.background):
            if isinstance(bg, xml_skin.XML_image):
                self.calc_geometry(bg)
                image = osd.loadbitmap(bg.filename)

                # if this is the real background image, ignore the
                # OVERSCAN to fill the whole screen
                if bg.label == 'background':
                    bg.x -= config.OVERSCAN_X
                    bg.y -= config.OVERSCAN_Y
                    bg.width  += 2 * config.OVERSCAN_X
                    bg.height += 2 * config.OVERSCAN_Y
                if image:
                    osd.screen.blit(pygame.transform.scale(image,(bg.width,bg.height)),
                                    (bg.x, bg.y))
            elif isinstance(bg, xml_skin.XML_rectangle):
                self.calc_geometry(bg, fit_area=FALSE)
                if not self.alpha:
                    self.alpha = osd.createlayer(area.width, area.height)
                    # clear surface
                    self.alpha.fill((0,0,0,0))
                osd.drawroundbox(bg.x, bg.y, bg.x+bg.width, bg.y+bg.height, bg.bgcolor,
                                 bg.size, bg.color, bg.radius, layer=self.alpha)

        if self.alpha:
            osd.screen.blit(self.alpha, (area.x, area.y))

        if hasattr(self, 'bg'):
            self.bg[1] = osd.createlayer(area.width, area.height)
            self.bg[1].blit(osd.screen, (0,0), (area.x, area.y,
                                                area.x + area.width,
                                                area.y + area.height))



    def drawroundbox(self, x, y, width, height, rect):
        area = self.area_val
        if self.alpha:
            osd.screen.blit(self.bg[0][0], (x, y), (x-area.x, y-area.y, width, height))
            a = osd.createlayer(width, height)
            a.blit(self.alpha, (0,0), (x - area.x, y - area.y, width, height))

            osd.drawroundbox(0, 0, width, height,
                             color = rect.bgcolor, border_size=rect.size,
                             border_color=rect.color, radius=rect.radius, layer=a)
            osd.screen.blit(a, (x, y))
        else:
            osd.drawroundbox(x, y, x+width, y+height,
                             color = rect.bgcolor, border_size=rect.size,
                             border_color=rect.color, radius=rect.radius)

        
    # Draws a text inside a frame based on the settings in the XML file
    def write_text(self, text, font, area, x=-1, y=-1, width=None, height=None,
                   mode='hard', ellipses='...'):
    
        if x == -1: x = area.x
        if y == -1: y = area.y

        if width == None:
            width  = area.width
        if height == None:
            height = area.height

        if font.shadow.visible:
            osd.drawstringframed(text, x+font.shadow.x, y+font.shadow.y,
                                 width, height, font.shadow.color, None,
                                 font=font.name, ptsize=font.size,
                                 mode=mode, ellipses=ellipses)
        osd.drawstringframed(text, x, y, width, height, font.color, None,
                             font=font.name, ptsize=font.size,
                             mode=mode, ellipses=ellipses)



    
