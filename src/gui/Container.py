#!/usr/bin/env python
#-----------------------------------------------------------------------
# Container.py - Container class for the GUI.
#-----------------------------------------------------------------------
# $Id$
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.4  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.3  2003/04/24 19:56:18  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.2  2003/04/22 23:54:08  rshortt
# Merge parts of popupbox and button.
#
# Revision 1.1  2003/04/09 01:38:10  rshortt
# Initial commit of some in-progress classes.
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

import pygame
import config
from GUIObject      import GUIObject
from GUIObject      import Align
from LayoutManagers import FlowLayout
from LayoutManagers import GridLayout
from LayoutManagers import BorderLayout
from Color import Color
from Border import Border

DEBUG = config.DEBUG


class Container(GUIObject):
    """
    """

    def __init__(self, type='frame', left=0, top=0, width=0, height=0, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None, vertical_expansion=0):

        GUIObject.__init__(self, left, top, width, height, bg_color, fg_color)

        self.layout_manager = None
        self.border         = border
        self.bd_color       = bd_color
        self.bd_width       = bd_width
        self.vertical_expansion = vertical_expansion

        self.internal_h_align = Align.LEFT
        self.internal_v_align = Align.TOP

        if self.skin_info_spacing:
            self.h_margin = self.skin_info_spacing
            self.v_margin = self.skin_info_spacing
        else:
            self.h_margin = 10
            self.v_margin = 10

        self.h_spacing = self.h_margin
        self.v_spacing = self.v_margin

        if type == 'frame':
            if not self.bd_color:
                # XXX TODO: background type 'image' is not supported here yet
                if self.skin_info_background[0] == 'rectangle':
                    self.bd_color = Color(self.skin_info_background[1].color)
                else:
                    self.bd_color = Color(self.osd.default_fg_color)
    
            if not self.bd_width:
                if self.skin_info_background[0] == 'rectangle' \
                    and self.skin_info_background[1].size:
                    self.bd_width = self.skin_info_background[1].size
                else:
                    self.bd_width = 2

            if not self.border:
                self.border = Border(self, Border.BORDER_FLAT,
                                     self.bd_color, self.bd_width)

        elif type == 'widget':
            self.selected_bg_color = selected_bg_color
            self.selected_fg_color = selected_fg_color

            if not bg_color:
                if self.skin_info_widget.rectangle.bgcolor:
                    self.bg_color = Color(self.skin_info_widget.rectangle.bgcolor)
                else:
                    self.bg_color = Color(self.osd.default_bg_color)
    
            if not fg_color:
                if self.skin_info_widget.font.color:
                    self.fg_color = Color(self.skin_info_widget.font.color)
                else:
                    self.fg_color = Color(self.osd.default_fg_color)
    
            if not self.selected_bg_color:
                if self.skin_info_widget_selected.rectangle.bgcolor:
                    self.selected_bg_color = Color(self.skin_info_widget_selected.rectangle.bgcolor)
                else:
                    self.selected_bg_color = Color((0,255,0,128))
    
            if not self.selected_fg_color:
                if self.skin_info_widget_selected.font.color:
                    self.selected_fg_color = Color(self.skin_info_widget_selected.font.color)
                else:
                    self.selected_fg_color = Color(self.osd.default_fg_color)
    
            if not self.bd_color:
                if self.skin_info_widget.rectangle.color:
                    self.bd_color = Color(self.skin_info_widget.rectangle.color)
                else:
                    self.bd_color = Color(self.osd.default_fg_color)
    
            if not self.bd_width:
                if self.skin_info_widget.rectangle.size:
                    self.bd_width = self.skin_info_widget.rectangle.size
                else:
                    self.bd_width = 2
    
            if not self.border:
                self.border = Border(self, Border.BORDER_FLAT,
                                     self.bd_color, self.bd_width)


    def set_layout(self, layout=None):
        if not layout: layout = FlowLayout(self)
        self.layout_manager = layout


    def get_layout(self):
        return self.layout_manager 


    def layout(self):
        if not self.layout_manager:
            self.layout_manager = FlowLayout(self)

        self.layout_manager.layout()


    def _draw(self):
        if DEBUG: print 'Container::draw %s' % self

        for child in self.children:
            child.draw()

        if self.icon:
            # note that icon handling will be changed totally, ignore this
            ix,iy = self.get_position()
            self.osd.screen.blit(self.icon, (ix+self.h_margin,iy+self.v_margin))


    def set_border(self, bs):
        """
        bs  Border style to create.

        Set which style to draw border around object in. If bs is 'None'
        no border is drawn.

        Default for PopubBox is to have no border.
        """
        if isinstance(self.border, Border):
            self.border.set_style(bs)
        elif not bs:
            self.border = None
        else:
            self.border = Border(self, bs)



