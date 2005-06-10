# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# widget.py - Menu widget for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'MenuWidget' ]


# python imports
import logging

# freevo imports
import config
import plugin
import gui.areas
import gui.theme
from gui.windows import MessageBox

from event import *
from application import Application

# menu imports
from menu import Menu

# get logging object
log = logging.getLogger('menu')


class MenuWidget(Application):
    """
    The MenuWidget handles a stack of Menus
    """
    def __init__(self, engine=None):
        Application.__init__(self, 'menu widget', 'menu', False, True)
        self.menustack = []
        if not engine:
            engine = gui.areas.Handler('menu', ('screen', 'title', 'subtitle',
                                                'view', 'listing', 'info'))
        self.engine = engine
        self.inside_menu = False


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
        if self.inside_menu:
            self.engine.show(0)
            self.inside_menu = False
        else:
            self.engine.show(config.GUI_FADE_STEPS)


    def hide(self, clear=True):
        """
        hide the menu
        """
        Application.hide(self)
        if self.inside_menu:
            self.engine.hide(0)
            self.inside_menu = False
        else:
            self.engine.hide(config.GUI_FADE_STEPS)


    def delete_menu(self, arg=None, menuw=None, allow_reload=True):
        """
        delete last menu from the stack, no redraw
        """
        if len(self.menustack) > 1:
            if hasattr(self.menustack[-1], 'hide'):
                self.menustack[-1].hide()
            del self.menustack[-1]
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
        if len(self.menustack) > 1 and \
               hasattr(self.menustack[-1], 'is_submenu') and \
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
        """
        Go back on menu. Or if the current menu has a variable called
        'back_one_menu' it is the real number of menus to go back
        """
        if len(self.menustack) == 1:
            return
        previous = self.menustack[-1]
        if previous and hasattr(previous, 'back_one_menu'):
            self.menustack = self.menustack[:-previous.back_one_menu]
        else:
            self.menustack = self.menustack[:-1]

        # get the current shown menu
        menu = self.menustack[-1]

        if not isinstance(menu, Menu):
            # The new menu is no 'Menu', it is a 'MenuApplication'
            # Mark both the previous shown Menu (app or self) and the
            # new one with 'inside_menu' to avoid fading in/out because
            # we still are in the menu and why should we fade here?
            menu.inside_menu = True
            if isinstance(previous, Menu):
                self.inside_menu = True
            else:
                previous.inside_menu = True
            # refresh will do the rest
            self.refresh()
            return True

        if not isinstance(previous, Menu):
            # Now we show a 'Menu' buit the previous is a 'MenuApplication'.
            # Make the widget and the previous app as 'inside_menu' to
            # avoid fading effects
            previous.inside_menu = True
            self.inside_menu = True

        if menu.reload_func:
            # The menu has a reload function. Call it to rebuild
            # this menu. If the functions returns something, replace
            # the old menu with the returned one.
            reload = menu.reload_func()
            if reload:
                self.menustack[-1] = reload
                menu = self.menustack[-1]

        # the the theme
        if isinstance(menu, Menu):
            gui.theme.set(menu.theme)
        if arg == 'reload':
            self.refresh(reload=1)
        else:
            self.refresh()


    def goto_main_menu(self, arg=None, menuw=None):
        """
        Go back to the main menu
        """
        self.menustack = [ self.menustack[0] ]
        menu = self.menustack[0]
        gui.theme.set(menu.theme)
        self.refresh()


    def pushmenu(self, menu):
        """
        Add a new Menu to the stack and show it
        """
        if len(self.menustack) > 0:
            previous = self.menustack[-1]
        else:
            previous = None
        # If the current shown menu is no Menu but a MenuApplication
        # hide it from the screen. Mark 'inside_menu' to avoid a
        # fade effect for hiding
        if previous and not isinstance(previous, Menu):
            self.inside_menu = True
            previous.inside_menu = True
            previous.hide()
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
                    menu.theme = gui.theme.set(menu.theme)
            gui.theme.set(menu.theme)
            if previous and not isinstance(previous, Menu):
                # Current showing is no Menu, we are hidden.
                self.show()
        else:
            # The current Menu is a MenuApplication, set menuw
            # to it so it can reference back to us. Also set
            # theme and 'inside_menu'.
            menu.menuw = self
            menu.theme = previous.theme
            self.inside_menu = True
            menu.inside_menu = True

        # refresh will do the update
        self.refresh()


    def refresh(self, reload=0):
        """
        Refresh the menuwidget. This includes some basic stuff
        like mounting/unmounting and also update the areas
        """
        menu = self.menustack[-1]

        if not isinstance(menu, Menu):
            if self.visible:
                menu.show()
            return

        if self.menustack[-1].umount_all == 1:
            for mp in vfs.mountpoints:
                mp.umount()

        if reload and menu.reload_func:
            new_menu = menu.reload_func()
            if new_menu:
                self.menustack[-1] = new_menu

        if self.visible:
            menu = self.menustack[-1]
            if menu.selected:
                menu.selected.__init_info__()
            self.engine.draw(menu)


    def make_submenu(self, menu_name, actions, item):
        """
        Make a submenu based on all actions for this item
        """
        items = []
        for a in actions:
            items.append(a)
        theme = None

        if item.skin_fxd:
            theme = item.skin_fxd

        for i in items:
            if not hasattr(item, 'is_mainmenu_item'):
                i.image = item.image
            if hasattr(item, 'display_type'):
                i.display_type = item.display_type
            elif hasattr(item, 'type'):
                i.display_type = item.type

        s = Menu(menu_name, items, theme=theme)
        s.is_submenu = True
        self.pushmenu(s)


    def eventhandler(self, event):
        """
        Eventhandler for menu controll
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
            if hasattr(menu.selected, 'eventhandler') and \
                   menu.selected.eventhandler:
                if menu.selected.eventhandler(event, self):
                    return True
            return False

        # handle menu not instance of class Menu
        if not isinstance(menu, Menu):
            return False

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
            actions = menu.selected.actions()
            if not actions:
                msg = _('No action defined for this choice!')
                MessageBox(text=msg).show()
            else:
                actions[0](menu.selected, self)
            return True


        if event == MENU_SUBMENU:
            if hasattr(menu, 'is_submenu'):
                return True

            actions = menu.selected.actions()
            force   = False
            if not actions:
                force   = True

            plugins = plugin.get('item') + \
                      plugin.get('item_%s' % menu.selected.type)

            if hasattr(menu.selected, 'display_type'):
                plugins += plugin.get('item_%s' % menu.selected.display_type)

            plugins.sort(lambda l, o: cmp(l._level, o._level))

            for p in plugins:
                for a in p.actions(menu.selected):
                    actions.append(a)
            if actions and (len(actions) > 1 or force):
                self.make_submenu(menu.selected.name, actions, menu.selected)
            return True


        if event == MENU_CALL_ITEM_ACTION:
            log.info('calling action %s' % event.arg)

            for a in menu.selected.actions():
                if not hasattr(a, 'shortcut'):
                    # FIXME: this shouldn't happen after restructuring
                    pass
                elif a.shortcut == event.arg:
                    a(menu.selected, self)
                    return True
                    
            plugins = plugin.get('item') + \
                      plugin.get('item_%s' % menu.selected.type)

            if hasattr(menu.selected, 'display_type'):
                plugins += plugin.get('item_%s' % menu.selected.display_type)

            for p in plugins:
                for a in p.actions(menu.selected):
                    if not hasattr(a, 'shortcut'):
                        # FIXME: this shouldn't happen after restructuring
                        pass
                    elif a.shortcut == event.arg:
                        a(menu.selected, self)
                        return True
            log.info('action %s not found' % event.arg)


        if event == MENU_CHANGE_STYLE and len(self.menustack) > 1:
            # did the menu change?
            self.engine.toggle_display_style(menu)
            self.refresh()

        if hasattr(menu.selected, 'eventhandler') and \
               menu.selected.eventhandler:
            if menu.selected.eventhandler(event, self):
                return True

        return False
