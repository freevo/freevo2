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
# Revision 1.51  2003/06/29 19:52:58  dischi
# small fix
#
# Revision 1.50  2003/06/07 11:30:27  dischi
# support for MENU_CALL_ITEM_ACTION
#
# Revision 1.49  2003/06/07 04:36:18  outlyer
# Prevent a crash.
#
# Revision 1.48  2003/05/30 00:53:19  rshortt
# Various event bugfixes.
#
# Revision 1.47  2003/05/27 17:53:33  dischi
# Added new event handler module
#
# Revision 1.46  2003/04/28 18:07:45  dischi
# restore the correct item
#
# Revision 1.45  2003/04/26 15:08:51  dischi
# o better mount/umount, also for directories who are no rom drive.
# o added list_usb_devices to util
#
# Revision 1.44  2003/04/24 19:55:48  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.43  2003/04/24 19:13:27  dischi
# bugfix
#
# Revision 1.42  2003/04/21 12:59:35  dischi
# better plugin event handling
#
# Revision 1.41  2003/04/20 12:43:32  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.40  2003/04/20 11:44:45  dischi
# add item plugins
#
# Revision 1.39  2003/04/20 10:55:40  dischi
# mixer is now a plugin, too
#
# Revision 1.38  2003/04/19 21:28:39  dischi
# identifymedia.py is now a plugin and handles everything related to
# rom drives (init, autostarter, items in menus)
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

import plugin

from item import Item

# Various utilities
import util

# The skin class
import skin

import event as em

from gui.GUIObject import *
from gui.AlertBox import AlertBox
TRUE  = 1
FALSE = 0

skin = skin.get_singleton() # Crate the skin object.

# Module variable that contains an initialized MenuWidget() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MenuWidget()
        
    return _singleton




class MenuItem(Item):
    """
    Default item for the main menu actions
    """
    def __init__( self, name, action=None, arg=None, type=None, image=None,
                  icon=None, parent=None):
        Item.__init__(self, parent)
        self.name     = name
        self.icon     = icon
        self.function = action
        self.arg      = arg
        self.type     = type
        self.image    = image
        
    def setImage(self, image):
        self.type  = image[0]
        self.image = image[1]

    def actions(self):
        return [ ( self.select, '' ) ]

    def select(self, arg=None, menuw=None):
        if self.function:
            self.function(arg=self.arg, menuw=menuw)



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
        self.eventhandler_plugins = None
        self.event_context = 'menu'
        
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
            else:
                self.init_page()

            if arg == 'reload':
                self.refresh(reload=1)
            else:
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
            util.umount_all()
                    
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
            items += [ MenuItem(title, function) ]
        xml_file = None
        if hasattr(item, 'xml_file'):
            xml_file = item.xml_file

        s = Menu(menu_name, items, xml_file=xml_file)
        self.pushmenu(s)
            
        
    def eventhandler(self, event):
        menu = self.menustack[-1]

        if event == em.MENU_GOTO_MAINMENU:
            self.goto_main_menu()
            return
        
        if event == em.MENU_BACK_ONE_MENU:
            self.back_one_menu()
            return

        if not isinstance(menu, Menu) and menu.eventhandler(event):
            return

        if event == 'MENU_REFRESH':
            self.refresh()
            return
        
        if event == 'MENU_REBUILD':
            self.init_page()
            self.refresh()
            return
        
        if not self.menu_items:
            if event in ( em.MENU_SELECT, em.MENU_SUBMENU, em.MENU_PLAY_ITEM):
                self.back_one_menu()
            return
            
        if not isinstance(menu, Menu):
            if self.eventhandler_plugins == None:
                self.eventhandler_plugins = plugin.get('daemon_eventhandler')

            for p in self.eventhandler_plugins:
                if p.eventhandler(event=event, menuw=self):
                    return

            print 'no eventhandler for event %s' % event
            return

        if event == em.MENU_UP:
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
            return


        elif event == em.MENU_DOWN:
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
            return


        elif event == em.MENU_LEFT or event == em.MENU_PAGEUP:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            if event == em.MENU_LEFT and self.cols > 1:
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
            return

        elif event == em.MENU_RIGHT or event == em.MENU_PAGEDOWN:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return

            if menu.selected == menu.choices[-1]:
                return
            
            if event == em.MENU_RIGHT and self.cols > 1:
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
            return


        elif event == em.MENU_PLAY_ITEM and hasattr(menu.selected, 'play'):
            menu.selected.play(menuw=self)
            
        elif event == em.MENU_SELECT or event == em.MENU_PLAY_ITEM:
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
                action( menuw=self )
            return


        elif event == em.MENU_SUBMENU:
            actions = menu.selected.actions()

            if hasattr(menu.selected, 'display_type'):
                if menu.selected.display_type:
                    actions_plugins = '_%s' % menu.selected.display_type
                else:
                    actions_plugins = ''
            else:
                actions_plugins = '_%s' % menu.selected.type
            
            for p in plugin.get('item%s' % actions_plugins):
                for a in p.actions(menu.selected):
                    actions.append(a[:2])

            if actions and len(actions) > 1:
                self.make_submenu(menu.selected.name, actions, menu.selected)
            return
            

        elif event == em.MENU_CALL_ITEM_ACTION:
            print 'calling action %s', event.arg
            if hasattr(menu.selected, 'display_type'):
                if menu.selected.display_type:
                    actions_plugins = '_%s' % menu.selected.display_type
                else:
                    actions_plugins = ''
            else:
                actions_plugins = '_%s' % menu.selected.type
            
            for p in plugin.get('item%s' % actions_plugins):
                for a in p.actions(menu.selected):
                    if len(a) > 2 and a[2] == event.arg:
                        a[0](arg=None, menuw=self)
                        return
            print 'action %s not found' % event.arg

                    
        elif event == em.MENU_CHANGE_STYLE and len(self.menustack) > 1:
            # did the menu change?
            if skin.ToggleDisplayStyle(menu):
                self.rebuild_page()
                self.refresh()
                return
                

        elif hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
            if menu.selected.eventhandler(event = event, menuw=self):
                return
            
        if self.eventhandler_plugins == None:
            self.eventhandler_plugins = plugin.get('daemon_eventhandler')

        for p in self.eventhandler_plugins:
            if p.eventhandler(event=event, menuw=self):
                return

        print 'no eventhandler for event %s' % str(event)
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
