# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sdl.py - SDL input support using pygame.
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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


# Python imports
import weakref
import pygame
import logging

# Freevo imports
import config
import gui

from menu import Item
from event import *
from input.interface import InputPlugin

# get logging object
log = logging.getLogger('input')

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        InputPlugin.__init__(self)

        # define the keymap
        self.keymap = {}
        for key in config.KEYBOARD_MAP:
            if hasattr(pygame.locals, 'K_%s' % key):
                code = getattr(pygame.locals, 'K_%s' % key)
                self.keymap[code] = config.KEYBOARD_MAP[key]
            elif hasattr(pygame.locals, 'K_%s' % key.lower()):
                code = getattr(pygame.locals, 'K_%s' % key.lower())
                self.keymap[code] = config.KEYBOARD_MAP[key]
            else:
                log.error('unable to find key code for %s' % key)

        # set mouse hiding on/off
        gui.display._window.hide_mouse = not config.INPUT_MOUSE_SUPPORT

        # connect to signals
        signals = gui.display._window.signals
        signals['key_press_event'].connect(self.key_press_event)
        if config.INPUT_MOUSE_SUPPORT:
            signals['mouse_down_event'].connect(self.mouse_down_event)
            signals['mouse_up_event'].connect(self.mouse_up_event)


    def key_press_event(self, key):
        """
        Callback when a key is pressed.
        """
        if key in self.keymap:
            self.post_key(self.keymap[key])


    def get_widget_at(self, point):
        """
        Return action at the given point.
        """
        for widget in gui.display.get_childs_at(point):
            if hasattr(widget, 'action'):
                if isinstance(widget.action, weakref.ReferenceType):
                    # follow the weakref
                    return widget.action()
                return widget.action
        return None


    def mouse_down_event(self, button, pos):
        """
        Mouse button event handling.
        This code is in an very early stage and may fail. It also
        only works with the menu right now, going back one menu
        is not working, there is a visible button the the screen
        missing to do that.
        A bigger eventmap should be created somewhere to make this
        work for the player as well.
        """
        action = self.get_widget_at(pos)
        if not action:
            return True

        if isinstance(action, Item):
            # Action is an item, do some menu code here.
            MENU_CHANGE_SELECTION.post(action)
        return True


    def mouse_up_event(self, button, pos):
        """
        Mouse button event handling.
        This code is in an very early stage and may fail. It also
        only works with the menu right now, going back one menu
        is not working, there is a visible button the the screen
        missing to do that.
        A bigger eventmap should be created somewhere to make this
        work for the player as well.
        """
        action = self.get_widget_at(pos)
        if not action:
            return True

        if isinstance(action, str):
            if action == 'PAGE_UP':
                # Action 'UP' is defined in the listing_area
                MENU_PAGEUP.post()
            elif action == 'PAGE_DOWN':
                # Action 'DOWN' is defined in the listing_area
                MENU_PAGEDOWN.post()

        elif isinstance(action, Item):
            if action.menu and action.menu.selected == action:
                # Action is an item, do some menu code here.
                if button == 1:
                    MENU_SELECT.post()
                elif button == 3:
                    MENU_SUBMENU.post()
            else:
                # mouse moved to much
                pass

        elif callable(action):
            # Action can be called
            action()
