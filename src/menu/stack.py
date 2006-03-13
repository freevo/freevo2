# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# stack.py - Menu stack for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a menu stack. It is not connected to the GUI so the real
# menu widget must inherit from this class and override the basic GUI functions
# show, hide, set_theme and redraw.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'MenuStack' ]

# python imports
import logging

# kaa imports
from kaa.weakref import weakref

# freevo imports
import config
from event import *

# menu imports
from menu import Menu
from item import Item

# get logging object
log = logging.getLogger('menu')


class MenuStack(object):
    """
    The MenuStack handles a stack of Menus
    """
    def __init__(self):
        self.menustack = []
        self.inside_menu = False
        self.previous = None
        self.visible = False


    def show(self):
        """
        Show the menu on the screen
        """
        if len(self.menustack) == 0:
            return
        if isinstance(self.menustack[-1], Menu):
            self.menustack[-1].show()


    def hide(self):
        """
        Hide the menu
        """
        if len(self.menustack) == 0:
            return
        if isinstance(self.menustack[-1], Menu):
            self.menustack[-1].hide()


    def redraw(self):
        """
        Redraw the menu.
        """
        raise AttributeError('MenuStack.redraw not defined')


    def set_theme(self, theme):
        """
        Set the theme for menu drawing.
        """
        raise AttributeError('MenuStack.set_theme not defined')


    def back_to_menu(self, menu, refresh=True):
        """
        Go back to the given menu.
        """
        while len(self.menustack) > 1 and self.menustack[-1] != menu:
            self.menustack.pop()
        if refresh:
            self.refresh(True)

            
    def back_one_menu(self, refresh=True):
        """
        Go back one menu page.
        """
        if len(self.menustack) == 1:
            return
        self.menustack.pop()
        if refresh:
            self.refresh(True)


    def delete_submenu(self, refresh=True, reload=False, osd_message=''):
        """
        Delete the last menu if it is a submenu. Also refresh or reload the
        new menu if the attributes are set to True. If osd_message is set,
        this message will be send if the current menu is no submenu
        """
        if len(self.menustack) > 1 and self.menustack[-1].submenu:
            self.back_one_menu(refresh)
        elif len(self.menustack) > 1 and osd_message:
            OSD_MESSAGE.post(osd_message)


    def pushmenu(self, menu):
        """
        Add a new Menu to the stack and show it
        """
        # set stack (self) pointer to menu
        menu.stack = weakref(self)

        if len(self.menustack) > 0:
            previous = self.menustack[-1]
        else:
            previous = None
        # If the current shown menu is no Menu but a MenuApplication
        # hide it from the screen. Mark 'inside_menu' to avoid a
        # fade effect for hiding
        if previous:
            if not isinstance(previous, Menu):
                self.inside_menu = True
                previous.inside_menu = True

        self.menustack.append(menu)
        # Check the new menu. Maybe we need to set 'inside_menu' if we
        # switch between MenuApplication(s) and also set a new theme
        # for the global Freevo look
        if isinstance(menu, Menu):
            if not menu.theme:
                menu.theme = previous.theme
            if isinstance(menu.theme, str):
                if menu.theme == previous.theme.filename:
                    menu.theme = previous.theme
                else:
                    menu.theme = self.set_theme(menu.theme)
            self.set_theme(menu.theme)
        else:
            # The current Menu is a MenuApplication, set
            # theme and 'inside_menu'.
            menu.theme = previous.theme
            self.inside_menu = True
            menu.inside_menu = True

        if isinstance(menu, Menu) and menu.autoselect and \
               len(menu.choices) == 1:
            log.info('autoselect action')
            # autoselect only item in the menu
            menu.choices[0].get_actions()[0]()
            return

        # refresh will do the update
        self.refresh()

        if previous and not isinstance(previous, Menu):
            # Current showing was no Menu, we are hidden.
            # So make menu stack visible again
            self.show()


    def refresh(self, reload=False):
        """
        Refresh the stack and redraw it.
        """
        menu = self.menustack[-1]
        
        if isinstance(menu, Menu) and menu.autoselect and \
               len(menu.choices) == 1:
            # do not show a menu with only one item. Go back to
            # the previous page
            log.info('delete menu with only one item')
            return self.back_one_menu()
            
        if not isinstance(menu, Menu):
            # The new menu is no 'Menu', it is a 'MenuApplication'
            # Mark both the previous shown Menu (app or self) and the
            # new one with 'inside_menu' to avoid fading in/out because
            # we still are in the menu and why should we fade here?
            menu.inside_menu = True
            if isinstance(self.previous, Menu):
                self.inside_menu = True
            elif self.previous:
                self.previous.inside_menu = True
            # hide previous menu page
            if self.previous and isinstance(self.previous, Menu):
                self.previous.hide()
            # set last menu to the current one visible
            self.previous = menu
            if self.visible:
                menu.show()
            return

        if self.previous and not isinstance(self.previous, Menu):
            # Now we show a 'Menu' but the previous is a 'MenuApplication'.
            # Make the widget and the previous app as 'inside_menu' to
            # avoid fading effects
            self.previous.inside_menu = True
            self.inside_menu = True

        if self.visible and menu != self.previous:
            # show the current page and hide the old one
            if self.previous:
                self.previous.hide()
            menu.show()
        elif not self.visible and self.previous:
            # hide the previous menu
            self.previous.hide()

        # set last menu to the current one visible
        self.previous = menu

        if reload and menu.reload_func:
            # The menu has a reload function. Call it to rebuild
            # this menu. If the functions returns something, replace
            # the old menu with the returned one.
            new_menu = menu.reload_func()
            if new_menu:
                self.menustack[-1] = new_menu
                menu = new_menu
                
        # set the theme
        if isinstance(menu, Menu):
            self.set_theme(menu.theme)

        if not self.visible:
            # nothing to do anymore
            return

        if menu.selected:
            # init the selected item
            menu.selected.__init_info__()

        # redraw the menu
        self.redraw()
        return


    def __getitem__(self, attr):
        """
        Return menustack item.
        """
        return self.menustack[attr]
    

    def __setitem__(self, attr, value):
        """
        Set menustack item.
        """
        self.menustack[attr] = value
    

    def get_selected(self):
        """
        Return the current selected item in the current menu.
        """
        return self.menustack[-1].selected

    
    def eventhandler(self, event):
        """
        Eventhandler for menu control
        """
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

        if event == MENU_GOTO_MAINMENU:
            while len(self.menustack) > 1:
                menu = self.menustack.pop()
            self.refresh()
            return True

        if event == MENU_BACK_ONE_MENU:
            self.back_one_menu()
            return True

        # handle empty menus
        if not menu.choices:
            if event in ( MENU_SELECT, MENU_SUBMENU, MENU_PLAY_ITEM):
                self.back_one_menu()
                return True
            menu = self.menustack[-2]
            if hasattr(menu.selected, 'eventhandler') and \
                   menu.selected.eventhandler:
                if menu.selected.eventhandler(event):
                    return True
            return False

        # handle menu not instance of class Menu
        if not isinstance(menu, Menu):
            return False

        if event == MENU_UP:
            menu.select(-menu.cols)
            self.refresh()
            return True


        if event == MENU_DOWN:
            menu.select(menu.cols)
            self.refresh()
            return True


        if event == MENU_PAGEUP:
            menu.select(-(menu.rows * menu.cols))
            self.refresh()
            return True


        if event == MENU_PAGEDOWN:
            menu.select(menu.rows * menu.cols)
            self.refresh()
            return True


        if event == MENU_LEFT:
            menu.select(-1)
            self.refresh()
            return True


        if event == MENU_RIGHT:
            menu.select(1)
            self.refresh()
            return True


        if event == MENU_PLAY_ITEM and hasattr(menu.selected, 'play'):
            menu.selected.play()
            self.refresh()
            return True


        if event == MENU_CHANGE_SELECTION:
            menu.select(event.arg)
            self.refresh()
            return True
        
        if event == MENU_SELECT or event == MENU_PLAY_ITEM:
            actions = menu.selected.get_actions()
            if not actions:
                OSD_MESSAGE.post(_('No action defined for this choice!'))
            else:
                actions[0]()
            return True


        if event == MENU_SUBMENU:
            if menu.submenu:
                return True

            actions = menu.selected.get_actions()
            if actions and len(actions) > 1:
                items = []
                for a in actions:
                    items.append(Item(menu.selected, a))
                theme = None

                if menu.selected.skin_fxd:
                    theme = menu.selected.skin_fxd

                for i in items:
                    if not menu.selected.type == 'main':
                        i.image = menu.selected.image
                    if hasattr(menu.selected, 'display_type'):
                        i.display_type = menu.selected.display_type
                    else:
                        i.display_type = menu.selected.type

                s = Menu(menu.selected.name, items, theme=theme)
                s.submenu = True
                s.item = menu.selected
                self.pushmenu(s)
            return True


        if event == MENU_CALL_ITEM_ACTION:
            log.info('calling action %s' % event.arg)
            for a in menu.selected.get_actions():
                if a.shortcut == event.arg:
                    a()
                    return True
            log.info('action %s not found' % event.arg)


        if hasattr(menu.selected, 'eventhandler') and \
               menu.selected.eventhandler:
            if menu.selected.eventhandler(event):
                return True

        return False
