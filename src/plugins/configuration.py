# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# config.py - a configuration plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Eric Bus <eric@fambus.nl>
#
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

#python modules
import logging

#freevo modules
import config
import plugin
import util
import gui

from menu import Item, Action, ActionItem, Menu
from gui.windows import InputBox
from config import rtXML

from mainmenu import MainMenuItem
from application import MenuApplication

# get logging object
log = logging.getLogger()

class PluginInterface(plugin.MainMenuPlugin):
    """
    A plugin to change the runtime configuration of Freevo
    To activate, put the following line in local_conf.py:
    plugin.activate('configuration')
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
        return [ ConfigMainMenuItem(parent) ]


class ConfigurationItem(Item):
    """
    Item for the menu for one configuration item
    """
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.path = []
        self.leaf_name = ''
        self.is_var = False
        self.config_value = ''
        self.var_name = ''
        self.var_type = ''
        self.options = {}


    def set_path(self, base, ext):
        self.base_path = base[:]
        self.path = base[:]
        self.path.append(ext)


    def mod_string(self):
        InputBox(text=_('Change value:'),
            start_value=rtXML.get_value(self.base_path, self.var_name),
            handler=self.alter_string).show()


    def mod_integer(self):
        InputBox(text=_('Change value:'), type='integer',
            start_value=rtXML.get_value(self.base_path, self.var_name),
            increment=self.options['increment'],
            min_int=self.options['min_int'],
            max_int=self.options['max_int'],
            handler=self.alter_string).show()


    def alter_string(self, string=None):
        if string:
            if rtXML.set_value(self.base_path, self.var_name, string):
                return None
            else:
                return "Cannot set variable"


    def edit_var(self):
        if self.var_type == 'string':
            self.mod_string()
        elif self.var_type == 'integer':
            self.mod_integer()
        else:
            log.error('%s is not supported yet' % self.var_type)


    def actions(self):
        """
        Follow this option, show sub-options or edit the value
        """
        if not self.is_var:
            return [ Action(_('Show options'), self.create_config_menu) ]
        else:
            return [ Action(self.name, self.edit_var) ]


    def create_config_menu(self):
        """
        Create a config menu for the given path
        """
        configuration_values = []

        items = rtXML.get_items( self.path )
        if items != False and len(items) > 0:
            for item in items:
                configuration_item = ConfigurationItem(self)
                configuration_item.name = item[0]
                configuration_item.leaf_name = item[1]
                configuration_item.is_var = item[1] == 'var'
                configuration_item.var_name = item[2]
                configuration_item.config_value = item[3]
                configuration_item.var_type = item[4]
                configuration_item.options = item[5]
                configuration_item.set_path(self.path, item[1])

                configuration_values += [ configuration_item ]

        if (len(configuration_values) == 0):
            mi = ActionItem(_('No configuration values'), None,
                            self.get_menustack().back_one_menu)
            configuration_values += [mi]

        configuration_menu = Menu(_('Configuration'), configuration_values)
        self.pushmenu(configuration_menu)





class ConfigMainMenuItem(MainMenuItem, ConfigurationItem):
    """
    This is the item for the main menu and creates the list
    of Headlines Sites in a submenu.
    """
    def __init__(self, parent):
        self.path = []
        MainMenuItem.__init__( self, _('Configuration'), type='main',
                               parent=parent)


    def actions(self):
        """
        Return a list of actions for this item
        """
        return [ Action(_('Show options'), self.create_config_menu) ]
