#!/usr/bin/env python
#-----------------------------------------------------------------------
# ZIndexRenderer - A class for handling layers of stuff.
#-----------------------------------------------------------------------
# $Id$
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/03/02 20:11:36  rshortt
# Started fixing up ZIndexRenderer.py.  Working on update_hide() and
# update_show(), commented out the old code for now.  show() and hide() on
# GUIObjects now keep track of what is behind them so it can be replaced
# when they go away.
#
# Revision 1.3  2003/02/24 11:53:23  rshortt
# ZIndexRenderer has a nasty bug which results in _huge_ memory usage.  For
# every single instance of GUIObject (even if it is not drawn, visible, or
# takes up any area) it creates a bitmap copy of the entire screen which are
# all ~1.3 Mb.  Right now the ZIndexRenderer functionality is not used
# anyway so I am temporarily commenting out the references to it in GUIObject.
# I will be working to fix it and to store proger background images for all
# visible objects.
#
# I have added some debugging code to ZIndexRenderer.py that dumps the bmp
# file for each object into /tmp.
#
# Revision 1.2  2003/02/18 13:40:53  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
# Revision 1.1  2002/12/07 15:21:31  dischi
# moved subdir gui into src
#
# Revision 1.2  2002/09/21 10:06:47  dischi
# Make it work again, the last change was when we used osd_sdl.py
#
# Revision 1.1  2002/08/15 22:45:42  tfmalt
# o Inital commit of Freevo GUI library. Files are put in directory 'gui'
#   under Freevo.
# o At the moment the following classes are implemented (but still under
#   development):
#     Border, Color, Label, GUIObject, PopupBox, ZIndexRenderer.
# o These classes are fully workable, any testing and feedback will be
#   appreciated.
#
#-----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------
"""
A class for handling layers of stuff on top of each other.

"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import osd
import pygame

osd = osd.get_singleton()

DEBUG = 1

_singleton = None

def get_singleton():
    """
    Singleton is a good way to keep an object consistant over several
    instances..
    """
    global _singleton
    if _singleton == None:
        _singleton = ZIndexRenderer()

    return _singleton


class ZIndexRenderer:
    """
    Keeps track of what is on top of under what.

    A simple render class updating the erasearea information of all GUI
    objects visible on screen. Handling screen updates on erase and
    draw.

    This should give you GUI objects you can freely move around under
    or over other objects on screen. We probably won't use very
    complicated screens so often, but this should handle it.

    Notes: I'd really like thoughts on this. I'm thinking about
           inheriting a render class from pygame.sprite, but I can't
           find a real good use for it yet.
    Todo:  Need to optimize the update functions. Only update rectangles
           which have coordinates inside the changing rectangle, only save
           the needed part of the the background.
           Implement 'raise' and 'lower' when I need them.
    """
    
    def __init__(self):
        """
        Don't know what to do with constructor yet, but I'm sure I want it.
        """
        self.zindex = []

    def get_zindex(self):
        """
        Return a reference to the zindex.
        """
        return self.zindex

    def add_object(self, object):
        """
        Appends a reference to object to the zindex list.
        All objects are put 'on top of each other' in the order they
        are instanticed.
 
        Arguments: object - the object to add
        Returns:   index  - the index no in the stack.
        Note:      Should objects themselves be alowed to raise or lower
                   themselves in the stack?
        """ 
        self.zindex.append(object)
        return self.zindex.index(object)
 
    def del_object(self, object):
        """
        Really delete object from stack.

        Arguments: object to delete.
        Notes:     Maybe rename to kill.
        """
        self.zindex.remove(object)


    def update_hide(self, object):
        """
        Updates all affected objects when there is a hide.
        
        Notify objects above the calling object to do a redraw.
        Does anyone have a better idea for a name for this function?
        """
        # oi = self.zindex.index(object)
        # if not len(self.zindex) > (oi+1):
        #     return

        # ol   = self.zindex[(oi+1):]
        # t_bg = object.bg_image.convert()
        # for o in ol:
        #     if o.is_visible():
        #         if o.border:
        #             # Erase a little bigger area when we have borders.
        #             x,y,w,h = o.border.get_erase_rect()
        #         else:
        #             x,y,w,h = o.get_rect()
                    
        #         o.bg_image.blit(t_bg, (x,y), (x,y,w,h))
        #         o._erase()

        # for o in ol:
        #     if o.is_visible():
        #         o.bg_image = osd.screen.convert()
        #         o._draw()

        for o in self.zindex:
            if o == object:
                if o.bg_surface:
                    osd.putsurface(o.bg_surface, o.left, o.top)


    def update_show(self, object):        
        """
        Updates all affected objects when there is a show.
        
        Notify objects above the calling object to do a redraw.
        Does anyone have a better idea for a name for this function?
        """

        # oi = self.zindex.index(object) 
        # ol = self.zindex[(oi):]

        # object.bg_surface = osd.getsurface(object.left, object.top, 
        #                                    object.width, object.height)
        # object.bg_image = object.bg_surface.convert()

        # if object.bg_image: t_bg = object.bg_image.convert()
        # xx = 0
        # for o in ol:
        #     if not o == object and o.is_visible():
        #         if o.border:
        #             x,y,w,h = o.border.get_erase_rect()
        #         else:
        #             x,y,w,h = o.get_rect()
 
        #         if t_bg: o.bg_image.blit( t_bg, (x,y), (x,y,w,h))
        #         o._erase() 

        xx = 0
        for o in self.zindex:
            if o == object:
                o.bg_surface = osd.getsurface(o.left, o.top, 
                                              o.width, o.height)
                if DEBUG:
                    o.bg_image = o.bg_surface.convert()
                    iname = '/tmp/bg1-%s.bmp' % xx
                    pygame.image.save( o.bg_image, iname )
                o._draw()
            xx += 1

        # xx = 0
        # for o in ol:
        #     if o == object or o.is_visible():
        #         o.bg_image = osd.screen.convert()
        #         iname = '/tmp/bg2-%s.bmp' % xx
        #         pygame.image.save( o.bg_image, iname )
        #         xx = xx + 1
        #         o._draw()


