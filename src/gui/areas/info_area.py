# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# info_area.py - An info area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# This module include the InfoArea used in the area code for showing additional
# information on the screen. Most of the work is done in the InfoText widget in
# src/gui/widget/infotext.py.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Gustavo Sverzut Barbieri <gsbarbieri@yahoo.com.br>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'InfoArea' ]

# freevo imports
import util
import util.tv_util

# gui imports
from area import Area
from gui import InfoText

# function calls to get more info from the skin
function_calls = { 'comingup': util.tv_util.comingup }

class InfoArea(Area):
    """
    This area draws additional information on the screen. The information what
    to draw and were to put it is defined in the skin fxd file.
    """
    def __init__(self):
        Area.__init__(self, 'info')
        self.last_item = None
        self.last_content = None
        self.content = None
        self.layout_content = None
        self.list = None
        self.canvas = None


    def clear(self):
        """
        Delete the information widget
        """
        if self.canvas:
            self.canvas.unparent()
        self.canvas = None
        self.last_item = None


    def update(self):
        """
        Update the information area.
        """
        self.set_list(self.set_content())

        if self.canvas and self.infoitem == self.last_item and \
           self.content == self.last_content:
            self.canvas.rebuild()
            return

        t = InfoText((self.content.x, self.content.y),
                     (self.content.width, self.content.height),
                     self.infoitem, self.list, function_calls)

        if self.canvas:
            self.canvas.unparent()
        self.canvas = t
        self.layer.add_child(t)
        self.last_item = self.infoitem
        self.last_content = self.content


    def set_content( self ):
        """
        Set self.content and self.layout_content if they need to be set
        (return 1) or does nothing (return 0)
        """
        update=0
        if self.content and self.area_values and \
               (self.content.width != self.area_values.width or \
                self.content.height != self.area_values.height or \
                self.content.x != self.area_values.x or \
                self.content.y != self.area_values.y):
            update=1

        if self.layout_content is not self.layout.content or update:
            types = self.layout.content.types
            self.content = self.calc_geometry(self.layout.content,
                                              copy_object=True)
            # backup types, which have the previously calculated fcontent
            self.content.types = types
            self.layout_content = self.layout.content
            return 1
        return 0


    def set_list( self, force = 0 ):
        """
        Set self.list if need (return 1) or does nothing (return 0)
        """
        if force or self.infoitem is self.infoitem != self.last_item:
            key = 'default'
            if hasattr( self.infoitem, 'info_type'):
                key = self.infoitem.info_type or key

            elif hasattr( self.infoitem, 'type' ):
                key = self.infoitem.type or key

            if self.content.types.has_key(key):
                val = self.content.types[ key ]
            else:
                val = self.content.types[ 'default' ]

            if not hasattr( val, 'fcontent' ):
                self.list = None
                return 1

            self.list = val.fcontent
            return 1

        return 0
