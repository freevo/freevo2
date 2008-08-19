# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menuw.py - Menu widget for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2008 Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
from freevo.ui.menu import MenuStack

# application imports
from base import Application, STATUS_RUNNING, CAPABILITY_TOGGLE


class MenuWidget(Application, MenuStack):
    """
    The MenuWidget is an Application for GUI and event handling and also
    an instance of MenuStack defined in menu.stack.
    """
    def __init__(self, menu):
        Application.__init__(self, 'menu', 'menu', (CAPABILITY_TOGGLE,))
        MenuStack.__init__(self)
        self.pushmenu(menu)
        self.status = STATUS_RUNNING
        self.signals['show'].connect_weak(self.refresh, True)


    def refresh(self, reload=False):
        if self.is_locked():
            return
        MenuStack.refresh(self, reload)
        self.gui_context.menu = self.menustack[-1]
        self.gui_context.item = self.menustack[-1].selected.properties
        self.gui_context.type = self.menustack[-1].type


    def eventhandler(self, event):
        """
        Eventhandler for menu control
        """
        return MenuStack.eventhandler(self, event)
