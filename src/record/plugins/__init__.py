# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# __init__.py - Recordserver plugin interface
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

# freevo plugin interface
import plugin

# internal list of plugins
list = []

class Plugin(plugin.Plugin):
    """
    Recordserver plugin.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        list.append(self)


    def start_recording(self, recording):
        """
        This function is called when the recording is started.
        """
        pass


    def stop_recording(self, recording):
        """
        This function is called when the recording is stopped.
        """
        pass
