# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Container.py - Container class for the GUI.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.9  2004/03/13 22:33:15  dischi
# changes for the new input widget
#
# Revision 1.8  2004/02/18 21:52:04  dischi
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


import config
from GUIObject      import GUIObject
from GUIObject      import Align
from LayoutManagers import FlowLayout
from LayoutManagers import GridLayout
from LayoutManagers import BorderLayout
from Color import Color
from Border import Border


class Container(GUIObject):
    """
    """

    def __init__(self, type='frame', left=0, top=0, width=0, height=0, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None, vertical_expansion=0):

        GUIObject.__init__(self, left, top, width, height, bg_color, fg_color)

        self.layout_manager     = None
        self.border             = border
        self.bd_color           = bd_color
        self.bd_width           = bd_width
        self.vertical_expansion = vertical_expansion

        self.internal_h_align   = Align.LEFT
        self.internal_v_align   = Align.TOP
        self.h_spacing          = self.h_margin
        self.v_spacing          = self.v_margin

        if type == 'widget':
            ci = self.content_layout.types['selected'].rectangle
            self.selected_bg_color = selected_bg_color or Color(ci.bgcolor)
            self.selected_fg_color = selected_fg_color or Color(ci.color)
    
            if not self.bd_color:
                self.bd_color = Color(self.skin_info_widget.rectangle.color)
    
            if not self.bd_width:
                self.bd_width = self.skin_info_widget.rectangle.size
    
            if not self.border:
                self.border = Border(self, Border.BORDER_FLAT, self.bd_color, self.bd_width)

            elif border == -1:
                self.border = None


    def set_layout(self, layout=None):
        if not layout:
            layout = FlowLayout(self)
        self.layout_manager = layout


    def get_layout(self):
        return self.layout_manager 


    def layout(self):
        if not self.layout_manager:
            self.layout_manager = FlowLayout(self)

        self.layout_manager.layout()


    def _draw(self):
        _debug_('Container::draw %s' % self, 2)

        for child in self.children:
            if not child == self.border:
                child.draw()

        if self.border and self.border != -1:
            self.border.draw()
