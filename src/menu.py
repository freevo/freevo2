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
# Revision 1.33  2003/04/13 10:35:39  dischi
# cleanup of unneeded stuff in menu.py
#
# Revision 1.32  2003/04/11 10:32:59  dischi
# fixed bug for non Menu items
#
# Revision 1.31  2003/04/06 21:11:09  dischi
# o Switch to the new main1 skin
# o You can now add any object to the menuwidget, not only Menu objects
#   This is needed to add the tv guide to the stack
#
# Revision 1.30  2003/03/31 18:59:27  dischi
# bugfix for going up on the first item in the new skin
#
# Revision 1.29  2003/03/30 19:10:32  dischi
# fixed some navigating bugs
#
# Revision 1.28  2003/03/30 17:00:00  dischi
# removed debug (again)
#
# Revision 1.27  2003/03/30 16:52:51  dischi
# removed debug
#
# Revision 1.26  2003/03/30 16:50:19  dischi
# pass xml_file definition to submenus
#
# Revision 1.25  2003/03/30 14:17:06  dischi
# added force_skin_layout for the new skin
#
# Revision 1.24  2003/03/27 20:07:06  dischi
# Fix for adding/deleting the only item in the directory for the new skin
#
# Revision 1.23  2003/03/23 21:39:03  dischi
# Added better up/down handling for text menus in the new skin
#
# Revision 1.22  2003/03/18 09:37:00  dischi
# Added viewitem and infoitem to the menu to set an item which image/info
# to take (only for the new skin)
#
# Revision 1.21  2003/03/09 21:38:37  rshortt
# In MenuWidget call child.draw() now instead of child._draw().
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

from gui.GUIObject import *
from gui.AlertBox import AlertBox
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

    def __init__( self, name, action=None, arg=None, type = None, icon=None):
        
        self.name              = name
        self.action            = action
        self.action_arg        = arg
        self.type              = type
        self.icon              = icon
        self.image             = None
        self.parent            = None
        
    def setImage(self, image):
        self.type  = image[0]
        self.image = image[1]



class Menu:

    def __init__(self, heading, choices, xml_file=None, umount_all = 0,
                 reload_func = None, item_types = None, force_skin_layout = -1):

        self.heading = heading
        self.choices = choices          # List of MenuItem:s
        if len(self.choices):
            self.selected = self.choices[0]
        else:
            self.selected = None
        self.page_start = 0
        self.previous_page_start = []
        self.previous_page_start.append(0)
        self.umount_all = umount_all    # umount all ROM drives on display?

        if xml_file:
            self.skin_settings = skin.LoadSettings(xml_file)
        else:
            self.skin_settings = None

        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        self.viewitem = None

        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func = reload_func  
        self.item_types = item_types
        self.force_skin_layout = force_skin_layout
        self.display_style = skin.GetDisplayStyle(self)


    def delete_item(self, item):
        pos = self.choices.index(item)
        self.choices.remove(item)

        if self.selected == item:
            if self.choices:
                self.selected = self.choices[max(pos-1,0)]
            else:
                self.selected = None

        if len(self.choices) <= self.page_start:
            if self.page_start != 0:
                self.page_start = self.previous_page_start.pop()
            

    def items_per_page(self):
        return skin.items_per_page(('menu', self))
    

    def add_item(self, item, pos):
        try:
            sel_pos = self.choices.index(self.selected)
        except:
            sel_pos = 0
            
        self.choices.insert(pos, item)

        rows, cols = self.items_per_page()
        items_per_page = rows*cols
        if sel_pos >= self.page_start + items_per_page - 1:
            self.previous_page_start.append(self.page_start)
            self.page_start += items_per_page



