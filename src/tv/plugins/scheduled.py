# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id: directory.py 9248 2007-02-19 20:06:25Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Jose <jose4freevo@chello.nl>
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

# python imports

# kaa imports

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui.mainmenu import Menu, MainMenuPlugin
from freevo.ui.menu import ActionItem
from freevo.ui.application import MessageWindow
from freevo.ui.tv.program import ProgramItem

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class PluginInterface(MainMenuPlugin):
    """
    This plugin is used to display your scheduled recordings.
    """
    def browse(self, parent):
        """ 
        Construct the menu
        """
        self.parent = parent
        items = self.get_items()
        if items:
            self.menu = Menu(_('View scheduled recordings'), items,
                                 type='tv program menu',
                                 reload_func = self.reload_scheduled)
            parent.get_menustack().pushmenu(self.menu)
        else:
            MessageWindow(_('There are no scheduled recordings.')).show()
    
    
    def reload_scheduled(self):
        """
        reload the list of scheduled recordings
        """
        items = self.get_items()
        if items:
            self.menu.set_items(items)
        else:
            self.parent.get_menustack().back_one_menu()

    
    def get_items(self):
        """
        create the list of scheduled recordings
        """
        items = []
        rec = tvserver.recordings.list()
        for scheduled in rec:
            if scheduled and not scheduled.status in ('deleted', 'missed'):
                items.append(ProgramItem(scheduled, self.parent))
        return items
        
                   
    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('View scheduled recordings'), parent, self.browse) ]
       
    
