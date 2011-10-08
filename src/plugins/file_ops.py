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
# Copyright (C) 2002-2011 Krister Lagerstrom, Dirk Meyer, et al.
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

# freevo imports
from .. import core as freevo

# get logging object
log = logging.getLogger()

class PluginInterface(freevo.ItemPlugin):
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
            # no files to operate on
            return []
        actions = []
        if item.files.delete_possible():
            actions.append(freevo.Action(_('Delete'), self.delete, 'delete'))
        return actions

    def delete(self, item):
        txt = _('Do you wish to delete\n \'%s\'?') % item.name
        box = freevo.ConfirmWindow(txt, default_choice=1)
        box.buttons[0].connect(self.do_delete, item)
        box.show()

    def do_delete(self, item):
        item.files.delete()
        item.menustack.back_submenu(True, True)
