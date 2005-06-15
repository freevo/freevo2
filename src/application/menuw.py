# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menuw.py - Menu widget for Freevo
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

# freevo imports
import config
import gui.areas
import gui.theme

from event import *
from menu import MenuStack

# application imports
from base import Application


class MenuWidget(Application, MenuStack):
    """
    The MenuWidget is an Application for GUI and event handling and also
    an instance of MenuStack defined in menu.stack.
    """
    def __init__(self):
        Application.__init__(self, 'menu widget', 'menu', False, True)
        MenuStack.__init__(self)

        # define areas
        areas = ('screen', 'title', 'subtitle', 'view', 'listing', 'info')
        # create engine
        self.engine = gui.areas.Handler('menu', areas)
        # set gui theme engine
        self.set_theme = gui.theme.set


    def show(self):
        """
        Show the menu on the screen
        """
        Application.show(self)
        self.refresh(True)
        if self.inside_menu:
            self.engine.show(0)
            self.inside_menu = False
        else:
            self.engine.show(config.GUI_FADE_STEPS)


    def hide(self, clear=True):
        """
        Hide the menu
        """
        Application.hide(self)
        if self.inside_menu:
            self.engine.hide(0)
            self.inside_menu = False
        else:
            self.engine.hide(config.GUI_FADE_STEPS)


    def redraw(self):
        """
        Redraw the menu.
        """
        self.engine.draw(self.menustack[-1])


    def eventhandler(self, event):
        """
        Eventhandler for menu controll
        """
        if MenuStack.eventhandler(self, event):
            return True

        if event == MENU_CHANGE_STYLE and len(self.menustack) > 1:
            # did the menu change?
            self.engine.toggle_display_style(menu)
            self.refresh()
            return True

        return False
