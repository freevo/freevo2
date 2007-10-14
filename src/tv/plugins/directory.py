# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Show directory with recorded shows
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

# kaa imports
import kaa.beacon
import kaa.notifier

# freevo imports
from freevo.ui import config
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.menu import ActionItem
from freevo.ui.directory import DirItem

class PluginInterface(MainMenuPlugin):

    def items(self, parent):
        if config.tv.plugin.directory.path:
            return [ ActionItem(_('Recorded Shows'), parent, self.browse) ]
        return []

    @kaa.notifier.yield_execution()
    def browse(self, parent):
        record_dir = kaa.beacon.get(config.tv.plugin.directory.path)
        if isinstance(record_dir, kaa.notifier.InProgress):
            yield record_dir
            record_dir = record_dir.get_result()
        d = DirItem(record_dir, parent, type='tv')
        d.browse()
