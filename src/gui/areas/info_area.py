# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# info_area.py - An info area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/08/22 20:06:18  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.3  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
#
# Revision 1.2  2004/07/24 12:21:31  dischi
# use new renderer and screen features
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.24  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.23  2004/06/02 19:04:35  dischi
# translation updates
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# -----------------------------------------------------------------------


import util

from area import Area
from gui import InfoText

# function calls to get more info from the skin
function_calls = { 'comingup': util.comingup }

class Info_Area(Area):
    """
    this call defines the view area
    """

    def __init__(self):
        Area.__init__(self, 'info')
        self.last_item = None
        self.content = None
        self.layout_content = None
        self.list = None
        self.canvas = None


    def clear(self):
        """
        delete the shown image from screen
        """
        if self.canvas:
            self.canvas.unparent()
        self.canvas = None
        self.last_item = None

        
    def update(self):
        # init some stuff
        self.set_list(self.set_content())
        t = InfoText((self.content.x, self.content.y),
                     (self.content.width, self.content.height),
                     self.infoitem, self.list, function_calls)
        
        if self.canvas:
            self.canvas.unparent()
        self.canvas = t
        self.screen.layer[2].add_child(t)
        self.last_item = self.infoitem


    def set_content( self ):
        """
        set self.content and self.layout_content if they need to be set (return 1)
        or does nothing (return 0)
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
            self.content = self.calc_geometry( self.layout.content, copy_object=True )
            # backup types, which have the previously calculated fcontent
            self.content.types = types
            self.layout_content = self.layout.content
            return 1
        return 0


    def set_list( self, force = 0 ):
        """
        set self.list if need (return 1) or does nothing (return 0)
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
