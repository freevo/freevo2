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
# Revision 1.94  2004/06/02 21:38:02  dischi
# fix crash
#
# Revision 1.93  2004/05/09 09:58:43  dischi
# make it possible to force a page rebuild
#
# Revision 1.92  2004/03/19 21:03:39  dischi
# fix tvguide context bug
#
# Revision 1.91  2004/03/14 19:43:27  dischi
# make it possible to create a submenu inside a plugin
#
# Revision 1.90  2004/02/25 17:44:30  dischi
# add special event mapping for tvmenu
#
# Revision 1.87  2004/02/14 19:29:07  dischi
# send osd message when not using a submenu
#
# Revision 1.86  2004/02/14 13:02:34  dischi
# o remove unneeded functions
# o add function to delete the submenu or do nothing (avoid duplicate code)
# o use new skin functions and do not call get_singleton()
#
# Revision 1.85  2004/02/12 16:27:06  dischi
# fix watermark problem once and for all
#
# Revision 1.84  2004/02/06 20:42:55  dischi
# fix LEFT and RIGHT for tv guide
#
# Revision 1.83  2004/02/05 19:56:40  dischi
# make it possible to change back to the old navigation style
#
# Revision 1.82  2004/02/04 22:32:42  gsbarbieri
# Changed LEFT/RIGHT behaviour.
# Now in single column mode it behaves like BACK_ONE_MENU/SELECT and in
# multi-column mode (2d menus) it goes one item LEFT/RIGHT (as before).
#
# This was asked in freevo-devel because it improve usability and it really
# does, since you just have to use arrows (UP/DOWN,LEFT/RIGHT) to navigate.
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


import copy

import config
import plugin
import util
import skin
import rc

from event import *
from item import Item
from gui import GUIObject, AlertBox


class MenuItem(Item):
    """
    Default item for the menu. It includes one action
    """
    def __init__( self, name, action=None, arg=None, type=None, image=None,
                  icon=None, parent=None, skin_type=None):
        Item.__init__(self, parent, skin_type = skin_type)
        if name:
            self.name  = Unicode(name)
        if icon:
            self.icon  = icon
        if image:
            self.image = image

        self.function = action
        self.arg      = arg
        self.type     = type

            
    def actions(self):
        """
        return the default action
        """
        return [ ( self.select, self.name ) ]


    def select(self, arg=None, menuw=None):
        """
        call the default acion
        """
        if self.function:
            self.function(arg=self.arg, menuw=menuw)



