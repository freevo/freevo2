#if 0
# -----------------------------------------------------------------------
# screen.py - The screen for the Freevo areas to draw on
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/12/09 20:34:36  dischi
# this code will never used for helpers
#
# Revision 1.2  2003/12/06 16:45:13  dischi
# do not create a screen for helpers
#
# Revision 1.1  2003/12/06 16:41:45  dischi
# move some classes into extra files
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

import config
import osd
osd = osd.get_singleton()


singleton = None

def get_singleton():
    global singleton
    if not singleton:
        singleton = Screen()
    return singleton


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
        self.avoid_list = []

        
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
                                   max(self.update_bg[3], rect[3]))
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

        if force_redraw:
            _debug_('show, force update', 2)
            self.update_bg      = (0,0,osd.width, osd.height)
            self.update_alpha   = []
            self.update_content = []

        update_area = self.update_alpha

        # if the background has some changes ...
        if self.update_bg:
            ux1, uy1, ux2, uy2 = self.update_bg 
            for area in self.drawlist:
                for x1, y1, x2, y2, image in area.bgimages:
                    if not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2):
                        self.s_bg.blit(image, (ux1, uy1), (ux1-x1, uy1-y1, ux2-ux1, uy2-uy1))

            update_area.append(self.update_bg)
            
        if update_area:
            # clear it
            self.s_alpha.fill((0,0,0,0))

            for area in self.drawlist:
                for x1, y1, x2, y2, bgcolor, size, color, radius in area.rectangles:
                    # only redraw if necessary
                    if self.in_update(x1, y1, x2, y2, update_area):
                        # if the radius and the border is not inside the update area,
                        # use drawbox, it's faster
                        if self.in_update(x1+size+radius, y1+size+radius, x2-size-radius,
                                          y2-size-radius, update_area, full=TRUE):
                            osd.drawroundbox(x1, y1, x2, y2, color=bgcolor,
                                             layer=self.s_alpha)
                        else:
                            osd.drawroundbox(x1, y1, x2, y2, color=bgcolor,
                                             border_size=size, border_color=color,
                                             radius=radius, layer=self.s_alpha)
            # and than blit only the changed parts of the screen
            for x0, y0, x1, y1 in update_area:
                self.s_content.blit(self.s_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))
                self.s_content.blit(self.s_alpha, (x0, y0), (x0, y0, x1-x0, y1-y0))

        layer = self.s_content.convert()
        update_area += self.update_content

        # if something changed redraw all content objects
        if update_area:
            for area in self.drawlist:
                for x1, y1, x2, y2, image in area.images:
                    if self.in_update(x1, y1, x2, y2, update_area):
                        layer.blit(image, (x1, y1))

                for x1, y1, x2, y2, text, font, height, align_h, align_v, mode, \
                        ellipses in area.text:
                    if self.in_update(x1, y1, x2, y2, update_area):
                        width = x2 - x1
                        if font.shadow.visible:
                            width -= font.shadow.x
                            osd.drawstringframed(text, x1+font.shadow.x, y1+font.shadow.y,
                                                 width, height, font.font, font.shadow.color,
                                                 None, align_h = align_h, align_v = align_v,
                                                 mode=mode, ellipses=ellipses, layer=layer)
                        osd.drawstringframed(text, x1, y1, width, height, font.font,
                                             font.color, None, align_h = align_h,
                                             align_v = align_v, mode=mode,
                                             ellipses=ellipses, layer=layer)

        for x0, y0, x1, y1 in update_area:
            osd.screen.blit(layer, (x0, y0), (x0, y0, x1-x0, y1-y0))

        if osd.must_lock:
            self.s_bg.unlock()
            self.s_alpha.unlock()
            self.s_content.unlock()
            osd.screen.unlock()



