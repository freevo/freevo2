# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# pygame_renderer.py - interface to output using pygame
# -----------------------------------------------------------------------
# $Id$
#
# Note: Work in Progress
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:16:01  dischi
# add first draft of new gui code
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


import copy


class Layer:
    """
    This is a layer implementation for pygame. You can add objects from
    basic.py to it and they will be drawn.
    """
    def __init__(self, name, renderer, alpha=False):
        self.name     = name
        self.renderer = renderer
        self.alpha    = alpha
        if alpha:
            self.screen = self.renderer.screen.convert_alpha()
            self.screen.fill((0,0,0,0))
        else:
            self.screen = self.renderer.screen.convert()

        # some Surface functions from pygame
        self.fill = self.screen.fill
        self.lock = self.screen.lock
        self.lock = self.screen.unlock

        self.update_rect = []
        self.objects     = []
        self.width       = self.renderer.width
        self.height      = self.renderer.height
        

    def blit(self, layer, *arg1, **arg2):
        """
        Interface for the objects to blit something on the layer
        """
        try:
            return self.screen.blit(layer.screen, *arg1, **arg2)
        except AttributeError:
            return self.screen.blit(layer, *arg1, **arg2)
            

    def drawroundbox(self, *arg1, **arg2):
        """
        Interface for the objects draw a round box
        """
        arg2['layer'] = self.screen
        return self.renderer.drawroundbox(*arg1, **arg2)


    def drawstringframed(self, *arg1, **arg2):
        """
        Interface for the objects draw a string
        """
        arg2['layer'] = self.screen
        return self.renderer.drawstringframed(*arg1, **arg2)


    def in_update(self, x1, y1, x2, y2, update_area, full=False):
        """
        Helper function to check if we need to update or not
        """
        if full:
            for ux1, uy1, ux2, uy2 in update_area:
                # check if x1, y1, x2, y2 are completly inside the rect
                if ux1 <= x1 <= x2 <= ux2 and uy1 <= y1 <= y2 <= uy2:
                    return True
            return False

        for ux1, uy1, ux2, uy2 in update_area:
            # check if x1, y1, x2, y2 is somewere inside the rect
            if not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2):
                return True
        return False


    def add_to_update_rect(self, x1, y1, x2, y2):
        """
        Add (x1,y1,x2,y2) to the list of rectangles we need to update
        """
        if not self.in_update(x1, y1, x2, y2, self.update_rect, True):
            self.update_rect.append((x1, y1, x2, y2))


    def expand_update_rect(self, update_area):
        """
        Add all rectangles in update_area to the list of rectangles we need
        to update
        """
        old_rect = self.update_rect
        self.update_rect = copy.copy(update_area)
        for x1, y1, x2, y2 in old_rect:
            self.add_to_update_rect(x1, y1, x2, y2)
        return self.update_rect

    
    def add(self, object):
        """
        Add an object to this layer
        """
        object.layer = self
        self.objects.append(object)
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)


    def remove(self, object):
        """
        Add an object from this layer
        """
        self.objects.remove(object)
        object.layer = None
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)
        return True


    def clear(self):
        """
        Clear this layer
        """
        self.update_rect = []
        self.objects     = []
        if self.alpha:
            self.screen.fill((0,0,0,0))
        else:
            self.screen.fill((0,0,0))


    def draw(self):
        """
        Draw all objects on this layer
        """
        rect = (self.width, self.height, 0, 0)

        if not self.update_rect:
            return self.update_rect, rect

        for x0, y0, x1, y1 in self.update_rect:
            rect = ( min(x0, rect[0]), min(y0, rect[1]),
                     max(x1, rect[2]), max(y1, rect[3]))
            
        for o in self.objects:
            if self.in_update(o.x1, o.y1, o.x2, o.y2, self.update_rect):
                o.draw(rect)

        ret = self.update_rect
        self.update_rect = []
        return ret, rect
    
        


class Screen:
    """
    The screen implementation for pygame
    """
    def __init__(self):
        import osd
        self.renderer = osd.get_singleton()
        self.layer          = {}
        self.layer['content'] = Layer('content', self.renderer)
        self.layer['alpha']   = Layer('alpha', self.renderer, True)
        self.layer['bg']      = Layer('bg', self.renderer)
        self.complete_bg      = self.renderer.screen.convert()

        self.width  = self.renderer.width
        self.height = self.renderer.height
        

    def clear(self):
        """
        Clear the complete screen
        """
        for l in self.layer:
            self.layer[l].clear()
        self.layer['bg'].add_to_update_rect(0, 0, 800, 600)


    def add(self, layer, object):
        """
        Add object to a specific layer. Right now, this screen has
        only three layers: bg, alpha and content
        """
        return self.layer[layer].add(object)
    
            
    def remove(self, layer, object):
        """
        Remove an object from the screen
        """
        return self.layer[layer].remove(object)



    def show(self):
        """
        Show the screen using pygame
        """
        if self.renderer.must_lock:
            # only lock s_alpha layer, because only there
            # are pixel operations (round rectangle)
            self.layer['alpha'].lock()

        bg    = self.layer['bg']
        alpha = self.layer['alpha']

        update_area = bg.draw()[0]

        update_area = alpha.expand_update_rect(update_area)

        if update_area:
            alpha.screen.fill((0,0,0,0))
            alpha.draw()

        # and than blit only the changed parts of the screen
        for x0, y0, x1, y1 in update_area:
            self.complete_bg.blit(bg.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))
            self.complete_bg.blit(alpha.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))

        content = self.layer['content']

        update_area = content.expand_update_rect(update_area)

        for x0, y0, x1, y1 in update_area:
            content.blit(self.complete_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))

        rect = content.draw()[1]

        for x0, y0, x1, y1 in update_area:
            self.renderer.screenblit(content.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))

        if self.renderer.must_lock:
            self.s_alpha.unlock()

        if update_area:
            self.renderer.update([rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]])
