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
# Revision 1.9  2003/06/26 01:41:16  rshortt
# Fixed a bug wit drawstringframed hard.  Its return coords were always 0's
# which made it impossible to judge the size.
#
# Revision 1.8  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.7  2003/05/21 00:04:25  rshortt
# General improvements to layout and drawing.
#
# Revision 1.6  2003/05/16 02:11:50  rshortt
# Fixed a nasty label alingment-bouncing bug.  There are lots of leftover
# comments and DEBUG statements but I will continue to make use of them
# for improvements.
#
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

DEBUG = 1


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
                # if next and next.h_align == Align.RIGHT and next.width > 0:
                #     if DEBUG: print '            next align is RIGHT'
                #     child.width = self.container.width - \
                #                   2 * self.container.h_margin - \
                #                   next.width - x
                # else:
                #     child.width = self.container.width - \
                #                   self.container.h_margin - x
                child.width = self.container.width - \
                              2 * self.container.h_margin
                if DEBUG: print '            child width set to %s' % child.width


            if child.height == -1 and isinstance(child, Label):
                if self.container.vertical_expansion:
                    child.height = config.CONF.height - 20
                else:
                    child.height = self.container.height - \
                                   self.container.v_margin - y
                if DEBUG: print '            child was %sx%s' % (child.width,child.height)
                child.get_rendered_size()
                if DEBUG: print '            child now %sx%s' % (child.width,child.height)
        
            end = x + child.width + self.container.h_margin 
            if DEBUG: print '            end is %s' % end

            if DEBUG: print '            child row len is %s' % len(self.table[row])
            if DEBUG: print '            child h_align is %s' % child.h_align

            if end > self.container.width or \
               (len(self.table[row]) and (child.h_align == Align.LEFT or \
                                          child.h_align == Align.CENTER)):
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
                if self.container.vertical_expansion:
                    self.container.height = y + child.height + \
                                            self.container.v_margin
                    if DEBUG: 
                        print 'LAYOUT:  fit me in! (%s) - %s' % \
                                     (self.container.height, self)
                else:
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

                # If there is really just one visible child inside this
                # container then we are done.
                return


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

            elif len(row) == 1 and row[0].h_align == Align.CENTER:
                x_offset = self.container.width / 2 - \
                           (row[0].left + row[0].width / 2)
                row[0].left += x_offset
                if DEBUG: print '            moved right by %s' % x_offset


class GridLayout(LayoutManager):

    def __init__(self):
        pass


class BorderLayout(LayoutManager):

    def __init__(self):
        pass


