# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# imlib2.py - Imlib2 output display
# -----------------------------------------------------------------------
# $Id$
#
# Note: This output plugin is work in progress
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/10/06 19:20:57  dischi
# add keyboard input plugin
#
# Revision 1.3  2004/08/23 14:29:46  dischi
# displays have information about animation support now
#
# Revision 1.2  2004/08/23 12:36:50  dischi
# cleanup, add doc
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

import plugin

# mevas imports
import mevas
from mevas.displays.imlib2canvas import Imlib2Canvas


class Display(Imlib2Canvas):
    def __init__(self, size, default=False):
        Imlib2Canvas.__init__(self, size)
        self.animation_possible = True
        plugin.activate( 'input.x11' )

    def hide(self):
        pass

    def show(self):
        pass

    def stop(self):
        pass
        
    def restart(self):
        pass
        
