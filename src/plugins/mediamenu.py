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
# Revision 1.16  2003/08/24 05:20:15  gsbarbieri
# Empty cdroms type is now 'empty_cdrom' instead of None
#
# Revision 1.15  2003/08/24 05:03:36  gsbarbieri
# List empty roms in video|audio menus.
#
# Revision 1.14  2003/08/23 19:42:09  dischi
# make a config option HIDE_UNUSABLE_DISCS
#
# Revision 1.13  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.12  2003/08/22 19:18:08  gsbarbieri
# Now it shows empty ROMs again.
#
# Revision 1.11  2003/08/21 20:54:44  gsbarbieri
#    *ROM media just shows up when needed, ie: audiocd is not displayed in
# video main menu.
#    * ROM media is able to use variants, subtitles and more.
#    * When media is not present, ask for it and wait until media is
# identified. A better solution is to force identify media and BLOCK until
# it's done.
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
import copy

import config
import menu as menu_module
import rc
import event as em

from item import Item
from directory import DirItem

TRUE  = 1
FALSE = 0

import plugin
import plugins.rom_drives

#
# Plugin interface to integrate the MediaMenu into Freevo
#
class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin to integrate a meniamenu (video/audio/image/games) into
    the Freevo main menu
    """
    def __init__(self, type=None, force_text_view=FALSE):
        plugin.MainMenuPlugin.__init__(self)
        self.type = type
        self.force_text_view = force_text_view
        
    def items(self, parent):
        import skin

        skin = skin.get_singleton()
        menu_items = skin.settings.mainmenu.items

        icon = ""
        if menu_items[self.type].icon:
            icon = os.path.join(skin.settings.icon_dir, menu_items[self.type].icon)
        return ( menu_module.MenuItem(menu_items[self.type].name, icon=icon,
                                      action=MediaMenu().main_menu,
                                      arg=(self.type,self.force_text_view), type='main',
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
        items = copy.copy(self.normal_items)

        if config.HIDE_UNUSABLE_DISCS:
            dir_types = {
                'audio': [ 'dir', 'audiocd', 'audio', 'empty_cdrom' ],
                'video': [ 'dir', 'video', 'vcd', 'dvd', 'empty_cdrom' ],
                'image': [ 'dir', 'empty_cdrom' ],
                'games': [ 'dir',  'empty_cdrom' ],
                }
        else:
            dir_types = {}
            for type in ('audio', 'video', 'image', 'games'):
                dir_types[type] = [ 'dir', 'audiocd', 'audio', 'video',
                                    'vcd', 'dvd', None ]
                
        if self.display_type:
            plugins_list = plugin.get('mainmenu_%s' % self.display_type)
        else:
            plugins_list = []

        dir_type = dir_types.get( self.display_type, [ ] )
        
        for p in plugins_list:
            
            if isinstance( p, plugins.rom_drives.rom_items ):
                # do not show media from other menus
                for i in p.items( self ):
                    if i.type in dir_type:
                        items.append(i)
            else:
                items += p.items( self )

        return items


    def main_menu(self, arg=None, menuw=None):
        """
        display the (IMAGE|VIDEO|AUDIO|GAMES) main menu
        """
        self.display_type, force_text_view = arg
        title = 'MEDIA'
        dirs  = []

        self.menuw = menuw
        
        if self.display_type == 'video':
            title = 'MOVIE'
            dirs += config.DIR_MOVIES
        if self.display_type == 'audio':
            title = 'AUDIO'
            dirs += config.DIR_AUDIO
        if self.display_type == 'image':
            title = 'IMAGE'
            dirs += config.DIR_IMAGES
        if self.display_type == 'games':
            title = 'GAMES'
            dirs += config.DIR_GAMES

        self.normal_items = []
        # add default items
        for d in dirs:
            try:
                (t, dir) = d
                d = DirItem(dir, self, name = t,
                            display_type = self.display_type)
                self.normal_items += [ d ]
            except:
                traceback.print_exc()


        item_menu = menu_module.Menu('%s Main Menu' % title.capitalize(), self.main_menu_generate(),
                                     item_types = self.display_type, umount_all=1,
                                     reload_func = self.reload)
        item_menu._skin_force_text_view = force_text_view
        self.menuw = menuw
        menuw.pushmenu(item_menu)


    def reload(self):
        menuw = self.menuw

        menu = menuw.menustack[1]

        sel = menu.choices.index(menu.selected)
        new_choices = self.main_menu_generate()
        if not menu.selected in new_choices:
            if len(new_choices) <= sel:
                menu.selected = new_choices[-1]
            else:
                menu.selected = new_choices[sel]
        menu.choices = new_choices
        return menu


    def eventhandler(self, event = None, menuw=None):
        """
        eventhandler for the main menu. The menu must be regenerated
        when a disc in a rom drive changes
        """
        if plugin.isevent(event):
            if not menuw:
                menuw = self.menuw

            menu = menuw.menustack[1]

            sel = menu.choices.index(menu.selected)
            menuw.menustack[1].choices = self.main_menu_generate()
            if not menu.selected in menu.choices:
                if len( menu.choices ) > sel:
                    menu.selected = menu.choices[sel]
                elif menu.choices:
                    menu.selected = menu.choices[ -1 ]
                else:
                    menu.selected = None

            if menu == menuw.menustack[-1] and not rc.app():
                menuw.init_page()
                menuw.refresh()
            return TRUE

        if event in (em.PLAY_END, em.USER_END, em.STOP) and event.context != 'menu':
            menuw.show()
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
