#!/usr/bin/env python
#if 0 /*
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
# Revision 1.5  2003/05/04 23:03:12  rshortt
# Fix for a crash with a row with no cols.
#
# Revision 1.4  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.3  2003/04/24 19:56:20  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.2  2003/04/22 23:55:20  rshortt
# FlowLayout now really works.  Still have some quirks to work out.
#
# Revision 1.1  2003/04/09 01:38:09  rshortt
# Initial commit of some in-progress classes.
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
#endif

import config
from Border    import *
from Scrollbar import *
from GUIObject import *
from Label     import *

DEBUG = 0


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
            if DEBUG: print 'FlowLayout: container="%s"' % self.container
            if DEBUG: print '            child="%s"' % child
            if DEBUG: print '            child is %sx%s' % (child.width,child.height)

            if not child.is_visible():
                if DEBUG: print '            skipping something invisible'
                continue
            if isinstance(child, Border):
                if DEBUG: print '            skipping border'
                continue
            if isinstance(child, Scrollbar):
                if DEBUG: print '            skipping scrollbar'
                continue

            x = next_x
            y = next_y

            next = self.get_next_child(i)

            if child.width == -1:
                if DEBUG: print '            child width not set'
                if next and next.h_align == Align.RIGHT and next.width > 0:
                    if DEBUG: print '            next align is RIGHT'
                    child.width = self.container.width - \
                                  2 * self.container.h_margin - \
                                  next.width - x
                else:
                    child.width = self.container.width - \
                                  self.container.h_margin - x
                if DEBUG: print '            child width set to %s' % child.width


            if child.height == -1 and isinstance(child, Label):
                child.height = self.container.height - \
                               self.container.v_margin - y
                if DEBUG: print '            child height set to %s' % child.height
                child.render('dummy')
                if DEBUG: print '            child now %sx%s' % (child.width,child.height)
        
            end = x + child.width + self.container.h_margin 
            if DEBUG: print '            end is %s' % end

            if end > self.container.width:
                if DEBUG: print '            new row'
                row += 1
                self.table.append([])
                x = self.container.h_margin
                y += line_height + self.container.v_spacing
                line_height = 0

            if child.height > line_height:
                line_height = child.height
                if DEBUG: print '            line_height now %s' % line_height

            if y + child.height > \
               self.container.height - self.container.v_margin:
                break

            next_x = x + child.width + self.container.h_spacing
            next_y = y
                
            if DEBUG: print '            position="%s,%s"' % (x, y)
            child.set_position(x, y)
            self.table[row].append(child)

        if not self.table[-1]: del(self.table[-1])
        self.internal_align()


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
                    if DEBUG: print '            moved right by %s' % x_offset

                if child.h_align == Align.LEFT:
                    pass
                if child.h_align == Align.RIGHT:
                    pass

                if child.v_align == Align.CENTER:
                    y_offset = self.container.height / 2 - \
                               (child.top + child.height / 2)
                    child.top += y_offset 
                    if DEBUG: print '            moved down by %s' % y_offset


        for row in self.table:
            if not len(row): continue
            row_width = 0
            for child in row:
                row_width += child.width
                if len(row) - row.index(child) > 1:
                    row_width += self.container.h_spacing

            if self.container.internal_h_align == Align.CENTER:
                row_center = row[0].left + row_width / 2
                x_offset = self.container.width / 2 - row_center

                for child in row:
                    child.left += x_offset 
                    if DEBUG: print '            moved right by %s' % x_offset


class GridLayout(LayoutManager):

    def __init__(self):
        pass


class BorderLayout(LayoutManager):

    def __init__(self):
        pass


