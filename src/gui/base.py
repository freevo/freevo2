# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# base.py - Basic objects for using a GUI
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


class Layer:
    def blit(self, layer, *arg1, **arg2):
        """
        Interface for the objects to blit something on the layer
        """
        raise TypeError, 'member function blit not defined for layer'
            

    def drawroundbox(self, *arg1, **arg2):
        """
        Interface for the objects draw a round box
        """
        raise TypeError, 'member function drawroundbox not defined for layer'


    def drawstringframed(self, *arg1, **arg2):
        """
        Interface for the objects draw a string
        """
        raise TypeError, 'member function drawstringframed not defined for layer'


    def add(self, object):
        """
        Add an object to this layer
        """
        raise TypeError, 'member function add not defined for layer'


    def remove(self, object):
        """
        Add an object from this layer
        """
        raise TypeError, 'member function remove not defined for layer'
        

    def clear(self):
        """
        Add an object from this layer
        """
        raise TypeError, 'member function clear not defined for layer'



class Screen:
    def clear(self):
        """
        Clear the complete screen
        """
        raise TypeError, 'member function clear not defined for layer'


    def add(self, layer, object):
        """
        Add object to a specific layer.
        """
        raise TypeError, 'member function add not defined for layer'
    
            
    def remove(self, layer, object):
        """
        Remove an object from the screen
        """
        raise TypeError, 'member function remove not defined for layer'


    def show(self):
        """
        Show the screen
        """
        raise TypeError, 'member function show not defined for layer'

        

class GUIObject:
    """
    Basic gui object
    """
    def __init__(self, x1, y1, x2, y2):
        self.x1    = x1
        self.y1    = y1
        self.x2    = x2
        self.y2    = y2
        self.layer = None


    def draw(self, rect=None):
        pass



class Text(GUIObject):
    """
    A text object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, text, font, height, align_h, align_v, mode, 
                 ellipses, dim):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.text     = text
        self.font     = font
        self.height   = height
        self.align_h  = align_h
        self.align_v  = align_v
        self.mode     = mode
        self.ellipses = ellipses
        self.dim      = dim


    def draw(self, rect=None):
        if not self.layer:
            raise TypeError, 'no layer defined for %s' % self
        self.layer.drawstringframed(self.text, self.x1, self.y1, self.x2 - self.x1,
                                    self.height, self.font, align_h = self.align_h,
                                    align_v = self.align_v, mode=self.mode,
                                    ellipses=self.ellipses, dim=self.dim)

        
    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.text != o.text or self.font != o.font or \
                   self.height != o.height or self.align_h != o.align_h or \
                   self.align_v != o.align_v or self.mode != o.mode or \
                   self.ellipses != o.ellipses or self.dim != o.dim
        except:
            return 1
        

class Rectangle(GUIObject):
    """
    A rectangle object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, bgcolor, size, color, radius):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.bgcolor = bgcolor
        self.size    = size
        self.color   = color
        self.radius  = radius


    def draw(self, rect=None):
        if not self.layer:
            raise TypeError, 'no layer defined for %s' % self
        self.layer.drawroundbox(self.x1, self.y1, self.x2, self.y2, color=self.bgcolor,
                                border_size=self.size, border_color=self.color,
                                radius=self.radius)

            
    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.bgcolor != o.bgcolor or \
                   self.size != o.size or self.color != o.color or self.radius != o.radius
        except:
            return 1
    



class Image(GUIObject):
    """
    An image object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, image):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.image = image


    def draw(self, rect=None):
        if not self.layer:
            raise TypeError, 'no layer defined for %s' % self
        if not rect:
            self.layer.blit(self.image, (self.x1, self.y1))
        else:
            x1, y1, x2, y2 = rect
            if not (self.x2 < x1 or self.y2 < y1 or self.x1 > x2 or self.y1 > y2):
                self.layer.blit(self.image, rect[:2],
                                (x1-self.x1, y1-self.y1, x2-x1, y2-y1))


    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.image != o.image
        except Exception, e:
            print e
            return 1
