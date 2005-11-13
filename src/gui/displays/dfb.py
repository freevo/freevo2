# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# dfb.py - DirectFB display
# -----------------------------------------------------------------------------
# $Id$
#
# This is a DirectFB output mechanism using mevas' DirectFBCanvas which
# in turn depends on pydirectfb - http://pydirectfb.sourceforge.net.
#
# TODO:
#     - Add a callback for DirectFB events.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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

__all__ = [ 'Display' ]

# mevas imports
from kaa.mevas.displays.directfbcanvas import DirectFBCanvas

# freevo imports
import config

# display imports
from display import Display as Base


class Display(DirectFBCanvas, Base):
    """
    Display class for DirectFB output
    """
    def __init__(self, size, default=False):
        DirectFBCanvas.__init__(self, size, config.GUI_DFB_LAYER)
        Base.__init__(self)
