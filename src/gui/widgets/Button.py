# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Button.py - a simple button class
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.21  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.20  2004/02/24 18:56:09  dischi
# add hfill to text_prop
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------- */


import config

from GUIObject  import *
from Container  import *
from Label      import * 


class Button(Container):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      The label on the button. String
    handler   Function to call when button is hit
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    selected_bg_color  Background color (Color)
    selected_fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """
    def __init__(self, text=' ', handler=None, left=None, top=None, 
                 width=70, height=None, bg_color=None, fg_color=None, 
                 selected_bg_color=None, selected_fg_color=None,
                 border=-1, bd_color=None, bd_width=None):

        default_button_height = 25

        if not height:
            height = default_button_height

        Container.__init__(self, 'widget', left, top, width, height, bg_color,
                           fg_color, selected_bg_color, selected_fg_color,
                           border, bd_color, bd_width)

        self.h_margin = 2
        self.v_margin = 2
        self.handler  = handler

        if text and type(text) in StringTypes:
            self.set_text(text)
        else:
            self.set_text('')

        button_normal      = self.content_layout.types['button']
        font_percent       = button_normal.font.size * 100 / default_button_height 
        self.info_normal   = button_normal, int(font_percent * self.height / 120)
        
        button_selected    = self.content_layout.types['button selected']
        font_percent       = button_selected.font.size * 100 / default_button_height 
        self.info_selected = button_selected, int(font_percent * self.height / 120)

        self.fg_color  = fg_color or Color(button_normal.rectangle.color)
        self.bg_color  = bg_color or Color(button_normal.rectangle.bgcolor)

        self.selected_fg_color = selected_fg_color or Color(button_selected.rectangle.color)
        self.selected_bg_color = selected_bg_color or Color(button_selected.rectangle.bgcolor)
    
        # now check the height, maybe the font is too large
        self.height = max(self.height, button_normal.height + 2 * self.v_margin,
                          button_selected.font.height + 2 * self.v_margin)

        # the label to not selected font
        self.__set_font__()

        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)


    def __set_font__(self):
        if self.selected:
            i = self.info_selected
        else:
            i = self.info_normal
        self.label.set_font(i[0].font.name, i[1], Color(i[0].font.color))
        

    def toggle_selected(self):
        self.selected = not self.selected
        self.__set_font__()


    def _draw(self):
        if not self.width or not self.height or not self.text:
            raise TypeError, 'Not all needed variables set.'

        if self.selected:
            rect = self.content_layout.types['button selected'].rectangle
        else:
            rect = self.content_layout.types['button'].rectangle

        self.surface = self.get_surface()
        if not self.border:
            self.osd.drawroundbox(0, 0, self.width, self.height,
                                  rect.bgcolor, rect.size, rect.color,
                                  rect.radius, self.surface)
        else:
            self.osd.drawroundbox(0, 0, self.width, self.height,
                                  rect.bgcolor, 0, rect.color,
                                  0, self.surface)
        Container._draw(self)

    
    def get_text(self):
        return self.text

        
    def set_text(self, text):
        if type(text) in StringTypes:
            self.text = text
        else:
            raise TypeError, type(text)

        if not self.label:
            self.label = Label(h_align = Align.CENTER, v_align = Align.CENTER,
                               text_prop = { 'align_h': 'center',
                                             'align_v': 'center',
                                             'mode' : 'hard',
                                             'hfill': False } )
            self.label.set_text(text)
            self.add_child(self.label)
        else:
            self.label.set_text(text)
