# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# grid_area.py - A grid area for the Freevo skin
# -----------------------------------------------------------------------------
# $Id: grid_area.py 9536 2007-05-01 11:35:34Z dmeyer $
#
# This module include the GridArea used in the area code for drawing the
# grid areas for menus. It inherits from Area (area.py) and the update
# function will be called to update this area.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Joost <joost.kop@gmail.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'GridArea' ]

# python imports
import copy
import os
import math
import time
import array

# kaa imports
from kaa.notifier import Timer

# gui import
from area import Area
from freevo.ui.gui.widgets import Image, Rectangle

import logging
log = logging.getLogger('gui')

from freevo.ui import config
from freevo.ui.gui import imagelib

class _Geometry(object):
    """
    Simple object with x, y, with, height values
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height
        self.active_col = 0
        self.active_row = 0

    def __str__(self):
        return '_Geometry: %s,%s %sx%s' % \
               (self.x, self.y, self.width, self.height)

class GridArea(Area):
    """
    This class defines the GridArea to draw menu grids for the area
    part of the gui code.
    """
    def __init__(self):
        """
        Create the Area and define some needed variables
        """
        Area.__init__(self, 'grid')
        self.col_width = 0
        self.col_height = 0
        self.cols = 1
        self.row_width = 0
        self.row_height = 0
        self.rows = 1
        
        self.row_val     = None
        self.column_val      = None
        self.selected_val  = None
        self.default_val   = None
        
        # objects on the area
        self.row_obj   = []
        self.col_obj   = []
        self.up_arrow   = None
        self.down_arrow = None
        self.objects    = []
        self.background = None


    def __calc_items_geometry(self):
        # get the settings
        settings = self.settings

        # get all values for the different types
        self.row_val       = settings.types['row']
        self.column_val    = settings.types['column']
        self.selected_val  = settings.types['selected']
        self.default_val   = settings.types['default']
        
        # get max font height
        max_font_h = max(self.selected_val.font.height, self.default_val.font.height,
                     self.row_val.font.height)


        # get Row width
        self.row_width = self.row_val.width

        # get col height
        self.col_height = self.column_val.font.height
        if self.column_val.rectangle:
            r = self.column_val.rectangle.calculate(20, self.column_val.font.height)[2]
            self.col_height = max(self.col_height, r.height + settings.spacing)
            settings_y = settings.y + r.height + settings.spacing
        else:
            settings_y = settings.y + self.column_val.font.height + settings.spacing

        # get Col width
        self.col_width = self.column_val.width
        self.cols = (settings.width-self.row_width) / self.col_width

        # get item height
        self.row_height = max_font_h
        for val in (self.row_val, self.default_val, self.selected_val):
            if val.rectangle:
                r = val.rectangle.calculate(20, val.font.height)[2]
                self.row_height = max(self.row_height, r.height + settings.spacing)
        self.rows = (self.settings.height / self.row_height)-1



    def __fit_in_rect(self, rectangle, width, height, font_h):
        """
        calculates the rectangle geometry and fits it into the area
        """
        x = 0
        y = 0

        r = rectangle.calculate(width, font_h)[2]
        if r.width > width:
            r.width, width = width, width - (r.width - width)
        if r.height > height:
            r.height, height = height, height - (r.height - height)
        if r.x < 0:
            r.x, x = 0, -r.x
            width -= x
        if r.y < 0:
            r.y, y = 0, -r.y
            height -= y
        return _Geometry(x, y, width, height), r


    def clear(self):
        for o in self.objects + self.row_obj + self.col_obj:
            if o:
                o.unparent()
        if self.background:
            self.background.unparent()
        self.background = None
        self.objects  = []
        self.row_obj = []
        self.col_obj = []


    def __draw_col_titles(self, settings, x, y, cols, height):
        """
        Draws the column titles
        """
        if self.col_obj:
            return
        for o in self.col_obj:
            if o:
                o.unparent()
 
        col_size = self.col_width
        if self.column_val.rectangle:
            rect = self.column_val.rectangle.calculate(col_size, height)[2]

        for i in range( cols ):
            str = self.menu.get_column_name(i)
            self.__draw_item(str, x, y, col_size, height, self.column_val, self.col_obj)

            x += col_size


    def __draw_row_titles(self, settings, x, y, rows, width, height):
        """
        Draws the row titles
        """
        for o in self.row_obj:
            if o:
                o.unparent()
        self.row_obj = []

        for i in range( rows ):
            str = self.menu.get_row_name(i)
            self.__draw_item(str, x, y, width, height, self.row_val, self.row_obj)

            #fix this in the skin
            #self.row_obj.append(self.drawbox(tx0, ty0, width, height, r))
            
            y += height

    def __draw_item(self, txt, x, y, width, height, type, gui_obj):
        """
        Draws an item, depending on the item type, with or without rect
        """
        ig = _Geometry(0, 0, width, height)
        if type.rectangle:
            ig, r = self.__fit_in_rect(type.rectangle, width, height, type.font.height)

            gui_obj.append(self.drawbox((x+r.x),
                                        (y+r.y),
                                        r.width+r.size,
                                        height+r.size,
                                        r))

        if txt:
            string = self.drawstring(txt, type.font,
                                     self.settings, x+ig.x, y+ig.y,
                                     ig.width, ig.height,
                                     align_h=type.align,
                                     align_v ='center')
            if string:
                gui_obj.append(string)


    def update(self):
        """
        Update the grid area. This function will be called from Area to
        do the real update.
        """
        menu     = self.menu
        settings = self.settings

        if not len(menu.choices):
            if not self.objects:
                self.clear()
                t = _('This directory is empty')
                self.objects.append(self.drawstring(t, settings.font,
                                                     settings,
                                                     settings.x + settings.spacing,
                                                     settings.y + settings.spacing))
            return

        if menu.update_view:
            menu.update_view = False
            # layout change, clean everything
            self.clear()
            self.last_base_col = menu.base_col
            self.last_base_row = menu.base_row
            #Calculate new settings
            self.__calc_items_geometry()
        else:
            #Todo: only redraw new and previous selected items
            # same layout, only clean 'objects'
            for o in self.objects:
                if o: o.unparent()
            self.objects = []

        menu.cols = self.cols
        menu.rows = self.rows

        col_x = settings.x + settings.spacing + self.row_width

        col_y = settings.y + settings.spacing

        #draw the background
        r = _Geometry(0, 0, settings.width, settings.height)
        if self.row_val.rectangle:
            r = self.row_val.rectangle.calculate( settings.width, settings.height )[ 2 ]
        if not self.background:
            self.background = self.drawbox( (settings.x + settings.spacing),
                                            (settings.y + settings.spacing),
                                            (((self.cols)*self.col_width + self.row_width))+r.size,
                                            (((self.rows)*self.row_height + self.col_height))+r.size,
                                             r )
        # Draw the columns(head)
        self.__draw_col_titles(settings, col_x, col_y, self.cols, self.col_height)

        row_x = settings.x + settings.spacing
        row_y = settings.y + settings.spacing + self.col_height
        y0 = row_y
        x0 = col_x
        # draw the rows(label)
        self.__draw_row_titles(settings, row_x, row_y, self.rows, self.row_width,
                                     self.row_height)
        
        #Prepare the left and right arrows
        left_arrow_file = None
        if settings.images['leftarrow']:
            left_arrow = settings.images['leftarrow']
            left_arrow_file = left_arrow.filename
        right_arrow_file = None
        if settings.images['rightarrow']:
            right_arrow = settings.images['rightarrow']
            right_arrow_file = right_arrow.filename

        col_end = col_x+(self.col_width * self.cols)

        #Start drawing the items. Draw row after row.
        for draw_row in range(self.rows):
            try:
                x0 = col_x
                draw_col = 0
                while (x0 < col_end):
                    item = self.menu.get_item(draw_row, draw_col)
                    if item != None:
                        if menu.advanced_mode:
                            size = item[0]
                            data = item[1]
                            width = (self.col_width * size) / 100
                        else:
                            data = item
                            width = self.col_width
                        #Item layout
                        val = self.default_val
                        layout = self.menu.get_item_state(draw_row, draw_col)
                        if layout == 'selected':
                            val = self.selected_val
                        elif self.settings.types.has_key(layout):
                            val = self.settings.types[layout]
                        str = data.name
                        if x0 == col_x:
                            # draw left arrow
                            if ( ( (menu.base_col + draw_col) != 0) or menu.advanced_mode ) and \
                               left_arrow_file:
                                y_arrow = y0 + ((self.row_height-left_arrow.height)/2)
                                x_arrow = col_x
                                left_arrow_settings = (x_arrow, y_arrow, left_arrow.width, left_arrow.height)
                                image = self.drawimage(left_arrow_file, left_arrow_settings )
                                if image:
                                    self.objects.append(image)
                            
                        #check that we don't write outside the columns
                        if x0+width > col_end:
                            width = col_end-x0
                        #draw the item
                        self.__draw_item(str, x0, y0, width, self.row_height,
                                         val, self.objects)
                        x0 += width
                    else:
                        #todo check this...
                        x0 += self.col_width
                    draw_col += 1

                # draw right arrow, Draw right arrow if there are more items to come.
                item = self.menu.get_item(draw_row, draw_col)
                if item and right_arrow_file:
                    y_arrow = y0 + ((self.row_height - right_arrow.height)/2)
                    x_arrow = x0 - right_arrow.width
                    right_arrow_settings = (x_arrow, y_arrow, right_arrow.width, right_arrow.height)
                    image = self.drawimage(right_arrow_file, right_arrow_settings )
                    if image:
                        self.objects.append(image)


            except:
                log.exception('grid')
            y0 += self.row_height

        # draw Up/down arrows
        #todo
