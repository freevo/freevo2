# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imlib2.py - Imlib2 output display
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Andreas Büsching <crunchy@tzi.de>
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

__all__ = [ 'Display' ]

# python imports
import plugin

# mevas imports
from mevas.displays.imlib2canvas import Imlib2Canvas

# display imports
from display import Display as Base


class Display(Imlib2Canvas, Base):
    """
    Display class for imlib2 x11 output
    """
    def __init__(self, size, default=False):
        Imlib2Canvas.__init__(self, size)
        Base.__init__(self)
        plugin.activate( 'input.x11' )

        self._display.expose_callback = self.__expose


    def __expose( self, pos, size ):
        """
        Callback for expose events from X11
        """
        self._display.render( self._backing_store._image, pos, pos, size )

