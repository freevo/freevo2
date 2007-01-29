# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# file_ops.py - Small file (item) operations
# -----------------------------------------------------------------------------
# $Id$
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
import logging

# kaa imports
from kaa.notifier import Callback

# freevo imports
from freevo.ui import config
from freevo.ui import plugin
from freevo.ui import util

from freevo.ui.menu import Action
from application import ConfirmWindow

# get logging object
log = logging.getLogger()


class PluginInterface(plugin.ItemPlugin):
    """
    Small plugin to delete files
    """

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
        txt = _('Do you wish to delete\n \'%s\'?') % item.name
        box = ConfirmWindow(txt, default_choice=1)
        box.buttons[0].connect(self.__delete, item)
        box.show()


    def delete_info(self, item):
        txt = _('Delete info about\n \'%s\'?') % item.name
        box = ConfirmWindow(txt, default_choice=1)
        box.buttons[0].connect(self.__delete_info, item)
        box.show()


    def delete_image(self, item):
        txt = _('Delete image about\n \'%s\'?') % item.name
        box = ConfirmWindow(txt, default_choice=1)
        box.buttons[0].connect(self.__delete_image, item)
        box.show()


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
