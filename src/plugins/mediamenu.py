# -*- coding: iso-8859-1 -*-
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
# Revision 1.42  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.41  2004/11/01 20:15:40  dischi
# fix debug
#
# Revision 1.40  2004/08/14 08:40:08  dischi
# bugfix for new menu interface
#
# Revision 1.39  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.38  2004/07/25 19:47:39  dischi
# use application and not rc.app
#
# Revision 1.37  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.36  2004/03/18 15:38:18  dischi
# Automouter patch to check for hosts in mediamenu from Soenke Schwardt.
# See doc of VIDEO_ITEMS for details
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


import os
import traceback
import copy

import config
import menu

import directory
import eventhandler

import plugin
import plugins.rom_drives

from event import *
from item import Item

import logging
log = logging.getLogger()

class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin to integrate a mediamenu (video/audio/image/games) into
    the Freevo main menu. This plugin is auto-loaded when you activate
    the 'video', 'audio', 'image' or 'games' plugin.
    """
    def __init__(self, type=None, force_text_view=FALSE):
        plugin.MainMenuPlugin.__init__(self)
        self.type = type
        self.force_text_view = force_text_view or config.SKIN_MEDIAMENU_FORCE_TEXTVIEW


    def items(self, parent):
        return [ menu.MenuItem('', action=MediaMenu().main_menu,
                               arg=(self.type,self.force_text_view), type='main',
                               parent=parent, skin_type = self.type) ]



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
                'games': [ 'dir', 'empty_cdrom' ],
                }
        else:
            dir_types = {}
            for type in ('audio', 'video', 'image', 'games'):
                dir_types[type] = [ 'dir', 'audiocd', 'audio', 'video',
                                    'vcd', 'dvd', 'empty_cdrom' ]
                
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
        title = _('Media')

        self.menuw = menuw
        
        if self.display_type == 'video':
            title = _('Movie')
        if self.display_type == 'audio':
            title = _('Audio')
        if self.display_type == 'image':
            title = _('Image')
        if self.display_type == 'games':
            title = _('Games')

        menutitle = _('%s Main Menu') % title
        
        if self.display_type:
            items = getattr(config, '%s_ITEMS' % self.display_type.upper())
        else:
            items = []

        self.normal_items = []

        # add default items
        for item in items:
            try:
                add_args = None
                if isstring(item):
                    title, filename = u'', item
                else:
                    (title, filename) = item[:2]
                    if len(item) > 2:
                        add_args = item[2:]

                reachable = 1
                pos = filename.find(':/')
                if pos > 0:
                    if filename.find(':/') < filename.find('/'):                        
                        hostname = filename[0:pos]
                        filename = filename[pos+1:]
                        try:
                            if os.system( config.HOST_ALIVE_CHECK % hostname ) != 0:
                                reachable = 0
                        except:
                            log.error('Error parsing %s' % filename)
                            traceback.print_exc()
                       
                if reachable:
                    if vfs.isdir(filename):
                        item = directory.DirItem(String(filename), self,
                                                 display_type=self.display_type,
                                                 add_args=add_args)
                        if title:
                            item.name = title
                        self.normal_items.append(item)
                    else:
                        if not vfs.isfile(filename):
                            filename = filename[len(os.getcwd()):]
                            if filename[0] == '/':
                                filename = filename[1:]
                            filename = vfs.join(config.SHARE_DIR, filename)
                        # normal file
                        for p in plugin.mimetype(self.display_type):
                            items = p.get(self, [ String(filename) ])
                            if title:
                                for i in items:
                                    i.name = title
                            self.normal_items += items
                            
            except:
                log.error('Error parsing %s' % item)
                traceback.print_exc()


        items = self.main_menu_generate()

        # autoselect one item
        if len(items) == 1:
            items[0](menuw=menuw)
            return
        
        item_menu = menu.Menu(menutitle, items,
                              item_types = '%s main menu' % self.display_type,
                              umount_all=1, reload_func = self.reload)
        item_menu.skin_force_text_view = force_text_view
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

            if menu == menuw.menustack[-1] and eventhandler.is_menu():
                menuw.refresh()
            # others may need this event, too
            return False

        if event in (PLAY_END, USER_END, STOP) and event.context != 'menu':
            menuw.show()
            return True

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
