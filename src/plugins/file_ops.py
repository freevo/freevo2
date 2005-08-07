# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# file_ops.py - Small file (item) operations
# -----------------------------------------------------------------------------
# $Id$
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
import logging

# kaa imports
from kaa.notifier import Callback

# freevo imports
import config
import plugin
import util

from menu import Action
from gui.windows import ConfirmBox

# get logging object
log = logging.getLogger()


class PluginInterface(plugin.ItemPlugin):
    """
    Small plugin to delete files
    """

    def config(self):
        return [ ('FILE_OPS_ALLOW_DELETE_IMAGE', True,
                  'Add delete image to the menu.'),
	         ('FILE_OPS_ALLOW_DELETE_INFO', True,
                  'Add delete info to the menu.') ]

    def actions(self, item):
        """
        Create list of possible actions
        """
        if not item.parent or not item.parent.type == 'dir':
            # only activate this for directory listings
            return []

        if not hasattr(item, 'files') or not item.files:
            # no files to operate one
            return []

        actions = []

        if item.files.delete_possible():
            a = Action(_('Delete'), self.delete, 'delete')
            actions.append(a)
        if item.files.fxd_file and config.FILE_OPS_ALLOW_DELETE_INFO:
            a = Action(_('Delete info'), self.delete_info, 'delete_info')
            actions.append(a)
        if item.files.image and config.FILE_OPS_ALLOW_DELETE_IMAGE:
            Action(_('Delete image'), self.delete_image, 'delete_image')
            actions.append(a)

        return actions


    def delete(self, item):
        ConfirmBox(text=_('Do you wish to delete\n \'%s\'?') % item.name,
                   handler=Callback(self.__delete, item),
                   default_choice=1, handler_message=_('Deleting...')).show()


    def delete_info(self, item):
        ConfirmBox(text=_('Delete info about\n \'%s\'?') % item.name,
                   handler=Callback(self.__delete_info, item),
                   default_choice=1).show()


    def delete_image(self, arg=None, menuw=None):
        ConfirmBox(text=_('Delete image about\n \'%s\'?') % item.name,
                   handler=Callback(self.__delete_image, item),
                   default_choice=1).show()


    def __delete(self, item):
        item.files.delete()
        item.get_menustack().delete_submenu(True, True)


    def __delete_info(self, item):
        util.unlink(item.files.image)
        util.unlink(item.files.fxd_file)
        item.get_menustack().delete_submenu(True, True)


    def __delete_image(self, item):
        util.unlink(item.files.image)
        item.image = None
        if item.parent:
            item.image = item.parent.image
        item.get_menustack().delete_submenu(True, True)