#
# The MenuWidget handles a stack of Menu:s
#
class MenuWidget(GUIObject):

    def __init__(self):
        GUIObject.__init__(self)
        self.menustack = []
        self.rows = 0
        self.cols = 0
        self.visible = 1


    def show(self):
        if not self.visible:
            self.visible = 1
            self.refresh(reload=1)
            
    def hide(self):
        if self.visible:
            self.visible = 0
            skin.clear()
        
    def delete_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                return TRUE
            
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
                
            self.init_page()

    def back_one_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                menu.refresh()
                return TRUE
            
            if skin.GetDisplayStyle(menu) != menu.display_style:
                self.rebuild_page()
                
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
                    self.init_page()
                    menu.selected = self.all_items[0]
                else:
                    self.init_page()
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

        if self.cols == 1:
            if menu.page_start != 0:
                menu.page_start = menu.previous_page_start.pop()
            self.init_page()
            menu.selected = self.all_items[0]
        else:
            if menu.page_start - self.cols >= 0:
                menu.page_start -= self.cols
                self.init_page()

        if arg != 'no_refresh':
            self.refresh()

    
    def goto_next_page(self, arg=None, menuw=None):
        menu = self.menustack[-1]
        self.rows, self.cols = menu.items_per_page()
        items_per_page = self.rows*self.cols

        if self.cols == 1:
            down_items = items_per_page - 1
                
            if menu.page_start + down_items < len(menu.choices):
                menu.previous_page_start.append(menu.page_start)
                menu.page_start += down_items
                self.init_page()
                menu.selected = self.menu_items[-1]
        else:
            if menu.page_start + self.cols * self.rows < len(menu.choices):
                if self.rows == 1:
                    menu.page_start += self.cols
                else:
                    menu.page_start += self.cols * (self.rows-1)
                self.init_page()
            
        if arg != 'no_refresh':
            self.refresh()
    
    
    def pushmenu(self, menu):
        self.menustack.append(menu)
        if isinstance(menu, Menu):
            menu.page_start = 0
            self.init_page()
            menu.selected = self.all_items[0]
            self.refresh()
        else:
            menu.refresh()


    def refresh(self, reload=0):
        menu = self.menustack[-1]

        if not isinstance(menu, Menu):
            return skin.draw((menu.type, menu))

        if self.menustack[-1].umount_all == 1:
            for media in config.REMOVABLE_MEDIA:
                util.umount(media.mountdir)

        if reload:
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
            self.init_page()

        skin.draw(('menu', self))

        # Draw any child UI objects
        for child in self.children:
            child.draw()


    def make_submenu(self, menu_name, actions, item):
        items = []
        for function, title in actions:
            items += [ MenuItem(title, function, item) ]
        xml_file = None
        if hasattr(item, 'xml_file'):
            xml_file = item.xml_file

        s = Menu(menu_name, items, xml_file=xml_file)
        self.pushmenu(s)
            
        
    def eventhandler(self, event):
        menu = self.menustack[-1]

        if event == rc.MENU:
            self.goto_main_menu()
            return
        
        if event == rc.EXIT:
            self.back_one_menu()
            return

        if not isinstance(menu, Menu) and menu.eventhandler(event):
            return
        
        if event == rc.REFRESH_SCREEN:
            self.refresh()
            return
        
        if event == rc.REBUILD_SCREEN:
            self.init_page()
            self.refresh()
            return
        
        if not self.menu_items:
            if event in ( rc.ENTER, rc.SELECT,event == rc.PLAY):
                self.back_one_menu()
            return
            
        if not isinstance(menu, Menu):
            return

        if event == rc.UP:
            curr_selected = self.all_items.index(menu.selected)
            if curr_selected-self.cols < 0 and \
                   menu.selected != menu.choices[0]:
                self.goto_prev_page(arg='no_refresh')
                try:
                    if self.cols == 1:
                        curr_selected = self.rows - 1
                    elif self.rows != 1:
                        curr_selected = self.all_items.index(menu.selected)
                    else:
                        curr_selected+=self.cols
                except ValueError:
                    curr_selected += self.cols
            curr_selected = max(curr_selected-self.cols, 0)
            menu.selected = self.all_items[curr_selected]
            self.refresh()


        elif event == rc.DOWN:
            curr_selected = self.all_items.index(menu.selected)
            if curr_selected+self.cols > len(self.all_items)-1 and \
                   menu.page_start + len(self.all_items) < len(menu.choices):

                self.goto_next_page(arg='no_refresh')
                try:
                    if self.cols == 1:
                        curr_selected = 0
                    elif self.rows != 1:
                        curr_selected = self.all_items.index(menu.selected)
                    else:
                        curr_selected-=self.cols
                except ValueError:
                    curr_selected -= self.cols
            curr_selected = min(curr_selected+self.cols, len(self.all_items)-1)
            menu.selected = self.all_items[curr_selected]
            self.refresh()


        elif event == rc.LEFT or event == rc.CHUP:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            if event == rc.LEFT and self.cols > 1:
                curr_selected = self.all_items.index(menu.selected)
                if curr_selected == 0:
                    self.goto_prev_page(arg='no_refresh')
                    try:
                        curr_selected = self.all_items.index(menu.selected)
                        if self.rows == 1:
                            curr_selected = len(self.all_items)
                    except ValueError:
                        curr_selected += self.cols
                curr_selected = max(curr_selected-1, 0)
                menu.selected = self.all_items[curr_selected]
                self.refresh()

            else:
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

            if event == rc.RIGHT and self.cols > 1:
                curr_selected = self.all_items.index(menu.selected)
                if curr_selected == len(self.all_items)-1:
                    self.goto_next_page(arg='no_refresh')
                    try:
                        curr_selected = self.all_items.index(menu.selected)
                        if self.rows == 1:
                            curr_selected -= 1
                    except ValueError:
                        curr_selected -= self.cols

                curr_selected = min(curr_selected+1, len(self.all_items)-1)
                menu.selected = self.all_items[curr_selected]
                self.refresh()

            else:
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
                AlertBox(text='No action defined for this choice!').show()
            else:
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
            

        elif event == rc.DISPLAY and len(self.menustack) > 1:
            # did the menu change?
            if skin.ToggleDisplayStyle(menu):
                self.rebuild_page()
                self.refresh()
                

        elif hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
            menu.selected.eventhandler(event = event, menuw=self)

        return 0



    def rebuild_page(self):
        menu = self.menustack[-1]
       
        if not menu:
            return

        # recalc everything!
        current = menu.selected
        pos = menu.choices.index(current)

        menu.previous_page_start = []
        menu.previous_page_start.append(0)
        menu.page_start = 0

        rows, cols = menu.items_per_page()
        items_per_page = rows*cols

        while pos >= menu.page_start + items_per_page:
            self.goto_next_page(arg='no_refresh')

        menu.selected = current
        self.init_page()
        menu.display_style = skin.GetDisplayStyle(menu)
        

    def init_page(self):

        menu = self.menustack[-1]
       
        if not menu:
            return

        # Create the list of main selection items (menu_items)
        menu_items = []
        first = menu.page_start
        self.rows, self.cols = menu.items_per_page()
        
        for choice in menu.choices[first : first+(self.rows*self.cols)]:
            menu_items += [choice]
     
        self.rows, self.cols = menu.items_per_page()

        self.menu_items = menu_items
        
        if len(menu_items) == 0:
            self.all_items = menu_items + [ MenuItem('Back', self.back_one_menu) ]
        else:
            self.all_items = menu_items
            
        if not menu.selected in self.all_items:
            menu.selected = self.all_items[0]

        if not menu.choices:
            menu.selected = self.all_items[0]
