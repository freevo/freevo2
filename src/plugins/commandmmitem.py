#if 0 /*
# -----------------------------------------------------------------------
# commandmmitem.py - a simple plugin to run arbitrary commands from a fxd
#                    as a main menu item. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes: To use add the following to local_conf.py:
# plugin.activate('commandmmitem', args=(/usr/local/freevo_data/Commands/Mozilla.fxd', ), level=45) 
# Todo: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/01/29 19:42:52  mikeruelle
# allow a use to add an fxd command file to the main menu. kinda like mediamenu. add you www, email or news app
#
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

#freevo modules
import config
import plugin
from item import Item
from command import CommandItem

class CommandMainMenuItem(Item):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent, myxmlfile):
        Item.__init__(self, parent, skin_type='commands')
        self.cmd_item = CommandItem(xmlfile=myxmlfile)
        self.name = self.cmd_item.name

        
    def actions(self):
        """
        return a list of actions for this item
        """
	items = [ ( self.cmd_item.flashpopup , _('Run Command') ) ]
        return items

class PluginInterface(plugin.MainMenuPlugin):
    """
    A small plugin to put a command in the main menu.
    Uses the command.py fxd file format to say which command to run.
    All output is logged in the freevo logdir.
    to activate it, put the following in your local_conf.py:

    plugin.activate('commandmmitem', args=(/usr/local/freevo_data/Commands/Mozilla.fxd', ), level=45) 

    The level argument is used to influence the placement in the Main Menu.
    consult freevo_config.py for the level of the other Menu Items if you
    wish to place it in a particular location.
    """
    def __init__(self, commandxmlfile):
        plugin.MainMenuPlugin.__init__(self)
        self.cmd_xml = commandxmlfile
    
    def items(self, parent):
        return [ CommandMainMenuItem(parent, self.cmd_xml) ]

