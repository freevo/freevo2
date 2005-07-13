# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# shutdown.py  -  shutdown plugin
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin creates the shutdown main menu item
#
# First edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
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

# python imports
import sys
import os

# kaa imports
import kaa.notifier

# freevo imports
import config
import gui
import gui.widgets

from gui.windows import ConfirmBox
from mainmenu import MainMenuItem
from plugin import MainMenuPlugin


class ShutdownItem(MainMenuItem):
    """
    Item for shutdown
    """
    def __init__(self, parent=None):
        MainMenuItem.__init__(self, parent=parent, skin_type='shutdown')
        self.menuw = None


    def actions(self):
        """
        return a list of actions for this item
        """
        if config.CONFIRM_SHUTDOWN:
            items = [ (self.confirm_freevo, _('Shutdown Freevo') ),
                      (self.confirm_system, _('Shutdown system') ),
                      (self.confirm_system_restart, _('Restart system') ) ]
        else:
            items = [ (self.shutdown_freevo, _('Shutdown Freevo') ),
                      (self.shutdown_system, _('Shutdown system') ),
                      (self.shutdown_system_restart, _('Restart system') ) ]
        if config.ENABLE_SHUTDOWN_SYS:
            items = [ items[1], items[0], items[2] ]

        return items


    def confirm_freevo(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to shut down Freevo?')
        ConfirmBox(text=what, handler=self.shutdown_freevo,
                   default_choice=1).show()


    def confirm_system(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to shut down the system?')
        ConfirmBox(text=what, handler=self.shutdown_system,
                   default_choice=1).show()

    def confirm_system_restart(self, arg=None, menuw=None):
        """
        Pops up a ConfirmBox.
        """
        self.menuw = menuw
        what = _('Do you really want to restart the system?')
        ConfirmBox(text=what, handler=self.shutdown_system_restart,
                   default_choice=1).show()


    def show_gui_message(self, text):
        """
        Clear the screen and show the message.
        """
        msg = gui.widgets.Text(text, (0, 0), (gui.width, gui.height),
                               gui.theme.font('default'), align_h='center',
                               align_v='center')
        gui.display.clear()
        gui.display.add_child(msg)
        gui.display.update()

        
    def shutdown_freevo(self, arg=None, menuw=None):
        """
        shutdown freevo, don't shutdown the system
        """
        self.show_gui_message(_('shutting down...'))
        kaa.notifier.OneShotTimer(sys.exit, 0).start(1000)


    def shutdown_system(self, arg=None, menuw=None):
        """
        shutdown the complete system
        """
        self.show_gui_message(_('shutting down system...'))
        kaa.notifier.OneShotTimer(os.system, config.SHUTDOWN_SYS_CMD).start(1000)


    def shutdown_system_restart(self, arg=None, menuw=None):
        """
        restart the complete system
        """
        self.show_gui_message(_('restarting system...'))
        kaa.notifier.OneShotTimer(os.system, config.RESTART_SYS_CMD).start(1000)





#
# the plugin is defined here
#

class PluginInterface(MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        return [ ShutdownItem(parent) ]
