#if 0 /*
# -----------------------------------------------------------------------
# mediamenu.py - Basic menu for all kinds of media
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/04/20 10:53:23  dischi
# moved identifymedia and mediamenu to plugins
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


import os
import traceback

import config
import menu as menu_module
import rc

from item import Item
from directory import DirItem

TRUE  = 1
FALSE = 0

rc = rc.get_singleton()

import plugin

#
# Plugin interface to integrate the MediaMenu into Freevo
#
class PluginInterface(plugin.MainMenuPlugin):
    def __init__(self, type=None):
        plugin.MainMenuPlugin.__init__(self)
        self.type = type

    def items(self, parent):
        import skin

        skin = skin.get_singleton()
        menu_items = skin.settings.mainmenu.items

        icon = ""
        if menu_items[self.type].icon:
            icon = os.path.join(skin.settings.icon_dir, menu_items[self.type].icon)
        return ( menu_module.MenuItem(menu_items[self.type].name, icon=icon,
                                      action=MediaMenu().main_menu,
                                      arg=self.type, type='main',
                                      image=menu_items[self.type].image, parent=parent), )



class MediaMenu(Item):
    """
    This is the main menu for audio, video and images. It displays the default
    directories and the ROM_DRIVES
    """
    
    def __init__(self):
        Item.__init__(self)
        self.type = 'mediamenu'

    def main_menu_generate(self):
        """
        generate the items for the main menu. This is needed when first generating
        the menu and if something changes by pressing the EJECT button
        """
        items = []
        dirs  = []
        
        if self.display_type == 'video':
            dirs += config.DIR_MOVIES
        if self.display_type == 'audio':
            dirs += config.DIR_AUDIO
        if self.display_type == 'image':
            dirs += config.DIR_IMAGES
        if self.display_type == 'games':
            dirs += config.DIR_GAMES

        if self.display_type:
            plugins = plugin.get('mainmenu_%s' % self.display_type)
        else:
            plugins = []
            
        # add default items
        for d in dirs:
            try:
                (title, dir) = d
                d = DirItem(dir, self, name = title,
                            display_type = self.display_type)
                items += [ d ]
            except:
                traceback.print_exc()

        for p in plugins:
            items += p.items(self)

        return items



    def main_menu(self, arg=None, menuw=None):
        """
        display the (IMAGE|VIDEO|AUDIO|GAMES) main menu
        """
        self.display_type = arg
        if self.display_type == 'video':
            title = 'MOVIE'
        elif self.display_type == 'audio':
            title = 'AUDIO'
        elif self.display_type == 'image':
            title = 'IMAGE'
        elif self.display_type == 'games':
            title = 'GAMES'
        else:
            title = 'MEDIA'
        item_menu = menu_module.Menu('%s MAIN MENU' % title, self.main_menu_generate(),
                                     item_types = self.display_type, umount_all=1)
        self.menuw = menuw
        menuw.pushmenu(item_menu)



    def eventhandler(self, event = None, menuw=None):
        """
        eventhandler for the main menu. The menu must be regenerated
        when a disc in a rom drive changes
        """
        if plugin.isevent(event):
            if not menuw:               # this shouldn't happen
                menuw = menu_module.get_singleton() 

            menu = menuw.menustack[1]

            sel = menu.choices.index(menu.selected)
            menuw.menustack[1].choices = self.main_menu_generate()
            if not menu.selected in menu.choices:
                menu.selected = menu.choices[sel]

            if menu == menuw.menustack[-1] and not rc.app:
                menuw.init_page()
                menuw.refresh()
            return TRUE

        if event in (rc.PLAY_END, rc.USER_END, rc.EXIT, rc.STOP):
            menuw.show()
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
