# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# recorder.py - base class for recorder plugins
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

# python imports
import time
import os

# notifier
import notifier

# freevo imports
import config
import plugin

# list of possible plugins
plugins = []

class Plugin(plugin.Plugin):
    """
    Plugin template for a recorder plugin
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self.type = 'recorder'
        # reference to the recordserver
        self.server = None
        plugins.append(self)


    def create_fxd(self, rec):
        """
        Create fxd file for the recording
        TODO: write this function
        """
        pass


    def get_channel_list(self):
        raise Exception('plugin has not defined get_channel_list()')


    def schedule(self, recordings):
        raise Exception('plugin has not defined schedule()')
