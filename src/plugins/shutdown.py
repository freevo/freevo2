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
from .. import core as freevo
from ..core.system import manager as system

# get shutdown config
config = freevo.config.plugin.shutdown

class ShutdownItem(freevo.MainMenuItem):
    """
    Item for shutdown
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        def choose_cb(confirm, noconfirm):
            if config.confirm:
                return confirm
            return noconfirm

        items = [ freevo.Action(_('Shutdown Freevo'), choose_cb(self.confirm_freevo, system.exit)),
                  freevo.Action(_('Restart Freevo'), choose_cb(self.confirm_freevo_restart, system.restart))]

        if system.can_suspend():
            items.append(freevo.Action(_('Suspend system'), choose_cb(self.confirm_suspend, system.suspend)))

        if system.can_hibernate():
            items.append(freevo.Action(_('Hibernate system'), choose_cb(self.confirm_hibernate, system.hibernate)))

        if system.can_shutdown():
            items.append(freevo.Action(_('Shutdown system'), choose_cb(self.confirm_system, system.shutdown)))

        if system.can_reboot():
            items.append(freevo.Action(_('Restart system'), choose_cb(self.confirm_sys_restart, system.restart)))

        if config.default == 'system':
            items = items[2:] + items[:2]

        return items


    def confirm_freevo(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to shut down Freevo?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.exit)
        box.show()


    def confirm_system(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to shut down the system?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.shutdown)
        box.show()


    def confirm_freevo_restart(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to restart Freevo?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.restart)
        box.show()


    def confirm_sys_restart(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to restart the system?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.reboot)
        box.show()

    def confirm_suspend(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to suspend the system?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.suspend)
        box.show()

    def confirm_hibernate(self):
        """
        Pops up a ConfirmWindow.
        """
        what = _('Do you really want to hibernate the system?')
        box = freevo.ConfirmWindow(what, default_choice=1)
        box.buttons[0].connect(system.hibernate)
        box.show()

#
# the plugin is defined here
#

class PluginInterface(freevo.MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """

    def items(self, parent):
        return [ ShutdownItem(parent, _('Shutdown')) ]
