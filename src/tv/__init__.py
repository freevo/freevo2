# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# __init__.py - Freevo tv plugin
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#                Rob Shortt <rob@tvcentric.com>
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

# freevo imports
import plugin


class PluginInterface(plugin.MainMenuPlugin):
    """
    Plugin interface to integrate the tv module into Freevo
    """
    def items(self, parent):
        """
        return the tv menu
        """
        # import here to avoid importing all this when some helpers only
        # want to import something from iside the tv directory

        import config
        from tvmenu import TVMenu
        from mainmenu import MainMenuItem

        # detect channels
        config.detect('channels')

        return [ TVMenu(parent) ]
