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

# python imports
import time

# freevo imports
import util
import util.tv_util

# gui imports
from area import Area
from gui import InfoText

def current_time():
    if time.strftime('%P') =='':
        format ='%a %H:%M'
    else:
        format ='%a %I:%M %P'
    return time.strftime(format)

# function calls to get more info from the skin
function_calls = { 'comingup': util.tv_util.comingup,
                   'time': current_time }

class InfoArea(Area):
    """
    This area draws additional information on the screen. The information what
    to draw and were to put it is defined in the skin fxd file.
    """
    def __init__(self):
        Area.__init__(self, 'info')
        self.last_item = None
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
        if not self.settings.changed and self.infoitem == self.last_item:
            self.canvas.rebuild()
            return
        
        # get key of the items based on item attributes
        key = 'default'
        if hasattr( self.infoitem, 'info_type'):
            key = self.infoitem.info_type or key
        elif hasattr( self.infoitem, 'type' ):
            key = self.infoitem.type or key

        # get the values for that item
        if self.settings.types.has_key(key):
            val = self.settings.types[ key ]
        else:
            val = self.settings.types[ 'default' ]

        if self.canvas:
            self.canvas.unparent()

        self.canvas = InfoText((self.settings.x, self.settings.y),
                               (self.settings.width, self.settings.height),
                               self.infoitem, val.fcontent, function_calls)
        self.layer.add_child(self.canvas)
        self.last_item = self.infoitem
