#!/usr/bin/env python
#-----------------------------------------------------------------------
# Panel.py - A simple subclass of Container
#-----------------------------------------------------------------------
# $Id$
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/04/09 01:38:10  rshortt
# Initial commit of some in-progress classes.
#
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

import config
from Container      import Container
from LayoutManagers import FlowLayout

DEBUG = config.DEBUG


class Panel(Container):
    """
    """

    def __init__(self, left=0, top=0, width=0, height=0, bg_color=None, 
                 fg_color=None, border=None, bd_color=None, bd_width=None):

        Container.__init__(self, left, top, width, height, bg_color, fg_color,
                           border, bd_color, bd_width)


    def _render(self):
        if isinstance(self.parent.get_layout(), FlowLayout):
            self.set_size((self.parent.width - 2 * self.parent.h_margin),
                          self.height)

        Container._render(self)
