#if 0 /*
# -----------------------------------------------------------------------
# base.py  -  Some basic plugins
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/08/24 06:58:18  gsbarbieri
# Partial support for "out" icons in main menu.
# The missing part is in listing_area, which have other changes to
# allow box_under_icon feature (I mailed the list asking for opinions on
# that)
#
# Revision 1.3  2003/04/24 19:56:34  dischi
# comment cleanup for 1.3.2-pre4
#
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
# ----------------------------------------------------------------------- */
#endif

from plugin import MainMenuPlugin

import config
import skin
import os

skin = skin.get_singleton()

from item import Item


TRUE  = 1
FALSE = 0


class ShutdownItem(Item):
    """
    Item for shutdown
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.shutdown_freevo, 'Shutdown Freevo' ),
                  ( self.shutdown_system, 'Shutdown system' ) ]
        if config.ENABLE_SHUTDOWN_SYS:
            items.reverse()
        return items


    def shutdown_freevo(self, arg=None, menuw=None):
        """
        shutdown freevo, don't shutdown the system
        """
        import main
        main.shutdown(menuw=menuw, arg=FALSE)

        
    def shutdown_system(self, arg=None, menuw=None):
        """
        shutdown the complete system
        """
        import main
        main.shutdown(menuw=menuw, arg=TRUE)
    


#
# the plugins defined here
#

class shutdown(MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        menu_items = skin.settings.mainmenu.items

        item = ShutdownItem()
        item.name = menu_items['shutdown'].name        
        if menu_items['shutdown'].icon:
            item.icon = os.path.join(skin.settings.icon_dir, menu_items['shutdown'].icon)
        if menu_items['shutdown'].image:
            item.image = menu_items['shutdown'].image
        if menu_items['shutdown'].outicon:
            item.outicon = os.path.join(skin.settings.icon_dir, menu_items['shutdown'].outicon)
        else:
            item.outicon = None
        item.parent = parent
        
        return [ item ]