class Menu:
    """
    a Menu with Items for the MenuWidget
    """
    def __init__(self, heading, choices, fxd_file=None, umount_all = 0,
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
        self.skin_settings = None
        if fxd_file:
            self.skin_settings = skin.load(fxd_file)

        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        self.viewitem = None

        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func       = reload_func  
        self.item_types        = item_types
        self.force_skin_layout = force_skin_layout
        self.display_style     = skin.get_display_style(self)

        # How many menus to go back when 'BACK_ONE_MENU' is called
        self.back_one_menu = 1
        

    def items_per_page(self):
        """
        return the number of items per page for this skin
        """
        return skin.items_per_page(('menu', self))
    



class MenuWidget(GUIObject):
    """
    The MenuWidget handles a stack of Menus
    """
    def __init__(self):
        GUIObject.__init__(self)
        self.menustack = []
        self.rows = 0
        self.cols = 0
        self.visible = 1
        self.eventhandler_plugins = None
        self.event_context  = 'menu'
        self.show_callbacks = []
        self.force_page_rebuild = False
        
        
    def get_event_context(self):
        """
        return the event context
        """
        if self.menustack and hasattr(self.menustack[-1], 'event_context'):
            return self.menustack[-1].event_context
        return self.event_context


    def show(self):
        if not self.visible:
            self.visible = 1
            self.refresh(reload=1)
            for callback in copy.copy(self.show_callbacks):
                callback()
        rc.app(None)

                
    def hide(self, clear=True):
        if self.visible:
            self.visible = 0
            if clear:
                skin.clear(osd_update=clear)

        
    def delete_menu(self, arg=None, menuw=None, allow_reload=True):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                return True
            
            if menu.reload_func and allow_reload:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
                
            self.init_page()


    def delete_submenu(self, refresh=True, reload=False, osd_message=''):
        """
        Delete the last menu if it is a submenu. Also refresh or reload the
        new menu if the attributes are set to True. If osd_message is set,
        this message will be send if the current menu is no submenu
        """
        if len(self.menustack) > 1 and hasattr(self.menustack[-1], 'is_submenu') and \
               self.menustack[-1].is_submenu:
            if refresh and reload:
                self.back_one_menu(arg='reload')
            elif refresh:
                self.back_one_menu()
            else:
                self.delete_menu()
        elif len(self.menustack) > 1 and osd_message:
            rc.post_event(Event(OSD_MESSAGE, arg=osd_message))

            
    def back_one_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            try:
                count = -self.menustack[-1].back_one_menu
            except:
                count = -1

            self.menustack = self.menustack[:count]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                menu.refresh()
                return True
            
            if skin.get_display_style(menu) != menu.display_style:
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
            # Do not draw if there are any children
            if self.children:
                return False
            
            return skin.draw(menu.type, menu)

        if self.menustack[-1].umount_all == 1:
            util.umount_all()
                    
        if reload:
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload
            if self.force_page_rebuild:
                self.force_page_rebuild = False
                self.rebuild_page()
            self.init_page()

        skin.draw('menu', self, self.menustack[-1])


    def make_submenu(self, menu_name, actions, item):
        items = []
        for a in actions:
            if isinstance(a, Item):
                items.append(a)
            else:
                items.append(MenuItem(a[1], a[0]))
        fxd_file = None

        if item.skin_fxd:
            fxd_file = item.skin_fxd

        for i in items:
            if not hasattr(item, 'is_mainmenu_item'):
                i.image = item.image
            if hasattr(item, 'display_type'):
                i.display_type = item.display_type
            elif hasattr(item, 'type'):
                i.display_type = item.type
                
        s = Menu(menu_name, items, fxd_file=fxd_file)
        s.is_submenu = True
        self.pushmenu(s)
            
        
    def eventhandler(self, event):
        menu = self.menustack[-1]

        if self.cols == 1 and isinstance(menu, Menu):
            if config.MENU_ARROW_NAVIGATION:
                if event == MENU_LEFT:
                    event = MENU_BACK_ONE_MENU
                elif event == MENU_RIGHT:
                    event = MENU_SELECT
            
            else:
                if event == MENU_LEFT:
                    event = MENU_PAGEUP
                elif event == MENU_RIGHT:
                    event = MENU_PAGEDOWN
            
        if self.eventhandler_plugins == None:
            self.eventhandler_plugins = plugin.get('daemon_eventhandler')

        if event == MENU_GOTO_MAINMENU:
            self.goto_main_menu()
            return
        
        if event == MENU_BACK_ONE_MENU:
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
            if event in ( MENU_SELECT, MENU_SUBMENU, MENU_PLAY_ITEM):
                self.back_one_menu()
                return
            menu = self.menustack[-2]
            if hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
                if menu.selected.eventhandler(event = event, menuw=self):
                    return
            for p in self.eventhandler_plugins:
                if p.eventhandler(event=event, menuw=self):
                    return
            return
            
        if not isinstance(menu, Menu):
            if self.eventhandler_plugins == None:
                self.eventhandler_plugins = plugin.get('daemon_eventhandler')

            for p in self.eventhandler_plugins:
                if p.eventhandler(event=event, menuw=self):
                    return

            _debug_('no eventhandler for event %s' % event, 2)
            return

        if event == MENU_UP:
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


        elif event == MENU_DOWN:
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


        elif event == MENU_PAGEUP:
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
            return


        elif event == MENU_PAGEDOWN:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return

            if menu.selected == menu.choices[-1]:
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
            return


        elif event == MENU_LEFT:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return

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
            return
        

        elif event == MENU_RIGHT:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return

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
            return


        elif event == MENU_PLAY_ITEM and hasattr(menu.selected, 'play'):
            menu.selected.play(menuw=self)
            
        elif event == MENU_SELECT or event == MENU_PLAY_ITEM:
            action = None
            arg    = None

            try:
                action = menu.selected.action
            except AttributeError:
                action = menu.selected.actions()
                if action:
                    action = action[0]
                    if isinstance(action, MenuItem):
                        action = action.function
                        arg    = action.arg
                    else:
                        action = action[0]
            if not action:
                print 'No action.. '
                AlertBox(text=_('No action defined for this choice!')).show()
            else:
                action( arg=arg, menuw=self )
            return


        elif event == MENU_SUBMENU:
            if hasattr(menu, 'is_submenu'):
                return

            actions = menu.selected.actions()
            force   = False
            if not actions:
                actions = []
                force   = True

            plugins = plugin.get('item') + plugin.get('item_%s' % menu.selected.type)

            if hasattr(menu.selected, 'display_type'):
                plugins += plugin.get('item_%s' % menu.selected.display_type)

            plugins.sort(lambda l, o: cmp(l._level, o._level))
            
            for p in plugins:
                for a in p.actions(menu.selected):
                    if isinstance(a, MenuItem):
                        actions.append(a)
                    else:
                        actions.append(a[:2])
                        if len(a) == 3 and a[2] == 'MENU_SUBMENU':
                            a[0](menuw=self)
                            return
                        
            if actions and (len(actions) > 1 or force):
                self.make_submenu(menu.selected.name, actions, menu.selected)
            return
            

        elif event == MENU_CALL_ITEM_ACTION:
            _debug_('calling action %s' % event.arg)

            for a in menu.selected.actions():
                if not isinstance(a, Item) and len(a) > 2 and a[2] == event.arg:
                    a[0](arg=None, menuw=self)
                    return
                
            plugins = plugin.get('item') + plugin.get('item_%s' % menu.selected.type)

            if hasattr(menu.selected, 'display_type'):
                plugins += plugin.get('item_%s' % menu.selected.display_type)

            for p in plugins:
                for a in p.actions(menu.selected):
                    if not isinstance(a, MenuItem) and len(a) > 2 and a[2] == event.arg:
                        a[0](arg=None, menuw=self)
                        return
            _debug_('action %s not found' % event.arg)

                    
        elif event == MENU_CHANGE_STYLE and len(self.menustack) > 1:
            # did the menu change?
            if skin.toggle_display_style(menu):
                self.rebuild_page()
                self.refresh()
                return
                

        elif hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
            if menu.selected.eventhandler(event = event, menuw=self):
                return
            
        for p in self.eventhandler_plugins:
            if p.eventhandler(event=event, menuw=self):
                return

        _debug_('no eventhandler for event %s' % str(event), 2)
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
        menu.display_style = skin.get_display_style(menu)
        

    def init_page(self):
        
        menu = self.menustack[-1]
        if not menu:
            return

        # Create the list of main selection items (menu_items)
        menu_items           = []
        first                = menu.page_start
        self.rows, self.cols = menu.items_per_page()
        
        for choice in menu.choices[first : first+(self.rows*self.cols)]:
            menu_items.append(choice)
     
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

        # make sure we are in context 'menu'
        rc.set_context(self.event_context)



# register menu to the skin
skin.register('menu', ('screen', 'title', 'subtitle', 'view', 'listing', 'info', 'plugin'))
