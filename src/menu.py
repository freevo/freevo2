#if 0 /*
# -----------------------------------------------------------------------
# menu.py - freevo menu handling system
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/01/07 20:43:38  dischi
# Small fixes, the actions get the item as arg
#
# Revision 1.6  2002/12/11 16:08:48  dischi
# no ENTER selects the item menu
#
# Revision 1.5  2002/12/07 15:23:46  dischi
# small fix for non-item menus
#
# Revision 1.4  2002/12/07 13:30:21  dischi
# Add plugin support
#
# Revision 1.3  2002/12/03 19:15:13  dischi
# Give all menu callback functions the parameter arg
#
# Revision 1.2  2002/11/25 02:17:54  krister
# Minor bugfixes. Synced to changes made in the main tree.
#
# Revision 1.41  2002/11/24 06:34:04  krister
# Added an option to reload a parent menu when returning from a submenu, useful for setting options etc.
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

import sys, os, time
import traceback

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The skin class
import skin

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

TRUE  = 1
FALSE = 0

rc   = rc.get_singleton()   # Create the remote control object
skin = skin.get_singleton() # Crate the skin object.

# Module variable that contains an initialized MenuWidget() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MenuWidget()
        
    return _singleton




class MenuItem:

    def __init__( self, name, action=None, arg=None, eventhandler = None,
                  eventhandler_args = None, type = None, icon=None, scale=1, popup=0 ):
        
        self.name              = name
        self.action            = action
        self.action_arg        = arg
        self.eventhandler      = eventhandler
        self.eventhandler_args = eventhandler_args
        self.type              = type
        self.icon              = icon
        self.scale             = scale
        self.popup             = popup
        self.image             = None

    def setImage(self, image):
        self.type  = image[0]
        self.image = image[1]
    
    # XXX do we need this function?
    def select(self):
        self.action(self.action_arg)

    def eventhandler(self):
        self.eventhandler(self.eventhandler_args)



class Menu:

    def __init__(self, heading, choices, xml_file=None, packrows=1, umount_all = 0,
                 reload_func = None):
        # XXX Add a list of eventhandlers?
        self.heading = heading
        self.choices = choices          # List of MenuItem:s
        self.page_start = 0
        self.previous_page_start = []
        self.previous_page_start.append(0)
        self.packrows = packrows
        self.umount_all = umount_all    # umount all ROM drives on display?
        if xml_file:
            self.skin_settings = skin.LoadSettings(xml_file)
        else:
            self.skin_settings = None
        self.reload_func = reload_func  # Called when a child menu returns


