#if 0 /*
# -----------------------------------------------------------------------
# tv.py - This is the Freevo TV plugin. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/21 18:20:44  dischi
# make tv itself and not tv.tv the plugin (using __init__.py)
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


import tv
import plugin
import menu
import os

#
# Plugin interface to integrate the tv module into Freevo
#
class PluginInterface(plugin.MainMenuPlugin):

    def items(self, parent):
        import skin

        skin = skin.get_singleton()
        menu_items = skin.settings.mainmenu.items

        icon = ""
        if menu_items['tv'].icon:
            icon = os.path.join(skin.settings.icon_dir, menu_items['tv'].icon)
        return ( menu.MenuItem(menu_items['tv'].name, icon=icon,
                               action=tv.TVMenu().main_menu, type='main',
                               image=menu_items['tv'].image, parent=parent), )



