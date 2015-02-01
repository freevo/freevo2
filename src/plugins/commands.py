# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# commands.py - commands plugin
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2015 Dirk Meyer, et al.
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
import subprocess

# kaa imports
import kaa

# freevo imports
from .. import core as freevo

class Application(freevo.Application):
    """
    Command application
    """
    def __init__(self, args, mode):
        """
        This application uses the fullscreen flag to hide the background
        and the idlebar. It also uses the menu eventmap and acts on
        MENU_BACK_ONE_MENU (ESC) to stop the application.
        """
        capabilities = (freevo.CAPABILITY_FULLSCREEN, )
        super(Application, self).__init__('menu', capabilities)
        self.proc = subprocess.Popen(args, stdin=None, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
        if mode == 'controlled':
            self.monitor()

    @kaa.coroutine()
    def monitor(self):
        """
        Monitor the application until it stopps
        """
        self.status = freevo.STATUS_RUNNING
        yield kaa.ThreadCallable(self.proc.wait)()
        self.status = freevo.STATUS_IDLE

    def eventhandler(self, event):
        """
        Eventhandler to handle MENU_BACK_ONE_MENU
        """
        if event == freevo.MENU_BACK_ONE_MENU:
            self.proc.kill()
            return True
        return False


class Item(freevo.Item):
    """
    Item for a command
    """
    def __init__(self, parent, name, args, mode):
        super(Item, self).__init__(parent)
        self.name = name
        self.args = args
        self.mode = mode

    def select(self):
        """
        Run the command in the Application class
        """
        Application(self.args, self.mode)


class MainMenuItem(freevo.MainMenuItem):
    """
    Item to create the command menu
    """
    def __init__(self, parent, name, items):
        super(MainMenuItem, self).__init__(parent, name)
        self.config = items

    def select(self):
        """
        Create the commands menu
        """
        items = []
        for item in self.config:
            items.append(Item(self, item.name, item.args, item.mode))
        self.menustack.pushmenu(freevo.Menu(self.name, items))


class PluginInterface(freevo.MainMenuPlugin):
    """
    Plugin to run commands from the main menu
    """
    def items(self, parent):
        if freevo.config.plugin.commands:
            return [ MainMenuItem(parent, _('Commands'), freevo.config.plugin.commands.items) ]
        return []
