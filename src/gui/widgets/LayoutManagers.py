# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# LayoutManagers.py - Different layout managers to manage the contents
#                     of a Container.
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
# Revision 1.16  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.15  2004/02/18 21:52:04  dischi
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

from Border    import *
from Scrollbar import *
from GUIObject import *
from Label     import *


class LayoutManager:

    def __init__(self, container):
        pass


    def layout(self):
        pass


class FlowLayout(LayoutManager):

    def __init__(self, container):
        self.container = container

    
    def get_next_child(self, j):
        num_children = len(self.container.children)
        if j < num_children - 1:
            next = self.container.children[j+1]
            if (isinstance(next, Border) \
               or isinstance(next, Scrollbar) \
               or not next.is_visible()) \
               and j < num_children - 2:
                next = self.get_next_child(j+1)
            else:
                next = None
        else:
            next = None

        return next


    def layout(self):
        next_x = self.container.h_margin
        next_y = self.container.v_margin
        line_height = 0
        row = 0
        self.table = [[],]

        num_children = len(self.container.children)
        for i in range(num_children):
            child = self.container.children[i]

            if not child.is_visible():
                continue
            if isinstance(child, Border):
                continue
            if isinstance(child, Scrollbar):
                continue

            x = next_x
            y = next_y

            next = self.get_next_child(i)

            if child.width == -1:
                child.width = self.container.width - 2 * self.container.h_margin


            if child.height == -1 and isinstance(child, Label):
                if self.container.vertical_expansion:
                    child.height = config.CONF.height - 20
                else:
                    child.height = self.container.height - \
                                   self.container.v_margin - y
                child.get_rendered_size()
        
            end = x + child.width + self.container.h_margin 

            if end > self.container.width or \
                   (len(self.table[row]) and (child.h_align == Align.LEFT or \
                                              child.h_align == Align.CENTER)):
                row += 1
                self.table.append([])
                x = self.container.h_margin
                y += line_height + self.container.v_spacing
                line_height = 0

            if child.height > line_height:
                line_height = child.height

            if y + child.height > self.container.height - self.container.v_margin:
                if self.container.vertical_expansion:
                    self.container.height = y + child.height + self.container.v_margin
                else:
                    break

            next_x = x + child.width + self.container.h_spacing
            next_y = y
            child.set_position(x, y)
            self.table[row].append(child)

        if not self.table[-1]:
            del(self.table[-1])
        self.internal_align()

        if hasattr(self.container, 'center_on_screen'):
            self.container.top = (self.container.osd.height - self.container.height) / 2




    def internal_align(self):
        if not self.table: return

        x_offset = 0
        y_offset = 0

        if len(self.table) == 1:
            if len(self.table[0]) == 1:
                # There is only one visible object inside the container.
                child = self.table[0][0]

                if child.h_align == Align.CENTER:
                    x_offset = self.container.width / 2 - \
                               (child.left + child.width / 2)
                    child.left += x_offset
                    _debug_('            moved right by %s' % x_offset, 2)

                if child.h_align == Align.LEFT:
                    pass
                if child.h_align == Align.RIGHT:
                    pass

                if child.v_align == Align.CENTER:
                    y_offset = self.container.height / 2 - (child.top + child.height / 2)
                    child.top += y_offset 

                # If there is really just one visible child inside this
                # container then we are done.
                return


        global_height = 0
        for row in self.table:
            if not len(row):
                continue

            row_width  = 0
            row_height = 0
            for child in row:
                row_width += child.width
                row_height = max(row_height, child.height)
                if len(row) - row.index(child) > 1:
                    row_width += self.container.h_spacing

            global_height += row_height + self.container.v_spacing

            if self.container.internal_h_align == Align.CENTER:
                row_center = row[0].left + row_width / 2
                x_offset = self.container.width / 2 - row_center

                for child in row:
                    child.left += x_offset 

            elif len(row) == 1 and row[0].h_align == Align.CENTER:
                x_offset = self.container.width / 2 - (row[0].left + row[0].width / 2)
                row[0].left += x_offset


        if len(self.table) > 1:
            space = self.container.height - self.container.v_spacing - global_height
            shift = space / (len(self.table) + 4)
            if self.container.internal_v_align == Align.CENTER and shift > 0:
                current = 2 * shift
                for row in self.table:
                    for child in row:
                        child.top += current
                    current += shift

        self.needed_space = global_height
        

class GridLayout(LayoutManager):

    def __init__(self):
        pass


class BorderLayout(LayoutManager):

    def __init__(self):
        pass


