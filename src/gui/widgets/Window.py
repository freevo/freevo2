# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Window - A window for freevo.
# -----------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.4  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.3  2004/06/23 20:23:57  dischi
# handle crash
#
# Revision 1.2  2004/06/13 19:21:39  dischi
# prevent strange crash
#
# Revision 1.1  2004/02/18 21:52:04  dischi
# Major GUI update:
# o started converting left/right to x/y
# o added Window class as basic for all popup windows which respects the
#   skin settings for background
# o cleanup on the rendering, not finished right now
# o removed unneeded files/functions/variables/parameter
# o added special button skin settings
#
# Some parts of Freevo may be broken now, please report it to be fixed
#
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

import copy

import config
import rc

from GUIObject import GUIObject, Align
from Container import Container


class Window(GUIObject):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    """
    
    def __init__(self, parent='osd', x=None, y=None, width=0, height=0):
        GUIObject.__init__(self, x, y, width, height)

        if not parent or parent == 'osd':
            parent = self.osd.app_list[0]

        parent.add_child(self)
        
        self.osd.add_app(self)

        self.event_context = 'input'
        rc.set_context(self.event_context) 

        if not width:
            self.width  = self.osd.width / 2

        if not height:
            self.height = self.osd.height / 4

        if not self.left:
            self.left = self.osd.width/2 - self.width/2

        if not self.top:
            self.top  = self.osd.height/2 - self.height/2
            self.center_on_screen = True

        self.internal_h_align = Align.CENTER
        self.internal_v_align = Align.CENTER


    def add_child(self, child):
        if self.content:
            self.content.add_child(child)

    def __init__content__(self):
        x, y, width, height = self.content_layout.x, self.content_layout.y, \
                              self.content_layout.width, self.content_layout.height
        width  = eval(str(width),  { 'MAX': self.width }) or self.width
        height = eval(str(height), { 'MAX': self.height }) or self.height

        self.content = Container('frame', x, y, width, height, vertical_expansion=1)
        GUIObject.add_child(self, self.content)

        # adjust left to content
        self.left += (self.width - width-x) / 2

        self.content.internal_h_align = Align.CENTER
        self.content.internal_v_align = Align.CENTER


    def set_size(self, width, height):
        width  -= self.width
        height -= self.height

        self.width  += width
        self.height += height

        width, height = self.content_layout.width, self.content_layout.height
        self.content.width  = eval(str(width),  { 'MAX': self.width }) or self.width
        self.content.height = eval(str(height), { 'MAX': self.height }) or self.height
        
        self.left = self.osd.width/2 - self.width/2
        self.top  = self.osd.height/2 - self.height/2

        # adjust left to content
        self.left += (self.width - self.content.width-self.content.left) / 2

        

    def _draw(self):
        """
        The actual internal draw function.

        """
        _debug_('Window::_draw %s' % self, 2)

        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'

        cheight = self.content.height
        self.content.layout()

        # resize when content changed the height because of the layout()
        if self.content.height - cheight > 0:
            self.height += self.content.height - cheight

        self.surface = self.osd.Surface(self.get_size()).convert_alpha()
        self.surface.fill((0,0,0,0))
            
        for o in self.background_layout:
            if o[0] == 'rectangle':
                r = copy.deepcopy(o[1])
                r.width  = eval(str(r.width),  { 'MAX' : self.get_size()[0] })
                r.height = eval(str(r.height), { 'MAX' : self.get_size()[1] })
                if not r.width:
                    r.width  = self.get_size()[0]
                if not r.height:
                    r.height = self.get_size()[1]
                if r.x + r.width > self.get_size()[0]:
                    r.width = self.get_size()[0] - r.x
                if r.y + r.height > self.get_size()[1]:
                    r.height = self.get_size()[1] - r.y
                self.osd.drawroundbox(r.x, r.y, r.x+r.width, r.y+r.height,
                                      r.bgcolor, r.size, r.color, r.radius,
                                      self.surface)

        self.get_selected_child = self.content.get_selected_child
        if not self.content.parent:
            print '******************************************************************'
            print 'Error: content has no parent, fixing...'
            print 'If you can reproduce this error message, please send a'
            print 'mail with the subject \'[Freevo-Bugreport] GUI\' to'
            print 'freevo@dischi-home.de.'
            print '******************************************************************'
            self.content.parent = self
            
        if not self.parent:
            print '******************************************************************'
            print 'Error: window has no parent, not showing...'
            print 'If you can reproduce this error message, please send a'
            print 'mail with the subject \'[Freevo-Bugreport] GUI\' to'
            print 'freevo@dischi-home.de.'
            print '******************************************************************'
            return
            
        self.content.surface = self.content.get_surface()
        self.content.draw()
        self.blit_parent()
        