#
# The MenuWidget handles a stack of Menu:s
#
class MenuWidget:

    def __init__(self):
        self.menustack = []
        self.prev_page = MenuItem('Prev Page', self.goto_prev_page)
        self.next_page = MenuItem('Next Page', self.goto_next_page)
        self.back_menu = MenuItem('Back', self.back_one_menu)
        self.main_menu = MenuItem('Main', self.goto_main_menu)


    def delete_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if menu.reload_func:
                self.menustack[-1] = menu.reload_func()
                
            self.init_page()

    def back_one_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if menu.reload_func:
                menu = self.menustack[-1] = menu.reload_func()
                self.init_page()
                menu.selected = self.all_items[0]
            else:
                self.init_page()

            self.refresh()

    def goto_main_menu(self, arg=None, menuw=None):
        self.menustack = [self.menustack[0]]
        menu = self.menustack[0]
        self.init_page()
        self.refresh()

    
    def goto_prev_page(self, arg=None, menuw=None):
        menu = self.menustack[-1]
        if menu.page_start != 0:
            menu.page_start = menu.previous_page_start.pop()
        self.init_page()
        menu.selected = self.all_items[0]
        self.refresh()

    
    def goto_next_page(self, arg=None, menuw=None):
        menu = self.menustack[-1]
        items_per_page = skin.ItemsPerMenuPage(menu)
        if menu.page_start +  items_per_page < len(menu.choices):
            menu.previous_page_start.append(menu.page_start)
            menu.page_start += items_per_page
        self.init_page()
        menu.selected = self.menu_items[-1]
        self.refresh()
    
    
    def pushmenu(self, menu):
        menu.page_start = 0
        self.menustack.append(menu)
        self.init_page()
        menu.selected = self.all_items[0]
        self.refresh()


    def refresh(self):
        if self.menustack[-1].umount_all == 1:
            for media in config.REMOVABLE_MEDIA:
                util.umount(media.mountdir)
    
        skin.DrawMenu(self)


    def make_submenu(self, menu_name, actions, item):
        items = []
        for function, title in actions:
            items += [ MenuItem(title, function, item) ]
        s = Menu(menu_name, items)
        self.pushmenu(s)
            
        
    def eventhandler(self, event):
        menu = self.menustack[-1]
        if event == rc.UP:
            curr_selected = self.all_items.index(menu.selected)
            curr_selected = max(curr_selected-1, 0)
            menu.selected = self.all_items[curr_selected]
            self.refresh()
        elif event == rc.DOWN:
            curr_selected = self.all_items.index(menu.selected)
            curr_selected = min(curr_selected+1, len(self.all_items)-1)
            menu.selected = self.all_items[curr_selected]
            self.refresh()
        elif event == rc.LEFT or event == rc.CHUP:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            curr_selected = self.all_items.index(menu.selected)

            # Move to the previous page if the current position is at the
            # top of the list, otherwise move to the top of the list.
            if curr_selected == 0:
                self.goto_prev_page()
            else:
                curr_selected = 0
                menu.selected = self.all_items[curr_selected]
                self.refresh()
        elif event == rc.RIGHT or event == rc.CHDOWN:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            curr_selected = self.all_items.index(menu.selected)
            bottom_index = self.menu_items.index(self.menu_items[-1])
            
            # Move to the next page if the current position is at the
            # bottom of the list, otherwise move to the bottom of the list.
            if curr_selected >= bottom_index:
                self.goto_next_page()
            else:
                curr_selected = bottom_index
                menu.selected = self.all_items[curr_selected]
                self.refresh()
        elif event == rc.MENU:
            self.goto_main_menu()
        elif event == rc.EXIT:
            self.back_one_menu()

        elif event == rc.SELECT or event == rc.PLAY:
            try:
                action = menu.selected.action
            except AttributeError:
                if menu.selected.actions():
                    action = menu.selected.actions()[0][0]
                else:
                    action = None
                    
            if action == None:
                print 'No action.. '
                self.refresh()
            else:
                print 'Calling action "%s"' % str(action)
                if hasattr(menu.selected, 'action_arg'):
                    action( arg=menu.selected.action_arg, menuw=self )
                else:
                    action( menuw=self )

        elif event == rc.ENTER:
            try:
                actions = menu.selected.actions()
                if config.FREEVO_PLUGINS.has_key(menu.selected.type):
                    for a in config.FREEVO_PLUGINS[menu.selected.type]:
                        try:
                            actions += a(menu.selected)
                        except:
                            traceback.print_exc()
                if len(actions) > 1:
                    self.make_submenu(menu.selected.name, actions, menu.selected)
            except:
                pass
            
        elif event == rc.REFRESH_SCREEN:
            self.refresh()
        else:
            action = menu.selected.eventhandler
            if action:
                print 'Calling action "%s"' % str(action)
                if hasattr(menu.selected, 'eventhandler_args'):
                    action(event = event, arg=menu.selected.eventhandler_args,
                           menuw=self)
                else:
                    action(event = event, menuw=self)
        return 0


    def init_page(self):

        menu = self.menustack[-1]
       
        if not menu:
            return

        # Create the list of main selection items (menu_items)
        menu_items = []
        first = menu.page_start
        for choice in menu.choices[first : first+skin.ItemsPerMenuPage(menu)]:
            menu_items += [choice]
     
        # Create the list of navigation items (nav_items)
        nav_items = []

        if skin.SubMenuVisible(menu):
            items_per_page = skin.ItemsPerMenuPage(menu)
            if menu.page_start + items_per_page < len(menu.choices):
                nav_items += [self.next_page]
            if menu.page_start != 0:
                nav_items += [self.prev_page]
            if len(self.menustack) >= 3:
                nav_items += [self.back_menu]
            if len(self.menustack) >= 2:
                nav_items += [self.main_menu]

        elif len(menu_items) == 0:
            nav_items += [self.back_menu]

        self.menu_items = menu_items
        self.nav_items = nav_items

        self.all_items = self.menu_items + self.nav_items
