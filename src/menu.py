# -*- coding: iso-8859-1 -*-
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
# Revision 1.101  2004/08/05 17:36:13  dischi
# remove "page" code, the skin takes care of that now
#
# Revision 1.100  2004/08/01 10:57:34  dischi
# make the menu an "Application"
#
# Revision 1.99  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.98  2004/07/25 19:47:38  dischi
# use application and not rc.app
#
# Revision 1.97  2004/07/25 18:22:27  dischi
# changes to reflect gui update
#
# Revision 1.96  2004/07/23 19:44:00  dischi
# move most of the settings code out of the skin engine
#
# Revision 1.95  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.94  2004/06/02 21:38:02  dischi
# fix crash
#
# Revision 1.93  2004/05/09 09:58:43  dischi
# make it possible to force a page rebuild
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


import copy

import config
import plugin
import util

from event import *
from item import Item
from eventhandler import Application

import gui
from gui import AlertBox


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
    def __init__(self, heading, choices=[], fxd_file=None, umount_all = 0,
                 reload_func = None, item_types = None, force_skin_layout = -1):

        self.heading = heading
        self.choices = choices             # List of MenuItem:s
        if len(self.choices):
            self.selected     = self.choices[0]
            self.selected_pos = 0
        else:
            self.selected     = None
            self.selected_pos = -1
            
        self.umount_all    = umount_all    # umount all ROM drives on display?
        self.skin_settings = None
        if fxd_file:
            self.skin_settings = gui.load_settings(fxd_file)

        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        self.viewitem = None

        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func       = reload_func  
        self.item_types        = item_types
        self.force_skin_layout = force_skin_layout

        # How many menus to go back when 'BACK_ONE_MENU' is called
        self.back_one_menu = 1

        # how many rows and cols does the menu has
        # (will be changed by the skin code)
        self.cols = 1
        self.rows = 1

        
    def change_selection(self, rel):
        """
        select a new item relative to current selected
        """
        self.selected_pos = min(max(0, self.selected_pos + rel), len(self.choices) - 1)
        self.selected = self.choices[self.selected_pos]


    def set_selection(self, item):
        """
        set the selection to a specific item in the list
        """
        if item:
            self.selected     = item
            self.selected_pos = self.choices.index(item)
        else:
            self.selected     = None
            self.selected_pos = -1



class MenuApplication(Application):
    """
    An application inside the menu
    """
    def __init__(self, name, event_context, fullscreen):
        Application.__init__(self, name, event_context, fullscreen)
        self.menuw = None
        

    def eventhandler(self, event):
        """
        Eventhandler for basic menu functions
        """
        if not self.menuw:
            return False
        if event == MENU_GOTO_MAINMENU:
            self.destroy()
            self.menuw.goto_main_menu()
            return True
        if event == MENU_BACK_ONE_MENU:
            self.destroy()
            self.menuw.back_one_menu()
            return True
        return False


    def show(self):
        """
        show the menu on the screen
        """
        Application.show(self)


    def refresh(self):
        """
        refresh display
        """
        pass



        
