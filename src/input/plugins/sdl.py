#if 0 /*
# -----------------------------------------------------------------------
# sdl.py - SDL input support using pygame.
# -----------------------------------------------------------------------
# $Id$
#
# This file handles pygame events and handles the keycode -> event
# mapping. You don't have to activate this plugin, it will be auto
# activated when the sdl display engine is used.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2005/07/09 09:08:39  dischi
# update mouse support
#
# Revision 1.6  2005/07/08 14:46:06  dischi
# add basic mouse support
#
# Revision 1.5  2005/05/07 18:09:41  dischi
# move InputPlugin definition to input.interface
#
# Revision 1.4  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.3  2004/10/06 18:52:27  dischi
# use KEYBOARD_MAP now and switch to new notifier code
#
# Revision 1.2  2004/09/27 18:40:35  dischi
# reworked input handling again
#
# Revision 1.1  2004/09/25 04:42:22  rshortt
# An SDL input handler using pygame.  This may work already but is still a
# work in progress.  Freevo still gets its input using src/gui/displays/sdl.py
# for the time being.  We need to work on universal user defined keymaps.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

# external imports
import notifier
import weakref

# python imports
import time
import pygame
from pygame import locals

# Freevo imports
import config
import gui
from menu import Item
from event import *
from input.interface import InputPlugin

import logging
log = logging.getLogger('input')

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        InputPlugin.__init__(self)
        
        self.keymap = {}
        for key in config.KEYBOARD_MAP:
            if hasattr(locals, 'K_%s' % key):
                code = getattr(locals, 'K_%s' % key)
                self.keymap[code] = config.KEYBOARD_MAP[key]
            elif hasattr(locals, 'K_%s' % key.lower()):
                code = getattr(locals, 'K_%s' % key.lower())
                self.keymap[code] = config.KEYBOARD_MAP[key]
            else:
                log.error('unable to find key code for %s' % key)
        if not config.INPUT_MOUSE_SUPPORT:
            self.mousehidetime = time.time()
        pygame.key.set_repeat(500, 30)
        notifier.addTimer( 20, self.handle )


    def handle(self):
        """
        Callback to handle the pygame events.
        """
        if not pygame.display.get_init():
            return True

        if not config.INPUT_MOUSE_SUPPORT:
            # Check if mouse should be visible or hidden
            mouserel = pygame.mouse.get_rel()
            mousedist = (mouserel[0]**2 + mouserel[1]**2) ** 0.5

            if mousedist > 4.0:
                pygame.mouse.set_visible(1)
                # Hide the mouse in 2s
                self.mousehidetime = time.time() + 1.0
            else:
                if time.time() > self.mousehidetime:
                    pygame.mouse.set_visible(0)

        # Return the next key event, or None if the queue is empty.
        # Everything else (mouse etc) is discarded.
        while 1:
            event = pygame.event.poll()

            if event.type == locals.NOEVENT:
                return True

            if event.type == locals.KEYDOWN:
                if event.key in self.keymap:
                    self.post_key(self.keymap[event.key])

            if not config.INPUT_MOUSE_SUPPORT:
                continue
            
            if event.type in (locals.MOUSEBUTTONDOWN, locals.MOUSEBUTTONUP):
                # Mouse button event handling.
                # This code is in an very early stage and may fail. It also
                # only works with the menu right now, going back one menu
                # is not working, there is a visible button the the screen
                # missing to do that.
                # A bigger eventmap should be created somewhere to make this
                # work for the player as well.
                action = None
                for widget in gui.display.get_childs_at(event.pos):
                    if hasattr(widget, 'action'):
                        action = widget.action
                        break
                else:
                    # no widget with an action found
                    continue
                
                if isinstance(action, weakref.ReferenceType):
                    # follow the weakref
                    action = action()

                # event to be posted to the eventhandler
                post_event = None
                
                if event.type == locals.MOUSEBUTTONDOWN:
                    # Handle mouse button down
                    if isinstance(action, Item):
                        # Action is an item, do some menu code here.
                        post_event = Event(MENU_CHANGE_SELECTION, action)

                if event.type == locals.MOUSEBUTTONUP:
                    # Handle mouse button up
                    if isinstance(action, str):
                        if action == 'PAGE_UP':
                            # Action 'UP' is defined in the listing_area
                            post_event = MENU_PAGEUP
                        elif action == 'PAGE_DOWN':
                            # Action 'DOWN' is defined in the listing_area
                            post_event = MENU_PAGEDOWN
                    elif isinstance(action, Item):
                        if action.menu and action.menu.selected == action:
                            # Action is an item, do some menu code here.
                            if event.button == 1:
                                post_event = MENU_SELECT
                            elif event.button == 3:
                                post_event = MENU_SUBMENU
                        else:
                            # mouse moved to much
                            pass
                    elif callable(action):
                        # Action can be called
                        action()
                        
                if post_event:
                    self.post_event(post_event)

        return True
