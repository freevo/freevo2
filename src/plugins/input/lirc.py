# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# lirc.py - A lirc input plugin for Freevo.
# -----------------------------------------------------------------------------
# $Id$
#
# This file handles the lirc input device and maps it to freevo events.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2007 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <https://github.com/Dischi>
# Maintainer:    Dirk Meyer <https://github.com/Dischi>
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

import kaa.input.lirc
from ... import core as freevo
from plugin import InputPlugin

class PluginInterface(InputPlugin):
    """
    Input plugin for lirc
    """
    def __init__(self):
        InputPlugin.__init__(self)
        kaa.input.lirc.init('freevo', freevo.config.input.plugin.lirc.lircrc)
        kaa.input.lirc.signal.connect(self.post_key)