class MenuWidget(Application):
    """
    The MenuWidget handles a stack of Menus
    """
    def __init__(self, engine=None):
        Application.__init__(self, 'menu widget', 'menu', False)
        self.menustack = []
        self.eventhandler_plugins = None
        if not engine:
            engine = gui.get_areas()
            # register menu to the skin
            engine.register('menu', ('screen', 'title', 'subtitle', 'view',
                                     'listing', 'info'))
        self.engine = engine
        

    def get_event_context(self):
        """
        return the event context
        """
        if self.menustack and hasattr(self.menustack[-1], 'event_context'):
            return self.menustack[-1].event_context
        return self.event_context


    def show(self):
        """
        show the menu on the screen
        """
        Application.show(self)
        self.refresh(reload=1)

                
    def hide(self, clear=True):
        """
        hide the menu
        """
        Application.hide(self)
        self.engine.clear('menu')
            
        
    def delete_menu(self, arg=None, menuw=None, allow_reload=True):
        """
        delete last menu from the stack, no redraw
        """
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                return True
            
            if menu.reload_func and allow_reload:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload


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
            self.post_event(Event(OSD_MESSAGE, arg=osd_message))

            
    def back_one_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            try:
                count = -self.menustack[-1].back_one_menu
            except:
                count = -1

            self.menustack = self.menustack[:count]
            menu = self.menustack[-1]

            if not isinstance(menu, Menu):
                self.refresh()
                return True
            
            if menu.reload_func:
                reload = menu.reload_func()
                if reload:
                    self.menustack[-1] = reload

            if arg == 'reload':
                self.refresh(reload=1)
            else:
                self.refresh()
                

    def goto_main_menu(self, arg=None, menuw=None):
        self.menustack = [self.menustack[0]]
        menu = self.menustack[0]
        self.refresh()

    
    def pushmenu(self, menu):
        gui.get_screen().prepare_for_move(1)
        if len(self.menustack) > 0 and not isinstance(self.menustack[-1], Menu):
            _debug_('menu auto-hide %s' % self.menustack[-1])
            self.menustack[-1].hide()
        self.menustack.append(menu)
        if not isinstance(menu, Menu):
            menu.menuw = self
        self.refresh()


    def refresh(self, reload=0):
        menu = self.menustack[-1]

        if not isinstance(menu, Menu):
            if self.visible:
                menu.show()
            return
        
        if self.menustack[-1].umount_all == 1:
            util.umount_all()
                    
        if reload and menu.reload_func:
            new_menu = menu.reload_func()
            if new_menu:
                self.menustack[-1] = new_menu

        if self.visible:
            self.engine.draw('menu', self.menustack[-1])


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

        if isinstance(menu, Menu) and menu.cols == 1:
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
            return True
        
        if event == MENU_BACK_ONE_MENU:
            self.back_one_menu()
            return True

        if event == 'MENU_REFRESH':
            self.refresh()
            return True
        
        if event == 'MENU_REBUILD':
            self.refresh()
            return True

        # handle empty menus
        if not menu.choices:
            if event in ( MENU_SELECT, MENU_SUBMENU, MENU_PLAY_ITEM):
                self.back_one_menu()
                return True
            menu = self.menustack[-2]
            if hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
                if menu.selected.eventhandler(event = event, menuw=self):
                    return True
            for p in self.eventhandler_plugins:
                if p.eventhandler(event=event, menuw=self):
                    return True
            return True

        # handle menu not instance of class Menu
        if not isinstance(menu, Menu):
            if self.eventhandler_plugins == None:
                self.eventhandler_plugins = plugin.get('daemon_eventhandler')

            for p in self.eventhandler_plugins:
                if p.eventhandler(event=event, menuw=self):
                    return True

            _debug_('no eventhandler for event %s' % event, 2)
            return True

        if event == MENU_UP:
            menu.change_selection(-menu.cols)
            self.refresh()
            return True


        if event == MENU_DOWN:
            menu.change_selection(menu.cols)
            self.refresh()
            return True


        if event == MENU_PAGEUP:
            menu.change_selection(-(menu.rows * menu.cols))
            self.refresh()
            return True


        if event == MENU_PAGEDOWN:
            menu.change_selection(menu.rows * menu.cols)
            self.refresh()
            return True


        if event == MENU_LEFT:
            menu.change_selection(-1)
            self.refresh()
            return True
        

        if event == MENU_RIGHT:
            menu.change_selection(1)
            self.refresh()
            return True


        if event == MENU_PLAY_ITEM and hasattr(menu.selected, 'play'):
            menu.selected.play(menuw=self)
            self.refresh()
            return True

        
        if event == MENU_SELECT or event == MENU_PLAY_ITEM:
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
            return True


        if event == MENU_SUBMENU:
            if hasattr(menu, 'is_submenu'):
                return True

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
            return True
            

        if event == MENU_CALL_ITEM_ACTION:
            _debug_('calling action %s' % event.arg)

            for a in menu.selected.actions():
                if not isinstance(a, Item) and len(a) > 2 and a[2] == event.arg:
                    a[0](arg=None, menuw=self)
                    return True
                
            plugins = plugin.get('item') + plugin.get('item_%s' % menu.selected.type)

            if hasattr(menu.selected, 'display_type'):
                plugins += plugin.get('item_%s' % menu.selected.display_type)

            for p in plugins:
                for a in p.actions(menu.selected):
                    if not isinstance(a, MenuItem) and len(a) > 2 and a[2] == event.arg:
                        a[0](arg=None, menuw=self)
                        return True
            _debug_('action %s not found' % event.arg)

                    
        if event == MENU_CHANGE_STYLE and len(self.menustack) > 1:
            # did the menu change?
            self.engine.toggle_display_style(menu)
            self.refresh()
                
        if hasattr(menu.selected, 'eventhandler') and menu.selected.eventhandler:
            if menu.selected.eventhandler(event = event, menuw=self):
                return True
            
        for p in self.eventhandler_plugins:
            if p.eventhandler(event=event, menuw=self):
                return True

        _debug_('no eventhandler for event %s' % str(event), 2)
        return False


