# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# GUIObject - Common object for all GUI Classes
# -----------------------------------------------------------------------
# $Id$
#
# Todo: o Add move function 
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.39  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.38  2004/07/10 10:43:57  dischi
# use screenblit
#
# -----------------------------------------------------------------------
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


import rc
import osd
import config
import skin
import traceback

from Color import *

class GUIObject:
    """
    Common parent class of all GUI objects. You can override this to make
    new Widgets.
    """


    def __init__(self, left=0, top=0, width=0, height=0,
                 bg_color=None, fg_color=None):

        self.osd  = osd.get_singleton()

        self.label       = None
        self.icon        = None
        self.surface     = None
        self.bg_surface  = None
        self.bg_image    = None

        self.parent      = None

        self.children    = []
        self.enabled     = 1
        self.visible     = 1
        self.selected    = 0

        self.left        = left
        self.top         = top
        self.width       = width
        self.height      = height
        self.bg_color    = bg_color
        self.fg_color    = fg_color

        self.event_context = None

        style = skin.get_singleton().get_popupbox_style(self)
        self.content_layout, self.background_layout = style
        
        self.skin_info_widget = self.content_layout.types['widget']
        self.skin_info_font   = self.skin_info_widget.font
        
        self.h_margin = self.content_layout.spacing
        self.v_margin = self.content_layout.spacing

        ci = self.content_layout.types['widget'].rectangle
        self.bg_color = self.bg_color or Color(ci.bgcolor)
        self.fg_color = self.fg_color or Color(ci.color)

        self.set_v_align(Align.NONE)
        self.set_h_align(Align.NONE)


    def get_event_context(self):
        """
        return the event context for that gui widget
        """
        return self.event_context


    def get_rect(self):
        """
        Return SDL rect information for the object.

        Returns: left,top,width,height
        """
        return (self.left, self.top, self.width, self.height)
 

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
        return (int(self.width), int(self.height))


    def set_size(self, width, height=None):
        """
        Set the width adn height of box
        """
        if type(width) is ListType or TupleType:
            self.width, self.height = width
        else:
            self.width  = width
            self.height = height


    def toggle_selected(self):
        self.selected = not self.selected


    def get_selected_child(self):
        for child in self.children:
            if not child.is_visible():
                continue
            if child.selected == 1:
                return child
            else:
                selected = child.get_selected_child()
                if selected:
                    return child


    def show(self):
        """
        Shows the object.

        This is really handled by the render object.
        """
        self.visible = 1    
        self.draw()
        self.osd.update(self.get_rect())


    def hide(self):
        """
        Hide the object.
        """
        self.visible = 0
        if self.parent and self.parent.visible and self.bg_surface:
            self.osd.screenblit(self.bg_surface, self.get_position())
            self.osd.update(self.get_rect())
                


    def move(self, x, y):
        """
        x Integer, amount to move along x axis.
        y Integer, amount to move along y axis.
        
        Move the object by a certain amount

        Note: either the user would have to hide and show the object
              moving, or we do it for him. Not decided yet.
        """
        self.hide()
        self.set_position(self.left+x, self.top+y)
        self.show()

        
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


    def refresh(self):
        """
        At the moment not implemented.
        """
        self.draw()


    def layout(self):
        """
        To be overriden by Container.
        """
        pass


    def draw(self, update=False):
        _debug_('GUIObject::draw %s' % self, 2)

        if self.is_visible() == 0:
            return False

        self.layout()
        self._draw()

        if not update:
            return
        
        # now blit all parent to really update
        object = self.parent
        while object:
            if not self.parent or not self.parent.surface or not object.surface:
                break
            if object.surface == object.surface.get_abs_parent():
                object.blit_parent(restore=False)
            object = object.parent

        self.osd.app_list[-1].blit_parent()
        self.osd.update()

        
    def _draw(self, surface=None):
        """
        This function should be overriden by those
        objects that inherit this.
        """
        pass


    def blit_parent(self, restore=True):
        """
        blit self.surface to the parent.surface
        """
        if self.osd.app_list.count(self):
            p = False
        elif self.parent.surface:
            p = True
        else:
            p = False

        if self.surface != self.surface.get_abs_parent():
            print '******************************************************************'
            print 'Error, surface is a subsurface (%s)' % self
            print 'Please report the following lines to the freevo mailing list'
            print 'or with the subject \'[Freevo-Bugreport\] GUI\' to'
            print 'freevo@dischi-home.de.'
            print
            print 'Error, surface is a subsurface (%s)' % self
            print traceback.print_exc()
            print
            print 'GUIObject stack:'
            c = self
            while c:
                print '  %s' % c
                c = c.parent
            print
            print '******************************************************************'
            return
        
        if not self.bg_surface:
            self.bg_surface = self.osd.Surface((int(self.width), int(self.height)))
            if p:
                self.bg_surface.blit(self.parent.surface, (0,0), self.get_rect())
            else:
                self.bg_surface.blit(self.osd.screen, (0,0), self.get_rect())
        elif restore:
            if p:
                self.parent.surface.blit(self.bg_surface, (self.left, self.top))
            else:
                self.osd.screenblit(self.bg_surface, (self.left, self.top))

        if p:
            self.parent.surface.blit(self.surface, self.get_position())
        else:
            self.osd.screenblit(self.surface, self.get_position())
            self.osd.update(self.get_rect())

            
    def get_surface(self):
        """
        get a subsurface from the parent to draw in
        """
        try:
            return self.parent.surface.subsurface(self.get_rect())
        except Exception, e:
            print '******************************************************************'
            print 'Exception: %s' % e
            print 'Please report the following lines to the freevo mailing list'
            print 'or with the subject \'[Freevo-Bugreport] GUI\' to'
            print 'freevo@dischi-home.de.'
            print
            if not self.parent:
                print 'object has no parent:'
                print self
            elif not hasattr(self.parent, 'surface'):
                print 'parent has no surface:'
                print self, self.parent
            elif not self.parent.surface:
                print 'parent surface is None:'
                print self, self.parent
            else:
                print 'wanted %s for %s' % (self.get_rect(), self.parent.surface)
            print traceback.print_exc()
            print
            print 'GUIObject stack:'
            c = self
            while c:
                print '  %s: %s' % (c, c.get_rect())
                c = c.parent
            print
            print 'Configuration: %sx%s %s %s' % \
                  (self.osd.width, self.osd.height, config.OSD_OVERSCAN_X,
                   config.OSD_OVERSCAN_Y)
            print
            raise Exception, e


    def set_parent(self, parent):
        """
        Set the parent of this widget
        """
        if self.parent != parent and self.parent and self in self.parent.children:
            self.parent.children.remove(self)
            
        self.parent = parent


    def get_parent(self):
        return self.parent


    def add_child(self, child):
        """
        Add a child widget.
        """
        self.children.append(child)
        child.set_parent(self)


    def get_children(self):
        return children


    def eventhandler(self, event):
        return self.parent.eventhandler(event)


    def destroy(self):
        self.visible = 0

        if self.children:
            while self.children:
                child = self.children[0]
                child.destroy() # the child will remove itself from children
                
        _debug_('parent: %s' % self.parent, 2)
        if self.parent:
            self.parent.children.remove(self)

        self.osd.remove_app(self)
                
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
        # XXX: fix this ugly statement
        if type(align) is IntType and \
               (align == 1000 or align == 1001 or (align > 1003 and align < 1007)):
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
        elif va == Align.CENTER:
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


