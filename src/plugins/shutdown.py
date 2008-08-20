# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# shutdown.py  -  shutdown plugin
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin creates the shutdown main menu item
#
# First edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
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

# python imports
import sys
import os

# kaa imports
import kaa

# freevo imports
# from freevo.ui import gui
from freevo.ui.menu import Action
from freevo.ui.application import ConfirmWindow
from freevo.ui.mainmenu import MainMenuItem, MainMenuPlugin
# from freevo.ui.gui import theme, widgets
from freevo.ui import config

# get shutdown config
config = config.plugin.shutdown

class ShutdownItem(MainMenuItem):
    """
    Item for shutdown
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        if config.confirm and False:
            items = [ Action(_('Shutdown Freevo'), self.confirm_freevo),
                      Action(_('Shutdown system'), self.confirm_system),
                      Action(_('Restart Freevo'), self.confirm_freevo_restart),
                      Action(_('Restart system'), self.confirm_sys_restart) ]
        else:
            items = [ Action(_('Shutdown Freevo'), self.shutdown_freevo),
                      Action(_('Shutdown system'), self.shutdown_system),
                      Action(_('Restart Freevo'), self.shutdown_freevo_restart),
                      Action(_('Restart system'), self.shutdown_sys_restart) ]

        if config.default == 'system':
            items = [ items[1], items[0], items[2] ]

        return items


    def confirm_freevo(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to shut down Freevo?')
        box = ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(self.shutdown_freevo)
        box.show()


    def confirm_system(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to shut down the system?')
        box = ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(self.shutdown_system)
        box.show()


    def confirm_freevo_restart(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to restart Freevo?')
        box = ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(self.shutdown_freevo_restart)
        box.show()


    def confirm_sys_restart(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to restart the system?')
        box = ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(self.shutdown_sys_restart)
        box.show()


    def show_gui_message(self, text):
        """
        Clear the screen and show the message.
        """
        pass
#         size = gui.get_display().width, gui.get_display().height
#         msg = widgets.Text(text, (0, 0), size,
#                            theme.font('default'), align_h='center',
#                            align_v='center')
#         gui.get_display().clear()
#         gui.get_display().add_child(msg)
#         gui.get_display().update()

        
    def shutdown_freevo(self):
        """
        shutdown freevo, don't shutdown the system
        """
        self.show_gui_message(_('shutting down...'))
        kaa.OneShotTimer(sys.exit, 0).start(0.01)


    def shutdown_system(self):
        """
        shutdown the complete system
        """
        self.show_gui_message(_('shutting down system...'))
        kaa.OneShotTimer(os.system, config.command.halt).start(1)


    def shutdown_freevo_restart(self):
        """
        restart freevo
        """
        self.show_gui_message(_('restart...'))
        kaa.main.signals['shutdown'].connect(os.execvp, sys.argv[0], sys.argv)
        kaa.OneShotTimer(sys.exit, 0).start(1)


    def shutdown_sys_restart(self):
        """
        restart the complete system
        """
        self.show_gui_message(_('restarting system...'))
        kaa.OneShotTimer(os.system, config.command.restart).start(1)





#
# the plugin is defined here
#

class PluginInterface(MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        return [ ShutdownItem(parent, _('Shutdown')) ]
