#!/usr/bin/env python
#-----------------------------------------------------------------------
# GUIObject - Common object for all GUI Classes
#-----------------------------------------------------------------------
# $Id$
#
# Todo: o Add move function 
#-----------------------------------------------------------------------
# $Log$
# Revision 1.19  2003/04/26 16:46:24  dischi
# added refresh bugfix from Matthieu Weber
#
# Revision 1.18  2003/04/24 19:56:19  dischi
# comment cleanup for 1.3.2-pre4
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
A Object Oriented GUI Widget library for Freevo

This is aimed at being a general library for GUI programming with Freevo.
It is built directly on top of SDL with pygame, and it's aimed at being
fairly fast.

Event though the library is built from the ground the design is heavy
influenced by other GUI toolkits, such as Java JDK and QT.

Currently not many classes are in place, but hopefully we will add more
in time.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import pygame
import rc
import osd
import config
import skin
import ZIndexRenderer

from Color import *

DEBUG = 0


class GUIObject:
    """
    Common parent class of all GUI objects. You can override this to make
    new Widgets.
    """


    def __init__(self, left=0, top=0, width=0, height=0,
                 bg_color=None, fg_color=None):

        self.osd  = osd.get_singleton()
        self.skin = skin.get_singleton()
        self.zir  = ZIndexRenderer.get_singleton()

        self.label          = None
        self.selected_label = None
        self.icon           = None
        self.bg_surface     = None
        self.bg_image       = None

        if not hasattr(self, 'parent'):
            self.parent = None

        elif self.parent == 'osd':
            self.parent = self.osd.focused_app
            
        self.children       = []
        self.enabled        = 1
        self.selected       = 0
        self.visible        = 1

        self.left     = left
        self.top      = top
        self.width    = width
        self.height   = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        

        if DEBUG: print "inside GUIOBJECT INIT"

        # XXX: skin settings
        # This if/else should be removed when the new skin is in place.
        self.skin_info                 = self.skin.GetPopupBoxStyle(self)
        self.skin_info_background      = self.skin_info[0]
        self.skin_info_spacing         = self.skin_info[1]
        self.skin_info_color           = self.skin_info[2]
        self.skin_info_font            = self.skin_info[3]
        self.skin_info_widget          = self.skin_info[4]
        self.skin_info_widget_selected = self.skin_info[5]

        if self.skin_info_spacing:
            self.h_margin = self.skin_info_spacing
            self.v_margin = self.skin_info_spacing
        else:
            self.h_margin = 10
            self.v_margin = 10

        if not self.bg_color:
            if self.skin_info_background[0] == 'rectangle' \
                and self.skin_info_background[1].bgcolor:
                self.bg_color = Color(self.skin_info_background[1].bgcolor)
            else:
                self.bg_color = Color(self.osd.default_bg_color)

        if not self.fg_color:
            if self.skin_info_color:
                self.fg_color = Color(self.skin_info_color)
            else:
                self.fg_color = Color(self.osd.default_fg_color)


        self.zindex_pos = self.zir.add_object(self)
        
        self.set_v_align(Align.NONE)
        self.set_h_align(Align.NONE)

        if self.parent:
            self.parent.add_child(self)
            if DEBUG: print 'set focus to %s' % self
            self.osd.focused_app = self


    def get_rect(self):
        """
        Return SDL rect information for the object.

        Returns: left,top,width,height
        """
        return (self.left, self.top, self.width, self.height)
        # return [self.left, self.top, self.width, self.height]
 

    def get_position(self):
        """
        Gets the coordinates of the GUIObject

        Arguments: None
        Returns:   (x, y) - The coordinates of top left coner as list.
        """
        return (self.left, self.top)


    def set_position(self, left, top=None):
        """
        Set the position of the GUIObject
        """
        # XXX Please tell if you know of a better way to accept both
        # XXX tuples and lists.
        if type(left) is ListType or type(left) is TupleType:
            self.left, self.top = left
        else:
            self.left = left
            self.top  = top


    def get_size(self):
        """
        Get the width and height of box

        Arguments: None
        Returns:   (width, height) - as list.
        """
        return (self.width, self.height)


    def set_size(self, width, height=None):
        """
        Set the width adn height of box
        """
        if type(width) is ListType or TupleType:
            self.width, self.height = width
        else:
            self.width  = width
            self.height = height


    def get_foreground_color(self):
        """
        Returns the foreground color of object
        """
        return self.fg_color
    

    def set_foreground_color(self, color):
        """
        Sets the foreground color of object.
        """
        if isinstance(color, Color):
            self.fg_color = color
        else:
            raise BadColorException, type(color)
           

    def get_background_color(self):
        """
        Returns the background color of object.
        """
        return self.bg_color
    

    def set_background_color(self, color):
        """
        Sets the background color of object.

        If None background color will be transparent.
        """
        if isinstance(color, Color):
            self.bg_color = color
        elif not color:
            self.bg_color = None
        else:
            raise BadColorException, type(color)


    def show(self):
        """
        Shows the object.

        This is really handled by the render object.
        """
        self.visible = 1    
        self.zir.update_show(self)
        self.osd.update(self.get_rect())


    def hide(self):
        """
        Hide the object.
        """

        self.visible = 0
        self.zir.update_hide(self)
        self.osd.update(self.get_rect())


    def move(self, x, y):
        """
        x Integer, amount to move along x axis.
        y Integer, amount to move along y axis.
        
        Move the object by a certain amount

        Note: either the user would have to hide and show the object
              moving, or we do it for him. Not decided yet.
        """
        self._erase()
        # self.zir.update_hide(self)
        self.visible = 0
        self.set_position( self.left+x, self.top+y )
        self.draw()
        # self.zir.update_show(self)
        self.visible = 1

        
    def is_visible(self):
        """
        Returns whether the object is visible or not.

        Returns: 0 or 1 
        """
        return self.visible

    
    def enable(self):
        self.enabled = 1


    def disable(self):
        self.enabled = 0


    def toggle_selected(self):
        if self.selected:
            self.selected = 0
        else:
            self.selected = 1


    def redraw(self):
        """
        Does a redraw of the object.

        At the moment not implemented.
        """
        pass


    def refresh(self):
        """
        At the moment not implemented.
        """
        pass


    def draw(self, surface=None):
        if self.is_visible() == 0: return

        if self.bg_surface:
            if DEBUG: print 'GUIObject::draw: have bg_surface'
            self.osd.putsurface(self.bg_surface, self.left, self.top)

        if surface:
            self._draw(surface)
        else:
            self._draw()


    def _draw(self, surface=None):
        """
        This function should be overriden by those
        objects that inherit this.
        """
        pass


    def set_parent(self, parent):
        """Set the parent of this widget
        """
        if self.parent != parent and self.parent and self in self.parent.children:
            self.parent.children.remove(self)
            
        self.parent = parent


    def get_parent(self):
        return self.parent


    def add_child(self, child):
        """Add a child widget.
        """
        self.children.append(child)
        child.set_parent(self)


    def get_children(self):
        return children


    def eventhandler(self, event):
        return self.parent.eventhandler(event)


    def destroy(self):
        if DEBUG:
            if self.bg_image:
                iname = '/tmp/bg-%s-%s.bmp' % (self.left, self.top)
                pygame.image.save( self.bg_image, iname )

        if DEBUG: print 'GUIObject.destroy(): %s' % self

        if self.children:
            while self.children:
                child = self.children[0]
                child.destroy() # the child will remove itself from children
                
        if DEBUG: print 'parent: %s' % self.parent
        if self.parent:
            self.parent.children.remove(self)
            if self.osd.focused_app == self:
                if DEBUG: print 'GUIObject.destroy(): focused_app=%s' % \
                                 self.osd.focused_app
                self.osd.focused_app = self.parent
                if DEBUG: print 'GUIObject.destroy(): focused_app=%s' % \
                                 self.osd.focused_app
            else:
                if DEBUG: print 'focus has %s not %s' % (self.osd.focused_app, self)
                
            # We shouldn't need to call this if we replace the bg right
            # self.parent.refresh()

        self.hide()
        if self.parent:
            self.parent.refresh()
        self.set_parent(None)


    def get_h_align(self):
        """
        Returns horisontal align of text.
        """
        return self.h_align


    def get_v_align(self):
        """
        returns vertical alignment of text
        """
        return self.v_align

    
    def set_h_align(self, align):
        """
        Sets horizontal alignment of text.
        """
        if type(align) is IntType and align >= 1000 and align < 1004:
                self.h_align = align
        else:
            raise TypeError, align


    def set_v_align(self, align):
        """
        Sets vertical alignment of text.
        """
        if type(align) is IntType and (align == 1000 or (align > 1003 and align < 1007)):
            self.v_align = align
        else:
            raise TypeError, align


    def get_v_margin(self):
        """
        Returns the margin for objects drawing directly on the osd.
        """
        return self.v_margin


    def get_h_margin(self):
        """
        Returns the margin for objects drawing directly on the osd.

        This is not optimal and I'll probably remove this function soon.
        """
        return self.h_margin


    def set_v_margin(self, marg):
        """
        Sets the vertical margin.
        """
        self.v_margin = marg


    def set_h_margin(self, marg):
        """
        Sets the horisontal margin
        """
        self.h_margin = marg


    def calc_position(self):
        """
        Private function to calculate correct positon of a widget.
        """
        if not self.parent: raise ParentException
        # if not self.font:   raise TypeError, 'No font'

        # Render the surface if we don't have it to get correct size.
        # if not self.surface: self.render()
        
        lx          = 0
        ly          = 0
        bx,by,bw,bh = self.parent.get_rect()
        lw,lh       = self.get_size()
        va          = self.v_align
        ha          = self.h_align
        hm          = self.h_margin
        vm          = self.v_margin
        
        if ha == Align.LEFT:
            if self.parent.icon:
                iw = self.parent.icon.get_width()
                pm = hm
                lx = bx+iw+(pm*2)
            else:
                lx = bx+hm
        elif ha == Align.CENTER:
            lx = bx+((bw-lw)/2)
        elif ha == Align.RIGHT:
            lx = bx+bw-lw-hm
        elif ha == Align.NONE:
            lx = self.left
        else:
            raise TypeError, 'Wrong h_align'

        if va == Align.TOP:
            ly = by+vm
        elif va == Align.BOTTOM:
            ly = by+bh-lh-vm
        elif va == Align.MIDDLE:
            ly = by+((bh-lh)/2)
        elif va == Align.NONE:
            ly = self.top
        else:
            raise TypeError, 'Wrong v_align'
            
        # for child in self.children:
        #     child.calc_position()

        return (lx,ly)


class Align:

    NONE   = 1000 
    CENTER = 1001
    LEFT   = 1002
    RIGHT  = 1003
    TOP    = 1004
    BOTTOM = 1005
    MIDDLE = 1006


