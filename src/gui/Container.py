#!/usr/bin/env python
#-----------------------------------------------------------------------
# Container.py - Container class for the GUI.
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
from GUIObject      import GUIObject
from LayoutManagers import FlowLayout
from LayoutManagers import GridLayout
from LayoutManagers import BorderLayout

DEBUG = config.DEBUG


class Container(GUIObject):
    """
    """

    def __init__(self, left=0, top=0, width=0, height=0, bg_color=None, 
                 fg_color=None, border=None, bd_color=None, bd_width=None):

        GUIObject.__init__(self, left, top, width, height, bg_color, fg_color)

        self.label          = None
        self.selected_label = None
        self.icon           = None
        self.layout         = None

        self.border         = border
        self.bd_color       = bd_color
        self.bd_width       = bd_width

        if self.skin_info_spacing:
            self.h_margin = self.skin_info_spacing
            self.v_margin = self.skin_info_spacing
        else:
            self.h_margin = 10
            self.v_margin = 10


    def set_layout(self, layout=FlowLayout()):
        self.layout = layout


    def _render(self, surface=None):
        pass


    def render(self, surface=None):
        if not self.layout:
            self.layout = FlowLayout()

        self._render(surface)

