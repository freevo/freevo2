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
# Revision 1.1  2003/04/09 01:38:09  rshortt
# Initial commit of some in-progress classes.
#
#
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

DEBUG = config.DEBUG


class LayoutManager:

    def __init__(self, container):
        pass


    def layout(self):
        pass


class FlowLayout(LayoutManager):

    def __init__(self, container):
        self.container = container

    
    def layout(self):
        next_x = self.container.h_margin
        next_y = self.container.v_margin
        line_height = 0
        
        for child in self.container.childeren:
            if isinstance(child, Border):
                continue

            x = next_x
            y = next_y
        
            if child.height > line_height:
                line_height = child.height

            end = x + child.width + self.container.h_margin 

            if end > self.container.width:
                x = self.container.h_margin
                y += line_height + self.container.v_margin
                line_height = 0

            if y + child.height > \
               self.container.height - self.container.v_margin:
                break

            next_x = x + child.width + self.container.h_margin
                
            child.set_position(x, y)


class GridLayout(LayoutManager):

    def __init__(self):
        pass


class BorderLayout(LayoutManaget):

    def __init__(self):
        pass


