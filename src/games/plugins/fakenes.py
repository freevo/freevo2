# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fakenes.py - the Freevo fakenes support
# -----------------------------------------------------------------------------
#
# Add support for the fakenes NES emulator
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dan Casimiro <dan.casimiro@gmail.com>
# Maintainer:    Dan Casimiro <dan.casimiro@gmail.com>
#
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
import plugin
from emulator import Emulator

class PluginInterface(plugin.Plugin):
    """
    fakenes plugin for gaming.  This plugin allows you to use the fakenes
    nintendo emulator from within freevo.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        plugin.register(FakeNES(), plugin.GAMES, True)

class FakeNES(Emulator):
    """
    Use this interface to control fakenes.
    """
    def __init__(self):
        Emulator.__init__(self, 'fakenes', 'NES')
